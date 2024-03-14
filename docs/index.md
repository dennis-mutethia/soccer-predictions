<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<div id="csv-table-container"></div>
<div id="pagination-container"></div>

<script>
  // Fetch CSV data and display in a table
  fetch("{{ site.baseurl }}/predictions.csv")
    .then(response => response.text())
    .then(data => {
      // Convert CSV to an array of arrays
      const csvArray = data.split('\n').map(row => row.split(','));

      // Define number of rows per page
      const rowsPerPage = 10;

      // Function to display a specific page
      function displayPage(pageNumber) {
        const start = (pageNumber - 1) * rowsPerPage + 1;
        const end = Math.min(pageNumber * rowsPerPage, csvArray.length - 1);

        // Clear previous table
        const tableContainer = document.getElementById('csv-table-container');
        tableContainer.innerHTML = '';

        // Create HTML table
        const table = document.createElement('table');
        table.classList.add('styled-table');

        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const columnsToDisplay = ['start_time', 'home_team', 'away_team', 'prediction'];

        columnsToDisplay.forEach(column => {
          const th = document.createElement('th');
          th.textContent = column;
          headerRow.appendChild(th);
        });
        const th = document.createElement('th');
        th.textContent = 'status';
        headerRow.appendChild(th);

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        for (let i = end; i >= start; i--) {
          const row = document.createElement('tr');
          columnsToDisplay.forEach(column => {
            const columnIndex = csvArray[0].indexOf(column);
            const td = document.createElement('td');
            td.textContent = csvArray[i][columnIndex];
            row.appendChild(td);
          });

          const status = csvArray[i][8];
          const td = document.createElement('td');

          if (status === 'WON') {
            td.innerHTML = '<img src="{{ site.baseurl }}/tick.png" alt="Green Tick" />';
          } else if (status === 'LOST') {
            td.innerHTML = '<img src="{{ site.baseurl }}/cross.png" alt="Red Cross" />';
          } else {
            td.textContent = status;
          }

          row.appendChild(td);

          tbody.appendChild(row);
        }
        table.appendChild(tbody);

        // Append table to the container
        tableContainer.appendChild(table);
      }

      // Function to generate pagination links
      function generatePaginationLinks() {
        const numPages = Math.ceil((csvArray.length - 1) / rowsPerPage);
        const paginationContainer = document.getElementById('pagination-container');
        paginationContainer.innerHTML = '';

        for (let i = 1; i <= numPages; i++) {
          const link = document.createElement('a');
          link.href = '#';
          link.textContent = i;
          link.addEventListener('click', function (event) {
            event.preventDefault();
            displayPage(i);
          });
          paginationContainer.appendChild(link);
          paginationContainer.appendChild(document.createTextNode(' '));
        }
      }

      // Display the first page by default
      displayPage(1);

      // Generate pagination links
      generatePaginationLinks();
    })
    .catch(error => console.error('Error fetching CSV:', error));
</script>
