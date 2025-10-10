# Authentication Setup Guide

## Summary of Changes

### ✅ Security Improvements
- **httpOnly Cookies**: Tokens now stored in secure httpOnly cookies (not localStorage)
- **XSS Protection**: JavaScript can't access authentication tokens
- **Automatic Token Handling**: Cookies sent automatically with every request

### ✅ Features Added
1. **Google One Tap Sign-In**: Faster, more convenient authentication
2. **Persistent Sessions**: No more logging out on refresh
3. **Proper Logout**: Backend clears cookies securely
4. **Session Verification**: `/auth/me` endpoint checks authentication status

---

## Backend Environment Variables (Render)

Set these in your Render user-service:

```bash
# Required
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=https://healprint.xyz/auth/google/callback

# Optional (recommended)
SECRET_KEY=your_secure_random_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://healprint.xyz,https://www.healprint.xyz,https://healprint.vercel.app
```

---

## Frontend Environment Variables (Vercel)

Set these in your Vercel project:

```bash
# Required for Google One Tap
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here

# API URLs
VITE_USER_API_URL=https://healprint-server-auth.onrender.com
VITE_CHAT_API_URL=https://healprint-server-chat.onrender.com
VITE_GOOGLE_REDIRECT_URI=https://healprint.xyz/auth/google/callback
```

---

## Google Cloud Console Setup

### 1. Enable Google One Tap

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your OAuth 2.0 Client ID
3. Under **"Authorized JavaScript origins"**, add:
   - `https://healprint.xyz`
   - `https://www.healprint.xyz`
   - `http://localhost:5173` (for development)

4. Under **"Authorized redirect URIs"**, add:
   - `https://healprint.xyz/auth/google/callback`

5. Click **Save**

### 2. Get Your Client ID

- Your Client ID will look like: `123456789-abc123def456.apps.googleusercontent.com`
- Use the same Client ID for both frontend and backend

---

## New API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/google/url` | Get OAuth URL |
| POST | `/auth/google/callback` | OAuth callback handler |
| POST | `/auth/google/token` | **NEW** - Google One Tap login |
| GET | `/auth/me` | **NEW** - Get current user from cookie |
| POST | `/auth/logout` | **NEW** - Logout (clear cookie) |
| POST | `/login` | Email/password login |
| POST | `/register` | User registration |

### Cookie Settings

```javascript
{
  httponly: true,      // Not accessible by JavaScript
  secure: true,        // HTTPS only
  samesite: "none",    // Cross-site requests
  max_age: 1800,       // 30 minutes
  domain: ".healprint.xyz"  // All subdomains
}
```

---

## Testing

### 1. Deploy Backend
```bash
git add .
git commit -m "Add secure cookie auth and Google One Tap"
git push
```
Render will auto-deploy.

### 2. Deploy Frontend
```bash
cd healprint-client
npm run build
vercel --prod
```

### 3. Test Flow
1. Visit `https://healprint.xyz/login`
2. You should see Google One Tap prompt automatically
3. Click to sign in with Google
4. You'll be logged in and redirected to `/chat`
5. Refresh the page - you should stay logged in ✅

---

## Troubleshooting

### "One Tap not displayed"

**Issue**: Google One Tap doesn't appear

**Solutions**:
1. Check `VITE_GOOGLE_CLIENT_ID` is set in Vercel
2. Verify JavaScript origins in Google Cloud Console
3. Clear browser cookies and try again
4. Check browser console for error messages

### "Logged out on refresh"

**Issue**: User gets logged out when refreshing page

**Solutions**:
1. Check `CORS_ORIGINS` includes your domain
2. Verify `credentials: 'include'` in all fetch requests
3. Check cookie domain is set to `.healprint.xyz`
4. Ensure backend `/auth/me` endpoint is working

### "400 Bad Request" on OAuth callback

**Issue**: OAuth callback fails

**Solutions**:
1. Ensure redirect URI in Google Console matches exactly
2. Check `GOOGLE_REDIRECT_URI` matches in both services
3. Verify `GOOGLE_CLIENT_SECRET` is set correctly
4. Check Render logs for detailed error messages

---

## Security Best Practices ✅

- ✅ Tokens in httpOnly cookies (not localStorage)
- ✅ HTTPS-only cookies (secure flag)
- ✅ SameSite protection
- ✅ CORS properly configured
- ✅ JWT token expiration (30 min)
- ✅ Token validation on every request

---

## Next Steps

1. **Set environment variables** on Render and Vercel
2. **Configure Google Cloud Console** with correct origins/redirects
3. **Deploy** both services
4. **Test** login flow
5. **Monitor** Render logs for any issues

🎉 Your authentication is now secure and user-friendly!

