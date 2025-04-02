from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
GOOGLE_API_KEY = os.getenv('YOUR_KEY')

@app.route('/api-key', methods=['GET'])
def get_api_key():
    """Securely serve the API key to the frontend"""
    return jsonify({'api_key': GOOGLE_API_KEY})


def extract_dates_from_news(news_data):
    """
    Extract dates and associated information from the news data
    """
    try:
        # First try to parse as JSON
        news_items = json.loads(news_data)
        dates = set()
        for item in news_items:
            if 'date' in item:
                try:
                    datetime.strptime(item['date'], '%Y-%m-%d')
                    dates.add(item['date'])
                except ValueError:
                    continue
        return sorted(list(dates))
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract from table format
        # Pattern to match date rows in the table
        date_pattern = r'\| (\d{4}-\d{2}-\d{2}) \|'
        dates = set(re.findall(date_pattern, news_data))
        
        if dates:
            # Extract full information for each date
            date_info = {}
            for date in dates:
                # Find the line containing this date
                date_line = re.search(f'\| {date} \|.*?\|.*?\|.*?\|.*?\|.*?\|', news_data, re.DOTALL)
                if date_line:
                    # Split the line into columns
                    columns = [col.strip() for col in date_line.group().split('|')]
                    if len(columns) >= 6:
                        date_info[date] = {
                            'impact': columns[2].strip(),
                            'movement': columns[3].strip(),
                            'volume': columns[4].strip(),
                            'correlation': columns[5].strip(),
                            'sentiment': columns[6].strip()
                        }
            
            # Store the extracted information in a global variable or return it
            app.date_info = date_info
            
        return sorted(list(dates))
    except Exception as e:
        print(f"Error extracting dates: {str(e)}")
        return []

@app.route('/extract-dates', methods=['POST'])
def extract_dates():
    try:
        data = request.get_json()
        news_data = data.get('news_data', '')
        
        if not news_data:
            return jsonify({'error': 'No news data provided'}), 400
            
        dates = extract_dates_from_news(news_data)
        return jsonify({'dates': dates})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_analysis_data(analysis_text):
    """
    Extract data from the analysis table format
    """
    try:
        # Pattern to match date rows in the table
        date_pattern = r'\| (\d{4}-\d{2}-\d{2}) \|'
        dates = set(re.findall(date_pattern, analysis_text))
        
        if dates:
            # Extract full information for each date
            analysis_data = {}
            for date in dates:
                # Find the line containing this date
                date_line = re.search(f'\| {date} \|.*?\|.*?\|.*?\|.*?\|.*?\|', analysis_text, re.DOTALL)
                if date_line:
                    # Split the line into columns
                    columns = [col.strip() for col in date_line.group().split('|')]
                    if len(columns) >= 6:
                        analysis_data[date] = {
                            'impact': columns[2].strip(),
                            'movement': columns[3].strip(),
                            'volume': columns[4].strip(),
                            'correlation': columns[5].strip(),
                            'sentiment': columns[6].strip()
                        }
            return analysis_data
        return {}
    except Exception as e:
        print(f"Error extracting analysis data: {str(e)}")
        return {}

@app.route('/extract-analysis', methods=['POST'])
def extract_analysis():
    try:
        data = request.get_json()
        analysis_text = data.get('analysis_text', '')
        
        if not analysis_text:
            return jsonify({'error': 'No analysis text provided'}), 400
            
        analysis_data = extract_analysis_data(analysis_text)
        print(f"output: {analysis_data}")
        return jsonify({'analysis_data': analysis_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log-response', methods=['POST'])
def log_response():
    try:
        data = request.get_json()
        stock_symbol = data.get('stock_symbol', '')
        response = data.get('response', '')
        
        if not response:
            return jsonify({'error': 'No response provided'}), 400
            
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/llm_response_{stock_symbol}_{timestamp}.txt'
        
        # Write response to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response)
            
        return jsonify({'status': 'success', 'file': filename})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 