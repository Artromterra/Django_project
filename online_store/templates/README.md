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

## Warning

- Some templates combined header and content in one tag. Therefore, such templates still have an empty content block. As soon as the header and footer are ready, these templates will be completed.
- Since all static files have been moved to the static directory, you need to fix the links to these files by adding /static/ at the beginning of the url. This is not fixed in all templates. If images or styles (or other static files) are not loaded on any page, then you just need to find this object in html and fix the link.

## Example
```commandline
{% extends "base.html" %}

{% block content %}
<h1>No Content</h1>
{% endblock %}
```