// Game state
let currentRound = 1;
let pedals = [];
let currentPedal = null;
let selectedPedals = [];
let usedPedals = new Set(); // Track used pedals

// DOM elements
const pedal1Element = document.getElementById('pedal1');
const pedal2Element = document.getElementById('pedal2');
const currentRoundElement = document.getElementById('current-round');
const roundCounter = document.querySelector('.round-counter');
const resultsElement = document.getElementById('results');
const finalResultsElement = document.getElementById('final-results');
const playAgainButton = document.getElementById('play-again');
const battleContainer = document.getElementById('battle-container');
const congratsMessage = document.getElementById('congrats-message');

// Parse CSV row correctly handling commas in TYPE field
function parseCSVRow(row) {
    const parts = [];
    let currentPart = '';
    let inBrackets = false;
    
    for (let i = 0; i < row.length; i++) {
        const char = row[i];
        
        if (char === '[') {
            inBrackets = true;
            currentPart += char;
        } else if (char === ']') {
            inBrackets = false;
            currentPart += char;
        } else if (char === ',' && !inBrackets) {
            parts.push(currentPart.trim());
            currentPart = '';
        } else {
            currentPart += char;
        }
    }
    
    // Add the last part
    if (currentPart) {
        parts.push(currentPart.trim());
    }
    
    return parts;
}

// Create safe filename from brand and model
function createSafeFilename(brand, model) {
    const safe_brand = brand.replace(/[^a-zA-Z0-9\s-_]/g, '').trim();
    const safe_model = model.replace(/[^a-zA-Z0-9\s-_]/g, '').trim();
    return `${safe_brand}_${safe_model}.jpg`;
}

// Load pedals from CSV
async function loadPedals() {
    try {
        const response = await fetch('database.csv');
        const data = await response.text();
        const rows = data.split('\n').slice(1); // Skip header row
        
        pedals = rows.map(row => {
            const [brand, model, type, link, image_url] = parseCSVRow(row);
            return { brand, model, type, link, image_url };
        }).filter(pedal => pedal.brand && pedal.model); // Filter out empty rows
    } catch (error) {
        console.error('Error loading pedals:', error);
    }
}

// Get random pedal that hasn't been used yet
function getRandomPedal() {
    // Filter out pedals that have already been used
    const availablePedals = pedals.filter(pedal => !usedPedals.has(`${pedal.brand}-${pedal.model}`));
    
    if (availablePedals.length === 0) {
        // If all pedals have been used, reset the used pedals set
        usedPedals.clear();
        return pedals[Math.floor(Math.random() * pedals.length)];
    }
    
    const randomIndex = Math.floor(Math.random() * availablePedals.length);
    const selectedPedal = availablePedals[randomIndex];
    usedPedals.add(`${selectedPedal.brand}-${selectedPedal.model}`);
    return selectedPedal;
}

// Update pedal display
function updatePedalDisplay(pedal1, pedal2) {
    // Update pedal 1
    pedal1Element.querySelector('.brand').textContent = pedal1.brand;
    pedal1Element.querySelector('.model').textContent = pedal1.model;
    const img1 = pedal1Element.querySelector('.pedal-image img');
    const localImage1 = `images/${createSafeFilename(pedal1.brand, pedal1.model)}`;
    
    // Try to load local image, fallback to placeholder if it fails
    img1.onerror = function() {
        this.src = 'placeholder.svg';
        this.alt = 'Pedal placeholder';
    };
    img1.src = localImage1;
    img1.alt = `${pedal1.brand} ${pedal1.model}`;
    
    // Update pedal 2
    pedal2Element.querySelector('.brand').textContent = pedal2.brand;
    pedal2Element.querySelector('.model').textContent = pedal2.model;
    const img2 = pedal2Element.querySelector('.pedal-image img');
    const localImage2 = `images/${createSafeFilename(pedal2.brand, pedal2.model)}`;
    
    // Try to load local image, fallback to placeholder if it fails
    img2.onerror = function() {
        this.src = 'placeholder.svg';
        this.alt = 'Pedal placeholder';
    };
    img2.src = localImage2;
    img2.alt = `${pedal2.brand} ${pedal2.model}`;
    
    // Reset animations
    pedal1Element.style.animation = 'none';
    pedal2Element.style.animation = 'none';
    void pedal1Element.offsetWidth; // Trigger reflow
    void pedal2Element.offsetWidth; // Trigger reflow
    pedal1Element.style.animation = 'slideInTop 0.5s ease-out';
    pedal2Element.style.animation = 'slideInBottom 0.5s ease-out';
}

