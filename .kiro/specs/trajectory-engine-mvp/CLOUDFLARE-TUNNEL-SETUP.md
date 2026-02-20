# Cloudflare Tunnel Setup Guide

**Date**: February 20, 2026  
**Purpose**: Expose local backend to internet for remote demo  
**Cost**: FREE (no Cloudflare account needed)

---

## What is Cloudflare Tunnel?

Cloudflare Tunnel creates a secure connection between your local backend (running on `localhost:8000`) and the internet through Cloudflare's network. This allows:

- ✅ Remote demo without deploying to a server
- ✅ Secure HTTPS automatically
- ✅ No port forwarding or firewall configuration
- ✅ Works with local Ollama, Qdrant, and PostgreSQL
- ✅ Anyone with the URL can access your API

---

## Installation

### Step 1: Download Cloudflare Tunnel (cloudflared)

**Option A: Using winget (Recommended for Windows)**
```bash
winget install --id Cloudflare.cloudflared
```

**Option B: Manual Download**
1. Go to: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
2. Download Windows installer
3. Run installer
4. Verify installation:
```bash
cloudflared --version
```

---

## Quick Start (For Demo Day)

### Step 1: Start Your Backend

Make sure your backend is running:
```bash
cd arun_backend/backend
python -m uvicorn app.main:app --reload --port 8000
```

Verify it's working: http://localhost:8000

### Step 2: Start Cloudflare Tunnel

Open a **new terminal** and run:
```bash
cloudflared tunnel --url http://localhost:8000
```

You'll see output like:
```
2026-02-20T10:30:00Z INF +--------------------------------------------------------------------------------------------+
2026-02-20T10:30:00Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2026-02-20T10:30:00Z INF |  https://random-name-abc123.trycloudflare.com                                              |
2026-02-20T10:30:00Z INF +--------------------------------------------------------------------------------------------+
```

**Copy this URL** - this is your public backend URL!

### Step 3: Update Frontend Configuration

Create a config file for API URL:

```typescript
// frontend/src/config.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Create environment file:

```bash
# frontend/.env.local
VITE_API_URL=https://random-name-abc123.trycloudflare.com
```

**Replace** `random-name-abc123.trycloudflare.com` with your actual tunnel URL.

### Step 4: Update API Calls

Update your API service to use the config:

```typescript
// frontend/src/services/api.ts (or wherever you make API calls)
import { API_BASE_URL } from '../config';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Step 5: Update Backend CORS

Update CORS to allow tunnel domain:

```python
# arun_backend/backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend
        "https://*.trycloudflare.com",  # Cloudflare tunnel (wildcard)
        # Or specify exact URL:
        # "https://random-name-abc123.trycloudflare.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart your backend** after making this change.

### Step 6: Test the Connection

1. Open your frontend: http://localhost:3000
2. Try logging in or making an API call
3. Check browser console for any CORS errors
4. Verify requests are going to the tunnel URL

---

## Testing Your Setup

### Test 1: Direct API Call

Open browser and visit:
```
https://your-tunnel-url.trycloudflare.com/
```

You should see:
```json
{"status": "Trajectory-X backend running"}
```

### Test 2: Health Check

```
https://your-tunnel-url.trycloudflare.com/api/admin/health
```

Should return:
```json
{"status": "healthy"}
```

### Test 3: Frontend Login

1. Open frontend: http://localhost:3000/login
2. Try logging in with test credentials
3. Check Network tab in browser DevTools
4. Verify requests go to tunnel URL

---

## Important Notes

### Tunnel URL Changes

⚠️ **The tunnel URL changes every time you restart cloudflared**

When you restart the tunnel:
1. Copy the new URL from terminal
2. Update `frontend/.env.local` with new URL
3. Restart frontend dev server

### Keeping Tunnel Running

The tunnel must stay running during your demo:
- Don't close the terminal window
- If it disconnects, restart with same command
- URL will change if you restart

### Performance

- Expect 100-300ms additional latency (requests go through Cloudflare)
- LLM responses may take 1.5-2.5s instead of 0.5-1s
- Still acceptable for demo purposes

---

## Alternative: Named Tunnel (Persistent URL)

If you want a **persistent URL** that doesn't change:

### Step 1: Create Cloudflare Account (Free)

1. Go to: https://dash.cloudflare.com/sign-up
2. Create free account
3. Verify email

### Step 2: Create Named Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create a named tunnel
cloudflared tunnel create trajectory-engine

# Route tunnel to a domain (if you have one)
cloudflared tunnel route dns trajectory-engine api.yourdomain.com

# Run the tunnel
cloudflared tunnel run trajectory-engine
```

### Step 3: Configure Tunnel

