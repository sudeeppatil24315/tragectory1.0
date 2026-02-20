# Qdrant Vector Database Setup Guide

## What is Qdrant?

Qdrant is an open-source vector database optimized for similarity search. We use it to:
- Store student and alumni vectors (15-dimensional)
- Find similar alumni using cosine similarity
- Perform fast searches (<100ms) using HNSW index

## Why Qdrant?

- **Fast**: <100ms similarity search with HNSW index
- **Free**: Open-source, self-hosted (no cloud costs)
- **Scalable**: Handles 1000+ vectors efficiently
- **Easy**: Simple REST API and Python client

## Installation Options

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))

**Steps:**

1. **Run the setup script:**
   ```bash
   cd arun_backend/backend
   setup_qdrant.bat
   ```

2. **Verify Qdrant is running:**
   - Open browser: http://localhost:6333/dashboard
   - You should see the Qdrant web UI

3. **Install Python client:**
   ```bash
   pip install qdrant-client
   ```

**Docker Commands:**
```bash
# Start Qdrant
docker start qdrant

# Stop Qdrant
docker stop qdrant

# View logs
docker logs qdrant

# Remove container
docker rm -f qdrant
```

### Option 2: Manual Docker Setup

If the script doesn't work, run these commands manually:

```bash
# Pull Qdrant image
docker pull qdrant/qdrant

# Run Qdrant container
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v ./qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Option 3: Local Binary (No Docker)

Download Qdrant binary from: https://github.com/qdrant/qdrant/releases

```bash
# Windows
qdrant.exe

# Linux/Mac
./qdrant
```

## Configuration

### Environment Variables

Add to your `.env` file:

```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Python Configuration

```python
from app.services.qdrant_service import QdrantService

# Initialize Qdrant service
qdrant = QdrantService(host="localhost", port=6333)

# Create collections (students and alumni)
qdrant.create_collections(vector_size=15)
```

## Testing Qdrant

### 1. Check if Qdrant is running

```bash
curl http://localhost:6333/
```

Expected response:
```json
{
  "title": "qdrant - vector search engine",
  "version": "1.x.x"
}
```

### 2. Test Python client

Create `test_qdrant.py`:

```python
from app.services.qdrant_service import QdrantService
import numpy as np

# Initialize service
qdrant = QdrantService()

# Create collections
qdrant.create_collections()

# Test storing a vector
test_vector = np.random.rand(15)
metadata = {
    "name": "Test Student",
    "major": "Computer Science",
    "semester": 5,
    "gpa": 7.5,
    "attendance": 85.0
}

success = qdrant.store_student_vector(
    student_id=1,
    vector=test_vector,
    metadata=metadata
)

print(f"Vector stored: {success}")

# Test similarity search
results = qdrant.find_similar_alumni(
    student_vector=test_vector,
    major="Computer Science",
    top_k=5
)

print(f"Found {len(results)} similar alumni")
```

Run:
```bash
cd arun_backend/backend
python test_qdrant.py
```

## Collections Structure

### Students Collection

```json
{
  "collection_name": "students",
  "vector_size": 15,
  "distance": "Cosine",
  "payload": {
    "student_id": "integer",
    "name": "string",
    "major": "string",
    "semester": "integer",
    "gpa": "float",
    "attendance": "float",
    "trajectory_score": "float",
    "updated_at": "datetime"
  }
}
```

### Alumni Collection

```json
{
  "collection_name": "alumni",
  "vector_size": 15,
  "distance": "Cosine",
  "payload": {
    "alumni_id": "integer",
    "name": "string",
    "major": "string",
    "graduation_year": "integer",
    "company_tier": "string",
    "salary_range": "string",
    "placement_status": "string",
    "outcome_score": "float"
  }
}
```

## Usage Examples

### Store Student Vector

```python
from app.services.qdrant_service import QdrantService
from app.services.vector_generation import generate_student_vector

qdrant = QdrantService()

# Generate vector from student profile
profile = {
    "gpa": 7.5,
    "attendance": 85.0,
    "study_hours_per_week": 20,
    "project_count": 3
}

vector = generate_student_vector(profile)

# Store in Qdrant
metadata = {
    "name": "John Doe",
    "major": "Computer Science",
    "semester": 5,
    "gpa": 7.5,
    "attendance": 85.0
}

qdrant.store_student_vector(
    student_id=123,
    vector=vector,
    metadata=metadata
)
```

