---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<table class="styled-table">
  <thead>
    <tr>
      {% assign headers = site.data.predictions | first %}
      {% for header in headers %}
        <th>{{ header[0] }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for row in site.data.predictions | offset:1 %}
      <tr>
        {% for value in row %}
          <td>{{ value[1] }}</td>
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>