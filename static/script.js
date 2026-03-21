// Utility functions
function getStatusLabel(status) {
    switch (status) {
        case 'full': return 'Full';
        case 'busy': return 'Busy';
        default: return 'Open';
    }
}

function getFillClass(pct) {
    if (pct >= 95) return "fill-danger";
    if (pct >= 70) return "fill-warn";
    return "fill-good";
}

function getValueClass(pct) {
    if (pct >= 95) return "bad";
    if (pct >= 70) return "warn";
    return "good";
}

// Fetch parking data from Flask API
async function fetchParkingData() {
    const response = await fetch('/api/parking-data');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

// Create cards once at runtime with blank data (initial setup)
function createCards() {
    const grid = document.getElementById("lots-grid");

    // Clear loading state
    grid.innerHTML = "";

    // Create placeholder cards - we'll get the lot count from a sample fetch later
    // For now, create a reasonable number of placeholder cards
    const placeholderLots = [
        { lot_id: 'Loading...', lot: 'placeholder-1' },
        { lot_id: 'Loading...', lot: 'placeholder-2' },
        { lot_id: 'Loading...', lot: 'placeholder-3' },
        { lot_id: 'Loading...', lot: 'placeholder-4' },
        { lot_id: 'Loading...', lot: 'placeholder-5' }
    ];

    // Create each lot card with blank data
    placeholderLots.forEach((lot, i) => {
        const card = document.createElement("div");
        card.className = "lot-card";
        card.style.animationDelay = `${i * 0.07}s`;
        card.dataset.lotId = lot.lot; // Add data attribute for identification

        card.innerHTML = `
        <div class="lot-header">
          <div>
            <div class="lot-id">${lot.lot_id}</div>
            <div class="lot-name">—</div>
          </div>
          <span class="status-chip open">Loading</span>
        </div>
        <div class="progress-section">
          <div class="progress-labels">
            <span>Occupancy</span>
            <span class="occupancy-percent">—%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill fill-good" style="width: 0%"></div>
          </div>
        </div>
        <div class="stats-row">
          <div class="stat-box">
            <div class="stat-label">Available</div>
            <div class="stat-value available-value good">—</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Max Capacity</div>
            <div class="stat-value capacity-value" style="color:var(--accent)">—</div>
          </div>
        </div>
      `;
        grid.appendChild(card);
    });
}

// Update existing cards with new data (called on each refresh)
async function updateCards() {
    console.log("updating cards")
    const grid = document.getElementById("lots-grid");

    try {
        const data = await fetchParkingData();
        const { lots, summary } = data;

        // If we have more lots than placeholder cards, recreate the grid
        const existingCards = grid.querySelectorAll('.lot-card');
        if (lots.length !== existingCards.length) {
            // only true if first time calling updateCards?
            grid.innerHTML = "";
            lots.forEach((lot, i) => {
                const card = document.createElement("div");
                card.className = "lot-card";
                card.style.animationDelay = `${i * 0.07}s`;
                card.dataset.lotId = lot.lot_id;

                card.innerHTML = `
                <div class="lot-header">
                  <div>
                    <div class="lot-id">—</div>
                    <div class="lot-name">—</div>
                  </div>
                  <span class="status-chip open">Loading</span>
                </div>
                <div class="progress-section">
                  <div class="progress-labels">
                    <span>Occupancy</span>
                    <span class="occupancy-percent">—%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill fill-good" style="width: 0%"></div>
                  </div>
                </div>
                <div class="stats-row">
                  <div class="stat-box">
                    <div class="stat-label">Available</div>
                    <div class="stat-value available-value good">—</div>
                  </div>
                  <div class="stat-box">
                    <div class="stat-label">Max Capacity</div>
                    <div class="stat-value capacity-value" style="color:var(--accent)">—</div>
                  </div>
                </div>
              `;
                grid.appendChild(card);
            });
        }

        // Update each lot card with the processed data
        lots.forEach((lot, i) => {
            // this ternary operation is kinda dumb
            const card = document.querySelector(`[data-lot-id="${lot.lot_id}"]`) || 
                        document.querySelector(`[data-lot-id="placeholder-${i + 1}"]`);
            if (!card) return; // Skip if card doesn't exist

            // Process data with same logic as original createCards
            const lotName = lot.name || ""
            const pct = Math.min(100, Math.max(0, Math.round((lot.percent_full || 0) * 100)));

            // Update data attribute if needed
            card.dataset.lotId = lot.lot_id;

            // Update lot ID and name
            const lotIdElement = card.querySelector('.lot-id');
            lotIdElement.textContent = lot.lot_id;
            
            const lotNameElement = card.querySelector('.lot-name');
            lotNameElement.textContent = lotName;

            // Update status chip
            const statusChip = card.querySelector('.status-chip');
            statusChip.className = `status-chip ${lot.status}`;
            statusChip.textContent = getStatusLabel(lot.status);

            // Update occupancy percentage
            const occupancyPercent = card.querySelector('.occupancy-percent');
            occupancyPercent.textContent = `${pct}%`;

            // Update progress bar
            const progressFill = card.querySelector('.progress-fill');
            progressFill.className = `progress-fill ${getFillClass(pct)}`;
            progressFill.style.width = `${pct}%`;

            // Update available spots
            const availableValue = card.querySelector('.available-value');
            availableValue.className = `stat-value available-value ${getValueClass(pct)}`;
            availableValue.textContent = lot.available;

            // Update capacity (in case it changes)
            const capacityValue = card.querySelector('.capacity-value');
            capacityValue.textContent = lot.capacity;
        });

        // Update summary
        await updateSummary(summary);

    } catch (error) {
        console.error('Error updating parking data:', error);
        // Show error state
        const grid = document.getElementById("lots-grid");
        grid.innerHTML = `
        <div class="error">
          <strong>Error loading parking data:</strong><br>
          ${error.message}<br>
          <small>Make sure the Flask server is running.</small>
        </div>
      `;
    }
}

// Helper function to update summary section
async function updateSummary(summary) {
    document.getElementById("total-lots").textContent = summary.total_lots;
    document.getElementById("total-available").textContent = summary.total_available;
    document.getElementById("total-capacity").textContent = summary.total_capacity;
    document.getElementById("last-updated").textContent = summary.last_updated;
}

// Initialize dashboard
createCards(); // Create cards once at runtime
updateCards(); // Immediately populate with data

// Refresh data every 10 seconds (update existing cards)
setInterval(updateCards, 10000);

// Manual refresh on click (for development)
document.addEventListener('keydown', (e) => {
    if (e.code === 'KeyR') {
        e.preventDefault();
        updateCards(); // Update cards instead of recreating them
    }
});
