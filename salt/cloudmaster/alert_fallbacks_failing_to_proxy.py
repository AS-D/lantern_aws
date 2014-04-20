#!/usr/bin/env python

import logging
import os
import sys

import boto.sqs
from boto.sqs.jsonmessage import JSONMessage
import salt.cli
import salt.client
import salt.key


AWS_REGION = "{{ grains['aws_region'] }}"
AWS_ID = "{{ pillar['aws_id'] }}"
AWS_KEY = "{{ pillar['aws_key'] }}"
aws_creds = {'aws_access_key_id': AWS_ID,
             'aws_secret_access_key': AWS_KEY}
CONTROLLER = "{{ grains['controller'] }}"

here = os.path.dirname(sys.argv[0]) if __name__ == '__main__' else __file__


def report(failures):
    fps_str = '\n' + '\n'.join(sorted(failures))
    log.warn("Fallbacks failed to proxy: %s" % fps_str)
    sqs = boto.sqs.connect_to_region(AWS_REGION, **aws_creds)
    report_q = sqs.get_queue("notify_%s" % CONTROLLER)
    msg = JSONMessage()
    msg.set_body({'fp-alarm': "Fallbacks not proxying",
                  'subject': "ALARM: fallback(s) failing to proxy",
                  'send-email': True,
                  'ip': fps_str,
                  # These fields are expected by the controller, but they
                  # make no sense in this case.
                  'user': "n/a",
                  'instance-id': 'unavailable',
                  'port': "n/a"})
    report_q.write(msg)


if __name__ == '__main__':
    # I have to do all this crap because salt hijacks the root logger.
    log = logging.getLogger('alert_fallbacks_failing_to_proxy')
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(here, "alert_fallbacks_failing_to_proxy.log"))
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
    log.addHandler(handler)
    log.info("report starting...")
    try:
        report(sys.argv[1:])
    except Exception as e:
        log.exception(e)
    log.info("report done.")

