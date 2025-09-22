<user>
<name>{{ user.name }}</name>
<gender>{{ user.gender }}</gender>
</user>
<role>
<name>{{ role.name }}</name>
{{ % if role.description % }}
<description>
{{ role.description }}
</description>
{% endif %}
</role>