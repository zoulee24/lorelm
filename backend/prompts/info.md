<user>
<name>{{ user.nickname }}</name>
<gender>{{ user.gender }}</gender>
</user>
<role-info>
{% for role in roles %}
<role-{{ loop.index }}>
<name>{{ role.nickname }}</name>
<description>
{{ role.description }}
</description>
</role-{{ loop.index }}>
{% endfor %}
</role-info>