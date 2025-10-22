# Deploy Google Auth - FINAL STEPS

## 🚀 IMMEDIATE ACTIONS REQUIRED

### Step 1: Add NEXTAUTH_SECRET to Vercel (CRITICAL)

1. Go to: https://vercel.com/raghavaaas-projects/lindia-f-work/settings/environment-variables

2. Add new variable:
   ```
   Key: NEXTAUTH_SECRET
   Value: 9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
   ```

3. Apply to: Production, Preview, Development (check all 3)

4. Click "Save"

### Step 2: Verify Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials

2. Find OAuth Client: `1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2`

3. **MUST HAVE** this exact redirect URI:
   ```
   https://lindia-f-work.vercel.app/api/auth/callback/google
   ```

4. **MUST HAVE** this in JavaScript origins:
   ```
   https://lindia-f-work.vercel.app
   ```

5. Click "Save" and wait 5 minutes

### Step 3: Deploy Code Changes

```bash
cd /Users/raghavankarthik/lindia-b

# Push to git
git add .
git commit -m "Add real Google OAuth authentication"
git push

# Vercel will auto-deploy
```

OR manually deploy:
```bash
cd frontend
npx vercel --prod
```

### Step 4: Test After Deployment

```bash
# Test OAuth endpoint
curl -I https://lindia-f-work.vercel.app/api/auth/signin/google

# Should see:
# Location: https://accounts.google.com/o/oauth2/v2/auth?...

# NOT:
# Location: /login?error=google
```

## 📋 Complete Checklist

- [ ] NEXTAUTH_SECRET added to Vercel
- [ ] Vercel redeployed (automatic after git push)
- [ ] Google Cloud redirect URI verified
- [ ] Wait 5 minutes after Google changes
- [ ] Test OAuth endpoint (should redirect to Google)
- [ ] Test actual sign-in flow in browser

## 🧪 Browser Test

1. Go to: https://lindia-f-work.vercel.app/login
2. Click "Sign in with Google"
3. Should redirect to Google login
4. After Google auth, should redirect to /app
5. You're logged in! ✅

## ⚠️ If It Doesn't Work

### Error: "redirect_uri_mismatch"
- Check Google Console redirect URI is EXACT
- Must be: `https://lindia-f-work.vercel.app/api/auth/callback/google`
- Wait 5 minutes after changing

### Error: "Configuration error"
- NEXTAUTH_SECRET not set in Vercel
- Redeploy after adding it

### Error: "error=google"
- Google credentials invalid
- Or redirect URI wrong
- Check both Google Console AND Vercel env vars

## 📦 Files Changed

✅ `/frontend/package.json` - Added next-auth dependency
✅ `/frontend/src/app/layout.tsx` - Added SessionProvider
✅ `/frontend/src/components/SessionProvider.tsx` - Created wrapper
✅ `/frontend/src/app/login/page.tsx` - Real Google sign in
✅ `/lib/auth-config.ts` - NextAuth configuration
✅ `/app/api/auth/[...nextauth]/route.ts` - NextAuth API route

## 🎯 What Changed

**BEFORE:**
- Button clicked → `simulateGoogleSignIn()` → Just showed form
- No real auth
- localStorage only

**NOW:**
- Button clicked → `signIn("google")` → Redirects to Google
- Real OAuth flow
- Server-side session
- Secure authentication ✅

## 🔧 Local Development

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_BACKEND_URL=https://lindia-b-production.up.railway.app
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=9I3S3NePfVM4X/HoM/M7h3o1MLWr8TV2LniGjVeMCPA=
GOOGLE_CLIENT_ID=1030638772763-q0d7g01rikdb0orl1s15a1n7k7u5vqu2.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-apCnXwM4drLbZno27pXAQntkSf_
EOF

# Run dev server
npm run dev

# Open http://localhost:3000/login
```

**Note:** Also add `http://localhost:3000/api/auth/callback/google` to Google Console for local dev.

## ✅ SUCCESS CRITERIA

When working, you'll see:

1. Click "Sign in with Google" → Redirects to accounts.google.com
2. Authorize app → Redirects back to your site
3. Automatically logged in
4. Can access /app with session
5. Session persists across page refreshes

DONE! 🎉

