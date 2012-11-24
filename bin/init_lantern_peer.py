#!/usr/bin/env python

import os
import shutil
import sys
import tempfile

import boto


verbose = False

def ec2_conn():
    try:
        return ec2_conn.conn
    except AttributeError:
        ec2_conn.conn = boto.connect_ec2()
        return ec2_conn.conn

def find_resource_id(resources, res_type):
    for res in resources:
        if res.resource_type == res_type:
            return res.physical_resource_id

def get_ip(resources):
    res_id = find_resource_id(resources, u'AWS::EC2::Instance')
    reservations = ec2_conn().get_all_instances(
                        instance_ids=[res_id],
                        filters={'group-name': 'lantern-peer'})
    if not reservations:
        return None
    instance, = reservations[0].instances
    return instance.ip_address

def get_port(resources):
    res_id = find_resource_id(resources, u'AWS::EC2::SecurityGroup')
    group, = ec2_conn().get_all_security_groups(groupnames=[res_id])
    rule, = group.rules
    assert rule.from_port == rule.to_port
    return rule.from_port

def run(which, client_secrets, user_credentials):
    if not client_secrets.endswith('client_secrets.json'):
        print usage
        print "WARNING: I was kind of expecting the client secrets file to be called 'client_secrets.json'."
        print "Are you sure you provided them in the right order (client secrets, user credentials)?"
        print "[y/N]:",
        if raw_input().strip().lower() != 'y':
            print "OK, try again with the right order."
            sys.exit(0)
        else:
            print "Ah, OK, sorry."

    cf_conn = boto.connect_cloudformation()

    any_inited = False

    for stack in cf_conn.list_stacks():
        if stack.stack_status != 'CREATE_COMPLETE':
            if verbose:
                print ("(Ignoring stack '%s' with status %s.)"
                       % (stack.stack_name, stack.stack_status))
            continue
        resources = cf_conn.describe_stack_resources(stack.stack_id)
        ip = get_ip(resources)
        if ip is None:
            # There is no EC2 instance in this stack that belongs to the
            # `lantern-peer` security group, so this is not a lantern stack.
            if verbose:
                print "(Ignoring non-lantern stack '%s'.)" % stack.stack_name
            continue
        port = get_port(resources)
        print "Found live stack '%s' at %s:%s." % (stack.stack_name,
                                                   ip,
                                                   port)
        if which in ['all', stack.stack_name, ip]:
            tmpdir = tempfile.mkdtemp()
            try:
                ip_path = os.path.join(tmpdir, 'ip')
                port_path = os.path.join(tmpdir, 'port')
                file(ip_path, 'w').write(ip)
                file(port_path, 'w').write(port)
                for path, remote_filename in [
                        (client_secrets, 'client_secrets.json'),
                        (user_credentials, 'user_credentials.json'),
                        (ip_path, 'ip'),
                        (port_path, 'public-proxy-port')]:
                    for command in [("scp %s lantern@%s:%s" % (path, ip, remote_filename)),
                                    ("ssh lantern@%s 'chmod 600 %s'" % (ip, remote_filename))]:
                        if os.system(command):
                            print "ERROR trying to copy/chmod %s to %s" % (path, remote_filename)
                            print "You probably want to troubleshoot this and retry.  Aborting."
                            sys.exit(1)
                print "Successfully initialized peer '%s' at %s." % (stack.stack_name, ip)
            finally:
                shutil.rmtree(tmpdir)
            any_inited = True
        elif verbose:
            print "(Ignoring unselected peer '%s' at %s.)" % (stack.stack_name, ip)

    if not any_inited:
        if which == 'all':
            print "No `lantern-peer` stacks found."
        else:
            print ("No `lantern-peer` stack found, with name or ip '%s'."
                   % which)

if __name__ == '__main__':
    usage = ("Usage: %s <name|ip|'all'> <client_secrets> <oauth data>"
            % sys.argv[0])
    if len(sys.argv) != 4:
        print usage
        sys.exit(1)
    run(*sys.argv[1:])