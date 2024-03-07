---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/docs/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<table class="styled-table">
  <thead>
    <tr>
      {% assign headers = site.data.predictions[0] | split: ',' %}
      {% for header in headers %}
        <th>{{ header }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for row in site.data.predictions | slice: 1 %}
      <tr>
        {% assign values = row | split: ',' %}
        {% for value in values %}
          <td>{{ value }}</td>
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>
