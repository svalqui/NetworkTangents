# Library for the Class, methods related to Network devices;
#
# Authors: Sergio Valqui
# Created : 2015/10/08
# Modified : 2016/

import netconfigparser

class Interface(object):
    """Class container for all attributes and methods related to an Interface, they are part of NetworkDevice"""
    def __init__(self):
        self.InterfaceName = ''
        self.InterfaceShortName = ''
        self.ShowInterface = []
        self.ShowInterfaceSwitchport = []
        self.ShowRunningConfiguration = []
        self.ShowInterfaceCapabilities = []
        self.InterfaceDescription = ''
        self.PacketsInput = 0
        self.PacketsOutput = 0
        self.LineProtocol = ''
        self.InputErrors = ''
        self.OutputErrors = ''
        self.LastClearing = ''
        self.AdministrativeMode = ''
        self.AccessModeVlan = ''
        self.VoiceVlan = ''
        self.Type = ''

    def load_interface_details(self):
        """
        fills in class details coming from 'sh int'
        and 'sh int switchport' both should be already filled
        :param:
        :return:
        """
        for line in self.ShowInterface:
            if line.find('Description:') >= 0:
                self.InterfaceDescription = line.replace('Description:', '')
            elif line.find('packets input') >= 0:
                self.PacketsInput = int(line.split()[0])
            elif line.find('packets output') >= 0:
                self.PacketsOutput = int(line.split()[0])
            elif line.find('line protocol') >= 0:
                self.LineProtocol = line
            elif line.find('Last clearing of') >= 0:
                self.LastClearing = line

        for line in self.ShowInterfaceSwitchport:
            if line.find('Administrative Mode:') >= 0:
                self.AdministrativeMode = line[19:]
            elif line.find('Access Mode VLAN:') >= 0:
                self.AccessModeVlan = line.split()[3]
            elif line.find('Voice VLAN:') >= 0:
                self.VoiceVlan = line.split()[2]

        for line in self.ShowInterfaceCapabilities:
            if line.find('Type:') >= 0:
                self.Type = line.split()[1]


class NetworkDevice(object):
    """ Class container for all attributes and methods related to a Network Device
    """
    def __init__(self, device_name, user_name, user_password, enable_password, device_type='cisco_ios'):
        self.DeviceName = device_name
        self.UserName = user_name
        self.UPassword = user_password
        self.EnablePassword = enable_password
        self.ShowRunning = ''
        self.Interfaces = {}
        self.Vlans = {}
        self.Modules = []
        self.ShowInterfacesStatus = []
        self.ShowInterfaces = []
        self.ShowInterfaceSwitchport = []
        self.ShowInterfaceCapabilities = []
        self.VRF = {}
        self.ShowVersion = ''
        self.ShowVlan = ''
        self.ListIntLonNam = []

        """ testing using Netmiko as seems stable
        """

        from netmiko import ConnectHandler
        self.Cisco_Device = {
            'device_type': device_type,
            'ip': self.DeviceName,
            'username': self.UserName,
            'password': self.UPassword,
            'secret': self.EnablePassword,
            }
        self.Device_Connection = ConnectHandler(**self.Cisco_Device)

    def send_command(self, command):
        output = self.Device_Connection.send_command(command)
        return output

    def disconnect(self):
        self.Device_Connection.disconnect()

    def show_version(self):
        self.ShowVersion = self.send_command("sh ver")
        self.ShowVersion = self.ShowVersion.splitlines()

    def show_module(self):
        self.ShowModule = self.send_command("sh module")
        self.ShowModule = self.ShowModule.splitlines()

    def show_running(self):
        self.ShowRunning = self.send_command("sh run")

    def show_int(self):
        self.ShowInterfaces = self.send_command("show interfaces")
        self.ShowInterfaces = self.ShowInterfaces.splitlines()

    def show_int_status(self):
        self.ShowInterfacesStatus = self.send_command("sh int status")
        self.ShowInterfacesStatus = self.ShowInterfacesStatus.splitlines()

    def show_int_switchport(self):
        self.ShowInterfaceSwitchport = self.send_command("sh int switchport")
        self.ShowInterfaceSwitchport = self.ShowInterfaceSwitchport.splitlines()

    def show_int_capabilities(self):
        self.ShowInterfaceCapabilities = self.send_command("sh int capabilities ")
        self.ShowInterfaceCapabilities = self.ShowInterfaceCapabilities.splitlines()

    def show_vlan(self):
        self.ShowVlan = self.send_command("sh vlan")
        self.ShowVlan = self.ShowVlan.splitlines()

    def populate_vlans(self):
        """
        :return: {vlan_id_int}: [Vlannumber_str, Vlanname, composite]
        """
        self.show_vlan()
        self.Vlans = netconfigparser.show_vlan_to_dictionary(self.ShowVlan)

    def populate_interfaces(self):
        """
        runs 'sh int status', 'sh int', 'sh int switchport', 'sh int capabilities';
        and fills in NetworkDevice.Interfaces, dictionary;
        items are Interface classes
        :return:
        """
        self.show_int_status()

        self.show_int()
        listshowint = netconfigparser.show_interface_to_list(self.ShowInterfaces)

        self.show_int_switchport()
        listshowintswi = netconfigparser.show_interface_switchport_to_list(self.ShowInterfaceSwitchport)


        for shintperint in listshowint:
            swi_int = Interface()
            swi_int.InterfaceName = shintperint[0].split()[0]
            swi_int.InterfaceShortName = netconfigparser.int_name_to_int_short_name(swi_int.InterfaceName)
            swi_int.ShowInterface = shintperint
            self.Interfaces[swi_int.InterfaceShortName] = swi_int
            self.ListIntLonNam.append(swi_int.InterfaceName)

        for shintswiperint in listshowintswi:
            intshortname = shintswiperint[0].split(":")[1].strip()
            self.Interfaces[intshortname].ShowInterfaceSwitchport = shintswiperint

        self.show_int_capabilities()
        listshowintcap = netconfigparser.cut_include_from_list(self.ShowInterfaceCapabilities,self.ListIntLonNam)

        for intkey in self.Interfaces.keys():
            intholder = self.Interfaces[intkey]
            intholder.load_interface_details()






