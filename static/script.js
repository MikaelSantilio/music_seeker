// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const searchInput = document.getElementById('search-input');
const clearBtn = document.getElementById('clear-btn');
const searchBtn = document.getElementById('search-btn');
const luckyBtn = document.getElementById('lucky-btn');
const newSearchBtn = document.getElementById('new-search-btn');
const retryBtn = document.getElementById('retry-btn');

const mainContainer = document.getElementById('main-container');
const loadingSection = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const header = document.querySelector('.header');

const searchQuery = document.getElementById('search-query');
const resultsCount = document.getElementById('results-count');
const searchTime = document.getElementById('search-time');
const resultsContainer = document.getElementById('results-container');
const errorMessage = document.getElementById('error-message');

const songCountEl = document.getElementById('song-count');
const artistCountEl = document.getElementById('artist-count');

// State
let currentSearchQuery = '';

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 DOM Content Loaded');
    console.log('🔍 Search input element:', searchInput);
    console.log('🔘 Search button element:', searchBtn);
    
    if (!searchInput) {
        console.error('❌ Search input not found!');
        return;
    }
    
    if (!searchBtn) {
        console.error('❌ Search button not found!');
        return;
    }
    
    setupEventListeners();
    await loadStats();
    
    // Auto-focus search input
    searchInput.focus();
    console.log('✅ Initialization complete');
});

// Event Listeners
function setupEventListeners() {
    console.log('🔗 Setting up event listeners');
    
    // Search input events
    searchInput.addEventListener('input', handleInputChange);
    searchInput.addEventListener('keypress', handleKeyPress);
    
    // Clear button
    clearBtn.addEventListener('click', clearSearch);
    
    // Search buttons
    searchBtn.addEventListener('click', (e) => {
        console.log('🔘 Search button clicked!', e);
        performSearch();
    });
    luckyBtn.addEventListener('click', (e) => {
        console.log('🎲 Lucky button clicked!', e);
        performLuckySearch();
    });
    newSearchBtn.addEventListener('click', resetToSearch);
    retryBtn.addEventListener('click', performSearch);
    
    // Suggestion tags
    document.querySelectorAll('.tag').forEach(tag => {
        tag.addEventListener('click', (e) => {
            const query = e.target.getAttribute('data-query');
            searchInput.value = query;
            handleInputChange();
            performSearch();
        });
    });
}

// Input handling
function handleInputChange() {
    const value = searchInput.value.trim();
    console.log('📝 Input changed:', value);
    clearBtn.style.display = value ? 'block' : 'none';
    searchBtn.disabled = !value;
    console.log('🔘 Search button disabled:', searchBtn.disabled);
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && searchInput.value.trim()) {
        performSearch();
    }
}

function clearSearch() {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchBtn.disabled = true;
    searchInput.focus();
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            const data = await response.json();
            songCountEl.textContent = data.total_songs?.toLocaleString() || '-';
            artistCountEl.textContent = data.total_artists?.toLocaleString() || '-';
        }
    } catch (error) {
        console.warn('Could not load stats:', error);
    }
}

// Search functions
async function performSearch() {
    console.log('🔍 performSearch called');
    
    const query = searchInput.value.trim();
    console.log('Query:', query);
    
    if (!query) {
        console.log('❌ Empty query, returning');
        return;
    }
    
    currentSearchQuery = query;
    console.log('📤 Starting search for:', currentSearchQuery);
    showLoading();
    
    try {
        const startTime = Date.now();
        console.log('📡 Making API request to:', `${API_BASE_URL}/search`);
        
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                limit: 10
            })
        });
        
        console.log('📡 Response status:', response.status);
        
        const searchTimeMs = Date.now() - startTime;
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error:', response.status, errorText);
            throw new Error(`API Error: ${response.status} ${response.statusText}\n${errorText}`);
        }
        
        const data = await response.json();
        console.log('📊 Search results:', data);
        showResults(data, searchTimeMs);
        
    } catch (error) {
        console.error('❌ Search error:', error);
        showError(error.message);
    }
}

async function performLuckySearch() {
    const suggestions = [
        "heartbreak and sadness",
        "dancing and party vibes", 
        "love and romance",
        "motivation and success",
        "nostalgia and memories",
        "summer and freedom"
    ];
    
    const randomQuery = suggestions[Math.floor(Math.random() * suggestions.length)];
    searchInput.value = randomQuery;
    handleInputChange();
    await performSearch();
}

// UI State Management
function showLoading() {
    hideAllSections();
    loadingSection.style.display = 'block';
    mainContainer.classList.add('has-results');
    header.style.display = 'block';
}

function showResults(data, searchTimeMs) {
    hideAllSections();
    
    // Update search info
    searchQuery.textContent = currentSearchQuery;
    resultsCount.textContent = data.results?.length || 0;
    searchTime.textContent = searchTimeMs;
    
    // Render results
    renderResults(data.results || []);
    
    resultsSection.style.display = 'block';
    mainContainer.classList.add('has-results');
    header.style.display = 'block';
}

function showError(message) {
    hideAllSections();
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    mainContainer.classList.add('has-results');
    header.style.display = 'block';
}

function resetToSearch() {
    hideAllSections();
    mainContainer.classList.remove('has-results');
    header.style.display = 'none';
    searchInput.focus();
}

function hideAllSections() {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// Results rendering
function renderResults(results) {
    resultsContainer.innerHTML = '';
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <h3>🎵 Nenhuma música encontrada</h3>
                <p>Tente usar termos diferentes ou menos específicos.</p>
                <br>
                <p><strong>Dicas:</strong></p>
                <ul style="text-align: left; color: #666;">
                    <li>Use sentimentos: "tristeza", "alegria", "nostalgia"</li>
                    <li>Descreva situações: "festa", "relaxar", "treino"</li>
                    <li>Combine conceitos: "amor e perda", "verão e liberdade"</li>
                </ul>
            </div>
        `;
        return;
    }
    
    results.forEach(result => {
        const songElement = createSongElement(result);
        resultsContainer.appendChild(songElement);
    });
}

function createSongElement(result) {
    const div = document.createElement('div');
    div.className = 'song-result';
    
    // Extract song data and similarity
    const song = result.song || result;
    const similarity = result.similarity || result.similarity_score || 0;
    
    // Format similarity score
    const similarityPercent = Math.round((1 - similarity) * 100);
    
    // Truncate lyrics preview
    const lyricsPreview = song.lyrics 
        ? song.lyrics.substring(0, 200).replace(/\n/g, ' ').trim() + '...'
        : 'Letra não disponível';
    
    div.innerHTML = `
        <div class="song-header">
            <div>
                <div class="song-title">🎵 ${escapeHtml(song.track_name)}</div>
                <div class="song-artist">👤 ${escapeHtml(song.artist_name)}</div>
                ${song.year ? `<div class="song-year">📅 ${song.year}</div>` : ''}
            </div>
            <div class="similarity-score">
                ${similarityPercent}% relevante
            </div>
        </div>
        <div class="song-lyrics">
            💭 "${escapeHtml(lyricsPreview)}"
        </div>
    `;
    
    return div;
}

// Utility functions
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Error handling for network issues
window.addEventListener('online', () => {
    console.log('Network connection restored');
});

window.addEventListener('offline', () => {
    showError('Sem conexão com a internet. Verifique sua conexão e tente novamente.');
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape key to return to search
    if (e.key === 'Escape') {
        resetToSearch();
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
    }
});

// Analytics (opcional)
function trackSearch(query, resultCount) {
    // Implementar analytics se necessário
    console.log(`Search: "${query}" -> ${resultCount} results`);
}
