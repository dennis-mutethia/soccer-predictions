---
layout: default
title: Soccer Predictions
---
<html>
  <head>
    <title>Soccer Predictions</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{{ site.baseurl }}/styles.css">
  </head>
  <body>

  <div id="csv-table-container"></div>

  <script>
    // Fetch CSV data and display in a table
    fetch("{{ site.baseurl }}/predictions.csv")
      .then(response => response.text())
      .then(data => {
        // Convert CSV to an array of arrays
        const csvArray = data.split('\n').map(row => row.split(','));

        // Create HTML table
        const table = document.createElement('table');
        table.classList.add('styled-table');

        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');

        const columnsToDisplay = ['start_time', 'home_team', 'away_team', 'prediction', 'odd'];

        columnsToDisplay.forEach(column => {
            // Capitalize the heading and remove underscores
            const columnHeader = column.replace('_', ' ').toUpperCase();

            const th = document.createElement('th');
            th.textContent = columnHeader;
            headerRow.appendChild(th);
        });
        const th = document.createElement('th');
        th.textContent = 'STATUS';
        headerRow.appendChild(th);

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        for (let i = csvArray.length - 1; i > 0; i--) {
          const row = document.createElement('tr');
          columnsToDisplay.forEach(column => {
            const columnIndex = csvArray[0].indexOf(column);
            const td = document.createElement('td');
            td.textContent = csvArray[i][columnIndex];
            row.appendChild(td);
          });         
          
          const td = document.createElement('td');
          const status = csvArray[i][8] ? csvArray[i][8].trim() : '';
          
          if (status === 'WON') {
            td.innerHTML = '<img src="{{ site.baseurl }}/tick.png" alt="Green Tick" />';
          } else if (status === 'LOST') {
            td.innerHTML = '<img src="{{ site.baseurl }}/cross.png" alt="Red Cross" />';
          } else{
            td.textContent = status;
          }
          
          row.appendChild(td);

          tbody.appendChild(row);
        }
        table.appendChild(tbody);

        // Append table to the container
        document.getElementById('csv-table-container').appendChild(table);
      })
      .catch(error => console.error('Error fetching CSV:', error));
  </script>
  </body>
</html> 