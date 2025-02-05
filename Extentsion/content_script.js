// content_script.js
function injectDownloadButton() {
  // Handle all video elements
  document.querySelectorAll('video').forEach(video => {
    if (!video.dataset.downloadButtonAdded) {
      const btn = document.createElement('button');
      btn.innerHTML = '⬇️ Download';
      btn.style.position = 'absolute';
      btn.style.zIndex = '9999';
      btn.style.backgroundColor = '#4CAF50';
      btn.style.color = 'white';
      btn.style.padding = '5px';

      // Position button near the video
      video.parentNode.style.position = 'relative';
      video.parentNode.appendChild(btn);

      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        
        // Try to get direct video URL first
        let videoUrl = video.src || video.querySelector('source')?.src;
        
        // If blob URL, fallback to page URL
        if (videoUrl?.startsWith('blob:')) {
          videoUrl = window.location.href;
        }

        if (videoUrl) {
          try {
            await fetch('https://localhost:5000/add_download', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url: videoUrl })
            });
          } catch (err) {
            console.error("Desktop app not running!");
          }
        }
      });

      video.dataset.downloadButtonAdded = true;
    }
  });
}

// Run periodically to catch dynamically loaded videos
setInterval(injectDownloadButton, 2000);