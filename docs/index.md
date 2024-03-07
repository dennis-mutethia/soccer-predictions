---
layout: default
title: Soccer Predictions
---

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
