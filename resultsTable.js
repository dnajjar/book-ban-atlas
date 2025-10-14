export function renderResultsTable(result, containerId = "results", showAllColumns = false, itemsPerPage = 50) {
  if (!result) {
    document.getElementById(containerId).innerHTML = `<div>No details found.</div>`;
    return;
  }

  // Store original data and current sort state
  let sortedDetails = [...result.details]; // Make a copy
  let currentPage = 1;
  let currentSort = { column: 'author', direction: 'asc' };

  // Initial sort by author
  sortData('author', 'asc');

  function sortData(column, direction) {
    sortedDetails.sort((a, b) => {
      let aValue, bValue;

      // Get values based on column
      switch(column) {
        case 'author':
          aValue = (a.author || "").toLowerCase();
          bValue = (b.author || "").toLowerCase();
          break;
        case 'book':
          aValue = (a.book || "").toLowerCase();
          bValue = (b.book || "").toLowerCase();
          break;
        case 'state':
          aValue = (a.state || "").toLowerCase();
          bValue = (b.state || "").toLowerCase();
          break;
        case 'district':
          aValue = (a.district || "").toLowerCase();
          bValue = (b.district || "").toLowerCase();
          break;
        case 'date_of_challenge':
          aValue = parseDate(a.date_of_challenge);
          bValue = parseDate(b.date_of_challenge);
          
          // Handle null dates
          if (!aValue && !bValue) return 0;
          if (!aValue) return 1;
          if (!bValue) return -1;
          
          const comparison = aValue - bValue;
          return direction === 'asc' ? comparison : -comparison;
        case 'ban_status':
          aValue = (a.ban_status || "").toLowerCase();
          bValue = (b.ban_status || "").toLowerCase();
          break;
        default:
          aValue = "";
          bValue = "";
      }

      // For non-date columns
      if (column !== 'date_of_challenge') {
        const comparison = aValue.localeCompare(bValue);
        return direction === 'asc' ? comparison : -comparison;
      }
    });

    currentSort = { column, direction };
  }

  function renderPage(page) {
    const totalPages = Math.ceil(sortedDetails.length / itemsPerPage);
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = sortedDetails.slice(startIndex, endIndex);

    // Show author statistics if this is an author search
    let authorStatsHTML = '';
    if (result.type === 'author' && result.author_stats) {
      const stats = result.author_stats;
      authorStatsHTML = `
        <div class="author-stats">
          <h4>📚 ${result.value} - Author Statistics</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-number">${stats.unique_books_banned || 0}</span>
              <span class="stat-label">Unique Books Banned</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">${stats.total_ban_instances || 0}</span>
              <span class="stat-label">Total Ban Instances</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">${stats.states_with_bans || 0}</span>
              <span class="stat-label">States with Bans</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">${stats.districts_with_bans || 0}</span>
              <span class="stat-label">Districts with Bans</span>
            </div>
          </div>
          ${stats.banned_books && stats.banned_books.length > 0 ? `
            <div class="banned-books-list">
              <strong>Banned Books by ${result.value}:</strong><br>
              ${stats.banned_books.join(', ')}
            </div>
          ` : ''}
        </div>
      `;
    }

    let tableHTML = `
      ${authorStatsHTML}
      <div>
        <h4>${result.value} - ${result.type.charAt(0).toUpperCase() + result.type.slice(1)}</h4>
        <p>Showing ${startIndex + 1}-${Math.min(endIndex, sortedDetails.length)} of ${sortedDetails.length} results</p>
      </div>
      <div class="table-wrapper">
        <table id="results-table">
          <thead>
            <tr>
    `;

    // Show all columns if showAllColumns is true
    if (showAllColumns) {
      tableHTML += `
              <th class="sortable ${currentSort.column === 'author' ? currentSort.direction : ''}" data-column="author">Author</th>
              <th class="sortable ${currentSort.column === 'book' ? currentSort.direction : ''}" data-column="book">Book</th>
              <th class="sortable ${currentSort.column === 'state' ? currentSort.direction : ''}" data-column="state">State</th>
              <th class="sortable ${currentSort.column === 'district' ? currentSort.direction : ''}" data-column="district">District</th>
              <th class="sortable ${currentSort.column === 'date_of_challenge' ? currentSort.direction : ''}" data-column="date_of_challenge">Date of Challenge</th>
              <th class="sortable ${currentSort.column === 'ban_status' ? currentSort.direction : ''}" data-column="ban_status">Ban Status</th>
      `;
    } else {
      tableHTML += `
              ${result.type === "book" || result.type === "state" ? `<th class='sortable ${currentSort.column === 'author' ? currentSort.direction : ''}' data-column='author'>Author</th>` : ""}
              ${result.type === "author" || result.type === "state" ? `<th class='sortable ${currentSort.column === 'book' ? currentSort.direction : ''}' data-column='book'>Book</th>` : ""}
              ${result.type !== "state" ? `<th class='sortable ${currentSort.column === 'state' ? currentSort.direction : ''}' data-column='state'>State</th>` : ""}
              <th class='sortable ${currentSort.column === 'district' ? currentSort.direction : ''}' data-column="district">District</th>
              <th class='sortable ${currentSort.column === 'date_of_challenge' ? currentSort.direction : ''}' data-column="date_of_challenge">Date of Challenge</th>
              <th class='sortable ${currentSort.column === 'ban_status' ? currentSort.direction : ''}' data-column="ban_status">Ban Status</th>
      `;
    }

    tableHTML += `
            </tr>
          </thead>
          <tbody>
    `;

    // Map rows for current page
    if (showAllColumns) {
      tableHTML += pageData.map(detail => `
        <tr>
          <td>${detail.author || "Unknown"}</td>
          <td>${detail.book || "Unknown"}</td>
          <td>${detail.state || "Unknown"}</td>
          <td>${detail.district || "Unknown"}</td>
          <td>${detail.date_of_challenge || "Unknown"}</td>
          <td>${detail.ban_status || "Unknown"}</td>
        </tr>
      `).join("");
    } else {
      tableHTML += pageData.map(detail => {
        let row = "<tr>";
        
        // Add cells in the same order as headers
        if (result.type === "book" || result.type === "state") {
          row += `<td>${detail.author || "Unknown"}</td>`;
        }
        if (result.type === "author" || result.type === "state") {
          row += `<td>${detail.book || "Unknown"}</td>`;
        }
        if (result.type !== "state") {
          row += `<td>${detail.state || "Unknown"}</td>`;
        }
        
        row += `<td>${detail.district || "Unknown"}</td>`;
        row += `<td>${detail.date_of_challenge || "Unknown"}</td>`;
        row += `<td>${detail.ban_status || "Unknown"}</td>`;
        row += "</tr>";
        
        return row;
      }).join("");
    }

    tableHTML += `
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <button id="prev-btn" ${page === 1 ? 'disabled' : ''}>Previous</button>
        <span class="page-info">Page ${page} of ${totalPages}</span>
        <button id="next-btn" ${page === totalPages ? 'disabled' : ''}>Next</button>
      </div>
    `;

    document.getElementById(containerId).innerHTML = tableHTML;

    // Add pagination event listeners
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          renderPage(currentPage);
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
          currentPage++;
          renderPage(currentPage);
        }
      });
    }

    // Add sorting functionality
    addSortingToTable();
  }

  function addSortingToTable() {
    const headers = document.querySelectorAll('.sortable');
    headers.forEach(header => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        const column = header.dataset.column;
        const newDirection = (currentSort.column === column && currentSort.direction === 'asc') ? 'desc' : 'asc';
        
        // Sort the entire dataset
        sortData(column, newDirection);
        
        // Reset to first page and re-render
        currentPage = 1;
        renderPage(currentPage);
      });
    });
  }

  // Initial page render
  renderPage(currentPage);
}

// Helper function to parse dates
function parseDate(dateString) {
  if (!dateString || dateString.startsWith("AY")) return null;
  const parsedDate = new Date(dateString);
  return isNaN(parsedDate) ? null : parsedDate;
}