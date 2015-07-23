#!/usr/bin/env python
from __future__ import division

from datetime import datetime as dt
import os

from vultr.vultr import Vultr

import util


instance_id = "{{ grains['id'] }}"
# For offline testing.
if instance_id.startswith("{"):
    instance_id = "fp-jp-20150531-001"
vultr_subid_filename = "vultr_id"

api_key = "{{ pillar['vultr_apikey'] }}"
# For offline testing.
if api_key.startswith("{"):
    api_key = os.getenv("VULTR_APIKEY")
vultr = Vultr(api_key)

# For statistical significance, don't worry if we're out of quota until we've
# consumed this much of our monthly allowance.
significant_usage = 0.25


def vultr_dict():
    try:
        subid = file(vultr_subid_filename).read()
    except IOError:
        for d in vultr.server_list(None).itervalues():
            if d['label'] == instance_id:
                file(vultr_subid_filename, 'w').write(d['SUBID'])
                return d
    return vultr.server_list(subid)

def usage_portion(vd):
    allowed = int(vd['allowed_bandwidth_gb'])
    current = vd['current_bandwidth_gb']
    return current / allowed

def time_portion():
    now = dt.utcnow()
    beginning_of_month = dt(year=now.year, month=now.month, day=1)
    if now.month == 12:
        beginning_of_next_month = dt(year=now.year+1, month=1, day=1)
    else:
        beginning_of_next_month = dt(year=now.year, month=now.month+1, day=1)
    whole_month = beginning_of_next_month - beginning_of_month
    elapsed = now - beginning_of_month
    return elapsed.total_seconds() / whole_month.total_seconds()

def over_quota(vd, t):
    usage = usage_portion(vd)
    return usage > significant_usage and usage > t

def run():
    print "Starting..."
    vd = vultr_dict()
    t = time_portion()
    if over_quota(vd, t):
        msg = ("used %s out of %s allowed traffic quota (%.2f%%)"
               " in %.2f%% of the current month" % (vd['current_bandwidth_gb'],
                                                    vd['allowed_bandwidth_gb'],
                                                    usage_portion(vd) * 100,
                                                    t * 100))
        print "Splitting because I", msg
        util.split_server(msg)
    else:
        print "Usage portion %s under time portion %s; not splitting." % (usage_portion(vd),
                                                                          t)
    print "Done."


if __name__ == '__main__':
    run()
