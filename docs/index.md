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
      csvArray[0].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Create table body
      const tbody = document.createElement('tbody');
      for (let i = csvArray.length - 1; i > 0; i--) {
        const row = document.createElement('tr');
        csvArray[i].forEach(cell => {
          const td = document.createElement('td');
          td.textContent = cell;
          row.appendChild(td);
        });
        tbody.appendChild(row);
      }
      table.appendChild(tbody);

      // Append table to the container
      document.getElementById('csv-table-container').appendChild(table);
    })
    .catch(error => console.error('Error fetching CSV:', error));
</script>
