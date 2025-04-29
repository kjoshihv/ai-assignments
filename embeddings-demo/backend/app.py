from flask import Flask, request, jsonify
from flask_cors import CORS
from cognitive_layers.perception import Perception
from cognitive_layers.memory import Memory

app = Flask(__name__)
CORS(app)

# Initialize cognitive layers
perception = Perception()
memory = Memory()

@app.route('/process', methods=['POST'])
def process_url():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Extract and convert content
    result = perception.extract_and_convert(url)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Process and store in memory
    num_chunks = memory.process_document(result['content'], url)
    
    return jsonify({
        'status': 'success',
        'chunks_processed': num_chunks
    })

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
    app.run(debug=True) 