from flask import Flask, request, jsonify
from flask_cors import CORS
from cognitive_layers.perception import Perception
from cognitive_layers.memory import Memory
from markitdown import MarkItDown
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize cognitive layers
perception = Perception()
memory = Memory()
markitdown = MarkItDown()

# Create storage directory if it doesn't exist
STORAGE_DIR = "processed_documents"
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route('/process', methods=['POST'])
def process_url():
    data = request.json
    url = data.get('url')
    html_content = data.get('html_content')
    
    if not url or not html_content:
        return jsonify({'error': 'URL and HTML content are required'}), 400
    
    try:
        # Convert HTML to Markdown using MarkItDown
        markdown_content = markitdown.convert(html_content)
        
        # Store the processed document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{STORAGE_DIR}/{timestamp}_{url.replace('://', '_').replace('/', '_')}.json"
        
        document_data = {
            'url': url,
            'markdown_content': markdown_content,
            'timestamp': timestamp
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(document_data, f, ensure_ascii=False, indent=2)
        
        # Process and store in memory
        num_chunks = memory.process_document(markdown_content, url)
        
        return jsonify({
            'status': 'success',
            'chunks_processed': num_chunks,
            'file_saved': filename
        })
        
    except Exception as e:
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