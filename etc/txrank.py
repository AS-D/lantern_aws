#!/usr/bin/env python

"""
For full functionality, you need:

- The following Python modules (pip names):
  - influxdb
  - redis
  - python-digitalocean
  - vultr

- The following environment variables:
  - PYTHONPATH (including ../lib)
  - INFLUX_PASSWORD (https://github.com/getlantern/too-many-secrets/blob/master/monitoring/credentials.txt#L8)
  - REDIS_URL (https://github.com/getlantern/too-many-secrets/blob/master/lantern_aws/config_server.yaml#L2)
  - DO_TOKEN (https://github.com/getlantern/too-many-secrets/blob/master/lantern_aws/do_credential#L11)
  - VULTR_APIKEY ('api-key' at https://github.com/getlantern/too-many-secrets/blob/master/vultr.md)
"""

import os
import sys

try:
    from influxdb import InfluxDBClient
except ImportError:
    print "You need the python-influxdb package installed.  Try:"
    print "   pip install influxdb"
    sys.exit(1)

import do_util
from misc_util import memoized
from redis_util import redis_shell
import vps_util
import vultr_util

envvars = ["INFLUX_PASSWORD", "REDIS_URL", "DO_TOKEN", "VULTR_APIKEY"]
locs = ["https://github.com/getlantern/too-many-secrets/blob/master/dashboard.getlantern.org ('operator password' in line 7)", "https://github.com/getlantern/too-many-secrets/blob/master/lantern_aws/config_server.yaml#L2", "https://github.com/getlantern/too-many-secrets/blob/master/lantern_aws/do_credential#L11", "https://github.com/getlantern/too-many-secrets/blob/master/vultr.md"]

# Make sure we have all the environment variables we need.
for i in range(len(envvars)):
    env = envvars[i]
    cur = os.getenv(env)
    if not cur:
        print "Set the environment variable {} to {}".format(env, locs[i])
        sys.exit(1)

influx_passw = os.getenv("INFLUX_PASSWORD")

@memoized
def name_by_ip():
    ret = {}
    print "Collecting VPS data (this will take a while)..."
    for x in vultr_util.vultr.server_list(None).values():
        ret[x['main_ip']] = x['label']
    for x in do_util.do.get_all_droplets():
        ret[x.ip_address] = x.name
    return ret

@memoized
def ip_by_name():
    return dict(map(reversed, name_by_ip().iteritems()))

def queued_names():
    nbyip = name_by_ip()
    return set(nbyip.get(cfg.split('|')[0])
               for region in regions()
               for cfg in redis_shell.lrange('%s:srvq' % region, 0, -1))

def collect_pairs():
    query = "SELECT DERIVATIVE(last(value)) AS bytes FROM \"collectd\".\"default\".\"interface_rx\" WHERE type='if_octets' AND instance='eth0' AND time > now() - 1d GROUP BY time(1h), host FILL(none)"
    client = InfluxDBClient('influx.getlantern.org', 8080, 'test', influx_passw, 'collectd', True)
    result = client.query(query)
    print "Got %s influxdb items" % len(result.items())
    return list(sorted((sum(x['bytes'] for x in item[1] if x['bytes'] > 0), item[0][1]['host'])
                       for item in result.items()))

@memoized
def byip():
    print "Getting server configs..."
    return vps_util.srv_cfg_by_ip()

@memoized
def regions():
    return redis_shell.smembers('user-regions')

@memoized
def bakedin():
    return set(x.split('|')[1]
               for region in regions()
               for x in redis_shell.lrange(region + ':bakedin', 0, -1))

def srv_cfg_by_name(name):
    return byip().get(ip_by_name()[name], [])

@memoized
def fp_status(name):
    if not name.startswith('fp-'):
        return "n/a"
    ip = ip_by_name().get(name)
    if not ip:
        return "destroyed"
    if ip in bakedin():
        return "baked-in"
    cfg = srv_cfg_by_name(name)
    if not cfg:
        return "???"
    region = vps_util.region_by_name(name)
    for srv in cfg[1]:
        for suffix in ["", "|0"]:
            if redis_shell.zscore(region + ':slices', "%s%s" % (srv, suffix)):
                return "open"
    else:
        return "full"

if __name__ == '__main__':
    def usage():
        print "Usage:"
        print "    %s [OPTIONS] [<lines, default 10>]" % sys.argv[0]
        print
        print "Enter a negative number to get the VPSs with highest traffic instead."
        print
        print "Servers which are still queued (and thus not used yet) are not printed."
        print
        print "A 'Status' column will be printed, with the possible values:"
        print "   - open: this server is currently taking users"
        print "   - full: this server is not taking users anymore"
        print "   - baked-in: this server was pulled from the queue to bake as chained default"
        print "   - destroyed: this server has been destroyed (in the last 24h)"
        print "   - ???: this is managed by a test cloudmaster, or it's being retired at this"
        print "          very moment, or it's a default chained server (fp-nl-2015032*), or we"
        print "          have an inconsistency"
        sys.exit(1)
    args = sys.argv[1:]
    if len(args) == 0:
        lines = 10
    elif len(args) == 1:
        try:
            lines = int(args[0])
        except ValueError:
            usage()
    else:
        usage()
    print "Collecting influx data..."
    pairs = collect_pairs()
    print "Collecting queued names..."
    qn = queued_names()
    pairs = [x for x in pairs if x[1] not in qn]
    if lines > 0:
        units = "MB"
        divisor = 1024 * 1024
    else:
        pairs.reverse()
        lines = -lines
        units = "GB"
        divisor = 1024 * 1024 * 1024
    byip()  # force this printout before the report
    print
    print "%-20s%20s%10s%15s" % ("Name", "IP Address", "Status", "Transfer (%s)" % units)
    print "=" * 65
    for tx, name in pairs[:lines]:
        print "%-20s%20s%10s%15.3f" % (name,
                                       ip_by_name().get(name, "( UNKNOWN )"),
                                       fp_status(name),
                                       tx / divisor)
