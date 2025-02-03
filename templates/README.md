## Description

Layout of an online store using the Jinja2 template engine.

## Basic blocks
- **pre-head** - The block that comes before the head tag
- **head** - The block inside the head tag
- **body** - The block that includes all the content inside the body tag
- **header** - The block that includes the header tag and the top menu. By default, it is loaded header.html
- **<ins>content</ins>** - The block that includes the content of the page. Basically, only this block changes in all templates.
- **footer** - The block that includes the content inside the footer tag. By default, it loads into itself footer.html
- **scripts-after-footer** - The block responsible for scripts that are loaded after the entire page is loaded. It is located after the footer tag.

## Example
```commandline
{% extends "base.html" %}

{% block content %}
<h1>No Content</h1>
{% endblock %}
```