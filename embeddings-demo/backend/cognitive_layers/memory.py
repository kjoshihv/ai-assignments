import faiss
import numpy as np
# from nomic.embeddings import Embeddings

class Memory:
    def __init__(self):
        # self.embeddings_model = Embeddings()
        self.index = None
        self.documents = []
        self.urls = []
        self.dimension = None

    def create_chunks(self, text, chunk_size=1000, overlap=100):
        """Create overlapping chunks from text"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

    def process_document(self, markdown_content, url):
        """Process document and store in FAISS index"""
        # Create chunks
        chunks = self.create_chunks(markdown_content)
        
        # Generate embeddings
        # chunk_embeddings = self.embeddings_model.embed(chunks)
        
        # Initialize FAISS index if not exists
        if self.index is None:
            # self.dimension = chunk_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add to FAISS index
        # self.index.add(chunk_embeddings)
        
        # Store document chunks and URLs
        self.documents.extend(chunks)
        self.urls.extend([url] * len(chunks))
        
        return len(chunks)

    def search(self, query, k=3):
        """Search for similar content"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embeddings_model.embed([query])
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, k)
        
        # Return results
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'url': self.urls[idx]
                })
        
        return results 