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

    let tableHTML = `
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
      tableHTML += pageData.map(detail => `
        <tr>
          ${detail.author ? `<td>${detail.author}</td>` : ""}
          ${detail.book ? `<td>${detail.book}</td>` : ""}
          ${result.type !== "state" ? `<td>${detail.state || "Unknown"}</td>` : ""}
          <td>${detail.district || "Unknown"}</td>
          <td>${detail.date_of_challenge || "Unknown"}</td>
          <td>${detail.ban_status || "Unknown"}</td>
        </tr>
      `).join("");
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