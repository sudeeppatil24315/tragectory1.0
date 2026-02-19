import os

# Define the persistence directory
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")

def get_collection():
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        
        # Initialize the Chroma client
        client = chromadb.PersistentClient(path=DB_PATH)

        # Embedding model
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Collection for Student Vectors
        collection = client.get_or_create_collection(
            name="student_vectors", 
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"}
        )
        return collection
    except Exception as e:
        print(f"Vector DB Error: {e}")
        return None

def upsert_student_vector(student_id, text, metadata):
    """
    Store or update a student's vector in ChromaDB
    """
    collection = get_collection()
    if collection:
        collection.upsert(
            ids=[str(student_id)],
            documents=[text],
            metadatas=[metadata]
        )
    else:
        print(f"Skipping vector storage for student {student_id} due to initialization error.")

def query_similar_students(query_text, n_results=5):
    """
    Search for similar student profiles
    """
    collection = get_collection()
    if collection:
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
    return None
