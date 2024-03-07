---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

{% assign csv_url = "https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv" %}
{% assign csv_data = site.github.data[ 'content_from_url' ] | parse_csv: csv_url %}

<table class="styled-table">
  <thead>
    <tr>
      {% for header in csv_data[0] %}
        <th>{{ header }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for row in csv_data | offset:1 %}
      <tr>
        {% for value in row %}
          <td>{{ value }}</td>
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>