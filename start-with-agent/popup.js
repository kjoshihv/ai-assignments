let apiKey = null;

// Initialize the API key
async function initializeGemini() {
  try {
    const response = await fetch('http://localhost:5000/api-key');
    if (!response.ok) {
      throw new Error('Failed to fetch API key');
    }
    const data = await response.json();
    apiKey = data.api_key;
    return true;
  } catch (error) {
    console.error('Failed to initialize Gemini:', error);
    return false;
  }
}

document.addEventListener('DOMContentLoaded', async function() {
  const stockInput = document.getElementById('stockInput');
  const analyzeButton = document.getElementById('analyze');
  const output = document.getElementById('output');
  const loading = document.getElementById('loading');

  // Initialize API key on page load
  const initialized = await initializeGemini();
  if (!initialized) {
    output.innerHTML = 'Failed to initialize the AI model. Please try again later.';
    return;
  }

  analyzeButton.addEventListener('click', async function() {
    const stockSymbol = stockInput.value.trim().toUpperCase();
    if (!stockSymbol) {
      output.innerHTML = 'Please enter a stock symbol';
      return;
    }

    try {
      loading.style.display = 'block';
      output.innerHTML = 'Starting analysis...<br><br>';

      // First iteration: Get news for the last month
      output.innerHTML += 'Fetching news for the last month...<br>';
      const newsResponse = await getStockNews(stockSymbol);
      output.innerHTML += 'News fetched successfully.<br>' +  '<br><br>';

      // Store LLM response in a file
    await fetch('http://localhost:5000/log-response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        stock_symbol: stockSymbol,
        response: newsResponse
      })
    });      

      // Send to Python backend to extract dates
      const dates = await extractDates(newsResponse);
      output.innerHTML += `Found ${dates.length} significant dates.<br><br>`;

      // Second iteration: Get stock movement for those dates
      output.innerHTML += 'Analyzing stock movements...<br>';
      const movementResponse = await getStockMovements(stockSymbol, dates, newsResponse);
      
      // Display final results
      output.innerHTML += '<br>Analysis Complete:<br><br>';
      output.innerHTML += movementResponse;
    } catch (error) {
      output.innerHTML = `Error: ${error.message}`;
    } finally {
      loading.style.display = 'none';
    }
  });
});

async function getStockNews(stockSymbol) {
  const prompt = `Get the news for a stock ${stockSymbol} in the August 2021 month. 
  Format the response as a JSON array of objects with the following structure:
  {
    "date": "YYYY-MM-DD",
    "title": "News title",
    "summary": "Brief summary of the news",
    "impact": "positive/negative/neutral"
  }
  Only include significant news that might affect the stock price.
  Return ONLY the JSON array without any markdown formatting or code block markers.`;

  try {
    console.log('Making API request with key:', apiKey ? 'Present' : 'Missing');
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error Response:', errorText);
      throw new Error(`Failed to fetch stock news: ${response.status} ${response.statusText}\nDetails: ${errorText}`);
    }

    const data = await response.json();
    let responseText = data.candidates[0].content.parts[0].text;
    
    // Clean up markdown formatting if present
    responseText = responseText.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    
    return responseText;
  } catch (error) {
    console.error('Full error details:', error);
    throw new Error(`Failed to fetch stock ${stockSymbol} news: ${error.message}`);
  }
}

async function extractDates(newsResponse) {
  const response = await fetch('http://localhost:5000/extract-dates', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      news_data: newsResponse
    })
  });

  if (!response.ok) {
    throw new Error('Failed to extract dates');
  }

  const data = await response.json();
  return data.dates;
}

async function getStockMovements(stockSymbol, dates, previousNews) {
  const prompt = `Based on the following news and dates, analyze how ${stockSymbol} stock moved on these dates:

Previous News Analysis:
${previousNews}

Significant Dates:
${dates.join(', ')}

Please provide a detailed analysis of the stock's movement on these dates, including:
1. Price movement (up/down)
2. Volume changes
3. Correlation with the news events
4. Overall market sentiment

Format the response in a clear, structured way with column date, impact, movement, volume, correlation, and sentiment.`;

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }]
      })
    });

    if (!response.ok) {
      throw new Error('Failed to analyze stock movements');
    }

    const data = await response.json();
    const analysisText = data.candidates[0].content.parts[0].text;

    // Store LLM response in a file
    await fetch('http://localhost:5000/log-response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        stock_symbol: stockSymbol,
        response: analysisText
      })
    });

    // Extract structured data from the analysis
    const analysisResponse = await fetch('http://localhost:5000/extract-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        analysis_text: analysisText
      })
    });

    if (!analysisResponse.ok) {
      throw new Error('Failed to extract analysis data');
    }

    const analysisData = await analysisResponse.json();
    return renderAnalysisData(analysisData.analysis_data);
  } catch (error) {
    throw new Error('Failed to analyze stock movements: ' + error.message);
  }
}

function renderAnalysisData(analysisData) {
  let html = '<div class="analysis-container">';
  
  // Add table header
  html += `
    <table class="analysis-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Impact</th>
          <th>Movement</th>
          <th>Volume</th>
          <th>Correlation</th>
          <th>Sentiment</th>
        </tr>
      </thead>
      <tbody>
  `;

  // Add table rows
  Object.entries(analysisData).forEach(([date, data]) => {
    html += `
      <tr>
        <td>${date}</td>
        <td class="${data.impact.toLowerCase()}">${data.impact}</td>
        <td>${data.movement}</td>
        <td>${data.volume}</td>
        <td>${data.correlation}</td>
        <td>${data.sentiment}</td>
      </tr>
    `;
  });

  html += `
      </tbody>
    </table>
  </div>`;

  return html;
} 