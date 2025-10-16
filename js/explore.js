// explore.js
export function renderExploreTab() {
    if (!window.searchData) {
      console.error('Search data not available');
      return;
    }
  
    const data = window.searchData;
    
    // Get counts from the search data structure instead of flattened details
    // This matches what the search results show
    
    // Calculate top 10 books using search data structure
    const bookData = data.filter(item => item.type === 'book');
    const topBooks = bookData
      .map(item => [item.value, item.details.length])
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
  
    // Calculate top 10 authors using search data structure  
    const authorData = data.filter(item => item.type === 'author');
    const topAuthors = authorData
      .map(item => [item.value, item.details.length])
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
  
    // Calculate top 10 states using search data structure
    const stateData = data.filter(item => item.type === 'state');
    const topStates = stateData
      .map(item => [item.value, item.details.length])
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
  
    // Calculate top 10 districts using search data structure
    const districtData = data.filter(item => item.type === 'district');
    const topDistricts = districtData
      .map(item => [item.value, item.details.length])
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    const themeData = data.filter(item => item.type === 'theme');
    const topThemes = themeData
      .map(item => [item.value, item.details.length])
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);

    
    // Render the lists
    renderTopList('top-books', topBooks, 'book');
    renderTopList('top-authors', topAuthors, 'author');
    renderTopList('top-states', topStates, 'state');
    renderTopList('top-districts', topDistricts, 'district');
    renderTopList('top-themes', topThemes, 'theme');
  }
  
  function renderTopList(containerId, items, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
  
    let html = '<ol class="top-list-items">';
    
    items.forEach(([name, count], index) => {
      html += `
        <li class="top-list-item" onclick="searchFor('${name.replace(/'/g, "\\'")}', '${type}')">
          <div class="item-info">
            <span class="item-name">${name}</span>
            <span class="item-count">${count} bans</span>
          </div>
          <div class="item-rank">#${index + 1}</div>
        </li>
      `;
    });
    
    html += '</ol>';
    container.innerHTML = html;
  }
  
  // Function to search for an item when clicked
  window.searchFor = function(name, type) {
    // Switch to search tab
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(button => {
      button.classList.remove('active');
    });
    
    document.getElementById('search-tab').classList.add('active');
    document.querySelector('.tab-button[onclick="showTab(\'search\')"]').classList.add('active');
    
    // Set search field value
    const searchField = document.getElementById('search-field');
    searchField.value = name;
    
    // Trigger search
    const result = window.searchData.find(item => 
      item.value.toLowerCase() === name.toLowerCase() && item.type === type
    );
    
    if (result) {
      import('./resultsTable.js').then(module => {
        module.renderResultsTable(result, "results", true);
      });
    }
  };