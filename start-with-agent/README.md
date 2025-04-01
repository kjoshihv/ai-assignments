# Stock Analysis Chrome Extension

A Chrome extension that leverages Google's Gemini AI to analyze stock movements based on historical news data. The extension provides a user-friendly interface to analyze stock performance and generates detailed reports with visual representations.

## Features

- **Stock Analysis**: Enter any stock symbol to get a detailed analysis of its historical performance
- **AI-Powered Insights**: Uses Google's Gemini AI to analyze stock movements and news impact
- **Structured Data Display**: Presents analysis in a clean, formatted table with:
  - Date-wise breakdown
  - Impact assessment (Positive/Negative/Neutral)
  - Stock movement predictions
  - Volume changes
  - News correlation analysis
  - Market sentiment analysis
- **Response Logging**: Automatically saves AI responses for future reference
- **Modern UI**: Clean and responsive interface with color-coded indicators

## Technical Stack

- **Frontend**:
  - HTML5
  - CSS3 (with modern styling and responsive design)
  - JavaScript (Vanilla)
  - Chrome Extension APIs

- **Backend**:
  - Python Flask server
  - Google Gemini AI API
  - JSON data handling
  - Regular expressions for data extraction

## Project Structure

```
agentic-app/
├── manifest.json           # Chrome extension configuration
├── popup.html             # Main extension interface
├── popup.js               # Frontend logic
├── app.py                 # Flask backend server
├── .env                   # Environment variables (API keys)
└── logs/                  # Directory for storing AI responses
```

## Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install flask flask-cors python-dotenv
   ```
3. Create a `.env` file with your Google API key:
   ```
   FLASH_KEY=your_api_key_here
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```
5. Load the extension in Chrome:
   - Open Chrome Extensions (chrome://extensions/)
   - Enable Developer Mode
   - Click "Load unpacked"
   - Select the project directory

## Usage

1. Click the extension icon in Chrome
2. Enter a stock symbol (e.g., AAPL, GOOGL, MSFT)
3. Click "Analyze Stock"
4. View the generated analysis in the formatted table
5. Check the `logs` directory for detailed AI responses

## API Endpoints

- `GET /api-key`: Securely serves the API key to the frontend
- `POST /extract-dates`: Extracts significant dates from news data
- `POST /extract-analysis`: Processes and structures the AI analysis
- `POST /log-response`: Saves AI responses for future reference

## Security Features

- API key stored securely in environment variables
- CORS enabled for local development
- Input validation and error handling
- Secure data transmission

## Future Enhancements

- Add historical price data integration
- Implement user authentication
- Add export functionality for analysis reports
- Include more detailed technical indicators
- Add support for multiple stock comparison
- Implement real-time updates

## License

MIT License - Feel free to use and modify as needed. 