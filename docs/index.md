---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<pre>
{% capture csv_content %}{% include https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv %}{% endcapture %}
{{ csv_content | newline_to_br }}
</pre>

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
      {% for column in row %}
        <td>{{ column[1] }}</td>
      {% endfor %}
    </tr>
  {% endfor %}
</tbody>

</table>
