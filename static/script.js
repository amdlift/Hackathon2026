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
  try {
    const response = await fetch('/api/parking-data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching parking data:', error);
    throw error;
  }
}

// Create cards once at runtime (initial setup)
async function createCards() {
  const grid = document.getElementById("lots-grid");

  try {
    const data = await fetchParkingData();
    const { lots } = data;

    // Clear loading state
    grid.innerHTML = "";

    // Create each lot card with initial data
    lots.forEach((lot, i) => {
      const card = document.createElement("div");
      card.className = "lot-card";
      card.style.animationDelay = `${i * 0.07}s`;
      card.dataset.lotId = lot.lot; // Add data attribute for identification

      const lotName = lot.name || `${lot.lot}`;

      card.innerHTML = `
        <div class="lot-header">
          <div>
            <div class="lot-id">${lot.lot}</div>
            <div class="lot-name">${lotName}</div>
          </div>
          <span class="status-chip ${lot.status}">${getStatusLabel(lot.status)}</span>
        </div>
        <div class="progress-section">
          <div class="progress-labels">
            <span>Occupancy</span>
            <span class="occupancy-percent">${lot.occupancy_pct}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill ${getFillClass(lot.occupancy_pct)}" style="width: ${lot.occupancy_pct}%"></div>
          </div>
        </div>
        <div class="stats-row">
          <div class="stat-box">
            <div class="stat-label">Available</div>
            <div class="stat-value available-value ${getValueClass(lot.occupancy_pct)}">${lot.available}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Max Capacity</div>
            <div class="stat-value capacity-value" style="color:var(--accent)">${lot.capacity}</div>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });

    // Initial summary update
    await updateSummary(data.summary);

  } catch (error) {
    // Show error state
    grid.innerHTML = `
      <div class="error">
        <strong>Error loading parking data:</strong><br>
        ${error.message}<br>
        <small>Make sure the Flask server is running.</small>
      </div>
    `;
  }
}

// Update existing cards with new data (called on each refresh)
async function updateCards() {
  try {
    const data = await fetchParkingData();
    const { lots, summary } = data;

    // Update each lot card
    lots.forEach(lot => {
      const card = document.querySelector(`[data-lot-id="${lot.lot}"]`);
      if (!card) return; // Skip if card doesn't exist

      // Update status chip
      const statusChip = card.querySelector('.status-chip');
      statusChip.className = `status-chip ${lot.status}`;
      statusChip.textContent = getStatusLabel(lot.status);

      // Update occupancy percentage
      const occupancyPercent = card.querySelector('.occupancy-percent');
      occupancyPercent.textContent = `${lot.occupancy_pct}%`;

      // Update progress bar
      const progressFill = card.querySelector('.progress-fill');
      progressFill.className = `progress-fill ${getFillClass(lot.occupancy_pct)}`;
      progressFill.style.width = `${lot.occupancy_pct}%`;

      // Update available spots
      const availableValue = card.querySelector('.available-value');
      availableValue.className = `stat-value available-value ${getValueClass(lot.occupancy_pct)}`;
      availableValue.textContent = lot.available;

      // Update capacity (in case it changes)
      const capacityValue = card.querySelector('.capacity-value');
      capacityValue.textContent = lot.capacity;
    });

    // Update summary
    await updateSummary(summary);

  } catch (error) {
    console.error('Error updating parking data:', error);
    // You could show a toast notification or update a status indicator here
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

// Refresh data every 10 seconds (update existing cards)
setInterval(updateCards, 10000);

// Manual refresh on click (for development)
document.addEventListener('keydown', (e) => {
  if (e.code === 'KeyR' && e.ctrlKey) {
    e.preventDefault();
    updateCards(); // Update cards instead of recreating them
  }
});