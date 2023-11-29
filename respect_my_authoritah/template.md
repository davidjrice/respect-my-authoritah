:robot: *beep* *boop* respect my authoritah!
---

I have updated your project authors list for you. Here's what I've done:

{% for author in authors %}
    * Added {{author.name}} ({{author.email}}) as an author
{% endfor %}