#!/usr/bin/env python


import os
import time

from redis_util import redis_shell
import redisq
import vps_util


TIMEOUT = 5 * 60


def run():
    cm = vps_util.my_cm()
    region = vps_util.my_region()
    print "Starting retire server at cloudmaster %s, region %s." % (cm, region)
    qname = cm + ":retireq"
    destroy_qname = cm + ":destroyq"
    q = redisq.Queue(qname, redis_shell, TIMEOUT)
    while True:
        task, remover = q.next_job()
        if task:
            name, ip = task.split('|')
            is_baked_in = redis_shell.sismember(region + ":bakedin-names", name)
            txn = redis_shell.pipeline()
            if is_baked_in:
                print "Not retiring baked-in server %s (%s)" % (name, ip)
            else:
                print "Retiring", name, ip
                vps_util.actually_retire_proxy(name=name,
                                               ip=ip,
                                               pipeline=txn)
            remover(txn)
            if not is_baked_in:
                # Introduce the job with the timestamp already filled in, so it will
                # only be pulled when it 'expires'. This effectively adds a delay to
                # give clients some time to move over to their new server before we
                # actually destroy the old one.
                txn.lpush(destroy_qname, "%s*%s" % (name, int(time.time())))
            txn.execute()
        else:
            time.sleep(10)


if __name__ == '__main__':
    run()
