import argparse
from os import sys
import random
from sys import path
from os import getcwd
import os, sys, inspect, pprint

# this is a hack to get the hp driver module
# and it's utils module on the search path.
cmd_folder = os.path.realpath(os.path.abspath("..") )
if cmd_folder not in sys.path:
     sys.path.insert(0, cmd_folder)

from hp3parclient import client, exceptions
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("-debug", help="Turn on http debugging", default=False, action="store_true")
args = parser.parse_args()

username = "3paradm"
password = "3pardata"

testVolName = "WALTTESTVOL99"
testSNAPName = testVolName+"SNAP"
testCPGName = "WALTTESTCPG"
TESTHOST = 'WALTOpenStackHost'
DOMAIN = 'WALT_TEST'

#cl = client.HP3ParClient("https://localhost:8080/api/v1")
cl = client.HP3ParClient("https://10.10.22.132:8080/api/v1")
if "debug" in args and args.debug == True:
    cl.debug_rest(True)


def create_test_volume():
    try:
        cl.createVolume(testVolName, testCPGName, 1000)
    except exceptions.HTTPUnauthorized as ex:
        print "You must login"
    except Exception as ex:
        print ex

def create_test_vlun():
    try:
        cl.createVLUN(testVolName, 1, TESTHOST, {'node': 1, 'slot' : 8, 'cardPort':1})
    except exceptions.HTTPUnauthorized as ex:
        print "You must login"
    except Exception as ex:
        print ex


def delete_test_vlun():
    try:
        cl.deleteVLUN(testVolName, 1, TESTHOST)
    except exceptions.HTTPUnauthorized as ex:
        print "You must login"
    except Exception as ex:
        print ex





def create_test_host():
    try:
        host = cl.getHost(TESTHOST)
        print "host already exists"
    except exceptions.HTTPNotFound as ex:
        extra = {
                 'domain':DOMAIN,
                 'iSCSINames': ['iqn.1993-08.org.debian:01:9f72d1b6c60'],
                 'descriptors': {
                     'ipAddr' : '10.10.22.132',
                     'os' : 'Ubuntu Linux 12.04'
                 }
                }
        cl.createHost(TESTHOST, extra)
        pass
    except exceptions.HTTPUnauthorized as ex:
        print "You must login"
    except Exception as ex:
        print ex

def delete_test_host():
    try:
        cl.deleteHost(TESTHOST)
    except exceptions.HTTPUnauthorized as ex:
        print "You must login"
    except Exception as ex:
        print ex

def create_volumes():
    print "Create Volumes"
    try:
       volName = "%s1" % testVolName
       print "Creating Volume '%s'" % volName
       cl.createVolume(volName, testCPGName, 300)
       volName = "%s2" % testVolName
       print "Creating Volume '%s'" % volName
       cl.createVolume(volName, testCPGName, 1024, 
                       {'comment': 'something', 'tpvv': True})

    except exceptions.HTTPUnauthorized as ex:
       pprint.pprint("You must login first")
    except Exception as ex:
       print ex

    try:
	volume = cl.createVolume("%s1" % testVolName, testCPGName, 2048)
    except exceptions.HTTPConflict as ex:
	print "Got Expected Exception %s" % ex
        pass

    print "Complete\n"

def delete_volumes():
    print "Delete Volumes"
    try:
       volumes = cl.getVolumes()
       if volumes:
           for volume in volumes['members']:
               if volume['name'].startswith(testVolName):
                   print "Deleting volume '%s'" % volume['name']
                   cl.deleteVolume(volume['name'])
    except exceptions.HTTPUnauthorized as ex:
       print "You must login first"
    except Exception as ex:
       print ex

    print "Complete\n"


cl.login(username, password, {'InServ':'10.10.22.241'})
#get_cpgs()
#get_host(cl, 'WALTTESTHOST')
#get_host(cl, 'devstackvm')
#get_vlun(cl, 'WALTTESTVOL11')
#get_vluns(cl)
get_ports(cl)
#create_test_volume()
#create_test_host()
#create_test_vlun()
#get_vlun(cl, testVolName)
#delete_test_vlun()
#create_test_host()
#delete_test_host()
#get_host('manualkvmtest')
#get_vluns()
#get_vlun('WALTTESTVOL11')
#delete_test_host()
#get_hosts()
#get_volumes()
#create_test_cpg()
#create_volumes()
#delete_volumes()
#create_snapshots()
#delete_snapshots()
#delete_test_cpg()
