// Status helpers
function getStatusLabel(status) {
  switch (status) {
    case 'full': return 'Full';
    case 'busy': return 'Busy';
    default: return 'Open';
  }
}

function getFillClass(pct) {
  if (pct >= 95) return 'fill-danger';
  if (pct >= 70) return 'fill-warn';
  return 'fill-good';
}

function getValueClass(pct) {
  if (pct >= 95) return 'bad';
  if (pct >= 70) return 'warn';
  return 'good';
}

// Main dashboard update function
async function updateDashboard() {
  try {
    const response = await fetch(window.apiLotsUrl);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    const lots = data.lots;

    // Handle both dashboard styles
    const grid = document.getElementById("lots-grid");
    const container = document.getElementById("lots-container");

    if (grid) {
      updateGridStyle(lots, grid, data);
    } else if (container) {
      updateBootstrapStyle(lots, container, data);
    }

    // Update summary if present
    updateSummary(lots, data);

  } catch (err) {
    console.error('Dashboard update failed:', err);
    const grid = document.getElementById('lots-grid');
    const container = document.getElementById("lots-container");
    
    if (grid) {
      grid.innerHTML = `
        <div class="error">
          <strong>Error loading data:</strong><br>${err.message}<br>
          <small>Check Flask server is running</small>
        </div>`;
    } else if (container) {
      container.innerHTML = `<div class="col-12"><div class="alert alert-danger text-center">Error loading data: ${err.message}</div></div>`;
    }
  }
}

// Grid style update (for lots_dashboard.html style)
function updateGridStyle(lots, grid, data) {
  // If number of lots changed → rebuild cards (rare, but safe)
  if (lots.length !== grid.querySelectorAll('.lot-card').length) {
    grid.innerHTML = '';
    lots.forEach((lot, i) => {
      const card = document.createElement('div');
      card.className = 'lot-card';
      card.style.animationDelay = `${i * 0.07}s`;
      card.dataset.lotId = lot.id;
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
            <div class="progress-fill fill-good" style="width:0%"></div>
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

  // Update each card
  lots.forEach(lot => {
    const card = document.querySelector(`[data-lot-id="${lot.id}"]`);
    if (!card) return;

    const pct = lot.percent;

    card.querySelector('.lot-id').textContent = lot.id;
    card.querySelector('.lot-name').textContent = lot.name;

    const chip = card.querySelector('.status-chip');
    const status = pct >= 95 ? 'full' : pct >= 70 ? 'busy' : 'open';
    chip.className = `status-chip ${status}`;
    chip.textContent = getStatusLabel(status);

    card.querySelector('.occupancy-percent').textContent = `${pct}%`;

    const fill = card.querySelector('.progress-fill');
    fill.className = `progress-fill ${getFillClass(pct)}`;
    fill.style.width = `${pct}%`;

    const avail = card.querySelector('.available-value');
    avail.className = `stat-value available-value ${getValueClass(pct)}`;
    avail.textContent = lot.available;

    card.querySelector('.capacity-value').textContent = lot.capacity;
  });
}

// Bootstrap style update (for basic dashboard style)
function updateBootstrapStyle(lots, container, data) {
  let html = "";
  if (lots.length === 0) {
    html = `<div class="col-12"><div class="alert alert-info text-center">No parking lots found.</div></div>`;
  } else {
    lots.forEach(lot => {
      const barClass = lot.percent < 60 ? 'bg-success' :
        lot.percent <= 85 ? 'bg-warning' : 'bg-danger';

      html += `
      <div class="col">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-bold">${lot.name}</h5>
            <div class="mb-3">
              <div class="d-flex justify-content-between mb-1 small">
                <span>Occupied: <strong>${lot.occupancy}</strong></span>
                <span>Available: <strong>${lot.available}</strong></span>
              </div>
              <div class="progress" role="progressbar" aria-label="Occupancy" 
                   aria-valuenow="${lot.percent}" aria-valuemin="0" aria-valuemax="100" style="height: 1.5rem;">
                <div class="progress-bar ${barClass} fw-bold" style="width: ${lot.percent}%">
                  ${lot.percent}%
                </div>
              </div>
            </div>
            <div class="text-muted small">Capacity: ${lot.capacity} spaces</div>
          </div>
        </div>
      </div>
    `;
    });
  }

  container.innerHTML = html;
}

// Update summary section if present
function updateSummary(lots, data) {
  const totalLotsEl = document.getElementById('total-lots');
  const totalAvailEl = document.getElementById('total-available');
  const totalCapacityEl = document.getElementById('total-capacity');
  const lastUpdatedEl = document.getElementById('last-updated');

  if (totalLotsEl) totalLotsEl.textContent = lots.length;
  if (totalAvailEl) totalAvailEl.textContent = lots.reduce((sum, l) => sum + l.available, 0);
  if (totalCapacityEl) totalCapacityEl.textContent = lots.reduce((sum, l) => sum + l.capacity, 0);
  if (lastUpdatedEl) lastUpdatedEl.textContent = data.now;
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  updateDashboard();                // initial load
  setInterval(updateDashboard, 5000);  // every 5 seconds
});