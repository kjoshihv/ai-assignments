const AGENT_URL = 'http://localhost:5001';

document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('saveButton');
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('results');

    async function checkTaskStatus(taskId) {
        try {
            const response = await fetch(`${AGENT_URL}/task/${taskId}`);
            const data = await response.json();
            
            if (data.status === 'processing') {
                // Check again after 1 second
                setTimeout(() => checkTaskStatus(taskId), 1000);
            } else {
                resultsDiv.innerHTML = `
                    <div class="result-item">
                        ${data.status === 'success' 
                            ? `Page processed successfully! (${data.chunks_processed} chunks created)`
                            : `Error: ${data.error}`}
                    </div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="result-item">
                    Error: ${error.message}
                </div>`;
        }
    }

    saveButton.addEventListener('click', async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        try {
            const response = await fetch(`${AGENT_URL}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: tab.url })
            });
            
            const data = await response.json();
            if (data.status === 'processing') {
                resultsDiv.innerHTML = `
                    <div class="result-item">
                        Processing page... Please wait.
                    </div>`;
                checkTaskStatus(data.task_id);
            }
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="result-item">
                    Error: ${error.message}
                </div>`;
        }
    });

    searchButton.addEventListener('click', async () => {
        const query = searchInput.value;
        if (!query) return;

        try {
            const response = await fetch(`${AGENT_URL}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                resultsDiv.innerHTML = data.results.map(result => `
                    <div class="result-item">
                        <a href="${result.url}" target="_blank">${result.url}</a>
                        <p>${result.content.substring(0, 150)}...</p>
                        <small>Relevance: ${(result.relevance_score * 100).toFixed(1)}%</small>
                    </div>
                `).join('');
            } else {
                resultsDiv.innerHTML = `
                    <div class="result-item">
                        ${data.message}
                    </div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="result-item">
                    Error: ${error.message}
                </div>`;
        }
    });
}); 