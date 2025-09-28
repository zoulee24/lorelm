<knowledge-base>
{% for item in knowledge_base %}
<item>
<id>{{ loop.index }}</id>
<content>{{ item }}</content>
</item>
{% endfor %}
</knowledge-base>