---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<table class="styled-table">
  <thead>
    <tr>
      <th>Column1</th>
      <th>Column2</th>
      <!-- Add more columns as needed -->
    </tr>
  </thead>
  <tbody>
    {% for row in site.data.predictions %}
      <tr>
        <td>{{ row.Column1 }}</td>
        <td>{{ row.Column2 }}</td>
        <!-- Add more columns as needed -->
      </tr>
    {% endfor %}
  </tbody>
</table>
