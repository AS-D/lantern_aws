stunnel4-deps:
  cmd.wait:
    - name: ":"
    - watch:
        - file: enable-stunnel
        - file: /etc/stunnel/*

stunnel4:
  pkg.installed:
    - refresh: True

  service.running:
    - enable: yes
    - require:
        - pkg: stunnel4
    - watch:
        - cmd: stunnel4-deps

enable-stunnel:
  file.replace:
    - name: /etc/default/stunnel4
    - pattern: "ENABLED=0"
    - repl: "ENABLED=1"
    - append_if_not_found: yes
    - require:
      - pkg: stunnel4
