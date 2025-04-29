from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class Action:
    def __init__(self):
        self.history = []

    def execute_search(self, query: str, results: List[Dict]) -> Dict:
        """Execute search and prepare response"""
        if not results:
            return {
                'status': 'no_results',
                'message': 'No relevant results found'
            }

        # Store in history
        self.history.append({
            'query': query,
            'results': results
        })

        # Prepare response
        return {
            'status': 'success',
            'results': results,
            'total_results': len(results)
        }

    def get_page_preview(self, url: str) -> Dict:
        """Get a preview of the page content"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and first paragraph
            title = soup.title.string if soup.title else url
            first_para = soup.find('p')
            preview = first_para.text if first_para else ''
            
            return {
                'success': True,
                'title': title,
                'preview': preview[:200] + '...' if len(preview) > 200 else preview
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 