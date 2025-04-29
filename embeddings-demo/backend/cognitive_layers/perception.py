from markitdown import MarkItDown
import requests

class Perception:
    def __init__(self):
        self.markdown_converter = MarkItDown()

    def extract_and_convert(self, url):
        """Extract HTML from URL and convert to markdown"""
        try:
            response = requests.get(url)
            html_content = response.text
            markdown_content = self.markdown_converter.convert(html_content)
            return {
                'success': True,
                'content': markdown_content,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 