"""ML Pipeline for training the property valuation XGBoost model."""

import asyncio
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Import DB components and models
from datasage.core.database import async_session_factory
from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.core.config import settings
from datasage.models.valuation import ModelVersion

async def extract_data() -> pd.DataFrame:
    """Extract property and locality data from PostgreSQL asynchronously."""
    print("Extracting data from database...")
    async with async_session_factory() as session:
        # We need property info and its locality info
        stmt = (
            select(Property)
            .options(selectinload(Property.locality))
            .where(Property.is_active == True)
        )
        result = await session.execute(stmt)
        properties = result.scalars().all()
        
        # Build list of dicts for pandas
        data = []
        for p in properties:
            locality_avg_price = None
            if hasattr(p, 'locality') and p.locality:
                locality_avg_price = p.locality.avg_price_per_sqft
            
            data.append({
                "id": str(p.id),
                "city_id": p.city_id,
                "locality_id": p.locality_id,
                "bhk": p.bhk,
                "area_sqft": p.area_sqft,
                "floor_number": p.floor_number or 1,
                "total_floors": p.total_floors or 1,
                "construction_year": p.construction_year or 2026,
                "parking_count": p.parking_count,
                "balcony_count": p.balcony_count,
                "bathroom_count": p.bathroom_count or p.bhk,
                "cached_location_score": p.cached_location_score or 50.0,
                "locality_avg_price": locality_avg_price or (p.listing_price / p.area_sqft),
                "listing_price": p.listing_price,
            })
            
        df = pd.DataFrame(data)
        print(f"Extracted {len(df)} properties.")
        return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create features for the valuation model."""
    print("Engineering features...")
    # Age of property (assume current year is 2026 as per requirements)
    df["age"] = 2026 - df["construction_year"]
    df["age"] = df["age"].clip(lower=0)
    
    # Fill any missing values
    df["floor_number"] = df["floor_number"].fillna(1)
    df["cached_location_score"] = df["cached_location_score"].fillna(df["cached_location_score"].median())
    df["locality_avg_price"] = df["locality_avg_price"].fillna(df["locality_avg_price"].median())
    
    return df

async def main():
    print("=== DataSage Model Training Pipeline ===")
    
    # 1. Load Data
    df = await extract_data()
    if df.empty:
        print("No data found. Please run database seeding first.")
        return
        
    # 2. Feature Engineering
    df = engineer_features(df)
    
    # Target variable
    y = df["listing_price"]
    
    # Features
    features = [
        "bhk", 
        "area_sqft", 
        "floor_number", 
        "age",
        "parking_count",
        "balcony_count",
        "bathroom_count",
        "cached_location_score",
        "locality_avg_price"
    ]
    X = df[features]
    
    # 3. Train/Test Split (stratified by city_id if possible, or just random)
    # Using simple train_test_split, stratifying by city_id to ensure representation
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=df["city_id"]
        )
    except ValueError:
        # Fallback if classes are too small for stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # 4. Train Model
    print("Training XGBoost Regressor...")
    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # 5. Evaluate Model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n--- Evaluation Metrics (Test Set) ---")
    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")
    
    # 6. Save Model
    os.makedirs(settings.ML_MODEL_DIR, exist_ok=True)
    model_path = os.path.join(settings.ML_MODEL_DIR, settings.ML_VALUATION_MODEL_NAME)
    
    # Package model with its expected feature names for safety
    model_artifact = {
        "model": model,
        "features": features,
        "version": "1.0.0",
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        },
        "trained_at": datetime.utcnow().isoformat()
    }
    
    joblib.dump(model_artifact, model_path)
    print(f"\nModel saved successfully to {model_path}")
    
    # 7. Register Model Version in Database
    async with async_session_factory() as session:
        # Check if version exists
        existing = await session.execute(
            select(ModelVersion).where(ModelVersion.version_label == "v1.0.0")
        )
        if not existing.scalar_one_or_none():
            new_version = ModelVersion(
                version_label="v1.0.0",
                algorithm="xgboost",
                is_active=True,
                mae=mae,
                r_squared=r2,
                training_sample_count=X_train.shape[0],
                hyperparameters={"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1},
                trained_at=datetime.utcnow()
            )
            session.add(new_version)
            await session.commit()
            print("Registered ModelVersion v1.0.0 in database.")
        else:
            print("ModelVersion v1.0.0 already exists in database.")

if __name__ == "__main__":
    asyncio.run(main())
