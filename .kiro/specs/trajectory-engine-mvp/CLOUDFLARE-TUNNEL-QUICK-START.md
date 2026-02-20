# Cloudflare Tunnel - Quick Start Card

**5-Minute Setup for Demo Day**

---

## Prerequisites

✅ Backend running on `http://localhost:8000`  
✅ Frontend running on `http://localhost:3000`  
✅ Cloudflared installed

---

## Step 1: Install Cloudflared (One-Time)

```bash
winget install --id Cloudflare.cloudflared
```

Verify:
```bash
cloudflared --version
```

---

## Step 2: Start Tunnel (Demo Day)

**Option A: Use Batch Script**
```bash
cd arun_backend/backend
start_tunnel.bat
```

**Option B: Manual Command**
```bash
cloudflared tunnel --url http://localhost:8000
```

**Copy the tunnel URL** from output:
```
https://random-name-abc123.trycloudflare.com
```

---

## Step 3: Configure Frontend

Create `frontend/.env.local`:
```bash
VITE_API_URL=https://random-name-abc123.trycloudflare.com
```

**Replace with your actual tunnel URL!**

---

## Step 4: Restart Frontend

```bash
cd frontend
npm run dev
```

---

## Step 5: Test

1. Open: http://localhost:3000
2. Try logging in
3. Check browser console (should show tunnel URL in API calls)

---

## Troubleshooting

### CORS Error?
- Restart backend (CORS config updated)
- Clear browser cache
- Try incognito mode

### Tunnel URL Changed?
- Update `frontend/.env.local` with new URL
- Restart frontend

### 502 Bad Gateway?
- Verify backend is running on port 8000
- Check `http://localhost:8000` works locally

---

## Demo Day Checklist

- [ ] Start backend
- [ ] Start tunnel (copy URL)
- [ ] Update frontend/.env.local
- [ ] Restart frontend
- [ ] Test all features
- [ ] Keep tunnel terminal open during demo

---

## After Demo

```bash
# Stop tunnel (Ctrl+C in tunnel terminal)
# Delete or update frontend/.env.local
VITE_API_URL=http://localhost:8000
```

---

**Full Guide**: See `CLOUDFLARE-TUNNEL-SETUP.md`

