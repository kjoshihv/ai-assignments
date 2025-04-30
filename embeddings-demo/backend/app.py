from flask import Flask, request, jsonify
from flask_cors import CORS
from cognitive_layers.perception import Perception
from cognitive_layers.memory import Memory
from markitdown import MarkItDown
import os
import json
import numpy as np
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
import faiss
import logging  # Import logging
import ollama

app = Flask(__name__)
CORS(app)

# Initialize cognitive layers
perception = Perception()
memory = Memory()

CHUNK_SIZE = 256
CHUNK_OVERLAP = 40
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

# Configure logging
logging.basicConfig(
    filename="embeddings-demo.log",  # Log file
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create storage directory if it doesn't exist
PROCESSED_DIR = "processed_documents"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i+size])

def get_embedding(text: str) -> np.ndarray:
    response = ollama.embeddings(model='nomic-embed-text', prompt=text)
    return np.array(response["embedding"], dtype=np.float32)

@app.route('/process', methods=['POST'])
def process_url():
    logging.info("inside process_url")
    data = request.json
    url = data.get('url')
    html_content = data.get('html_content')
    ROOT = Path(__file__).parent.resolve()
    INDEX_CACHE = ROOT / "faiss_index"
    INDEX_CACHE.mkdir(exist_ok=True)
    INDEX_FILE = INDEX_CACHE / "index.bin"
    METADATA_FILE = INDEX_CACHE / "metadata.json"
    CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"

    DOC_STORE = ROOT / "doc_store"
    os.makedirs(DOC_STORE, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not url or not html_content:
        logging.error("error: URL and HTML content are required")
        return jsonify({'error': 'URL and HTML content are required'}), 400
    
    try:
        # Save HTML data into file

        file_name = f"{DOC_STORE}/{timestamp}_{url.replace('://', '_').replace('/', '_')}.htmlhtml_file_content.txt"
        file = open(file_name, "w", encoding="utf-8")
        file.write(html_content)
        file.close()

        # Convert HTML to Markdown using MarkItDown
        markitdown = MarkItDown()
        markdown_content = markitdown.convert(file_name)
        
        index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else None
        metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []

        document_data = {
            'url': url,
            'markdown_content': markdown_content.text_content,
            'timestamp': timestamp
        }

        # Create chunks
        chunks = list(chunk_text(markdown_content.text_content))
        logging.info(f"Done chunks. Size {len(chunks)}")

        embeddings_for_file = []
        new_metadata = []
        for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {file_name}")):
            embedding = get_embedding(chunk)
            embeddings_for_file.append(embedding)
            new_metadata.append({"doc": file_name, "chunk": chunk})
        if embeddings_for_file:
            if index is None:
                dim = len(embeddings_for_file[0])
                index = faiss.IndexFlatL2(dim)
            index.add(np.stack(embeddings_for_file))
            metadata.extend(new_metadata)
        # CACHE_META[file.name] = fhash

        METADATA_FILE.write_text(json.dumps(metadata, indent=2))
        if index and index.ntotal > 0:
            faiss.write_index(index, str(INDEX_FILE))
            logging.info("Saved FAISS index and metadata")

        return jsonify({
            'status': 'success',
            'chunks_processed': "num_chunks",
            'file_saved': file_name
        })
        
    except Exception as e:
        logging.error(f"exception: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Search in memory
    results = memory.search(query)
    
    return jsonify({
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 