function showQualityOptions(formats, downloadButton, videoUrl) {
  // Remove existing quality selector if present
  const existingSelector = document.querySelector('.quality-selector');
  if (existingSelector) existingSelector.remove();

  // Create quality selector container
  const selector = document.createElement('div');
  selector.className = 'quality-selector';
  selector.style.position = 'absolute';
  selector.style.zIndex = '99999';
  selector.style.backgroundColor = '#ffffff';
  selector.style.border = '1px solid #ddd';
  selector.style.borderRadius = '4px';
  selector.style.padding = '8px';
  selector.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
  
  // Make it scrollable if too many options
  selector.style.maxHeight = '200px'; // Set max height for scrollability
  selector.style.overflowY = 'auto'; // Enable vertical scrolling

  // Add quality options
  formats.forEach(format => {
    const btn = document.createElement('button');
    btn.textContent = `${format.resolution || 'Unknown'} (${format.ext}) ${format.has_audio ? '🔊' : '🔇'}`;
    btn.style.display = 'block';
    btn.style.width = '100%';
    btn.style.padding = '6px 12px';
    btn.style.margin = '4px 0';
    btn.style.textAlign = 'left';
    btn.style.cursor = 'pointer';
    btn.style.border = 'none';
    btn.style.background = 'none';

    btn.addEventListener('click', () => {
      fetch('https://localhost:5000/add_download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: videoUrl, format: format.format_id })
      });
      selector.remove();
      document.removeEventListener('click', outsideClickListener);
    });

    selector.appendChild(btn);
  });

  // Position selector relative to download button
  const btnRect = downloadButton.getBoundingClientRect();
  selector.style.top = `${btnRect.bottom + window.scrollY + 8}px`;
  selector.style.left = `${btnRect.left + window.scrollX}px`;

  document.body.appendChild(selector);

  // Click outside to close function
  function outsideClickListener(event) {
    if (!selector.contains(event.target) && event.target !== downloadButton) {
      selector.remove();
      document.removeEventListener('click', outsideClickListener);
    }
  }

  // Add event listener to detect clicks outside of the quality selector
  setTimeout(() => {
    document.addEventListener('click', outsideClickListener);
  }, 0);
}


async function handleDownloadButtonClick(video, downloadButton) {
  try {
    let videoUrl = video.src || video.querySelector('source')?.src;

    // Handle blob URLs and missing sources
    if (!videoUrl || videoUrl.startsWith('blob:')) {
      videoUrl = window.location.href;
    }

    const response = await fetch('https://localhost:5000/get_formats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: videoUrl })
    });

    if (!response.ok) throw new Error('Server error');

    const data = await response.json();
console.log(data)
    if (data.formats?.length > 1) {
      showQualityOptions(data.formats, downloadButton, videoUrl);
    } else {
      fetch('https://localhost:5000/add_download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: videoUrl })
      });
    }
  } catch (err) {
    console.error('Download error:', err);
  }
}

function injectDownloadButton(video) {
  if (video.dataset.downloadButtonAdded) return;

  const btn = document.createElement('button');
  btn.innerHTML = '⬇️ Download';
  btn.style.position = 'absolute';
  btn.style.zIndex = '9999';
  btn.style.top = '10px';
  btn.style.right = '10px';
  btn.style.backgroundColor = '#2196F3';
  btn.style.color = 'white';
  btn.style.padding = '6px 12px';
  btn.style.borderRadius = '4px';
  btn.style.cursor = 'pointer';
  btn.style.border = 'none';
  btn.style.fontSize = '14px';

  // Ensure proper positioning container
  if (window.getComputedStyle(video.parentElement).position === 'static') {
    video.parentElement.style.position = 'relative';
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    handleDownloadButtonClick(video, btn);
  });

  video.parentNode.insertBefore(btn, video.nextSibling);
  video.dataset.downloadButtonAdded = true;
}

// Main observer for video elements
const observer = new MutationObserver((mutations) => {
  document.querySelectorAll('video').forEach(video => {
    if (!video.dataset.downloadButtonAdded) {
      injectDownloadButton(video);
    }
  });
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Initial injection for existing videos
document.querySelectorAll('video').forEach(injectDownloadButton);