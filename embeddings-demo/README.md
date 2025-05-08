# Document Search Chrome Extension with Embeddings

This project implements a Chrome extension that allows users to save web pages and perform semantic search across saved content using embeddings and vector similarity search.

## Features

- Save current web page content for later search
- Semantic search across saved pages using natural language queries
- Real-time progress indication during search
- Relevance scoring for search results
- Clickable links to original content

## Architecture

The project consists of two main components:

1. **Chrome Extension (Frontend)**
   - User interface for saving pages and searching
   - Communicates with backend API
   - Displays search results with relevance scores

2. **Backend Server**
   - Processes and stores web page content
   - Implements semantic search using embeddings
   - Manages asynchronous processing of saved pages

## Technical Implementation

### Embeddings and Vector Search

The project uses several key technologies for semantic search:

1. **Text Embeddings**
   - Converts text into high-dimensional vectors that capture semantic meaning
   - Enables similarity-based search rather than just keyword matching
   - Maintains context and meaning in search results

2. **Text Chunking**
   - Splits long documents into smaller, manageable chunks
   - Preserves context within each chunk
   - Enables more precise search results

3. **FAISS (Facebook AI Similarity Search)**
   - Efficient vector similarity search library
   - Enables fast nearest-neighbor search in high-dimensional spaces
   - Optimized for large-scale similarity search

### Search Process

1. When a page is saved:
   - Content is extracted and cleaned
   - Text is split into semantic chunks
   - Each chunk is converted into an embedding vector
   - Vectors are stored in FAISS index

2. During search:
   - Query is converted into an embedding vector
   - FAISS finds most similar vectors in the index
   - Results are ranked by similarity score
   - Original content is retrieved and displayed

## Setup and Installation

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. **Chrome Extension Setup**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension` directory

## Usage

1. **Saving Pages**
   - Navigate to any webpage
   - Click the extension icon
   - Click "Save Current Page"

2. **Searching**
   - Click the extension icon
   - Enter your search query
   - View results ranked by relevance

## Dependencies

- Python 3.8+
- Flask
- FAISS
- Sentence Transformers
- Chrome Extension APIs

## Future Improvements

- Add support for more document types
- Implement user authentication
- Add batch processing capabilities
- Improve chunking strategies
- Add result filtering options
