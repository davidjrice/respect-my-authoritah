:robot: respect my authoritah!
---

![Respect My Authority](https://raw.githubusercontent.com/davidjrice/respect-my-authoritah/main/respect_my_authoritah/templates/eric-cartman-respect-my-authoritah.gif)

I have updated your project authors list for you. Here's what I've done:

{% for author in authors %}
  * Added {{author.name}} ({{author.email}}) as an author
{% endfor %}
