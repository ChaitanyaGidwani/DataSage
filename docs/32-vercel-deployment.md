# Deploying DataSage Frontend on Vercel

This guide explains how to deploy the DataSage Next.js frontend to **Vercel** with full zero-configuration support.

---

## 1. Quick Deploy via Vercel Dashboard

1. Push your repository to GitHub: `https://github.com/ChaitanyaGidwani/DataSage`.
2. Go to [Vercel Dashboard](https://vercel.com/new).
3. Select **Import Git Repository** and choose `ChaitanyaGidwani/DataSage`.
4. Configure the project:
   - **Framework Preset**: `Next.js` (automatically detected).
   - **Root Directory**: Leave as `./` (or optionally select `frontend`).
     - *Note: Both options are supported out-of-the-box thanks to root and nested `vercel.json` and `package.json` scripts.*
   - **Build Command**: `npm run build` (or `cd frontend && npm run build`).
   - **Output Directory**: `frontend/.next` (or `.next` if root is `frontend`).

---

## 2. Environment Variables Configuration

In your Vercel Project Settings under **Environment Variables**, add the following:

| Variable | Description | Example Value |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Public endpoint for backend API v1 | `https://api.yourdomain.com/api/v1` or `/api/v1` |
| `BACKEND_URL` *(Optional)* | Backend origin for Next.js internal proxy rewrites (bypasses CORS) | `https://datasage-backend.onrender.com` |
| `NEXT_PUBLIC_APP_NAME` | Branding title | `DataSage` |

### Architecture Options

#### Option A: Direct Backend Call (Standard)
- Set `NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1` (where your FastAPI backend is deployed, e.g., Render, Railway, AWS EC2, or Fly.io).
- Ensure your backend has your Vercel domain in its `CORS_ORIGINS` environment variable (e.g., `https://datasage.vercel.app`).

#### Option B: Next.js Rewrite Proxy (Zero CORS)
- Set `NEXT_PUBLIC_API_URL=/api/v1`.
- Set `BACKEND_URL=https://api.yourdomain.com`.
- Next.js will automatically proxy all `/api/v1/*` browser requests to the backend server-side, eliminating CORS issues entirely.

---

## 3. Local Verification

To verify the production build locally before triggering a Vercel deployment:

```bash
# From repository root
npm run build
```

The build will compile with 0 errors and produce optimized static & dynamic server routes.
