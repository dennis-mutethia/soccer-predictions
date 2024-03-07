---
layout: default
title: Soccer Predictions
---

[Download predictions.csv](https://raw.githubusercontent.com/kamquatz/soccer-predictions/master/data/predictions.csv)

<link rel="stylesheet" href="{{ site.baseurl }}/styles.css">

<pre>
{% for row in site.data.predictions %}
  {% for column in row %}
    {{ column[0] }}: {{ column[1] }}{% unless forloop.last %}, {% endunless %}
  {% endfor %}
  {% unless forloop.last %}{% endunless %}
{% endfor %}
</pre>
