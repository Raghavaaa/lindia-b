# Debug OAuth 400 Error - NEXTAUTH_SECRET is Set

## Current Status

✅ **Confirmed Working:**
- NEXTAUTH_SECRET is set in Vercel: `9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=`
- NextAuth API routes exist and respond
- Providers endpoint works: `{"google":{"id":"google",...}}`
- Session endpoint works
- Code is deployed

❌ **Still Broken:**
- `/api/auth/signin/google` returns HTTP 400
- Should return HTTP 302 redirect to Google

## Possible Causes (NEXTAUTH_SECRET is NOT the issue)

### 1. Google OAuth Credentials Issue

**Check in Vercel Environment Variables:**
- `GOOGLE_CLIENT_ID` should be: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com`
- `GOOGLE_CLIENT_SECRET` should be: `GOCSPX-apCnXwM4drLbZno27pXAQntkSf_`

### 2. Google Cloud Console Redirect URI

**Required redirect URI in Google Console:**
```
https://lindia-f-work.vercel.app/api/auth/callback/google
```

**Check:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find OAuth Client: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2`
3. Verify "Authorized redirect URIs" contains:
   ```
   https://lindia-f-work.vercel.app/api/auth/callback/google
   ```

### 3. Deployment Issue

The code might not be fully deployed or there might be a build error.

**Solution:** Force redeploy in Vercel:
1. Go to Deployments tab
2. Click "..." on latest deployment
3. Click "Redeploy"

### 4. NextAuth Configuration Issue

There might be an issue with the NextAuth configuration in the deployed code.

## Debug Steps

### Step 1: Verify All Environment Variables in Vercel

Check that these are set correctly:
```env
NEXTAUTH_URL=https://lindia-f-work.vercel.app
NEXTAUTH_SECRET=9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
GOOGLE_CLIENT_ID=1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-apCnXwM4drLbZno27pXAQntkSf_
```

### Step 2: Check Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find OAuth Client ID: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2`
3. Verify:
   - **Authorized JavaScript origins:**
     ```
     https://lindia-f-work.vercel.app
     ```
   - **Authorized redirect URIs:**
     ```
     https://lindia-f-work.vercel.app/api/auth/callback/google
     ```

### Step 3: Force Redeploy

1. Go to Vercel → Deployments
2. Click "..." on latest deployment
3. Click "Redeploy"
4. Wait 3-5 minutes

### Step 4: Test Again

```bash
curl -I https://lindia-f-work.vercel.app/api/auth/signin/google
```

Expected: `HTTP/2 302` with `location: https://accounts.google.com/...`

## Most Likely Issue

Based on the symptoms (providers work, CSRF works, but signin fails), this is most likely:

1. **Google OAuth credentials invalid** in Vercel environment variables
2. **Redirect URI mismatch** in Google Cloud Console
3. **Need to redeploy** after adding NEXTAUTH_SECRET

## Quick Fix

1. **Verify Google Console redirect URI** (most common issue)
2. **Force redeploy** in Vercel
3. **Test again**

The fact that providers and CSRF work means NextAuth is deployed correctly, but Google OAuth configuration has an issue.
