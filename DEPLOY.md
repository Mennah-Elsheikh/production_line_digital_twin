# Vercel Deployment Instructions

## Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create a Vercel account at https://vercel.com

## Deployment Steps

### 1. Login to Vercel
```bash
vercel login
```

### 2. Deploy to Production
```bash
vercel --prod
```

### 3. Environment Configuration
No environment variables are required for basic deployment.

### 4. Test Deployment
After deployment, Vercel will provide a URL (e.g., `https://your-project.vercel.app`).
Test the API endpoint: `https://your-project.vercel.app/api/health`

## Local Testing

### Test API Locally
```bash
uvicorn api.index:app --reload
```
Visit: `http://localhost:8000`

### Test Frontend Locally
Open `public/index.html` in browser or use a simple server:
```bash
python -m http.server 8080
```

## Notes
- Vercel has a 10-second timeout on Hobby tier
- Keep `SIM_TIME` under 300 minutes for web deployment
- The frontend automatically calls `/api/simulate` endpoint
