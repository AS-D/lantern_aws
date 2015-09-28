/etc/hosts:
    file.append:
        - text: "127.0.1.1\t{{ grains['id'] }}\t{{ grains['id'] }}"

base-packages:
    pkg.installed:
        - order: 1
        - names:
            - python-software-properties
            - curl
            - python-pycurl
            - git
            - mailutils
            - debconf-utils
        - reload_modules: yes

/usr/local/lib/pylib:
    file.directory:
        - order: 1
        - user: root
        - group: root
        - mode: 755
        - makedirs: yes
        - recurse:
              - user
              - group
              - mode