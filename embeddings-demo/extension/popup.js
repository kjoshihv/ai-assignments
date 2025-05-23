const APP_URL = 'http://localhost:5001';

document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('saveButton');
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('results');
    const progressContainer = document.getElementById('progressContainer');

    function showProgress() {
        progressContainer.style.display = 'block';
        resultsDiv.innerHTML = '';
    }

    function hideProgress() {
        progressContainer.style.display = 'none';
    }

    async function getPageContent() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const [{result}] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.documentElement.outerHTML
        });
        return result;
    }

    async function checkTaskStatus(taskId) {
        try {
            const response = await fetch(`${APP_URL}/task/${taskId}`);
            const data = await response.json();
            
            if (data.status === 'processing') {
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
            const htmlContent = await getPageContent();
            const response = await fetch(`${APP_URL}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    url: tab.url,
                    html_content: htmlContent
                })
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

        showProgress();

        try {
            const response = await fetch(`${APP_URL}/search`, {
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
        } finally {
            hideProgress();
        }
    });
}); 