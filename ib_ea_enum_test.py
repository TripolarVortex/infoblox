#!/usr/bin/python3
#
# IB_EA_ENUM_TEST
#
# Script to test the insertion of entries into an Infoblox NIOS Extensible
# Attribute type "ENUM."  The intent of the script is to stress-test both
# the API and the apppliance/system to validate the number of ENUM entries
# that may exist in an EA.  This script assumes the test EA is already of
# type ENUM and the last entry in the list is numeric.
#
# Author: Thomas McRae
# Date: 2022-02-02
# Version: 1.0
#
# Copyright 2022 Infoblox Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import requests
import json
import sys

#
# update these settings to access your grid
#
gm_ip = '192.168.1.131'
gm_user = 'admin'
gm_pwd = 'infoblox'
ea_name = 'GRE'
ea_bulkadd = 100
sslkeylog = True

#
# DO NOT EDIT BELOW THIS LINE
#
if sslkeylog:
   try:
      import os
      import sslkeylog
      sslkeylog.set_keylog(os.environ.get('SSLKEYLOGFILE'))
   except:
      print("Module sslkeylog is not installed.  Logging disabled.")
      print("To enable SSL pre-master key logging, install the sslkeylog module:")
      print("  pip3 install sslkeylog")
requests.packages.urllib3.disable_warnings()
base_url = "https://{}/wapi/v2.7".format(gm_ip)
# go find the EA UID
url = "{}/extensibleattributedef?name={}".format(base_url, ea_name)
r = requests.get(url, verify=False, auth=(gm_user, gm_pwd))
if r.status_code != 200:
    print("Failed to find EA.")
    print("Error Message: {}".format(r.content))
    sys.exit()
eas = json.loads(r.text)
ea_ref = eas[0]['_ref']

url = "{}/{}?_return_fields%2B=list_values".format(base_url, ea_ref)
header = {'Content-type': 'application/json'}
go = True
while go:
    r = requests.get(url, verify=False, auth=(gm_user, gm_pwd))
    if r.status_code != 200:
        print("Failed to load the defined EA.")
        print("Error Message: {}".format(r.content))
        sys.exit()
    ea = json.loads(r.text)
    if ea['default_value'] == None:
        del ea['default_value']
    print("Loaded EA '{}' with {} entries".format(ea_name, len(ea['list_values'])))

    for i in range(0, ea_bulkadd):
        ea['list_values'].append({'value': str(int(ea['list_values'][len(ea['list_values'])-1]['value'])+1)})
    r = requests.put(url, data=json.dumps(ea), headers=header, verify=False, auth=(gm_user, gm_pwd))
    if r.status_code != 200:
        go = False
        print("Failed to add {} entries to list.".format(ea_bulkadd))
        print("Response code: {}".format(r.status_code))
        print("Error Message: {}".format(r.content))
        print("EA List Length: {}; attempted: {}".format(len(ea['list_values'])-ea_bulkadd, len(ea['list_values'])))
    else:
        print("Successfully updated EA list.")

