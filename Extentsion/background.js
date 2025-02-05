// Capture HLS/DASH manifests and MP4 URLs
chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
      const url = details.url;
      if (url.includes('.m3u8') || url.includes('.mpd') || url.includes('.mp4')) {
        chrome.tabs.sendMessage(details.tabId, {
          type: 'VIDEO_URL_DETECTED',
          url: url
        });
      }
    },
    { urls: ["<all_urls>"] }
  );
  
  // Forward detected URLs to content script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'VIDEO_URL_DETECTED') {
      chrome.tabs.sendMessage(sender.tab.id, message);
    }
  });