// Fetch and display YouTube videos for @ArchJay
// Uses YouTube Data API v3 (requires API key)
// Replace 'YOUR_API_KEY' with your actual API key

const YT_API_KEY = 'AIzaSyBYZ0Z59Dvp4QC1dGGXonRSj99erbFXRL8'; // <-- Replace with your YouTube Data API v3 key
const CHANNEL_ID = 'UCb0h60L9R7KfsUFBDG03goQ'; // <-- Replace with your channel's ID
const MAX_RESULTS = 12;

async function fetchYouTubeVideos() {
  const url = `https://www.googleapis.com/youtube/v3/search?key=${YT_API_KEY}&channelId=${CHANNEL_ID}&part=snippet,id&order=date&maxResults=${MAX_RESULTS}`;
  const res = await fetch(url);
  const data = await res.json();
  return data.items.filter(item => item.id.kind === 'youtube#video');
}

function createVideoCard(video) {
  const { videoId } = video.id;
  const { title, thumbnails, description } = video.snippet;
  return `
    <article class="game-embed">
      <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener">
        <img src="${thumbnails.medium.url}" alt="${title}" class="thumb" loading="lazy" width="320" height="180">
      </a>
      <div class="game-meta">
        <h2 style="font-size:1.1rem;margin:.7em 0 .3em 0;">${title}</h2>
        <p class="lead" style="font-size:.98rem;">${description.substring(0, 90)}...</p>
        <a class="btn" href="https://www.youtube.com/watch?v=${videoId}" target="_blank">Watch on YouTube</a>
      </div>
    </article>
  `;
}

async function renderYouTubeVideos() {
  const grid = document.getElementById('videos-grid');
  if (!grid) return;
  grid.innerHTML = '<p>Loading videos...</p>';
  try {
    const videos = await fetchYouTubeVideos();
    if (!videos.length) {
      grid.innerHTML = '<p>No videos found.</p>';
      return;
    }
    grid.innerHTML = videos.map(createVideoCard).join('');
  } catch (e) {
    grid.innerHTML = '<p>Could not load videos. Please try again later.</p>';
  }
}

document.addEventListener('DOMContentLoaded', renderYouTubeVideos);
