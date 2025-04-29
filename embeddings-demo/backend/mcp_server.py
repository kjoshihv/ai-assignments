from flask import Flask, request, jsonify
from flask_cors import CORS
from cognitive_layers.perception import Perception
from cognitive_layers.memory import Memory
from cognitive_layers.decision import Decision
from cognitive_layers.action import Action
import threading
import queue
import time

app = Flask(__name__)
CORS(app)

# Initialize cognitive layers
perception = Perception()
memory = Memory()
decision = Decision()
action = Action()

# Task queue for background processing
task_queue = queue.Queue()
result_queue = queue.Queue()

def background_worker():
    """Background worker to process tasks"""
    while True:
        try:
            task = task_queue.get()
            if task['type'] == 'process_url':
                # Process URL
                result = perception.extract_and_convert(task['url'])
                if result['success']:
                    num_chunks = memory.process_document(result['content'], task['url'])
                    result_queue.put({
                        'task_id': task['task_id'],
                        'status': 'success',
                        'chunks_processed': num_chunks
                    })
                else:
                    result_queue.put({
                        'task_id': task['task_id'],
                        'status': 'error',
                        'error': result['error']
                    })
            task_queue.task_done()
        except Exception as e:
            result_queue.put({
                'task_id': task['task_id'],
                'status': 'error',
                'error': str(e)
            })
        time.sleep(0.1)

# Start background worker
worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

@app.route('/api/process', methods=['POST'])
def process_url():
    """Process URL endpoint"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create task
    task_id = str(time.time())
    task_queue.put({
        'type': 'process_url',
        'url': url,
        'task_id': task_id
    })
    
    return jsonify({
        'status': 'processing',
        'task_id': task_id
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status endpoint"""
    # Check result queue
    while not result_queue.empty():
        result = result_queue.get()
        if result['task_id'] == task_id:
            return jsonify(result)
    
    return jsonify({
        'status': 'processing',
        'task_id': task_id
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint"""
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Search in memory
    results = memory.search(query)
    
    # Analyze results
    analyzed_results = decision.analyze_results(results, query)
    
    # Execute search action
    response = action.execute_search(query, analyzed_results)
    
    return jsonify(response)

@app.route('/api/preview', methods=['POST'])
def get_preview():
    """Get page preview endpoint"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    preview = action.get_page_preview(url)
    return jsonify(preview)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 