export function renderResultsTable(result, containerId = "results") {
  if (!result) {
    document.getElementById(containerId).innerHTML = `<div>No details found.</div>`;
    return;
  }

  // Sort the details array by date
  const sortedDetails = result.details.sort((a, b) => {
    const dateA = parseDate(a.date_of_challenge);
    const dateB = parseDate(b.date_of_challenge);

    // Place invalid dates (e.g., "AY 2022-2023") at the bottom
    if (!dateA) return 1;
    if (!dateB) return -1;

    // Sort valid dates in descending order (most recent first)
    return dateB - dateA;
  });

  let tableHTML = `
    <div>
      <h4>${result.value} - ${result.type.charAt(0).toUpperCase() + result.type.slice(1)}</h4>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            ${result.type === "book" || result.type === "state" ? "<th>Author</th>" : ""}
            ${result.type === "author" || result.type === "state" ? "<th>Book</th>" : ""}
            ${result.type !== "state" ? "<th>State</th>" : ""}
            <th>District</th>
            <th>Date of Challenge</th>
            <th>Ban Status</th>
          </tr>
        </thead>
        <tbody>
  `;

  tableHTML += sortedDetails.map(detail => `
    <tr>
      ${detail.author ? `<td>${detail.author}</td>` : ""}
      ${detail.book ? `<td>${detail.book}</td>` : ""}
      ${result.type !== "state" ? `<td>${detail.state || "Unknown"}</td>` : ""}
      <td>${detail.district || "Unknown"}</td>
      <td>${detail.date_of_challenge || "Unknown"}</td>
      <td>${detail.ban_status || "Unknown"}</td>
    </tr>
  `).join("");

  tableHTML += `
        </tbody>
      </table>
    </div>
  `;

  document.getElementById(containerId).innerHTML = tableHTML;
}

// Helper function to parse dates
function parseDate(dateString) {
  // Handle invalid or non-standard dates like "AY 2022-2023"
  if (!dateString || dateString.startsWith("AY")) return null;

  // Parse valid dates
  const parsedDate = new Date(dateString);
  return isNaN(parsedDate) ? null : parsedDate;
}