### Find Similar Alumni

```python
# Find top 5 similar alumni
results = qdrant.find_similar_alumni(
    student_vector=vector,
    major="Computer Science",  # Optional filter
    top_k=5
)

for result in results:
    print(f"Alumni: {result['name']}")
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Company: {result['company_tier']}")
    print(f"Outcome Score: {result['outcome_score']}")
    print("---")
```

### Update Student Vector

```python
# When student profile changes, update vector
new_vector = generate_student_vector(updated_profile)

qdrant.update_student_vector(
    student_id=123,
    vector=new_vector
)
```

## Fallback to PostgreSQL

If Qdrant is unavailable, the system automatically falls back to PostgreSQL + NumPy:

```python
from app.services.qdrant_service import find_similar_alumni_fallback

# Load all alumni vectors from PostgreSQL
alumni_vectors = [
    (alumni_id, vector, metadata)
    for alumni in db.query(Alumni).all()
]

# Find similar alumni using NumPy
results = find_similar_alumni_fallback(
    student_vector=vector,
    alumni_vectors=alumni_vectors,
    major="Computer Science",
    top_k=5
)
```

**Note:** PostgreSQL fallback is slower (~500ms vs <100ms) but ensures system works even if Qdrant is down.

## Performance Optimization

### HNSW Index Configuration

Qdrant uses HNSW (Hierarchical Navigable Small World) index by default:

- **m=16**: Number of connections per node (higher = more accurate, slower)
- **ef_construct=100**: Construction time parameter (higher = better quality)

For our MVP (1000 students, 500 alumni), default settings are optimal.

### Query Performance

Expected performance:
- **Vector storage**: <10ms per vector
- **Similarity search**: <100ms for top 5 results
- **Batch operations**: ~1s for 100 vectors

## Monitoring

### Web Dashboard

Access Qdrant dashboard: http://localhost:6333/dashboard

Features:
- View collections
- Check vector counts
- Monitor query performance
- Inspect stored vectors

### Collection Info

```python
info = qdrant.get_collection_info("students")
print(f"Students: {info['points_count']} vectors")

info = qdrant.get_collection_info("alumni")
print(f"Alumni: {info['points_count']} vectors")
```

## Troubleshooting

### Issue: "Connection refused"

**Solution:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running, start it
docker start qdrant

# If container doesn't exist, run setup script
setup_qdrant.bat
```

### Issue: "Collection not found"

**Solution:**
```python
# Create collections
qdrant = QdrantService()
qdrant.create_collections()
```

### Issue: "Vector dimension mismatch"

**Solution:**
- Ensure all vectors are 15-dimensional
- Check vector generation function
- Verify collection was created with vector_size=15

### Issue: Docker not installed

**Solution:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and restart computer
3. Run `docker --version` to verify
4. Run `setup_qdrant.bat`

## Data Persistence

Qdrant data is stored in `qdrant_storage/` directory:
- Survives container restarts
- Can be backed up by copying directory
- Can be restored by replacing directory

**Backup:**
```bash
# Stop Qdrant
docker stop qdrant

# Backup data
xcopy qdrant_storage qdrant_backup /E /I

# Start Qdrant
docker start qdrant
```

**Restore:**
```bash
# Stop Qdrant
docker stop qdrant

# Restore data
xcopy qdrant_backup qdrant_storage /E /I /Y

# Start Qdrant
docker start qdrant
```

## Next Steps

After setting up Qdrant:

1. ✅ Install qdrant-client: `pip install qdrant-client`
2. ✅ Run Qdrant: `setup_qdrant.bat`
3. ✅ Test connection: `python test_qdrant.py`
4. ✅ Create collections: `qdrant.create_collections()`
5. ✅ Import alumni data and generate vectors
6. ✅ Test similarity search with sample student

## Resources

- Qdrant Documentation: https://qdrant.tech/documentation/
- Python Client: https://github.com/qdrant/qdrant-client
- Docker Hub: https://hub.docker.com/r/qdrant/qdrant
- GitHub: https://github.com/qdrant/qdrant

## Support

If you encounter issues:
1. Check Qdrant logs: `docker logs qdrant`
2. Verify Docker is running: `docker ps`
3. Test connection: `curl http://localhost:6333/`
4. Check Python client: `pip show qdrant-client`

---

**Status:** Qdrant setup complete! Ready for vector storage and similarity search. 🚀
