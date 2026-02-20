# Start Qdrant - Quick Guide

## Current Status

❌ Docker Desktop is NOT running
✅ Docker is installed (version 29.2.1)
✅ Qdrant setup script exists
✅ Qdrant storage directory exists

## Steps to Start Qdrant

### Step 1: Start Docker Desktop

**You need to manually start Docker Desktop:**

1. Press `Windows Key` and search for "Docker Desktop"
2. Click to open Docker Desktop
3. Wait for Docker to fully start (whale icon in system tray should be steady)
4. This usually takes 30-60 seconds

### Step 2: Run Qdrant Setup Script

Once Docker Desktop is running, execute:

```bash
cd arun_backend/backend
setup_qdrant.bat
```

This script will:
- Pull the Qdrant Docker image (if not already downloaded)
- Create a container named "qdrant"
- Start Qdrant on ports 6333 (HTTP) and 6334 (gRPC)
- Mount the `qdrant_storage` directory for data persistence

### Step 3: Verify Qdrant is Running

Open your browser and go to:
```
http://localhost:6333/dashboard
```

You should see the Qdrant web interface.

## Alternative: Start Existing Container

If the Qdrant container already exists, you can just start it:

```bash
docker start qdrant
```

## After Qdrant is Running

Once Qdrant is running, you need to:

1. **Re-run the import script** to store vectors:
   ```bash
   cd arun_backend/backend
   python import_students_from_csv.py
   ```

2. **Or generate vectors for existing students**:
   ```bash
   cd arun_backend/backend
   python vectorize_all.py
   ```

## Troubleshooting

### "Container already exists" error

If you get an error that the container already exists:

```bash
# Remove the old container
docker rm -f qdrant

# Run setup script again
setup_qdrant.bat
```

### Check if Qdrant is running

```bash
docker ps | findstr qdrant
```

Should show a running container.

### View Qdrant logs

```bash
docker logs qdrant
```

## Quick Commands Reference

```bash
# Start Qdrant
docker start qdrant

# Stop Qdrant
docker stop qdrant

# Restart Qdrant
docker restart qdrant

# View logs
docker logs qdrant

# Check status
docker ps -a | findstr qdrant

# Remove container (if needed)
docker rm -f qdrant
```

## What Happens Next

Once Qdrant is running and vectors are generated:

✅ Student vectors will be stored in Qdrant
✅ Alumni similarity search will work
✅ Trajectory predictions will use vector-based matching
✅ Dashboard will show similar alumni recommendations

## Current Students Waiting for Vectors

These 4 students are in PostgreSQL but need vectors in Qdrant:

1. Arun Prakash Pattar (ID: 7)
2. Sudeep (ID: 8)
3. Mayur Madiwal (ID: 9)
4. Vivek Desai (ID: 10)

---

**Next Action:** Start Docker Desktop, then run `setup_qdrant.bat`
