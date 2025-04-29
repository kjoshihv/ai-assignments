from typing import List, Dict
import numpy as np

class Decision:
    def __init__(self):
        self.relevance_threshold = 0.7

    def analyze_results(self, search_results: List[Dict], query: str) -> List[Dict]:
        """Analyze search results and determine relevance"""
        if not search_results:
            return []

        # Calculate relevance scores based on content length and position
        analyzed_results = []
        for idx, result in enumerate(search_results):
            # Simple relevance scoring based on position and content length
            position_score = 1.0 / (idx + 1)
            content_length_score = min(len(result['content']) / 1000, 1.0)
            
            relevance_score = (position_score * 0.7) + (content_length_score * 0.3)
            
            if relevance_score >= self.relevance_threshold:
                analyzed_results.append({
                    **result,
                    'relevance_score': relevance_score
                })

        return sorted(analyzed_results, key=lambda x: x['relevance_score'], reverse=True) 