// Start new round
function startNewRound() {
    if (currentRound === 1) {
        // First round: two random pedals
        const pedal1 = getRandomPedal();
        const pedal2 = getRandomPedal();
        currentPedal = pedal1;
        updatePedalDisplay(pedal1, pedal2);
    } else if (currentRound <= 10) {
        // Next rounds: previous winner vs new random pedal
        const newPedal = getRandomPedal();
        updatePedalDisplay(currentPedal, newPedal);
    } else {
        // Game over
        showResults();
    }
}

// Handle pedal selection
function handlePedalSelection(selectedPedal) {
    if (currentRound <= 10) {
        currentPedal = selectedPedal;
        selectedPedals.push(selectedPedal);
        currentRound++;
        currentRoundElement.textContent = currentRound;
        
        if (currentRound <= 10) {
            startNewRound();
        } else {
            showResults();
        }
    }
}

// Show results
function showResults() {
    // Hide battle container and round counter, show results
    battleContainer.style.display = 'none';
    roundCounter.style.display = 'none';
    resultsElement.style.display = 'block';
    
    // Get the final winning pedal
    const finalWinner = selectedPedals[selectedPedals.length - 1];
    congratsMessage.textContent = 'WINNER';
    
    // Show the journey with links in reverse order
    const resultsList = [...selectedPedals].reverse().map((pedal, index) => {
        // Find the full pedal data to get the link
        const fullPedalData = pedals.find(p => 
            p.brand === pedal.brand && p.model === pedal.model
        );
        const reverbLink = fullPedalData ? fullPedalData.link : '#';
        // Create affiliate link that redirects to the specific pedal
        const affiliateLink = `https://www.awin1.com/cread.php?awinmid=67144&awinaffid=1772610&clickref=&p=${encodeURIComponent(reverbLink)}`;
        const roundNumber = selectedPedals.length - index;
        const isWinner = roundNumber === 10;
        
        return `
            <a href="${affiliateLink}" target="_blank" class="result-link ${isWinner ? 'winner' : ''}">
                <p>Round ${roundNumber}: ${pedal.brand} ${pedal.model}</p>
            </a>
        `;
    }).join('');
    finalResultsElement.innerHTML = resultsList;

    // Set up share functionality
    setupShareButton(finalWinner);
}

// Add share functionality
function setupShareButton(winner) {
    const shareButton = document.getElementById('share-button');
    const shareText = `${winner.brand} ${winner.model} 🏆 won after 10 rounds in GEAR BATTLE! 🎸 Try it yourself at https://gearbattle.netlify.app 🎮`;
    
    // Create Twitter share URL
    const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
    
    shareButton.addEventListener('click', () => {
        // Open Twitter share in a new window
        window.open(tweetUrl, '_blank', 'width=600,height=400');
    });
}

// Reset game
function resetGame() {
    currentRound = 1;
    currentPedal = null;
    selectedPedals = [];
    usedPedals.clear(); // Clear used pedals when resetting
    currentRoundElement.textContent = currentRound;
    resultsElement.style.display = 'none';
    roundCounter.style.display = 'block';
    battleContainer.style.display = 'flex';
    startNewRound();
}

// Event listeners
pedal1Element.addEventListener('click', () => {
    const pedal1 = {
        brand: pedal1Element.querySelector('.brand').textContent,
        model: pedal1Element.querySelector('.model').textContent
    };
    handlePedalSelection(pedal1);
});

pedal2Element.addEventListener('click', () => {
    const pedal2 = {
        brand: pedal2Element.querySelector('.brand').textContent,
        model: pedal2Element.querySelector('.model').textContent
    };
    handlePedalSelection(pedal2);
});

playAgainButton.addEventListener('click', resetGame);

// Initialize game
loadPedals().then(() => {
    startNewRound();
}); 