export function initializeMap() {
  const mapContainer = document.getElementById('map');
  
  // Show loading indicator for map
  mapContainer.innerHTML = `
    <div class="map-loading-indicator">
      <div class="loading-spinner"></div>
      <p>Loading map data...</p>
    </div>
  `;

  const usBounds = L.latLngBounds(
    [24.396308, -125.0],
    [49.384358, -66.93457]
  );

  const eastCoastBounds = L.latLngBounds(
    [24.396308, -82.0], // Southwest corner (Key West, Florida)
    [40.712776, -70.0]  // Northeast corner (New York City, NY)
  );

  // Clear the loading indicator and create the map
  setTimeout(() => {
    mapContainer.innerHTML = ''; // Clear loading indicator
    
    const map = L.map('map', {
      maxBoundsViscosity: 1.0,    // Optional: Sticky bounds
      minZoom: 4,
      maxZoom: 10
    }).setView([39.8283, -98.5795], 4);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 10,
    }).addTo(map);

    function getColor(banCount, maxBan) {
      const t = banCount / maxBan;
      if (t === 0) return "#f5f5f5";
      if (t < 0.2) return "#BFB2F3";
      if (t < 0.4) return "#96CAF7";
      if (t < 0.6) return "#9CDCAA";
      if (t < 0.8) return "#F3C6A5";
      return "#F8A3A8";
    }

    fetch('./geojson/districts_with_ban_counts.geojson')
      .then(response => response.json())
      .then(geojsonData => {
        const legend = L.control({ position: 'bottomright' });
        const maxBan = Math.max(...geojsonData.features.map(f => f.properties.ban_count || 0));

        legend.onAdd = function(map) {
          const div = L.DomUtil.create('div', 'info legend');
          const steps = 6; // Number of steps in the legend
          const breakpoints = Array.from({ length: steps + 1 }, (_, i) => Math.round((maxBan / steps) * i));

          div.innerHTML = '<strong>Bans</strong><br>';

          // Add the first box for "0"
          div.innerHTML += `
            <i style="background:${getColor(0, maxBan)}; width: 18px; height: 18px; display: inline-block; margin-right: 8px;"></i>
            0<br>
          `;

          // Add the remaining ranges
          for (let i = 1; i < breakpoints.length - 1; i++) {
            const color = getColor(breakpoints[i], maxBan);
            div.innerHTML += `
              <i style="background:${color}; width: 18px; height: 18px; display: inline-block; margin-right: 8px;"></i>
              ${breakpoints[i]}&ndash;${breakpoints[i + 1]}<br>
            `;
          }
          
          return div;
        };

        legend.addTo(map);

        L.geoJSON(geojsonData, {
          style: feature => ({
            fillColor: getColor(feature.properties.ban_count || 0, maxBan),
            weight: 0.5,
            opacity: 0.3,
            color: '#bbb',
            fillOpacity: 1
          }),
          onEachFeature: (feature, layer) => {
            layer.bindPopup(`${feature.properties.LEA_NAME || feature.properties.NAME} <br> ${feature.properties.ban_count || 0} bans`);
          }
        }).addTo(map);
      })
      .catch(error => {
        console.log('Map data not available:', error);
        mapContainer.innerHTML = `
          <div class="map-error">
            <h3>Map Data Not Available</h3>
            <p>Could not load district ban data.</p>
          </div>
        `;
      });
  }, 100); // Small delay to show loading indicator
}