# Cloudflare Tunnel Setup - README

This project is configured to use **Cloudflare Tunnel** for remote demos while keeping all development local.

---

## Quick Links

- **Full Setup Guide**: `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-SETUP.md`
- **Quick Start (5 min)**: `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-QUICK-START.md`
- **Summary**: `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-SUMMARY.md`

---

## What is This?

Cloudflare Tunnel allows you to:
- ✅ Demo your project remotely without deploying
- ✅ Keep backend, Ollama, and Qdrant running locally
- ✅ Get secure HTTPS automatically
- ✅ Share with anyone via a public URL
- ✅ **Completely FREE** (no account needed)

---

## When to Use

### Local Development (Most of the time)
**Don't use tunnel** - Just run backend and frontend locally:
```bash
# Backend
cd arun_backend/backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Remote Demo (Demo Day)
**Use tunnel** - Expose backend to internet:
```bash
# Start tunnel
cd arun_backend/backend
start_tunnel.bat

# Update frontend config with tunnel URL
# See Quick Start guide
```

---

## Installation (One-Time)

```bash
winget install --id Cloudflare.cloudflared
```

Verify:
```bash
cloudflared --version
```

---

## Demo Day Setup (5 Minutes)

1. **Start backend** (Terminal 1)
   ```bash
   cd arun_backend/backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start tunnel** (Terminal 2)
   ```bash
   cd arun_backend/backend
   start_tunnel.bat
   ```
   **Copy the tunnel URL** from output!

3. **Configure frontend** (Terminal 3)
   ```bash
   cd frontend
   echo VITE_API_URL=https://your-tunnel-url.trycloudflare.com > .env.local
   npm run dev
   ```

4. **Test**: Open http://localhost:3000 and try logging in

---

## Files Modified

### Configuration
- `frontend/src/config.ts` - API URL configuration
- `frontend/.env.example` - Environment variable template
- `arun_backend/backend/app/main.py` - CORS updated for tunnel

### Scripts
- `arun_backend/backend/start_tunnel.bat` - Tunnel startup script

### Documentation
- `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-SETUP.md` - Full guide
- `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-QUICK-START.md` - Quick reference
- `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-SUMMARY.md` - Summary

---

## Troubleshooting

### CORS Errors
- Restart backend
- Clear browser cache
- Try incognito mode

### Tunnel URL Changed
- Update `frontend/.env.local` with new URL
- Restart frontend

### 502 Bad Gateway
- Verify backend is running on port 8000
- Check http://localhost:8000 works

**Full troubleshooting**: See `CLOUDFLARE-TUNNEL-SETUP.md`

---

## Security Notes

- Tunnel exposes your backend API publicly
- JWT authentication still protects routes
- Only run tunnel during demos
- Stop tunnel after demo (Ctrl+C)

---

## Cost

**$0** - Completely free, no account needed

---

## Questions?

See the full setup guide: `.kiro/specs/trajectory-engine-mvp/CLOUDFLARE-TUNNEL-SETUP.md`

