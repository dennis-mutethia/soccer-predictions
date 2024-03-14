I need to add a green tick when the status = WON and red cross when the status = LOST
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
      for (let i = csvArray.length - 1; i > 0; i--) {
        const row = document.createElement('tr');
        columnsToDisplay.forEach(column => {
          const columnIndex = csvArray[0].indexOf(column);
          const td = document.createElement('td');
          td.textContent = csvArray[i][columnIndex];
          row.appendChild(td);
        });        
        const td = document.createElement('td');
        td.textContent = csvArray[i][8];
        row.appendChild(td);

        const statusTd = document.createElement('td');
        if (csvArray[i][8] === 'WON') {
          statusTd.innerHTML = '<img src="green_tick.png" alt="Green Tick">';
        } else if (csvArray[i][8] === 'LOST') {
          statusTd.innerHTML = '<img src="red_cross.png" alt="Red Cross">';
        } 
        row.appendChild(statusTd);

        tbody.appendChild(row);
      }
      table.appendChild(tbody);

      // Append table to the container
      document.getElementById('csv-table-container').appendChild(table);
    })
    .catch(error => console.error('Error fetching CSV:', error));
</script>
