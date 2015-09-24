import os
import re
import stat
import sys
import time
from functools import wraps

import yaml

import config
import here


def in_production():
    return config.cloudmaster_name in config.production_cloudmasters

def memoized(f):
    d = {}
    @wraps(f)
    def deco(*args):
        try:
            return d[args]
        except KeyError:
            ret = d[args] = f(*args)
            return ret
    return deco

@memoized
def read_do_credential():
    return secrets_from_yaml(['lantern_aws', 'do_credential'],
                             ['client_id', 'api_key', 'rw_token'])

@memoized
def read_vultr_credential():
    return secrets_from_yaml(['vultr.md'],
                             ['api-key'])[0]

@memoized
def read_cfgsrv_credential():
    return secrets_from_yaml(['lantern_aws', 'config_server.yaml'],
                             ['auth_token', 'redis_url'])

def secrets_from_yaml(path, keys):
    d = yaml.load(file(os.path.join(here.secrets_path, *path)))
    return map(d.get, keys)

def set_secret_permissions():
    """Secret files should be only readable by user, but git won't remember
    read/write settings for group and others.

    We can't even create an instance unless we restrict the permissions of the
    corresponding .pem.
    """
    for path, dirnames, filenames in os.walk(os.path.join(here.secrets_path,
                                                          'lantern_aws')):
        for name in filenames:
            os.chmod(os.path.join(path, name), stat.S_IREAD)

def ssh_cloudmaster(cmd=None, out=None):
    full_cmd = "ssh -o StrictHostKeyChecking=no -i %s root@%s" % (
                    config.key_path,
                    config.cloudmaster_address)
    if cmd:
        full_cmd += " '%s'" % cmd
    if out:
        full_cmd += "| tee %s" % out
    return os.system(full_cmd)
