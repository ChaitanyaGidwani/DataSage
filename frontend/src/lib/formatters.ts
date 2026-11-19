/**
 * Formatting utilities for DataSage.
 */

/**
 * Format a number as Indian Rupees (INR).
 * Examples: 7500000 → "₹75.00 L", 15000000 → "₹1.50 Cr"
 */
export function formatINR(amount: number): string {
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  }
  if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} L`;
  }
  return `₹${amount.toLocaleString('en-IN')}`;
}

/**
 * Format area in square feet.
 */
export function formatArea(sqft: number): string {
  return `${sqft.toLocaleString('en-IN')} sq ft`;
}

/**
 * Format a price-per-sqft value.
 */
export function formatPricePerSqft(price: number): string {
  return `₹${price.toLocaleString('en-IN')}/sq ft`;
}

/**
 * Format a date string to locale format.
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

/**
 * Format distance in meters to a readable string.
 */
export function formatDistance(meters: number): string {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)} km`;
  }
  return `${Math.round(meters)} m`;
}

/**
 * Format a property type enum to display text.
 */
export function formatPropertyType(type: string): string {
  const map: Record<string, string> = {
    apartment: 'Apartment',
    builder_floor: 'Builder Floor',
    house: 'House',
    plot: 'Plot',
  };
  return map[type] || type;
}

/**
 * Format a percentage with sign.
 */
export function formatPercent(value: number, decimals = 1): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format direction facing (e.g. north_west -> North West).
 */
export function formatFacing(facing: string): string {
  if (!facing) return '';
  return facing
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Format furnishing status (e.g. semi_furnished -> Semi Furnished).
 */
export function formatFurnishing(furnishing: string): string {
  if (!furnishing) return '';
  return furnishing
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

