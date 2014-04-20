#!/usr/bin/env python

import os

# sudo pip install -U python-digitalocean
import digitalocean


FIX_FILENAME = 'auth_flood_fix.conf'

all_fallbacks = [
    "fp-from-old-controller-96-at-getlantern-dot-org-8f94-1-2014-4-8",
    "fp-from-old-controller-25-at-getlantern-dot-org-1616-1-2014-4-8",
    "fp-from-old-controller-23-at-getlantern-dot-org-f1f8-1-2014-4-9",
    "fp-from-old-controller-41-at-getlantern-dot-org-6708-1-2014-4-8",
    "fp-from-old-controller-19-at-getlantern-dot-org-f937-1-2014-4-9",
    "fp-from-old-controller-3-at-getlantern-dot-org-08a5-1-2014-4-8",
    "fp-from-old-controller-78-at-getlantern-dot-org-a00c-1-2014-4-9",
    "fp-from-old-controller-87-at-getlantern-dot-org-795e-1-2014-4-9",
    "fp-from-old-controller-51-at-getlantern-dot-org-b1d5-1-2014-4-9",
    "fp-from-old-controller-43-at-getlantern-dot-org-4b76-1-2014-4-8",
    "fp-from-old-controller-5-at-getlantern-dot-org-f745-1-2014-4-8",
    "fp-from-old-controller-81-at-getlantern-dot-org-58ec-1-2014-4-9",
    "fp-from-old-controller-82-at-getlantern-dot-org-5853-1-2014-4-8",
    "fp-invite-at-getlantern-dot-org-7600-1-2014-2-17",
    "fp-from-old-controller-4-at-getlantern-dot-org-4b4e-1-2014-4-8",
    "fp-from-old-controller-39-at-getlantern-dot-org-356f-1-2014-4-9",
    "fp-from-old-controller-97-at-getlantern-dot-org-c643-1-2014-4-9",
    "fp-from-old-controller-77-at-getlantern-dot-org-ddbf-1-2014-4-9",
    "fp-from-old-controller-50-at-getlantern-dot-org-8fe6-1-2014-4-8",
    "fp-from-old-controller-29-at-getlantern-dot-org-6fce-1-2014-4-8",
    "fp-from-old-controller-10-at-getlantern-dot-org-3942-1-2014-4-8",
    "fp-from-old-controller-37-at-getlantern-dot-org-58fb-1-2014-4-8",
    "fp-from-old-controller-59-at-getlantern-dot-org-5db3-1-2014-4-9",
    "fp-from-old-controller-74-at-getlantern-dot-org-ee40-1-2014-4-8",
    "fp-from-old-controller-16-at-getlantern-dot-org-900c-1-2014-4-8",
    "fp-from-old-controller-70-at-getlantern-dot-org-2e74-1-2014-4-8",
    "fp-from-old-controller-93-at-getlantern-dot-org-acc7-1-2014-4-8",
    "fp-from-old-controller-99-at-getlantern-dot-org-ff9f-1-2014-4-9",
    "fp-from-old-controller-38-at-getlantern-dot-org-6f70-1-2014-4-8",
    "fp-from-old-controller-8-at-getlantern-dot-org-2b8e-1-2014-4-8",
    "fp-from-old-controller-76-at-getlantern-dot-org-7ac2-1-2014-4-8",
    "fp-afisk-at-getlantern-dot-org-50e8-4-2014-2-24",
    "fp-from-old-controller-91-at-getlantern-dot-org-9d17-1-2014-4-8",
    "fp-from-old-controller-15-at-getlantern-dot-org-e0b3-1-2014-4-8",
    "fp-from-old-controller-7-at-getlantern-dot-org-c277-1-2014-4-8",
    "fp-from-old-controller-2-at-getlantern-dot-org-0658-1-2014-4-8",
    "fp-from-old-controller-9-at-getlantern-dot-org-33ef-1-2014-4-8",
    "fp-from-old-controller-45-at-getlantern-dot-org-f5b4-1-2014-4-9",
    "fp-from-old-controller-13-at-getlantern-dot-org-3d3f-1-2014-4-8",
    "fp-from-old-controller-90-at-getlantern-dot-org-ad16-1-2014-4-9",
    "fp-from-old-controller-21-at-getlantern-dot-org-957a-1-2014-4-8",
    "fp-from-old-controller-95-at-getlantern-dot-org-960b-1-2014-4-9",
    "fp-from-old-controller-53-at-getlantern-dot-org-9add-1-2014-4-8",
    "fp-from-old-controller-49-at-getlantern-dot-org-2c00-1-2014-4-9",
    "fp-from-old-controller-17-at-getlantern-dot-org-1d45-1-2014-4-8",
    "fp-from-old-controller-55-at-getlantern-dot-org-89c9-1-2014-4-9",
    "fp-from-old-controller-62-at-getlantern-dot-org-117b-1-2014-4-8",
    "fp-from-old-controller-98-at-getlantern-dot-org-8362-1-2014-4-9",
    "fp-from-old-controller-75-at-getlantern-dot-org-8141-1-2014-4-9",
    "fp-from-old-controller-56-at-getlantern-dot-org-73c8-1-2014-4-9",
    "fp-from-old-controller-6-at-getlantern-dot-org-07a4-1-2014-4-8",
    "fp-from-old-controller-84-at-getlantern-dot-org-541f-1-2014-4-8",
    "fp-from-old-controller-52-at-getlantern-dot-org-5e8c-1-2014-4-9",
    "fp-from-old-controller-35-at-getlantern-dot-org-2313-1-2014-4-9",
    "fp-from-old-controller-30-at-getlantern-dot-org-6348-1-2014-4-8",
    "fp-from-old-controller-27-at-getlantern-dot-org-8e1c-1-2014-4-8",
    "fp-from-old-controller-63-at-getlantern-dot-org-5734-1-2014-4-8",
    "fp-from-old-controller-22-at-getlantern-dot-org-1657-1-2014-4-9",
    "fp-from-old-controller-85-at-getlantern-dot-org-7360-1-2014-4-8",
    "fp-from-old-controller-89-at-getlantern-dot-org-c12c-1-2014-4-9",
    "fp-from-old-controller-31-at-getlantern-dot-org-8d17-1-2014-4-8",
    "fp-from-old-controller-71-at-getlantern-dot-org-dbc5-1-2014-4-8",
    "fp-from-old-controller-46-at-getlantern-dot-org-2feb-1-2014-4-8",
    "fp-from-old-controller-66-at-getlantern-dot-org-6d01-1-2014-4-8",
    "fp-from-old-controller-65-at-getlantern-dot-org-4502-1-2014-4-8",
    "fp-from-old-controller-32-at-getlantern-dot-org-3d3a-1-2014-4-8",
    "fp-from-old-controller-40-at-getlantern-dot-org-5067-1-2014-4-8",
    "fp-from-old-controller-11-at-getlantern-dot-org-1f3f-1-2014-4-8",
    "fp-from-old-controller-28-at-getlantern-dot-org-4d0f-1-2014-4-8",
    "fp-from-old-controller-57-at-getlantern-dot-org-bb27-1-2014-4-8",
    "fp-from-old-controller-80-at-getlantern-dot-org-d31b-1-2014-4-9",
    "fp-from-old-controller-12-at-getlantern-dot-org-acc0-1-2014-4-8",
    "fp-from-old-controller-34-at-getlantern-dot-org-bca4-1-2014-4-8",
    "fp-from-old-controller-1-at-getlantern-dot-org-4c59-1-2014-4-8",
    "fp-from-old-controller-60-at-getlantern-dot-org-2f0d-1-2014-4-8",
    "fp-from-old-controller-58-at-getlantern-dot-org-3c02-1-2014-4-8",
    "fp-from-old-controller-18-at-getlantern-dot-org-ee4a-1-2014-4-8",
    "fp-from-old-controller-94-at-getlantern-dot-org-7c06-1-2014-4-9",
    "fp-from-old-controller-83-at-getlantern-dot-org-495e-1-2014-4-8",
    "fp-from-old-controller-88-at-getlantern-dot-org-0483-1-2014-4-9",
    "fp-from-old-controller-67-at-getlantern-dot-org-1580-1-2014-4-8",
    "fp-from-old-controller-14-at-getlantern-dot-org-bf02-1-2014-4-8",
    "fp-from-old-controller-42-at-getlantern-dot-org-a7f7-1-2014-4-8",
    "fp-from-old-controller-48-at-getlantern-dot-org-2b81-1-2014-4-9",
    "fp-from-old-controller-64-at-getlantern-dot-org-097f-1-2014-4-9",
    "fp-from-old-controller-72-at-getlantern-dot-org-7d82-1-2014-4-8",
    "fp-from-old-controller-54-at-getlantern-dot-org-8eb6-1-2014-4-9",
    "fp-from-old-controller-47-at-getlantern-dot-org-8826-1-2014-4-9",
    "fp-from-old-controller-20-at-getlantern-dot-org-7379-1-2014-4-8",
    "fp-from-old-controller-68-at-getlantern-dot-org-8e95-1-2014-4-9",
    "fp-from-old-controller-73-at-getlantern-dot-org-9f33-1-2014-4-9",
    "fp-from-old-controller-61-at-getlantern-dot-org-ffbe-1-2014-4-8",
    "fp-from-old-controller-33-at-getlantern-dot-org-fbc7-1-2014-4-9",
    "fp-from-old-controller-69-at-getlantern-dot-org-46a6-1-2014-4-8",
    "fp-from-old-controller-36-at-getlantern-dot-org-452a-1-2014-4-9",
    "fp-from-old-controller-86-at-getlantern-dot-org-3ea1-1-2014-4-9",
    "fp-from-old-controller-24-at-getlantern-dot-org-76bb-1-2014-4-9",
    "fp-from-old-controller-79-at-getlantern-dot-org-dc5d-1-2014-4-9",
    "fp-from-old-controller-0-at-getlantern-dot-org-d136-1-2014-4-8",
    "fp-from-old-controller-92-at-getlantern-dot-org-b568-1-2014-4-8",
    "fp-from-old-controller-26-at-getlantern-dot-org-5553-1-2014-4-8",
    "fp-from-old-controller-44-at-getlantern-dot-org-9363-1-2014-4-8"]

_, do_id, _, do_api_key = file(os.path.join("..",
                                            "..",
                                            "too-many-secrets",
                                            "lantern_aws",
                                            "do_credential")
                              ).read().strip().split()

mgr = digitalocean.Manager(client_id=do_id, api_key=do_api_key)

droplets_by_name = {d.name: d
                    for d in mgr.get_all_droplets()}

def fix_fallback(ip):
    print "Uploading fix..."
    os.system("scp -o StrictHostKeyChecking=no %s lantern@%s:"
              % (FIX_FILENAME, ip))
    print "Moving fix..."
    run_command(ip, "sudo mv /home/lantern/%s /etc/salt/minion.d/"
                    % FIX_FILENAME)
    print "Rebooting..."
    run_command(ip, "sudo reboot")

def run_command(ip, cmd):
    os.system("ssh -o StrictHostKeyChecking=no lantern@%s '%s'" % (ip, cmd))

for name in all_fallbacks:
    ip = droplets_by_name[name].ip_address
    print "\nChecking %s (%s)" % (name, ip)
    run_command(ip, "ps aux | grep Xmx")



