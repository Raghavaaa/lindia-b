# Environment Variables Setup Guide

## Required Environment Variables for Vercel

Add these to your Vercel project at: https://vercel.com/raghavaaa/lindia-f-work/settings/environment-variables

### Current Variables (Keep These)

```env
NEXT_PUBLIC_BACKEND_URL=https://lindia-b-production.up.railway.app
GOOGLE_CLIENT_ID=1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-apCnXwM4drLbZno27pXAQntkSf_
NEXTAUTH_URL=https://lindia-f-work.vercel.app
```

### ⚠️ CRITICAL: Add This New Variable

```env
NEXTAUTH_SECRET=9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
```

This secret was generated using:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## How to Add to Vercel

1. Go to: https://vercel.com
2. Select your project: `lindia-f-work`
3. Go to: Settings → Environment Variables
4. Click "Add" button
5. Enter:
   - Key: `NEXTAUTH_SECRET`
   - Value: `9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=`
   - Environment: Production, Preview, Development (select all)
6. Click "Save"
7. Redeploy the app:
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Click "Redeploy"

## Verify Google Cloud Console Settings

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2...`
3. Click to edit
4. Ensure these URIs are in "Authorized redirect URIs":
   ```
   https://lindia-f-work.vercel.app/api/auth/callback/google
   ```
5. Ensure this domain is in "Authorized JavaScript origins":
   ```
   https://lindia-f-work.vercel.app
   ```
6. Click "Save"
7. Wait 5 minutes for changes to propagate

## Complete Environment Variable List

| Variable | Value | Where |
|----------|-------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://lindia-b-production.up.railway.app` | Vercel |
| `NEXTAUTH_URL` | `https://lindia-f-work.vercel.app` | Vercel |
| `NEXTAUTH_SECRET` | `9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=` | Vercel ⚠️ ADD THIS |
| `GOOGLE_CLIENT_ID` | `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2...` | Vercel (existing) |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-apCnXwM4drLbZno27pXAQntkSf_...` | Vercel (existing) |

## For Local Development

Create a `.env.local` file in the `/frontend` directory:

```env
NEXT_PUBLIC_BACKEND_URL=https://lindia-b-production.up.railway.app
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
GOOGLE_CLIENT_ID=1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-apCnXwM4drLbZno27pXAQntkSf_
```

**Note:** For local development, also add `http://localhost:3000/api/auth/callback/google` to your Google Cloud Console authorized redirect URIs.

## Verification

After adding `NEXTAUTH_SECRET` and redeploying, test:

```bash
curl -I https://lindia-f-work.vercel.app/api/auth/signin/google
```

Should see:
```
Location: https://accounts.google.com/o/oauth2/v2/auth?...
```

NOT:
```
Location: /login?error=google
```

