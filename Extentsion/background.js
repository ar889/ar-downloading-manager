// background.js (Manifest V3)
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;
    // Capture HLS/DASH manifests
    if (url.includes('.m3u8') || url.includes('.mpd')) {
      chrome.tabs.sendMessage(details.tabId, {
        type: 'STREAM_URL_DETECTED',
        url: url
      });
    }
  },
  { urls: ["<all_urls>"] }
);

// Forward to content script
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type === 'STREAM_URL_DETECTED') {
    chrome.tabs.sendMessage(sender.tab.id, message);
  }
});