Create config file: `~/.cloudflared/config.yml`

```yaml
tunnel: trajectory-engine
credentials-file: C:\Users\YourName\.cloudflared\<tunnel-id>.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

**Pros**:
- ✅ Persistent URL (doesn't change)
- ✅ Custom domain support
- ✅ Better for long-term use

**Cons**:
- ❌ Requires Cloudflare account
- ❌ More setup steps
- ❌ Need a domain (optional)

---

## Troubleshooting

### Issue 1: CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**:
1. Check backend CORS configuration includes tunnel URL
2. Restart backend after CORS changes
3. Clear browser cache
4. Try incognito mode

### Issue 2: Tunnel Won't Start

**Symptom**: `cloudflared` command not found

**Solution**:
```bash
# Verify installation
cloudflared --version

# If not found, reinstall
winget install --id Cloudflare.cloudflared

# Restart terminal
```

### Issue 3: Backend Not Accessible

**Symptom**: Tunnel URL returns 502 Bad Gateway

**Solution**:
1. Verify backend is running on port 8000
2. Check `http://localhost:8000` works locally
3. Restart tunnel
4. Check firewall isn't blocking cloudflared

### Issue 4: Slow Response Times

**Symptom**: API calls take 5+ seconds

**Solution**:
- This is normal for LLM calls (1-2s) + tunnel latency (100-300ms)
- For demo, explain this is due to tunnel overhead
- In production, backend would be deployed closer to users

---

## Demo Day Checklist

### Before Demo (30 minutes before)

- [ ] Start backend: `uvicorn app.main:app --reload --port 8000`
- [ ] Start Cloudflare tunnel: `cloudflared tunnel --url http://localhost:8000`
- [ ] Copy tunnel URL from terminal
- [ ] Update `frontend/.env.local` with tunnel URL
- [ ] Restart frontend: `npm run dev`
- [ ] Test login flow
- [ ] Test trajectory prediction
- [ ] Test all major features
- [ ] Keep tunnel terminal window open

### During Demo

- [ ] Don't close tunnel terminal
- [ ] Monitor tunnel for disconnections
- [ ] Have backup plan (local demo if tunnel fails)
- [ ] Explain tunnel is for demo only (not production)

### After Demo

- [ ] Stop tunnel (Ctrl+C)
- [ ] Revert frontend to localhost
- [ ] Delete `.env.local` or update to localhost

---

## Security Considerations

### What's Exposed

When tunnel is running, your backend API is **publicly accessible**:
- ✅ Anyone with URL can access API
- ✅ JWT authentication still required for protected routes
- ✅ Database is still on Arun's PC (not exposed)
- ✅ Ollama/Qdrant are local (not exposed)

### Best Practices

1. **Only run tunnel during demo** - Don't leave it running 24/7
2. **Use strong passwords** - For demo accounts
3. **Don't share tunnel URL publicly** - Only with demo audience
4. **Monitor access logs** - Check for unexpected requests
5. **Stop tunnel after demo** - Close terminal when done

---

## Cost Breakdown

### Quick Tunnel (Recommended for MVP)
- **Cost**: $0 (completely free)
- **Limits**: None for demo purposes
- **Account**: Not required

### Named Tunnel (Optional)
- **Cost**: $0 (free tier)
- **Limits**: Unlimited bandwidth on free tier
- **Account**: Required (free)

---

## Alternative Solutions (Not Recommended for MVP)

### ngrok
- Similar to Cloudflare Tunnel
- Free tier has limits (40 connections/minute)
- Requires account for persistent URLs

### localtunnel
- Open source alternative
- Less reliable than Cloudflare
- No HTTPS by default

### Port Forwarding
- Requires router configuration
- Security risks
- Exposes your home IP

**Verdict**: Cloudflare Tunnel is the best option for your MVP demo.

---

## Summary

**For Local Development (Days 1-14)**:
- Use `http://localhost:8000` (no tunnel needed)
- Fast, simple, free

**For Demo Day (Day 15)**:
- Use Cloudflare Tunnel
- 5-minute setup
- Secure HTTPS
- Remote access

**Commands to Remember**:
```bash
# Start tunnel
cloudflared tunnel --url http://localhost:8000

# Update frontend
# Edit frontend/.env.local with tunnel URL

# Restart frontend
npm run dev
```

---

## Next Steps

1. **Install cloudflared now** (takes 2 minutes)
2. **Test tunnel once** to verify it works
3. **Continue building dashboard** (Task 24)
4. **Use tunnel on demo day** (Day 15)

---

**Questions?**
- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Troubleshooting: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/troubleshooting/

**Ready to continue with Task 24 (Dashboard UI)?**

