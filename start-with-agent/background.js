chrome.runtime.onInstalled.addListener(() => {
  console.log('Stock analysis (month based) extension installed');
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'VALIDATE_TEXT') {
    // Handle validation requests if needed
    sendResponse({ status: 'received' });
  }
  return true;
}); 