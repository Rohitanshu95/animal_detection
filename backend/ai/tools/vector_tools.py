"""
Vector Search Tools for LangGraph Agent
Semantic search using FAISS vector store
"""

import os
from typing import List, Dict, Optional
import numpy as np


class VectorSearchTools:
    """Tools for semantic search using FAISS"""
    
    def __init__(self, vector_store_path: str = "vector_store"):
        """
        Initialize vector search tools
        
        Args:
            vector_store_path: Path to FAISS index directory
        """
        self.vector_store_path = vector_store_path
        self.index = None
        self.embeddings_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize FAISS index and embeddings model"""
        try:
            import faiss
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            # Load embeddings model
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("Warning: GOOGLE_API_KEY not found for embeddings.")
                self.embeddings_model = None
            else:
                self.embeddings_model = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001", 
                    google_api_key=api_key
                )
            
            # Load FAISS index if exists
            index_path = os.path.join(self.vector_store_path, "faiss_index")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            else:
                # Create new index (768 dimensions for embedding-001)
                self.index = faiss.IndexFlatL2(768)
                
        except ImportError as e:
            print(f"Warning: Could not initialize vector search: {e}")
            self.index = None
            self.embeddings_model = None
    
    def add_documents(self, documents: List[Dict]):
        """
        Add documents to vector store
        
        Args:
            documents: List of document dictionaries with 'text' and metadata
        """
        if not self.embeddings_model or not self.index:
            return
        
        texts = [doc.get('text', doc.get('description', '')) for doc in documents]
        
        # Generate embeddings
        # LangChain embeddings return a list of floats
        embeddings = self.embeddings_model.embed_documents(texts)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index
        self._save_index()
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Perform semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self.embeddings_model or not self.index or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embeddings_model.embed_query(query)
        
        # Search
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'),
            top_k
        )
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid index
                results.append({
                    "rank": i + 1,
                    "index": int(idx),
                    "distance": float(dist),
                    "similarity_score": float(1 / (1 + dist))  # Convert distance to similarity
                })
        
        return results
    
    def find_similar_to_document(
        self,
        document_text: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find documents similar to a given document
        
        Args:
            document_text: Document text
            top_k: Number of results
            
        Returns:
            List of similar documents
        """
        return self.semantic_search(document_text, top_k)
    
    def _save_index(self):
        """Save FAISS index to disk"""
        if self.index:
            import faiss
            os.makedirs(self.vector_store_path, exist_ok=True)
            index_path = os.path.join(self.vector_store_path, "faiss_index")
            faiss.write_index(self.index, index_path)
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if not self.index:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d
        }


class HybridSearchTools:
    """Combines vector search with database search"""
    
    def __init__(self, vector_tools: VectorSearchTools, db_tools):
        self.vector_tools = vector_tools
        self.db_tools = db_tools
    
    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        semantic_weight: float = 0.5
    ) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            query: Search query
            limit: Maximum results
            semantic_weight: Weight for semantic search (0-1)
            
        Returns:
            Combined search results
        """
        # Semantic search
        semantic_results = self.vector_tools.semantic_search(query, top_k=limit)
        
        # Database keyword search
        db_results = await self.db_tools.search_incidents(query=query, limit=limit)
        
        # Combine results (simple approach - can be improved)
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            idx = result['index']
            combined[idx] = {
                'score': result['similarity_score'] * semantic_weight,
                'semantic_rank': result['rank']
            }
        
        # Add DB results
        for i, result in enumerate(db_results):
            idx = result.get('_id')
            if idx in combined:
                combined[idx]['score'] += (1 - semantic_weight) * (1 / (i + 1))
            else:
                combined[idx] = {
                    'score': (1 - semantic_weight) * (1 / (i + 1)),
                    'db_rank': i + 1
                }
            combined[idx]['data'] = result
        
        # Sort by combined score
        sorted_results = sorted(
            combined.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [
            {
                'id': idx,
                'score': data['score'],
                **data.get('data', {})
            }
            for idx, data in sorted_results[:limit]
        ]


# LangChain tool wrappers
def create_vector_tools(vector_store_path: str = "vector_store"):
    """
    Create LangChain-compatible vector search tools
    
    Args:
        vector_store_path: Path to vector store
        
    Returns:
        List of LangChain tools
    """
    from langchain.tools import Tool
    
    vector_tools = VectorSearchTools(vector_store_path)
    
    tools = [
        Tool(
            name="semantic_search",
            description="Perform semantic search to find similar incidents based on meaning, not just keywords. Returns most relevant incidents.",
            func=lambda x: vector_tools.semantic_search(x, top_k=5),
        ),
        Tool(
            name="find_similar_incidents",
            description="Find incidents similar to a given text description. Useful for pattern detection and case comparison.",
            func=lambda x: vector_tools.find_similar_to_document(x, top_k=5),
        ),
        Tool(
            name="vector_store_stats",
            description="Get statistics about the vector search index including total documents indexed.",
            func=lambda x: vector_tools.get_index_stats(),
        ),
    ]
    
    return tools
