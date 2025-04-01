// Content script that can interact with the webpage
console.log('Stock analysis (month based) content script loaded');

// Example: Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'GET_PAGE_TEXT') {
    // Get selected text or page content
    const selectedText = window.getSelection().toString();
    sendResponse({ text: selectedText });
  }
  return true;
}); 