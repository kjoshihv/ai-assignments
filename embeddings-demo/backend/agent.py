from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

MCP_SERVER_URL = 'http://localhost:5000/api'

class Agent:
    def __init__(self):
        self.active_tasks = {}

   
    def check_task_status(self, task_id):
        """Check task status from MCP server"""
        try:
            response = requests.get(f'{MCP_SERVER_URL}/task/{task_id}')
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def search(self, query):
        """Search through MCP server"""
        try:
            response = requests.post(
                f'{MCP_SERVER_URL}/search',
                json={'query': query}
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def get_preview(self, url):
        """Get page preview from MCP server"""
        try:
            response = requests.post(
                f'{MCP_SERVER_URL}/preview',
                json={'url': url}
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

# Initialize agent
agent = Agent()


@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status endpoint"""
    result = agent.check_task_status(task_id)
    return jsonify(result)

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint"""
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    result = agent.search(query)
    return jsonify(result)

@app.route('/preview', methods=['POST'])
def get_preview():
    """Get page preview endpoint"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    result = agent.get_preview(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 