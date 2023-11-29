:robot: respect my authoritah!
---

![Respect My Authority](https://github.com/davidjrice/respect-my-authoritah/templates/eric-cartman-respect-my-authoritah.gif)

I have updated your project authors list for you. Here's what I've done:

{% for author in authors %}
    * Added {{author.name}} ({{author.email}}) as an author
{% endfor %}
