---
layout: default
title: Soccer Predictions
---

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

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
      const columnsToDisplay = ['Kickoff', 'Home', 'Away', 'Prediction', 'Status'];

      columnsToDisplay.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
      });

      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Create table body
      const tbody = document.createElement('tbody');

      // Iterate over the CSV array
      csvArray.forEach(rowData => {
        const row = document.createElement('tr');

        // Fetch data from columns 0, 2, 3, and 4
        [0, 2, 3, 4].forEach(index => {
          const td = document.createElement('td');
          const cellData = rowData[index] ? rowData[index].trim() : '';
          td.textContent = cellData;
          row.appendChild(td);
        });

        // Fetch status from column 8
        const status = rowData[8] ? rowData[8].trim() : '';

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
      });

      table.appendChild(tbody);

      // Append table to the container
      document.getElementById('csv-table-container').appendChild(table);
    })
    .catch(error => console.error('Error fetching CSV:', error));
</script>
