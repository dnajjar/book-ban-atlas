export function renderResultsTable(result, containerId = "results", showAllColumns = false, itemsPerPage = 50) {
  if (!result) {
    document.getElementById(containerId).innerHTML = `<div>No details found.</div>`;
    return;
  }
  function formatAuthorName(authorName) {
    if (!authorName || authorName === 'Unknown') {
      return authorName;
    }
    
    // Check if name contains a comma (indicating "Last, First" format)
    if (authorName.includes(',')) {
      const parts = authorName.split(',').map(part => part.trim());
      if (parts.length === 2) {
        return `${parts[1]} ${parts[0]}`; // Return "First Last"
      }
    }
    
    // Return as-is if no comma found
    return authorName;
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
        case 'themes':
          aValue = (a.themes || "").toLowerCase();
          bValue = (b.themes || "").toLowerCase();
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
  
  // Collect all themes from this author's books
  const authorThemes = new Set();
  sortedDetails.forEach(detail => {
    if (detail.themes) {
      detail.themes.split(',').forEach(theme => {
        const cleanTheme = theme.trim();
        if (cleanTheme) {
          authorThemes.add(cleanTheme);
        }
      });
    }
  });
  
  authorStatsHTML = `
  <div class="author-stats">
    <h4>📚 ${formatAuthorName(result.value)} - Author Summary </h4>
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
    ${authorThemes.size > 0 ? `
      <div class="author-themes">
        <strong>Common Themes in ${formatAuthorName(result.value)}'s Banned Books:</strong>
        <div class="themes-list">
          ${Array.from(authorThemes).map(theme => `<span class="theme-badge">${theme}</span>`).join(' ')}
        </div>
      </div>
    ` : ''}
    ${stats.banned_books && stats.banned_books.length > 0 ? `
      <div class="banned-books-list">
        <strong>Banned Books by ${formatAuthorName(result.value)}:</strong><br>
        ${stats.banned_books.join(', ')}
      </div>
    ` : ''}
  </div>
`;
  }

  let bookSummaryHTML = '';
  if (result.type === 'book' && sortedDetails.length > 0) {
    const firstDetail = sortedDetails[0]; // Get book info from first record
    const coverUrl = firstDetail.cover_url;
    const description = firstDetail.description;
    const themes = firstDetail.themes;
    const author = firstDetail.author;
    const publishYear = firstDetail.publish_year;
    const workUrl = firstDetail.work_id ? `https://openlibrary.org/works/${firstDetail.work_id}` : null;
  
    bookSummaryHTML = `
    <div class="book-summary">
      <div class="book-summary-header">
        <div class="book-cover-container">
          ${coverUrl ? `<img src="${coverUrl}" alt="${result.value}" class="book-summary-cover" onerror="this.style.display='none'">` : ''}
        </div>
        <div class="book-info">
          <h4>📖 ${workUrl ? 
            `<a href="${workUrl}" target="_blank" class="book-title-link">${result.value}</a>` : 
            result.value
          }</h4>
          ${author && author !== 'Unknown' ? `<p class="book-author">by ${formatAuthorName(author)}</p>` : ''}
          ${publishYear ? `<p class="book-year">Published: ${publishYear}</p>` : ''}
          ${themes ? `<div class="book-themes">${formatThemes(themes)}</div>` : ''}
        </div>
        ${description && description !== 'No description available' ? `
          <div class="book-description">
            <strong>Description:</strong>
            <p>${description}</p>
          </div>
        ` : ''}
      </div>
    </div>
  `;
    }

    let tableHTML = `
      ${authorStatsHTML}
      ${bookSummaryHTML}
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
              <th class="sortable ${currentSort.column === 'themes' ? currentSort.direction : ''}" data-column="themes">Themes</th>
              <th class="sortable ${currentSort.column === 'date_of_challenge' ? currentSort.direction : ''}" data-column="date_of_challenge">Date of Challenge</th>
              <th class="sortable ${currentSort.column === 'ban_status' ? currentSort.direction : ''}" data-column="ban_status">Ban Status</th>
      `;
    } else {
      tableHTML += `
              ${result.type === "book" || result.type === "state" ? `<th class='sortable ${currentSort.column === 'author' ? currentSort.direction : ''}' data-column='author'>Author</th>` : ""}
              ${result.type === "author" || result.type === "state" ? `<th class='sortable ${currentSort.column === 'book' ? currentSort.direction : ''}' data-column='book'>Book</th>` : ""}
              ${result.type !== "state" ? `<th class='sortable ${currentSort.column === 'state' ? currentSort.direction : ''}' data-column='state'>State</th>` : ""}
              <th class='sortable ${currentSort.column === 'district' ? currentSort.direction : ''}' data-column="district">District</th>
              <th class='sortable ${currentSort.column === 'themes' ? currentSort.direction : ''}' data-column="themes">Themes</th>
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
          <td>${formatAuthorName(detail.author) || "Unknown"}</td>
          <td>${detail.book || "Unknown"}</td>
          <td>${detail.state || "Unknown"}</td>
          <td>${detail.district || "Unknown"}</td>
          <td class="themes-cell">${formatThemes(detail.themes)}</td>
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
        row += `<td class="themes-cell">${formatThemes(detail.themes)}</td>`;
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

// Helper function to format themes nicely
function formatThemes(themesString) {
  if (!themesString || themesString.trim() === '') {
    return '<span class="no-themes">No themes identified</span>';
  }
  
  // Split themes by comma and create badges
  const themes = themesString.split(',').map(theme => theme.trim()).filter(theme => theme);
  
  if (themes.length === 0) {
    return '<span class="no-themes">No themes identified</span>';
  }
  
  return themes.map(theme => 
    `<span class="theme-badge">${theme}</span>`
  ).join(' ');
}

// Helper function to parse dates
function parseDate(dateString) {
  if (!dateString || dateString.startsWith("AY")) return null;
  const parsedDate = new Date(dateString);
  return isNaN(parsedDate) ? null : parsedDate;
}