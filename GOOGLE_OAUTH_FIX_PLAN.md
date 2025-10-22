# Google OAuth Fix Plan

## Current Status Analysis

✅ **Working:**
- NextAuth API routes exist and respond
- Providers endpoint: `{"google":{"id":"google",...}}`
- CSRF endpoint: `{"csrfToken":"2002d33edfc55d42f2d75146288066246dfaae88284045486e56d1e745af7cb4"}`
- NEXTAUTH_SECRET is set in Vercel
- Code is deployed

❌ **Not Working:**
- `/api/auth/signin/google` returns HTTP 400
- Should return HTTP 302 redirect to Google

## Root Cause Analysis

Since NextAuth is working (providers, CSRF), but signin fails, the issue is likely:

1. **Google OAuth credentials invalid** in Vercel environment variables
2. **Redirect URI mismatch** in Google Cloud Console
3. **Google OAuth client configuration** issue

## Fix Plan

### Step 1: Verify Vercel Environment Variables

Check these are set correctly in Vercel:
```env
NEXTAUTH_URL=https://lindia-f-work.vercel.app
NEXTAUTH_SECRET=9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
GOOGLE_CLIENT_ID=1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-apCnXwM4drLbZno27pXAQntkSf_
```

### Step 2: Verify Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find OAuth Client: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2`
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

### Step 4: Test

```bash
curl -I https://lindia-f-work.vercel.app/api/auth/signin/google
```

Expected: `HTTP/2 302` with `location: https://accounts.google.com/...`

## Most Likely Issue

Based on symptoms, this is most likely a **redirect URI mismatch** in Google Cloud Console.

The NextAuth configuration is correct, but Google is rejecting the OAuth request because the redirect URI doesn't match what's configured in Google Console.
