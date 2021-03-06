{% from 'install_from_release.sls' import install_from_release %}

{# define cmd: checkfallbacks-installed #}
{{ install_from_release('checkfallbacks', '2.1.1', 'b3d988327f51ba752ab03edb22b30c558ecf7144') }}

/usr/bin/checkfallbacks.py:
  file.managed:
    - source: salt://checkfallbacks/checkfallbacks.py
    - template: jinja
    - user: root
    - group: root
    - mode: 755

"/usr/bin/checkfallbacks.py | logger -t checkfallbacks":
{% if pillar['in_production'] or pillar['in_staging'] %}
  cron.present:
    - minute: '*/11'
    - user: lantern
    - require:
        - cmd: checkfallbacks-installed
        - file: /usr/bin/checkfallbacks.py
{% else %}
  cron.absent:
    - user: lantern
{% endif %}
