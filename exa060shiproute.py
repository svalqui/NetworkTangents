# Copyright 2019 by Sergio Valqui. All rights reserved.
#
# Authors: Sergio Valqui
# Created : 2017/06/
# Modified : 2017/06

import getpass
from datetime import datetime
from networktangents import cisconet

device_name = input('DeviceName: ')
user_name = getpass.getpass("Username: ")
password = getpass.getpass()
enable_pass = getpass.getpass("Enabled Password: ")

network_device_1 = cisconet.Device(device_name, user_name, password, enable_pass)
network_device_1.populate_ip_route()

for line in network_device_1.base_ip_route:
    if line.find('irec') > 0 and line[0] == 'C':  # if directly connected
        print(line)

for index in network_device_1.VRF.keys():
    for line in network_device_1.VRF[index][2]:  # Routes per vrf
        if line.find('irec') > 0 and line[0] == 'C':  # if directly connected
            route_split = line.split(" ")
            line_print = device_name.strip() + "," + index + "," + route_split[-5].strip() + "," + \
                         route_split[-1].strip()
            print(line_print)

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
