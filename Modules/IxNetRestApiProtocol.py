# PLEASE READ DISCLAIMER
#
#    This class demonstrates sample IxNetwork REST API usage for
#    demo and reference purpose only.
#    It is subject to change for updates without warning.
#
# Here are some APIs that get object handles:
#
#    obj = getNgpfObjectHandleByName(ngpfEndpointObject='bgpIpv4Peer', ngpfEndpointName='bgp_2')
#
#    Get all device group objects for all the created topology groups
#       obj = getTopologyObjAndDeviceGroupObjByPortName(portName='2/1'):
#       Returns: ['/api/v1/sessions/1/ixnetwork/topology/2', ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1']]
#
#    deviceGroupObj = getDeviceGroupObjAndIpObjBySrcIp(srcIpAddress='1.1.1.1')
#       Returns: ('/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1',
#                 '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1')
#    deviceGroupObj = getDeviceGroupByRouterId(routerId='192.0.0.3')
#
#    ethernetObj = getNgpfObjectHandleByRouterId(routerId=routerId, ngpfEndpointObject='ethernet')
#    ipv4Obj = getIpv4ObjByPortName(portName='1/2')
#
#    gatewayObj = getDeviceGroupSrcIpGatewayIp(srcIpAddress)
# 
#    indexNumber = getIpAddrIndexNumber('10.10.10.1')
#    networkGroupObj = getNetworkGroupObjByIp(networkGroupIpAddress='10.10.10.1')

#    Get any NGPF object handle by host IP:
#       x = getProtocolListByHostIpNgpf('1.1.1.1')
#       objHandle = getProtocolObjFromHostIp(x, protocol='bgpIpv4Peer')
#
#    Get any NGPF object handle by either the physical port or by the vport name.
#       x = getProtocolListByPortNgpf(port=['192.168.70.120', '1', '1'])
#       x = getProtocolListByPortNgpf(portName='1/1')
#       objHandle = getProtocolObjFromProtocolList(x['deviceGroup'], 'bgpIpv4Peer')
#
#       Filter by the deviceGroupName if there are multiple device groups
#       x = getProtocolObjFromProtocolList(x['deviceGroup'], 'ethernet', deviceGroupName='DG2')
#
#    Get a NGPF object handle that is configured in a Device Group by the name.
#    x = getEndpointObjByDeviceGroupName('DG-2', 'bgpIpv4Peer')
#

import re, time
from IxNetRestApi import IxNetRestApiException
from IxNetRestApiPortMgmt import PortMgmt
from IxNetRestApiStatistics import Statistics
from IxNetRestApiClassicProtocol import ClassicProtocol

class Protocol(object):
    def __init__(self, ixnObj=None, portMgmtObj=None):
        """
        Parameters
           ixnObj: <str>: The main connection object.
           portMgmtObj: <str>: Optional. This is deprecated. Leaving it here for backward compatibility.
        """
        self.ixnObj = ixnObj
        self.ixNetwork = ixnObj.ixNetwork
        self.configuredProtocols = []
        self.portMgmtObj = PortMgmt(self.ixnObj)
        self.statObj = Statistics(self.ixnObj)
        self.classicProtocolObj = ClassicProtocol(self.ixnObj)

    def setMainObject(self, mainObject):
        """
        Description
           For Python Robot Framework support
        
        Parameter
           mainObject: <str>: The connect object.
        """
        self.ixnObj = mainObject
        self.portMgmtObj.setMainObject(mainObject)
        self.statObj.setMainObject(mainObject)

    def getSelfObject(self):
        """
        Description
           For Python Robot Framework support.
           Get the Connect object.
        """
        return self

    def createTopologyNgpf(self, portList, topologyName=None):
        """
        Description
            Create a new Topology and assign ports to it.

        Parameters
            portList: <list>: format = [[(str(chassisIp), str(slotNumber), str(portNumber)] ]
                      Example 1: [ ['192.168.70.10', '1', '1'] ]
                      Example 2: [ ['192.168.70.10', '1', '1'], ['192.168.70.10', '2', '1'] ]

            topologyName: <str>: Give a name to the Topology Group.

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology

        Return
            /api/v1/sessions/{id}/topology/{id}
        """
        vportList = self.portMgmtObj.getVports(portList)
        if len(vportList) != len(portList):
            raise IxNetRestApiException('createTopologyNgpf: There is not enough vports created to match '
                                        'the number of ports.')

        topologyObj = self.ixNetwork.Topology.add(Name=topologyName, Vports=vportList)
        return topologyObj

    def createDeviceGroupNgpf(self, topologyObj, multiplier=1, deviceGroupName=None):
        """
        Description
            Create a new Device Group.

        Parameters
            topologyObj: <str>: A Topology object: /api/v1/sessions/1/ixnetwork/topology/{id}
            multiplier: <int>: The amount of host to create (In integer).
            deviceGroupName: <str>: Optional: Device Group name.

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup

        Returns:
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}
        """
        self.ixnObj.logInfo('Create new Device Group')
        deviceGroupObj = topologyObj.DeviceGroup.add(Name=deviceGroupName, Multiplier=multiplier)
        return deviceGroupObj

    def configLacpNgpf(self, ethernetObj, **kwargs):
        """
        Description
            Create new LACP group.

        Parameter
            ethernetObj: <str>: The Ethernet stack object to create the LACP.
                         Example: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1

            administrativeKey: <int>: Default=1
            actorSystemId: <str>: Default='00 00 00 00 00 01'.
            actorSystemPriority: <int>: Default=1
            actorKey: <int>: Default=1
            actorPortNumber: <int>: Default=1
            actorPortPriority: <int>: Default=1

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/lacp
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/lacp/{id}

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/lacp/{id}
        """
        lacpObj = ethernetObj.Lacp.add()
        self.configuredProtocols.append(lacpObj)
        self.ixnObj.logInfo('Create new LACP NGPF')
        for key, value in kwargs.items():
            key = key[0:1].capitalize() + key[1:]
            try:
                eval("lacpObj." + key + ".Single(value)")
            except:
                setattr(lacpObj, key, value)
        return lacpObj

    def createEthernetNgpf(self, obj=None, port=None, portName=None, ngpfEndpointName=None, **kwargs):
        """
        Description
           This API is for backward compatiblility.  Use self.configEthernetNgpf()
        """
        ethernetObj = self.configEthernetNgpf(obj=obj, port=port, portName=portName, ngpfEndpointName=ngpfEndpointName,
                                              **kwargs)
        return ethernetObj

    def configEthernetNgpf(self, obj=None, port=None, portName=None, ngpfEndpointName=None, **kwargs):
        """
        Description
            Create or modify NGPF Ethernet.
            To create a new Ethernet stack in NGPF, pass in the device group object.
            To modify an existing Ethernet stack in NGPF, pass in the Ethernet object.

        Parameters
            obj: <str>: Device Group obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2'
                        Ethernet obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1'
            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF Ethernet endpoint.
            name|ethernetName: <str>:  Ethernet name.
            macAddressMultivalueType: Default=counter.
                                      Options: alternate, custom, customDistributed, random, repeatableRandom,
                                                                repeatableRandomRange, valueList
                                    To get the multivalue settings, refer to the API browser.

            macAddress: <dict>: By default, IxNetwork will generate unique Mac Addresses.
                         configIpv4Ngpf      {'start': '00:01:02:00:00:01', 'direction': 'increment',
                         'step': '00:00:00:00:00:01'}
                               Note: step: '00:00:00:00:00:00' means don't increment.

            macAddressPortStep:<str>: disable|00:00:00:01:00:00
                                      Incrementing the Mac address on each port based on your input.
                                      '00:00:00:00:00:01' means to increment the last byte on each port.

            vlanId: <dict>: Example: {'start': 103, 'direction': 'increment', 'step': 1}
            vlanPriority: <dict>:  Example: {'start': 2, 'direction': 'increment', 'step': 1}
            mtu: <dict>: Example: {'start': 1300, 'direction': 'increment', 'step': 1})


        Syntax
             POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet
             PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}

        Example:
             createEthernetNgpf(deviceGroupObj1,
                                ethernetName='Eth1',
                                macAddress={'start': '00:01:01:00:00:01',
                                            'direction': 'increment',
                                            'step': '00:00:00:00:00:01'},
                                macAddressPortStep='00:00:00:00:01:00',
                                vlanId={'start': 128, 'direction': 'increment', 'step':0},
                                vlanPriority={'start': 7, 'direction': 'increment', 'step': 0},
                                mtu={'start': 1400, 'direction': 'increment', 'step': 0},
                                )
        """
        if obj != None:
            if 'ethernet' in obj.href:
                ethObj = obj
            else:
                ethObj = obj.find().Ethernet.add()

        # To modify
        if ngpfEndpointName:
            ethObj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='ethernet')

        # To modify
        if port:
            x = self.getProtocolListByPortNgpf(port=port)
            ethObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ethernet')[0]

        # To modify
        if portName:
            x = self.getProtocolListByPortNgpf(portName=portName)
            ethObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ethernet')[0]

        if 'ethernetName' in kwargs:
            # ethObj.Name = kwargs['ethernetName']
            kwargs['name'] = kwargs['ethernetName'] 
            del kwargs['ethernetName'] 

        if 'macAddress' in kwargs:
            macObj = ethObj.Mac
            macValues = kwargs['macAddress']
            self.configMultivalue(macObj, 'counter', macValues)
            del kwargs['macAddress'] 

        if 'macAddressPortStep' in kwargs:
            macStepObj = ethObj.Mac.Steps.find()
            macStepValue = kwargs['macAddressPortStep']

            if macStepValue != 'disabled':
                macStepObj.Enabled = True
                macStepObj.Step = macStepValue
            else:
                macStepObj.Enabled = False
            del kwargs['macAddressPortStep']

        if 'vlanId' in kwargs:
            vlanObj = ethObj.Vlan.find().VlanId
            enableVlanObj = ethObj.EnableVlans
            enableVlanObj.Single(True)

            vlanValues = kwargs['vlanId']
            self.configMultivalue(vlanObj, 'counter', vlanValues)
            del kwargs['vlanId']

        if 'vlanPriority' in kwargs:
            priorityObj = ethObj.Vlan.find().Priority
            enableVlanObj = ethObj.EnableVlans
            enableVlanObj.Single(True)
            priorityValues = kwargs['vlanPriority']
            self.configMultivalue(priorityObj, 'counter', priorityValues)
            del kwargs['vlanPriority']

        for key, value in kwargs.items():
            key = key[0:1].capitalize() + key[1:]
            multivalueObj = eval("ethObj.find()." + key)
            try:
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)
            except:
                setattr(ethObj, key, value)

        if ethObj not in self.configuredProtocols:
            self.configuredProtocols.append(ethObj)
        return ethObj

    # Was configIsIsL3Ngpf
    def configIsIsL3Ngpf(self, obj, **data):
        """
        Description
            Create or modify ethernet/ISISL3

        Parameters
            ethernetObj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1'
            data: The ISISL3 attributes.  You could view all the attributes from the IxNetwork API browser.

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/isisL3
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/isisL3/{id}

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/isisL3/{id}
        """

        if 'isis' in obj.href:
            # To modify ISIS
            isisObj = obj
        else:
            isisObj = obj.IsisL3.add()

        for key, value in data.items():
            key = key[0:1].capitalize() + key[1:]
            print("checking for key", key)
            try:
                multivalueObj = eval('isisObj.find()'+key)
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)
            except:
                setattr(isisObj, key, value)

        if isisObj not in self.configuredProtocols:
            self.configuredProtocols.append(isisObj)
        return isisObj

    def getDeviceGroupIsIsL3RouterObj(self, deviceGroupObj):
        """
        Description
           Get and the Device Group's ISIS L3 Router object.
           Mainly used after configIsIsNgpf().

        Parameter
           deviceGroupObj: <str:obj>: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{1}

        Return
           IsIsL3Router obj: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/isisL3Router/{id}
        """
        isisL3RouterObj = deviceGroupObj.IsisL3Router.find()
        return isisL3RouterObj

    def configIsIsL3RouterNgpf(self, isisL3RouterObj, **data):
        """
        Description
           Configure ISIS L3 Router.

        Parameter
           isisL3RouterObj: <str:obj>: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/isisL3Router/{id}

           data: <dict>:  Get attributes from the IxNetwork API browser.
        """
        if 'enableBIER' in data:
            isisL3RouterObj.EnableBIER = data['enableBIER']

        for key, value in data.items():
            key = key[0:1].capitalize() + key[1:]
            try:
                eval("isisL3RouterObj." + key + ".Single(value)")
            except:
                setattr(isisL3RouterObj, key, value)

    def configIsIsBierSubDomainListNgpf(self, isisL3RouterObj, **data):
        """
        Description
           Configure ISIS BIER Subdomain.

        Parameter
           isisL3RouterObj: <str:obj>: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/isisL3Router/{id}

           data: <dict>:  active, subDomainId, BAR
        """
        isisBierSubDomainListObj = isisL3RouterObj.IsisBierSubDomainList
        for key, value in data.items():
            key = key[0:1].capitalize() + key[1:]
            try:
                eval("isisBierSubDomainListObj." + key + ".Single(value)")
            except:
                setattr(isisBierSubDomainListObj, key, value)

    def createIpv4Ngpf(self, obj=None, port=None, portName=None, ngpfEndpointName=None, **kwargs):
        """
        Description
           This API is for backward compatiblility.  Use self.configIpv4Ngpf()
        """
        ipv4Obj = self.configIpv4Ngpf(obj=obj, port=port, portName=portName, ngpfEndpointName=ngpfEndpointName,
                                      **kwargs)
        return ipv4Obj

    def configIpv4Ngpf(self, obj=None, port=None, portName=None, ngpfEndpointName=None, **kwargs):
        """
        Description
            Create or modify NGPF IPv4.
            To create a new IPv4 stack in NGPF, pass in the Ethernet object.
            If modifying, there are four options. 2-4 will query for the IP object handle.

               1> Provide the IPv4 object handle using the obj parameter.
               2> Set port: The physical port.
               3> Set portName: The vport port name.
               4> Set NGPF IP name that you configured.

        Parameters
            obj: <str>: None or Ethernet obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1'
                                IPv4 obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1'

            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF IPv4 endpoint.

            kwargs:
               ipv4AddressMultivalueType & gatewayMultivalueType:
                                    Default='counter'. Options: alternate, custom, customDistributed, random,
                                    repeatableRandom, repeatableRandomRange, valueList
                                    To get the multivalue settings, refer to the API browser.

               ipv4Address: <dict>: {'start': '100.1.1.100', 'direction': 'increment', 'step': '0.0.0.1'},
               ipv4AddressPortStep: <str>|<dict>:  disable|0.0.0.1 
                                    Incrementing the IP address on each port based on your input.
                                    0.0.0.1 means to increment the last octet on each port.

               gateway: <dict>: {'start': '100.1.1.1', 'direction': 'increment', 'step': '0.0.0.1'},
               gatewayPortStep:  <str>|<dict>:  disable|0.0.0.1 
                                 Incrementing the IP address on each port based on your input.
                                 0.0.0.1 means to increment the last octet on each port.

               prefix: <int>:  Example: 24
               rsolveGateway: <bool>

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}

        Example to create a new IPv4 object:
             ipv4Obj1 = createIpv4Ngpf(ethernetObj1,
                                       ipv4Address={'start': '100.1.1.1', 'direction': 'increment', 'step': '0.0.0.1'},
                                       ipv4AddressPortStep='disabled',
                                       gateway={'start': '100.1.1.100', 'direction': 'increment', 'step': '0.0.0.0'},
                                       gatewayPortStep='disabled',
                                       prefix=24,
                                       resolveGateway=True)

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}
        """
        # To modify
        if ngpfEndpointName:
            ipv4Obj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='ipv4')

        # To modify
        if port:
            x = self.getProtocolListByPortNgpf(port=port)
            ipv4Obj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ipv4')[0]
            createNewIpv4Obj = False

        # To modify
        if portName:
            x = self.getProtocolListByPortNgpf(portName=portName)
            ipv4Obj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ipv4')[0]
            createNewIpv4Obj = False

        if obj != None:
            if 'ipv4' in obj.href:
                ipv4Obj = obj
            else:
                ipv4Obj = obj.Ipv4.add()

        if 'gatewayPortStep' in kwargs:
            gatewayPortStepObj = ipv4Obj.GatewayIp.Steps.find()
            gatewayPortStepValues = kwargs['gatewayPortStep']
            if gatewayPortStepValues == 'enabled':
                self.configMultivalue(gatewayPortStepObj, 'counter', gatewayPortStepValues)
            else:
                gatewayPortStepObj.Enabled = False
            del kwargs['gatewayPortStep']

        if 'ipv4AddressPortStep' in kwargs:
            addrPortStepObj = ipv4Obj.Address.Steps.find()
            addrPortStepValues = kwargs['ipv4AddressPortStep']

            if addrPortStepValues != 'disabled':
                addrPortStepObj.Enabled = True
                addrPortStepObj.Step = addrPortStepValues
            else:
                addrPortStepObj.Enabled = False
            del kwargs['ipv4AddressPortStep']

        for key, value in kwargs.items():
            key = key [0:1].capitalize() + key[1:]
            multivalueObj = eval("ospfObj.find()." + key)
            try:
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)
            except:
                setattr(ipv4Obj, key, value)

        if ipv4Obj not in self.configuredProtocols:
            self.configuredProtocols.append(ipv4Obj)
        return ipv4Obj

    def configIpv4Loopback(self, deviceGroupObj, **kwargs):
        """
        Description
            Configure an IPv4 loopback.

        Parameters
            deviceGroupObj: <str>: /api/v1/sessions/1/ixnetwork/topology{id}/deviceGroup/{id}
            kwargs: <dict>

        Example:
            protocolObj.configIpv4Loopback(deviceGroupObj,
                                           name='ipv4Loopback-1',
                                           multiplier=10,
                                           ipv4Address={'start': '1.1.1.1',
                                                        'direction': 'increment',
                                                        'step': '0.0.0.1'},
                                           prefix=32,
                                          )

        """
        createNewIpv4Obj = True
        ipv4LoopbackObj = deviceGroupObj.Ipv4Loopback.add()
        if 'name' in kwargs:
            ipv4LoopbackObj.Name = kwargs['name']

        if 'multiplier' in kwargs:
            ipv4LoopbackObj.Multiplier = kwargs['multiplier']

        if 'prefix' in kwargs:
            ipv4LoopbackObj.Prefix.Single(kwargs['prefix'])

        if 'ipv4Address' in kwargs:
            addressObj = ipv4LoopbackObj.Address
            self.ixnObj.logInfo('Configuring IPv4 address. Attribute for multivalueId = addressObj.href')

            # Default to counter
            multivalueType = 'counter'

            if 'ipv4AddressMultivalueType' in kwargs:
                multivalueType = kwargs['ipv4AddressMultivalueType']

            if multivalueType == 'random':
                addressObj.Random()
            else:
                self.configMultivalue(addressObj, multivalueType, data=kwargs['ipv4Address'])

        if createNewIpv4Obj:
            self.configuredProtocols.append(ipv4LoopbackObj)

    def configDhcpClientV4(self, obj, **kwargs):
        """
        Description
            Create or modify DHCP V4 Client in NGPF.
            To create a new DCHP v4 Client stack in NGPF, pass in the Ethernet object.
            To modify an existing DHCP V4 Client stack in NGPF, pass in the dhcpv4client object.

        Parameters
            obj: <str>: To create new DHCP obj.
                 Example: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1

            obj: <str>: To Modify DHCP client.
                 Example: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/dhcpv4client/1

            dhcp4Broadcast: <bool>
            multiplier: <int>: The amount of DHCP clients to create.
            dhcp4ServerAddress: <str>: The DHCP server IP address.
            dhcp4UseFirstServer: <bool>: Default=True
            dhcp4GatewayMac: <str>: Gateway mac address in the format of 00:00:00:00:00:00
            useRapdCommit: <bool>: Default=False
            renewTimer: <int>: Default=0
    
        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/dhcpv4client
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/
            dhcpv4client/{id}

        Example:
            dhcpClientObj = protocolObj.configV4DhcpClient(ethernetObj1,
                                                           dhcp4Broadcast=True,
                                                           multiplier = 10,
                                                           dhcp4ServerAddress='1.1.1.11',
                                                           dhcp4UseFirstServer=True,
                                                           dhcp4GatewayMac='00:00:00:00:00:00',
                                                           useRapdCommit=False,
                                                           renewTimer=0)

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/dhcpv4client/{id}
        """

        if 'dhcp' not in obj.href:
            # self.ixnObj.logInfo('Create new DHCP client V4')
            dhcpObj = obj.Dhcpv4client.add()

        # To modify DHCP
        if 'dhcp' in obj.href:
            dhcpObj = obj

        if 'name' in kwargs:
            dhcpObj.Name = kwargs['name']

        for key, value in kwargs.items():
            key = key[0:1].capitalize() + key[1:]
            multivalueObj = eval("dhcpObj.find()." + key)

            try:
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)
            except:
                setattr(dhcpObj, key, value)

        if dhcpObj not in self.configuredProtocols:
            self.configuredProtocols.append(dhcpObj)
        return dhcpObj

    def configDhcpServerV4(self, obj, **kwargs):
        """
        Description
            Create or modify DHCP v4 Server in NGPF.
            To create a new DCHP v4 server stack in NGPF, pass in the IPv4 object.
            To modify an existing DHCP V4 server stack in NGPF, pass in the dhcpv4server object.

        Parameters
            obj: <str>: To create new DHCP: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
            obj: <str>: To modify DHCP server: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/
            ipv4/1/dhcpv4server/1

            useRapidCommit: <bool>: Default=False
            multiplier: <int>: Default-1
            subnetAddrAssign: <bool>: Default=False
            defaultLeaseTime: <int>: Default=86400
            echoRelayInfo: <bool>: Default=True
            ipAddress: <str>: The DHCP server IP address.
            ipAddressIncrement: <str>: format='0.0.0.1'
            ipDns1: <str>: Default='0.0.0.0'
            ipDns2: <str>: Default=='0.0.0.0'
            ipGateway: <str>: The DHCP server gateway IP address.
            ipPrefix: <int>: The DHCP server IP address prefix. Ex: 16.
            poolSize: <int>: The DHCP server pool size.

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/dhcpv4server
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/
            dhcpv4server/{id}

        Example:
            protocolObj.configV4DhcpServer('/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1/ethernet/1/ipv4/1',
                                           name='DHCP-Server-1',
                                           multiplier='1',
                                           useRapidCommit=False,
                                           subnetAddrAssign=False,
                                           defaultLeaseTime=86400,
                                           echoRelayInfo=True,
                                           ipAddress='1.1.1.1',
                                           ipAddressIncrement='0.0.0.1',
                                           ipDns1='0.0.0.0',
                                           ipDns2='0.0.0.0',
                                           ipGateway='1.1.1.11',
                                           ipPrefix=24,
                                           poolSize=10)

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/dhcpv4server/{id}
        """
        if 'dhcp' not in obj.href:
            # self.ixnObj.logInfo('Create new DHCP server v4')
            dhcpObj = obj.Dhcpv4server.add()

        # To modify DHCP server
        if 'dhcp' in obj.href:
            dhcpObj = obj

        if 'name' in kwargs:
            dhcpObj.Name = kwargs['name']

        dhcpServerAttributes = ['useRapidCommit', 'subnetAddrAssign']
        dhcpServerSessionAttributes = ['defaultLeaseTime', 'echoRelayInfo', 'ipAddress', 'ipAddressIncrement', 'ipDns1', 'ipDns2', 'ipGateway', 'ipPrefix', 'poolSize']

        # All of these DHCP attributes configures multivalue singleValue. So just loop them to do the same thing.
        for key, value in kwargs.items():
            if key in dhcpServerAttributes:
                key = key[0:1].capitalize() + key[1:]
                multivalueObj = eval('dhcpObj.find().'+key)
                try:
                    if type(value) == dict:
                        self.configMultivalue(multivalueObj, 'counter', value)
                    else:
                        multivalueObj.Single(value)
                except:
                    setattr(dhcpObj, key, value)

        if 'multiplier' in kwargs:
            dhcpObj.Multiplier = kwargs['multiplier']
            # self.ixnObj.patch(self.ixnObj.httpHeader+dhcpObj, data={'multiplier': kwargs['multiplier']})

        dhcpServerSessionObj = dhcpObj.Dhcp4ServerSessions
        for key, value in kwargs.items():
            if key in dhcpServerSessionAttributes:
                key = key[0:1].capitalize() + key[1:]
                multivalObj = eval('dhcpServerSessionObj.'+key)
                try:
                    if type(value) == dict:
                        self.configMultivalue(multivalObj, 'counter', value)
                    else:
                        multivalObj.Single(value)
                except:
                    setattr(dhcpServerSessionObj, key, value)

        if dhcpObj not in self.configuredProtocols:
            self.configuredProtocols.append(dhcpObj)
        return dhcpObj

    def configOspf(self, obj=None, routerId=None, port=None, portName=None, ngpfEndpointName=None, hostIp=None,
                   **kwargs):
        """
        Description
            Create or modify OSPF. If creating a new OSPF, provide an IPv4 object handle.
            If modifying a OSPF, there are five options. 2-6 will query for the OSPF object handle.

               1> Provide the OSPF object handle using the obj parameter.
               2> Set routerId.
               3> Set port: The physical port.
               4> Set portName: The vport port name.
               5> Set NGPF OSPF name that you configured.
               6> Set hostIp: The src IP.

        Parameters
            IPv4 object handle example:
               obj: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1

            OSPF object handle example:
               obj: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/ospfv2/1

            routerId: <str>: The router ID IP address.
            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF endpoint.
            hostIp: <src>: The source IP address to query for the object.
            kwargs: OSPF configuration attributes. The attributes could be obtained from the IxNetwork API browser.

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/ospfv2
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/ospfv2/{id}

        Example:
            ospfObj1 = configOspf(ipv4Obj,
                          name = 'ospf_1',
                          areaId = '0',
                          neighborIp = '1.1.1.2',
                          helloInterval = '10',
                          areaIdIp = '0.0.0.0',
                          networkType = 'pointtomultipoint',
                          deadInterval = '40')

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/ospfv2/{id}
        """
        if obj != None:
            if routerId:
                ospfObj = self.getNgpfObjectHandleByRouterId(routerId=routerId, ngpfEndpointObject='ospfv2')

            if port:
                x = self.getProtocolListByPortNgpf(port=port)
                ospfObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ospfv2')[0]

            if portName:
                x = self.getProtocolListByPortNgpf(portName=portName)
                ospfObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ospfv2')[0]

            if 'ospf' not in obj.href:
                ospfObj = obj.Ospfv2.add()

            if 'ospf' in obj.href:
                ospfObj = obj

            for key, value in kwargs.items():
                if key not in ['lsaRefreshTime', 'lsaRetransmitTime', 'interFloodLsUpdateBurstGap']:
                    itemObj =  key[0:1].capitalize() + key[1:]
                    multivalueObj = eval("ospfObj.find()."+ itemObj)
                    try:
                        if type(value) == dict:
                            self.configMultivalue(multivalueObj, 'counter', value)
                        else:
                            multivalueObj.Single(value)
                    except:
                        setattr(ospfObj, itemObj, value)

            if 'lsaRefreshTime' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().Ospf.Router.find().LsaRefreshTime = kwargs['lsaRefreshTime']
            if 'lsaRetransmitTime' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().Ospf.Router.find().LsaRefreshTime = kwargs['lsaRetransmitTime']
            if 'interFloodLsUpdateBurstGap' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().Ospf.Router.find().LsaRefreshTime = kwargs['interFloodLsUpdateBurstGap']

        if ospfObj not in self.configuredProtocols:
            self.configuredProtocols.append(ospfObj)
        return ospfObj
      
    def configOspfv3(self, obj=None, routerId=None, port=None, portName=None, ngpfEndpointName=None, hostIp=None, **kwargs):
        """
        Description
            Create or modify OSPFv3. If creating a new OSPFv3, provide an IPv6 object handle.
            If modifying a OSPF, there are five options. 2-6 will query for the OSPFv3 object handle.

               1> Provide the OSPFv3 object handle using the obj parameter.
               2> Set routerId.
               3> Set port: The physical port.
               4> Set portName: The vport port name.
               5> Set NGPF OSPF name that you configured.
               6> Set hostIp: The src IP.

        Parameters
            IPv6 object handle example:
               obj: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/1

            OSPF object handle example:
               obj: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/1/ospfv3/1

            routerId: <str>: The router ID IP address.
            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF endpoint.
            hostIp: <src>: The source IP address to query for the object.
            kwargs: OSPF configuration attributes. The attributes could be obtained from the IxNetwork API browser.

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}/ospfv3
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}/ospfv3/{id}

        Example:
            ospfObj1 = configOspf(ipv6Obj,
                          name = 'ospf_1',
                          areaId = '0',
                          neighborIp = '::2',
                          helloInterval = '10',
                          areaIdIp = '::0',
                          networkType = 'pointtomultipoint',
                          deadInterval = '40')

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}/ospfv3/{id}
        """
        if obj != None:
            if routerId:
                ospfObj = obj.find().Ospfv3.find(LocalRouterID=routerId)

            if port:
                x = self.getProtocolListByPortNgpf(port=port)
                ospfObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ospfv3')[0]

            if portName:
                x = self.getProtocolListByPortNgpf(portName=portName)
                ospfObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ospfv3')[0]
            
            if ngpfEndpointName:
                ospfObj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='ospfv3')

            if hostIp:
                x = self.getProtocolListByHostIpNgpf(hostIp)
                ospfObj = self.getProtocolObjFromHostIp(x, protocol='ospfv3')

            if ospfObj == None:
                if 'ospf' not in obj.href:
                    ospfObj = obj.Ospfv3.add()
                else:
                    ospfObj = obj

            for item, value in kwargs.items():
                if item not in ['lsaRefreshTime', 'lsaRetransmitTime', 'interFloodLsUpdateBurstGap']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    print("checking for key", itemObj)
                    try:
                        multivalObj = eval("ospfObj.find()." + itemObj)
                        if type(value) == dict:
                            self.configMultivalue(multivalObj, 'counter', value)
                        else:
                            multivalObj.Single(value)
                    except:
                        setattr(ospfObj, itemObj, value)

            if 'lsaRefreshTime' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().OspfV3.Router.find().LsaRefreshTime = kwargs['lsaRefreshTime']
            if 'lsaRetransmitTime' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().OspfV3.Router.find().LsaRefreshTime = kwargs['lsaRetransmitTime']
            if 'interFloodLsUpdateBurstGap' in kwargs:
                self.ixNetwork.Vport.find(Name=portName).Protocols.find().OspfV3.Router.find().LsaRefreshTime = kwargs['interFloodLsUpdateBurstGap']

            if ospfObj not in self.configuredProtocols:
                self.configuredProtocols.append(ospfObj)
        return ospfObj
      
    def configBgp(self, obj=None, routerId=None, port=None, portName=None, ngpfEndpointName=None, hostIp=None, **kwargs):
        """
        Description
            Create or modify BGP.  If creating a new BGP, provide an IPv4 object handle.
            If modifying a BGP, there are five options. 2-6 will query for the BGP object handle.

               1> Provide the BGP object handle using the obj parameter.
               2> Set routerId.
               3> Set port: The physical port.
               4> Set portName: The vport port name.
               5> Set NGPF BGP name that you configured.
               6> Set hostIp: The src IP.

        Parameters
            obj: <str>: None or Either an IPv4 object or a BGP object.
               If creating new bgp object:
                  IPv4 object example: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
               If modifying, you could provide the bgp object handle using the obj parameter:
                  BGP object example: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/
                  bgpIpv4Peer/1
            
            routerId: <str>: The router ID IP address.
            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF endpoint.
            hostIp: <src>: The source IP address to query for the object.
            kwargs: BGP configuration attributes. The attributes could be obtained from the IxNetwork API browser.

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/bgpIpv4Peer
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}
            /bgpIpv4Peer/{id}

        Example: Create a new bgp object...
            configBgp(ipv4Obj,
                  name = 'bgp_1',
                  enableBgp = True,
                  holdTimer = 90,
                  dutIp={'start': '1.1.1.2', 'direction': 'increment', 'step': '0.0.0.0'},
                  localAs2Bytes=101,
                  enableGracefulRestart = False,
                  restartTime = 45,
                  type = 'internal',
                  enableBgpIdSameasRouterId = True

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/bgpIpv4Peer/{id}
        """
        # To modify
        if ngpfEndpointName:
            bgpObj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='bgpIpv4Peer')

        # To modify
        if port:
            x = self.getProtocolListByPortNgpf(port=port)
            bgpObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'bgpIpv4Peer')[0]

        # To modify
        if portName:
            x = self.getProtocolListByPortNgpf(portName=portName)
            bgpObj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'bgpIpv4Peer')[0]

        # To modify
        if routerId:
            bgpObj = self.getNgpfObjectHandleByRouterId(routerId=routerId, ngpfEndpointObject='bgpIpv4Peer')

        # To modify
        if hostIp:
            x = self.getProtocolListByHostIpNgpf(hostIp)
            bgpObj = self.getProtocolObjFromHostIp(x, protocol='bgpIpv4Peer')

        if 'Bgp' in obj.href or 'bgp' in obj.href:
            # To modify BGP
            bgpObj = obj
        else:
            ## Common code for BgpIpv4 and BgpIpv6
            if hasattr(obj, 'BgpIpv4Peer'):
                bgpObj = obj.BgpIpv4Peer.add()
            if hasattr(obj,'BgpIpv6Peer'):
                bgpObj = obj.BgpIpv6Peer.add()

        for key, value in kwargs.items():
            key = key[0:1].capitalize() + key[1:]
            multivalue = eval("bgpObj.find()." + key)
            try:
                if type(value) == dict:
                    self.configMultivalue(multivalue, 'counter', value)
                else:
                    multivalue.Single(value)
            except:
                setattr(bgpObj, key, value)

        if bgpObj not in self.configuredProtocols:
            self.configuredProtocols.append(bgpObj)
        return bgpObj

    def configBgpIpv6(self, obj=None, routerId=None, port=None, portName=None, ngpfEndpointName=None, hostIp=None, **kwargs):
        """
        Creating a namespace for BgpIpv6Peer.  Pass everything to configBgp()
        
        Example:
           ipv6Obj2 = '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1/ethernet/1/ipv6'

           bgpObj2 = protocolObj.configBgpIpv6(ipv6Obj2,
                                        name = 'bgp_2',
                                        active = True,
                                        holdTimer = 90,
                                        dutIp={'start': '2001:0:0:1:0:0:0:1', 'direction': 'increment', 'step': '0:0:0:0:0:0:0:0'},
                                        localAs2Bytes = 101,
                                        enableGracefulRestart = False,
                                        restartTime = 45,
                                        type = 'internal',
                                        enableBgpIdSameasRouterId = True)

        """
        return self.configBgp(obj, routerId, port, portName, ngpfEndpointName, hostIp, **kwargs)

    def configIgmpHost(self, ipObj, **kwargs):
        """
        Description
            Create or modify IGMP host.
            Provide an IPv4|IPv6 obj to create a new IGMP host object.
            Provide an IGMP host object to modify.

        Parameters
            ipObj: <str:obj>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
            igmpObj: <str:obj>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/igmp/1

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/igmp
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/igmp/{id}
        
        Example:

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/igmp/{id}
        """
        # To create new IGMP object
        def configIgmpHost(self, ipObj, **kwargs):
    """
    Description
        Create or modify IGMP host.
        Provide an IPv4|IPv6 obj to create a new IGMP host object.
        Provide an IGMP host object to modify.
    Parameters
        ipObj: <str:obj>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
        igmpObj: <str:obj>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/igmp/1
    Syntax
        POST:  /api/v1/sessions/{​​​​​​​id}​​​​​​​/ixnetwork/topology/{​​​​​​​id}​​​​​​​/deviceGroup/{​​​​​​​id}​​​​​​​/ethernet/{​​​​​​​id}​​​​​​​/ipv4/{​​​​​​​id}​​​​​​​/igmp
        PATCH: /api/v1/sessions/{​​​​​​​id}​​​​​​​/ixnetwork/topology/{​​​​​​​id}​​​​​​​/deviceGroup/{​​​​​​​id}​​​​​​​/ethernet/{​​​​​​​id}​​​​​​​/ipv4/{​​​​​​​id}​​​​​​​/igmp/{​​​​​​​id}​​​​​​​
    Example:
    Return
        /api/v1/sessions/{​​​​​​​id}​​​​​​​/ixnetwork/topology/{​​​​​​​id}​​​​​​​/deviceGroup/{​​​​​​​id}​​​​​​​/ethernet/{​​​​​​​id}​​​​​​​/ipv4/{​​​​​​​id}​​​​​​​/igmp/{​​​​​​​id}​​​​​​​
    """
        # To create new IGMP object
        igmpObj = None
        if 'igmp' not in ipObj.href:
            self.ixnObj.logInfo('Create new IGMP V4 host')
            igmpObj = ipObj.IgmpHost.add()

        # To modify IGMP
        if 'igmp' in ipObj.href:
            igmpObj = ipObj

        for key, value in kwargs.items():
            key = key[0:1].capitalize() + key[1:]
            multivalueObj = eval("igmpObj.find()." + key)
            try:
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)
            except:
                setattr(igmpObj, key, value)

        if igmpObj not in self.configuredProtocols:
            self.configuredProtocols.append(igmpObj)
        return igmpObj

    def configMpls(self, ethernetObj, **kwargs):
        """
        Description
            Create or modify static MPLS.  

        Parameters
            ethernetObj: <str>: The Ethernet object handle.
                         Example: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/mpls
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/mpls/{id}

        Example:
            mplsObj1 = protocolObj.configMpls(ethernetObj1,
                                      name = 'mpls-1',
                                      destMac = {'start': '00:01:02:00:00:01', 'direction': 'increment',
                                      'step': '00:00:00:00:00:01'},
                                      exp = {'start': 0, 'direction': 'increment', 'step': 1},
                                      ttl = {'start': 16, 'direction': 'increment', 'step': 1},
                                      rxLabelValue = {'start': 288, 'direction': 'increment', 'step': 1},
                                      txLabelValue = {'start': 888, 'direction': 'increment', 'step': 1})

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/mpls/{id}
        """
        if 'mpls' not in ethernetObj:
            mplsObj = ethernetObj.Mpls.add()
        else:
            mplsObj = ethernetObj

        if 'name' in kwargs:
            setattr(mplsObj, 'Name', kwargs['name'])
            del kwargs['name']

        mplsAttributes = ['rxLabelValue', 'txLabelValue', 'destMac', 'cos', 'ttl']

        for key, value in kwargs.items():
            if key in mplsAttributes:
                key = key[0].capitalize() + key[1:]
                multivalueObj = eval('mplsObj.find().'+key)
                if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
                else:
                    multivalueObj.Single(value)

        if mplsObj not in self.configuredProtocols: 
            self.configuredProtocols.append(mplsObj)
        return mplsObj

    def configVxlanNgpf(self, obj=None, routerId=None, port=None, portName=None, ngpfEndpointName=None, hostIp=None, **kwargs):
        """
        Description
            Create or modify a VXLAN.  If creating a new VXLAN header, provide an IPv4 object handle.
            If creating a new VxLAN object, provide an IPv4 object handle.
            If modifying a OSPF, there are five options. 2-6 will query for the OSPF object handle.

               1> Provide the OSPF object handle using the obj parameter.
               2> Set routerId.
               3> Set port: The physical port.
               4> Set portName: The vport port name.
               5> Set NGPF OSPF name that you configured.
               6> Set hostIp: The src IP.
            
        Parameters
               obj: <str>: IPv4 Obj example: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}
                           VxLAN Obj example: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/vxlan/{id}

        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/vxlan
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/vxlan/{id}

        Example:
            createVxlanNgpf(ipv4Object='/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1',
                            vtepName='vtep_1',
                            vtepVni={'start':2008, 'step':2, 'direction':'increment'},
                            vtepIpv4Multicast={'start':'225.8.0.1', 'step':'0.0.0.1', 'direction':'increment'})

            start = The starting value
            step  = 0 means don't increment or decrement.
                    For IP step = 0.0.0.1.  Increment on the last octet.
                                  0.0.1.0.  Increment on the third octet.
            direction = increment or decrement the starting value.

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/vxlan/{id}
        """
                if obj != None:
            if 'vxlan' not in obj:
                vxlanId = obj.Ipv4.find().Vxlan.add()

            if 'vxlan' in obj:
                vxlanId = obj

            # To modify
        if ngpfEndpointName:
            vxlanId = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='vxlan')

            # To modify
        if port:
            x = self.getProtocolListByPortNgpf(port=port)
            vxlanId = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'vxlan')[0]

            # To modify
        if portName:
            x = self.getProtocolListByPortNgpf(portName=portName)
            vxlanId = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'vxlan')[0]

            # To modify
        if routerId:
            vxlanId = self.getNgpfObjectHandleByRouterId(routerId=routerId, ngpfEndpointObject='vxlan')

            # To modify
        if hostIp:
            x = self.getProtocolListByHostIpNgpf(hostIp)
            vxlanId = self.getProtocolObjFromHostIp(x, protocol='vxlan')

        if 'vtepName' in kwargs:
            kwargs['name'] = kwargs['vtepName']
            del kwargs['vtepName']

        if 'vtepIpv4Multicast' in kwargs:
            kwargs['ipv4_multicast'] = kwargs['vtepIpv4Multicast']
            del kwargs['vtepIpv4Multicast']

        for key, value in kwargs.items():
            itemObj = key[0:1].captilize()+key[1:]
            multivalueObj = eval("vxlanId.find()."+itemObj)

            try:
               if type(value) == dict:
                    self.configMultivalue(multivalueObj, 'counter', value)
               else:
                    multivalueObj.Single(value)
            except:
               setattr(vxlanId, itemObj, value)

        if vxlanId not in self.configuredProtocols:
            self.configuredProtocols.append(vxlanId)
        return vxlanId

    def configRsvpTeLsps(self, ipv4Obj):
        """
        Description
            Create new RSVP-TE LSPS Tunnel. A RSVP-TE interface is created automatically if there 
            is no RSVR-TE configured.

        Parameter
            ipv4Obj: <str>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/rsvpteLsps

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/rsvrteLsps/{id}
        """
        rsvpTeObj = ipv4Obj.RsvpteLsps.add()
        return rsvpTeObj 

    def deleteRsvpTeLsps(self, rsvpTunnelObj):
        """
        Description
            Delete a RSVP-TE tunnel.
            Note: Deleting the last tunnel will also delete the RSVR-TE Interface.

        Parameter
            rsvrTunnelObj: <str>: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/rsvpteLsps/{id}

        Syntax
            DELETE: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/rsvpteLsps/{id}
        """
        rsvpTunnelObj.remove()

    def configNetworkGroup(self, **kwargs):
        """
        Description
            Create or modify a Network Group for network advertisement.
            Supports both IPv4 and IPv6

            Pass in the Device Group obj for creating a new Network Group.
                /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
        
            Pass in the Network Group obj to modify.
               /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools

        Example:
              NOTE: Supports both IPv4 and IPv6

               Device Group object sample: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
               configNetworkGroup(create=deviceGroupObj
                                  name='networkGroup1',
                                  multiplier = 100,
                                  networkAddress = {'start': '160.1.0.0', 'step': '0.0.0.1', 'direction': 'increment'},
                                  prefixLength = 24)

               
               To modify a Network Group:
               NetworkGroup obj sample: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1
               configNetworkGroup(modify=networkGroupObj,
                                  name='networkGroup-ospf',
                                  multiplier = 500,
                                  networkAddress = {'start': '200.1.0.0', 'step': '0.0.0.1', 'direction': 'increment'},
                                  prefixLength = 32)

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}
        """
        ipVersion = kwargs.get('ipVersion','ipv4')

        if 'create' not in kwargs and 'modify' not in kwargs:
            raise IxNetRestApiException('configNetworkGroup requires either a create or modify parameter.')

        if 'create' in kwargs:
            deviceGroupObj = kwargs['create']
            networkGroupObj = deviceGroupObj.find().NetworkGroup.add()

        if 'modify' in kwargs:
            networkGroupObj = kwargs['modify']

        if 'name' in kwargs:
            networkGroupObj.Name = kwargs['name']

        if 'multiplier' in kwargs:
            networkGroupObj.Multiplier = kwargs['multiplier']

        if 'networkAddress' in kwargs:
            networkAddrValue = kwargs['networkAddress']
            if ipVersion == 'ipv4':
                prefixObj = networkGroupObj.find().Ipv4PrefixPools.add()
                networkAddrObj = prefixObj.find().NetworkAddress

                if networkAddrValue['direction'] == "increment":
                    networkAddrObj.Increment(start_value = networkAddrValue['start'], step_value = networkAddrValue['step'])
                if networkAddrValue['direction'] == "decrement":
                    networkAddrObj.Decrement(start_value=kwargs['start'], step_value=networkAddrValue['step'])

                if 'prefixLength' in kwargs:
                    if type(kwargs['prefixLength']) == 'int':
                        if networkAddrObj is not None:
                            networkAddrObj.Single(kwargs['prefixLength'])

            elif ipVersion == "ipv6":
                prefixObj = networkGroupObj.find().Ipv6PrefixPools.add()
                networkAddrObj = prefixObj.find().NetworkAddress

                if networkAddrValue['direction'] == "increment":
                    networkAddrObj.Increment(start_value=networkAddrValue['start'], step_value=networkAddrValue['step'])
                if kwargs['direction'] == "decrement":
                    networkAddrObj.Decrement(start_value=networkAddrValue['start'], step_value=networkAddrValue['step'])

                if 'prefixLength' in kwargs:
                    if type(kwargs['prefixLength']) == 'int':
                        if networkAddrObj is not None:
                            networkAddrObj.Single(kwargs['prefixLength'])

        return networkGroupObj, prefixObj
      
    def configNetworkGroupWithTopology(self, topoType='Linear', **kwargs):
        """
        Description
            Create or modify a Network Group Topology for network advertisement.

            Pass in the Device Group obj for creating a new Network Group.
                /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1

            Pass in the Network Group obj to modify.
               /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1

            Pass in topoType(topology type) to configure require network with topology type
                Ex: 'Custom','Fat Tree','Grid','Hub-And-Spoke','Linear','Mesh','Ring','Tree'

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup
            POST: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/networkTopology/

        Example:
               Device Group object sample: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
               configNetworkGroupWithTopology(topoType='Linear',create=deviceGroupObj
                                  name='networkGroup1',
                                  multiplier = 100
                                  )


               To modify a Network Group:
               NetworkGroup obj sample: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1
               configNetworkGroupWithTopology(topoType='Linear',modify=networkGroupObj,
                                  name='networkGroup-ospf',
                                  multiplier = 100,
                                  )

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/networkTopology/netTopologyLinear
        """
        # In case it is modify, we still need to return self.prefixPoolObj
        self.topoTypeDict = {'Custom': 'NetTopologyCustom',
                             'Fat Tree': 'NetTopologyFatTree',
                             'Grid': 'NetTopologyGrid',
                             'Hub-And-Spoke': 'NetTopologyHubNSpoke',
                             'Linear': 'NetTopologyLinear',
                             'Mesh': 'NetTopologyMesh',
                             'Ring': 'NetTopologyRing',
                             'Tree': 'NetTopologyTree',
                             }

        self.networkTopologyObj = None
        self.networkTopology = None

        if 'create' not in kwargs and 'modify' not in kwargs:
            raise IxNetRestApiException('configNetworkGroup requires either a create or modify parameter.')

        if 'create' in kwargs:
            deviceGroupObj = kwargs['create']
            self.ixnObj.logInfo('Creating new Network Group')
            networkGroupObj = deviceGroupObj.NetworkGroup.add()
        if 'modify' in kwargs:
            networkGroupObj = kwargs['modify']

        if 'name' in kwargs:
            networkGroupObj.Name = kwargs['name']

        if 'multiplier' in kwargs:
            networkGroupObj.Multiplier = kwargs['multiplier']

        if 'create' in kwargs:
            self.ixnObj.logInfo('Create new Network Group network topology')
            networkTopology = networkGroupObj.NetworkTopology.add()
            networkTopologyObj = eval("networkTopology." + self.topoTypeDict[topoType] + ".add()")
        else:
            networkTopology = networkGroupObj.NetworkTopology.find()
            if eval("networkTopology." + self.topoTypeDict[topoType] + ".find()"):
                networkTopologyObj = eval("networkTopology." + self.topoTypeDict[topoType] + ".find()")
            else:
                eval("networkTopology." + self.topoTypeDict[topoType] + ".add()")
        return networkGroupObj, networkTopologyObj

    def configNetworkTopologyProperty(self, networkGroupObj, pseudoRouter, **kwargs):
        """
        Description
            Configure Network Group Topology properties.
            Supports all networkTopology.
            For networkTopologyRange attributes, use the IxNetwork API browser.

        Parameters
            networkGroupObj: <str>: Example:
                             /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}

            pseudoRouter: <str> : Example: ospfv3PseudoRouter

            data: The protocol properties.  Make your configuration and get from IxNetwork API Browser.

        Syntax
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/networkTopology/simRouter/1{id}
        """
        simRouteObj = networkGroupObj.NetworkTopology.find().SimRouter.find()
        if 'routerId' in kwargs:
            data = {'start': kwargs['routerId']['start'],
                    'step': kwargs['routerId']['step'],
                    'direction': kwargs['routerId']['direction']}
            self.configMultivalue(simRouteObj.RouterId, 'counter', data)

        pseudoRouter = pseudoRouter[0].capitalize() + pseudoRouter[1:]
        if 'routerLsaBit' in kwargs:
            self.ixnObj.logInfo('Config router lsa type')
            if kwargs['routerLsaBit'] == 'B':
                data = {'value': 'True'}
                multivalue = eval('simRouteObj.'+pseudoRouter+'.find().BBit')
                self.configMultivalue(multivalue, 'singleValue', data)

            elif kwargs['routerLsaBit'] == 'E':
                data = {'value': 'True'}
                multivalue = eval('simRouteObj.'+pseudoRouter+'.find().EBit')
                self.configMultivalue(multivalue, 'singleValue', data)

    def prefixPoolsConnector(self, prefixPoolsObj, protocolObj):
        """
        Description
           To attach prefixPoolsObj to required protocolobj stack

        :param prefixPoolsObj: Prefix Pools Object which should be connected to given protocol object
        :param protocolObj: Protocol object for which prefixpool object should be connected
        """
        connectorObj = prefixPoolsObj.Connector.add(ConnectedTo=protocolObj)

    def networkGroupWithTopologyConnector(self, networkGroupObj, protocolObj):
        """
        Description
           To attach networkgroupobj to required protocolobj stack

        :param networkGroupObj: networkgroup object with topology which should be connected to protocol object
        :param protocolObj:  protocol object for which networkgroup with topology object should be connected
        """
        connectorObj = networkGroupObj.NetworkTopology.find().SimRouter.find().Connector.find()
        connectorObj.ConnectedTo = protocolObj

    def configBgpRouteRangeProperty(self, prefixPoolsObj, protocolRouteRange, data, asPath):
        """
        Description
            Configure Network Group Prefix Pools for all Route properties.
            Supports both IPv4PrefixPools and IPv6PrefiPools.
            For protocolRouteRange attributes, use the IxNetwork API browser.

        Parameters
            prefixPoolsObj: <str>: Example:
                  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}

            protocolRouteRange: <str>: Get choices from IxNetwork API Browser.  Current choices:
                     bgpIPRouteProperty, isisL3RouteProperty, etc.

            data: The protocol properties.  Make your configuration and get from IxNetwork API Browser.

            asPath: AS path protocol properties. Make your configuration and get from IxNetwork API Browser

        Syntax
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}/protocolRouterRange/{id}
        """
        response = self.ixnObj.get(self.ixnObj.httpHeader + prefixPoolsObj + '/{0}/1'.format(protocolRouteRange))
        routeRangeObj = response.json()['links'][0]['href']
        for attribute, value in data.items():
            multivalue = response.json()[attribute]
            self.ixnObj.logInfo('Configuring PrefixPools {0} Route Property multivalue attribute: {1}'.format(protocolRouteRange, attribute))
            self.ixnObj.patch(self.ixnObj.httpHeader+multivalue+"/singleValue", data={'value': data[attribute]})

        if asPath != {}:
            response = self.ixnObj.get(self.ixnObj.httpHeader + routeRangeObj + '/{0}/1'.format('bgpAsPathSegmentList'))
            for attribute, value in asPath.items():
                multivalue = response.json()[attribute]
                self.ixnObj.logInfo('Configuring AsPath {0} Segment Property multivalue attribute: {1}'.format('bgpAsPathSegmentList', attribute))
                self.ixnObj.patch(self.ixnObj.httpHeader + multivalue + "/singleValue", data={'value': asPath[attribute]})

    def configPrefixPoolsIsisL3RouteProperty(self, prefixPoolsObj, **data):
        """
        Description
            Configure Network Group Prefix Pools ISIS L3 Route properties.
            Supports both IPv4PrefixPools and IPv6PrefiPools.
            For more property and value references, use the IxNetwork API browser.

        Parameters
            prefixPoolsObj: <str>: Example:
                  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}

            data: Properties: active, advIPv6Prefix, BAR, BFRId, BFRIdStep, BIERBitStingLength, eFlag, labelRangeSize,
                  labelStart, nFlag, pFlag, rFlag, vFlag, redistribution,  routeOrigin, subDomainId
        Syntax
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}
        """
        response = self.ixnObj.get(self.ixnObj.httpHeader + prefixPoolsObj + '/isisL3RouteProperty/1')
        for attribute, value in data.items():
            multivalue = response.json()[attribute]
            self.ixnObj.logInfo('Configuring PrefixPools ISIS L3 Route Property multivalue attribute: %s' % attribute)
            self.ixnObj.patch(self.ixnObj.httpHeader+multivalue+"/singleValue", data={'value': data[attribute]})

    def configPrefixPoolsRouteProperty(self, prefixPoolsObj, protocolRouteRange, **data):
        """
        Description
            Configure Network Group Prefix Pools for all Route properties.
            Supports both IPv4PrefixPools and IPv6PrefiPools.
            For protocolRouteRange attributes, use the IxNetwork API browser.

        Parameters
            prefixPoolsObj: <str>: Example:
                  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}

           protocolRouteRange: <str>: Get choices from IxNetwork API Browser.  Current choices:
                     bgpIPRouteProperty, isisL3RouteProperty, etc.

            data: The protocol properties.  Make your configuration and get from IxNetwork API Browser.
        Syntax
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/networkGroup/{id}/ipv4PrefixPools/{id}/protocolRouterRange/{id}
        """
        protocolRouteRange = protocolRouteRange[0:1].capitalize() + protocolRouteRange
        protocolRouteRangeObj = eval("prefixPoolsObj." + protocolRouteRange + ".find()")

        for attribute, value in data.items():
            attribute = attribute[0:1].capitalize() + attribute
            self.ixnObj.logInfo('Configuring PrefixPools {0} Route Property multivalue attribute: {1}'
                                .format(protocolRouteRange, attribute))
            try:
                multivalue = eval("protocolRouteRangeObj." + attribute)
                if type(value) == dict:
                    if 'direction' in value:
                        self.configMultivalue(multivalue, 'counter', data=value)
                else:
                    self.configMultivalue(multivalue, "singleValue", data={'value': data[attribute]})
            except:
                setattr(protocolRouteRangeObj, attribute, value)

    def configMultivalue(self, multivalueUrl, multivalueType, data):
        """
        Description
           Configure multivalues.

        Parameters
           multivalueUrl: <str>: The multivalue: /api/v1/sessions/{1}/ixnetwork/multivalue/1
           multivalueType: <str>: counter|singleValue|valueList|repeatableRandom|repeatableRandomRange|custom
           data: <dict>: singleValue: data={'value': '1.1.1.1'})
                             valueList:   data needs to be in a [list]:  data={'values': [list]}
                             counter:     data={'start': value, 'direction': increment|decrement, 'step': value}

        data examples
           if multivalueType == 'counter':
               data = {'start': '00:01:01:00:00:01', 'direction': 'increment', 'step': '00:00:00:00:00:01'}

           if multivalueType == 'singleValue': data={'value': value}

           if multivalueType == 'valueList': data={'values': ['item1', 'item2']}

        SyntaxconfigBgpRouteRangeProperty
            PATCH: /api/v1/sessions/{id}/ixnetwork/multivalue/{id}/singleValue
            PATCH: /api/v1/sessions/{id}/ixnetwork/multivalue/{id}/counter
            PATCH: /api/v1/sessions/{id}/ixnetwork/multivalue/{id}/valueList
        """
        if multivalueType.lower() == "counter":
            if data['direction'] == "increment":
                multivalueUrl.Increment(start_value=data['start'], step_value=data['step'])
            if data['direction'] == "decrement":
                multivalueUrl.Decrement(start_value=data['start'], step_value=data['step'])
        elif multivalueType.lower() == "singlevalue":
            multivalueUrl.Single(data['value'])
        elif multivalueType.lower() == "valuelist":
            multivalueUrl.ValueList(data['values'])
        elif multivalueType.lower() == "randomrange":
            multivalueUrl.RandomRange(min_value=data['min_value'], max_value=data['max_value'], step_value=data['step_value'], seed=data['seed'])
        elif multivalueType.lower() == "custom":
            multivalueUrl.Custom(start_value=data['start_value'], step_value=data['step_value'], increments=data['increments'])
        elif multivalueType.lower() == "alternate":
            multivalueUrl.Alternate(data['alternating_value'])
        elif multivalueType.lower() == "distributed":
            multivalueUrl.Distributed(algorithm=data['algorithm'], mode=data['mode'], values=data['values'])
        elif multivalueType.lower() == "randommask":
            multivalueUrl.RandomMask(fixed_value=data['fixed_value'], mask_value=data['mask_value'], seed=data['seed'], count=data['count'])
        elif multivalueType.lower() == "string":
            multivalueUrl.String(string_pattern=data['string_pattern'])

    def getMultivalueValues(self, multivalueObj, silentMode=False):
        """
        Description
           Get the multivalue values.

        Parameters
           multivalueObj: <str>: The multivalue object: /api/v1/sessions/{1}/ixnetwork/multivalue/{id}
           silentMode: <bool>: True=Display the GET and status code. False=Don't display.
        
        Syntax
            /api/v1/sessions/{id}/ixnetwork/multivalue/{id}?includes=count

        Requirements
           self.ixnObj.waitForComplete()

        Return
           The multivalue values
        """
        return multivalueObj.Values

    def verifyProtocolSessionsUp(self, protocolViewName='BGP Peer Per Port', timeout=60):
        """
        Description
            This method either verify a specified protocol sessions for UP or automatically verify for all
            the configured protocols for sessions UP.  

            This method calls verifyProtocolSessionsNgpf() if you're using IxNetwork version prior to 8.50.
            For IxNetwork versions >8.50, it calls verifyProtocolSessionsUp2() which is more robust 
            because 8.50 introduced new APIs.
        
        Parameters
            protocolViewName: <string>: The protocol to verify. You could get the exact view name in the 
                                        IxNetwork API browser.

        Some protocolViewName options:
            'ISIS-L3 RTR Per Port'
            'BGP Peer Per Port'
            'OSPFv2-RTR Per Port'
        """
        buildNumber = float(self.ixnObj.getIxNetworkVersion()[:3])
        if buildNumber >= 8.5:
            self.verifyProtocolSessionsUp2(protocolViewName, timeout)
        else:
            self.verifyAllProtocolSessionsNgpf(timeout)

    def verifyProtocolSessionsUp1(self, protocolViewName='BGP Peer Per Port', timeout=60):
        """
        Description
            Verify a specified protocol sessions for UP.
            This method is mainly for IxNetwork version prior to 8.50.  8.50+ could still use this method,
            but using verifyProtocolSessionsUp2 is more robust because 8.50 introduced new APIs.

        Parameter
            protocolViewName: The protocol view name.

        Some protocolViewName options:
            'ISIS-L3 RTR Per Port'
            'BGP Peer Per Port'
            'OSPFv2-RTR Per Port'
        """
        totalPortsUpFlag = 0
        sessionsUp = 0
        totalExpectedSessionsUp = 0
        for counter in range(1, timeout+1):
            stats = self.ixnObj.getStatsPage(viewName=protocolViewName, displayStats=False)
            totalPorts = len(stats.keys())
            self.ixnObj.logInfo('\nProtocolName: {0}'.format(protocolViewName))

            for session in stats.keys():
                sessionsUp = int(stats[session]['Sessions Up'])
                totalSessions = int(stats[session]['Sessions Total'])
                totalSessionsNotStarted = int(stats[session]['Sessions Not Started'])
                totalExpectedSessionsUp = totalSessions - totalSessionsNotStarted

                self.ixnObj.logInfo('\n\tPortName: {0}\n\t   TotalSessionsUp: {1}\n\t   ExpectedTotalSessionsup: {2}'.format(
                    stats[session]['Port'], sessionsUp, totalExpectedSessionsUp))

                if counter < timeout and sessionsUp != totalExpectedSessionsUp:
                    self.ixnObj.logInfo('\t   Session is still down')

                if counter < timeout and sessionsUp == totalExpectedSessionsUp:
                    totalPortsUpFlag += 1
                    if totalPortsUpFlag == totalPorts:
                        self.ixnObj.logInfo('\n\tAll sessions are up!')
                        return

            if counter == timeout and sessionsUp != totalExpectedSessionsUp:
                raise IxNetRestApiException('\nSessions failed to come up')

            self.ixnObj.logInfo('\n\tWait {0}/{1} seconds'.format(counter, timeout))
            print()
            time.sleep(1)

    def verifyProtocolSessionsUp2(self, protocolViewName='Protocols Summary', timeout=60):
        """
        Description
            For IxNetwork version >= 8.50.
            Defaults to Protocols Summary to verify all configured protocol sessions. There is no need
            to specify specific protocols to verify.  However, you still have the option to specific
            protocol session to verify.

            Note: This get stats by using /statistics/statview/<id>/data. Prior to 8.50, 
                  get stats uses /statistics/statview/<id>/page, which is deprecated started 8.50.
                  /statistics/statview/<id>/data is more robust.

        Parameter
            protocolViewName: <str>: The protocol view name. 
                              Get this name from API browser or in IxNetwork GUI statistic tabs.
                              Defaults to 'Protocols Summary'
        
            timeout: <int>: The timeout value to declare as failed. Default = 60 seconds.

        protocolViewName options:
            'BGP Peer Per Port'
            'DHCPV4 Client Per Port'
            'DHCPV4 Server Per Port'
            'ISIS-L3 RTR Per Port'
            'OSPFv2-RTR Per Port'
            'Protocols Summary'
        """
        label = None
        for counter in range(1, timeout+1):
            stats = self.statObj.getStatsData(viewName=protocolViewName, displayStats=False, silentMode=True)
            self.ixnObj.logInfo('\n%-16s %-14s %-16s %-23s %-22s' % ('Name', 'SessionsUp', 'SessionsDown',
                                                                     'ExpectedSessionsUp', 'SessionsNotStarted'),
                                timestamp=False)
            self.ixnObj.logInfo('-'*91, timestamp=False)
            sessionDownFlag = 0
            sessionNotStartedFlag = 0

            for session in stats.keys():
                if 'Protocol Type' in stats[session]:
                    label = stats[session]['Protocol Type']

                if 'Port' in stats[session]:
                    label = stats[session]['Port']

                sessionsDown = int(stats[session]['Sessions Down'])
                sessionsUp = int(stats[session]['Sessions Up'])
                totalSessions = int(stats[session]['Sessions Total'])
                sessionsNotStarted = int(stats[session]['Sessions Not Started'])
                expectedSessionsUp = totalSessions - sessionsNotStarted

                self.ixnObj.logInfo('%-16s %-14s %-16s %-23s %-22s' % (label, sessionsUp, sessionsDown,
                                                                       expectedSessionsUp, sessionsNotStarted),
                                    timestamp=False)

                if counter < timeout:
                    if sessionsNotStarted != 0:
                        sessionNotStartedFlag = 1

                    if sessionsDown != 0:
                        sessionDownFlag = 1

                if counter == timeout:
                    if sessionsNotStarted != 0:
                        raise IxNetRestApiException('Sessions did not start up')

                    if sessionsDown != 0:
                        raise IxNetRestApiException('Sessions failed to come up')

            if sessionNotStartedFlag == 1:
                if counter < timeout:
                    self.ixnObj.logInfo('Protocol sessions are not started yet. Waiting {0}/{1} seconds'.format(
                        counter, timeout))
                    time.sleep(1)
                    continue

                if counter == timeout:
                    raise IxNetRestApiException('Sessions are not started')

            if sessionDownFlag == 1:
                print('\nWaiting {0}/{1} seconds'.format(counter, timeout))
                time.sleep(1)
                continue

            if counter < timeout and sessionDownFlag == 0:
                print('\nProtocol sessions are all up')
                break

    def startAllOspfv2(self):
        """
        Description
            Start all OSPFv2.
        """
        queryData = {'from': '/',
                     'nodes': [{'node': 'topology',    'properties': ['name'], 'where': []},
                              {'node': 'deviceGroup', 'properties': [], 'where': []},
                              {'node': 'ethernet',    'properties': [], 'where': []},
                              {'node': 'ipv4',        'properties': [], 'where': []},
                              {'node': 'ospfv2',      'properties': [], 'where': []}]
                     }
        queryResponse = self.ixnObj.query(data=queryData)
        for topologyObj in queryResponse.json()['result'][0]['topology']:
            for deviceGroupObj in topologyObj['deviceGroup']:
                if deviceGroupObj['ethernet'][0]['ipv4'][0]['ospfv2']:
                    for ospfObj in deviceGroupObj['ethernet'][0]['ipv4'][0]['ospfv2']:
                        data = {'arg1': [ospfObj['href']]}
                        self.ixnObj.post(self.ixnObj.httpHeader+ospfObj['href']+'/operations/start', data=data)

    def startAllRsvpTeIf(self):
        """
        Description
            Start all RSVP-TE Interface.
        """
        queryData = {'from': '/',
                     'nodes': [{'node': 'topology',    'properties': ['name'], 'where': []},
                              {'node': 'deviceGroup', 'properties': [], 'where': []},
                              {'node': 'ethernet',    'properties': [], 'where': []},
                              {'node': 'ipv4',        'properties': [], 'where': []},
                              {'node': 'rsvpteIf',    'properties': [], 'where': []}]
                     }
        queryResponse = self.ixnObj.query(data=queryData)
        for topologyObj in queryResponse.json()['result'][0]['topology']:
            for deviceGroupObj in topologyObj['deviceGroup']:
                if deviceGroupObj['ethernet'][0]['ipv4'][0]['rsvpteIf']:
                    for rsvpTeIfObj in deviceGroupObj['ethernet'][0]['ipv4'][0]['rsvpteIf']:
                        data = {'arg1': [rsvpTeIfObj['href']]}
                        self.ixnObj.post(self.ixnObj.httpHeader+rsvpTeIfObj['href']+'/operations/start', data=data)

    def startAllRsvpTeLsps(self):
        """
        Description
            Start all RSVP-TE LSPS (Tunnels).
        """
        queryData = {'from': '/',
                     'nodes': [{'node': 'topology',    'properties': ['name'], 'where': []},
                              {'node': 'deviceGroup', 'properties': [], 'where': []},
                              {'node': 'ethernet',    'properties': [], 'where': []},
                              {'node': 'ipv4',        'properties': [], 'where': []},
                              {'node': 'rsvpteLsps',    'properties': [], 'where': []}]
                     }
        queryResponse = self.ixnObj.query(data=queryData)
        for topologyObj in queryResponse.json()['result'][0]['topology']:
            for deviceGroupObj in topologyObj['deviceGroup']:
                if deviceGroupObj['ethernet'][0]['ipv4'][0]['rsvpteLsps']:
                    for rsvpTeLspsObj in deviceGroupObj['ethernet'][0]['ipv4'][0]['rsvpteLsps']:
                        data = {'arg1': [rsvpTeLspsObj['href']]}
                        self.ixnObj.post(self.ixnObj.httpHeader+rsvpTeLspsObj['href']+'/operations/start', data=data)

    def verifyDeviceGroupStatus(self):
        queryData = {'from': '/',
                     'nodes': [{'node': 'topology', 'properties': [], 'where': []},
                                  {'node': 'deviceGroup', 'properties': ['href', 'enabled'], 'where': []},
                                  {'node': 'deviceGroup', 'properties': ['href', 'enabled'], 'where': []}]
                     }

        queryResponse = self.ixnObj.query(data=queryData)

        deviceGroupTimeout = 90
        for topology in queryResponse.json()['result'][0]['topology']:
            for deviceGroup in topology['deviceGroup']:
                deviceGroupObj = deviceGroup['href']
                response = self.ixnObj.get(self.ixnObj.httpHeader+deviceGroupObj, silentMode=False)
                # Verify if the Device Group is enabled. If not, don't go further.
                enabledMultivalue = response.json()['enabled']
                enabled = self.ixnObj.getMultivalueValues(enabledMultivalue, silentMode=False)
                if enabled[0] == 'true':
                    for counter in range(1,deviceGroupTimeout+1):
                        response = self.ixnObj.get(self.ixnObj.httpHeader+deviceGroupObj, silentMode=False)
                        deviceGroupStatus = response.json()['status']
                        self.ixnObj.logInfo('\t%s' % deviceGroupObj, timestamp=False)
                        self.ixnObj.logInfo('\t\tStatus: %s' % deviceGroupStatus, timestamp=False)
                        if counter < deviceGroupTimeout and deviceGroupStatus != 'started':
                            self.ixnObj.logInfo('\t\tWaiting %d/%d seconds ...' % (counter, deviceGroupTimeout), timestamp=False)
                            time.sleep(1)
                        if counter < deviceGroupTimeout and deviceGroupStatus == 'started':
                            break
                        if counter == deviceGroupTimeout and deviceGroupStatus != 'started':
                            raise IxNetRestApiException('\nDevice Group failed to start up')
                    
                    # Inner Device Group
                    if deviceGroup['deviceGroup']:
                        innerDeviceGroupObj = deviceGroup['deviceGroup'][0]['href']
                        for counter in range(1,deviceGroupTimeout):
                            response = self.ixnObj.get(self.ixnObj.httpHeader+innerDeviceGroupObj, silentMode=True)
                            innerDeviceGroupStatus = response.json()['status']
                            self.ixnObj.logInfo('\tInnerDeviceGroup: %s' % innerDeviceGroupObj, timestamp=False)
                            self.ixnObj.logInfo('\t   Status: %s' % innerDeviceGroupStatus, timestamp=False)
                            if counter < deviceGroupTimeout and innerDeviceGroupStatus != 'started':
                                self.ixnObj.logInfo('\tWait %d/%d' % (counter, deviceGroupTimeout), timestamp=False)
                                time.sleep(1)
                            if counter < deviceGroupTimeout and innerDeviceGroupStatus == 'started':
                                break
                            if counter == deviceGroupTimeout and innerDeviceGroupStatus != 'started':
                                raise IxNetRestApiException('\nInner Device Group failed to start up')
        print()

    def startAllProtocols(self):
        """
        Description
            Start all protocols in NGPF and verify all Device Groups are started.

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/operations/startallprotocols
        """
        self.ixNetwork.StartAllProtocols()

    def stopAllProtocols(self):
        """
        Description
            Stop all protocols in NGPF

        Syntax
            POST: /api/v1/sessions/{id}/ixnetwork/operations/stopallprotocols
        """
        self.stopAllProtocols()

    def startProtocol(self, protocolObj):
        """
        Description
            Start the specified protocol by its object handle.

        Parameters
            protocolObj: <str|obj>: Ex: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1
        
        Syntax
            POST: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1/operations/start
            DATA: {['arg1': [/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1']}
        """
        protocolObj.Start()

    def stopProtocol(self, protocolObj):
        """
        Description
            Stop the specified protocol by its object handle.

        Parameters
            protocolObj: <str|obj>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1

        Syntax
            POST: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1/operations/stop
            DATA: {['arg1': [/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1']}
        """
        protocolObj.Stop()

    def startTopology(self, topologyObjList='all'):
        """
        Description
            Start a Topology Group and all of its protocol stacks.

        Parameters
            topologyObjList: <str>|<list>: 'all' or a list of Topology Group href.
                             Ex: ['/api/v1/sessions/1/ixnetwork/topology/1']
        """
        if topologyObjList == 'all':
           self.ixNetwork.Topology.find().Start()
        else:
            topologyObjList.Start()
        self.verifyDeviceGroupStatus()

    def stopTopology(self, topologyObjList='all'):
        """
        Description
            Stop the running Topology and all protocol sessions.

        Parameters
            topologyObjList: <list>: A list of Topology Group href.
                             Ex: ['/api/v1/sessions/1/ixnetwork/topology/1']
        """
        if topologyObjList == 'all':
            self.ixNetwork.Topology.find().Stop()
        else:
            topologyObjList.Stop()

    def startStopDeviceGroup(self, deviceGroupObjList='all', action='start'):
        """
        Description
            Start one or more Device Groups and all its protocols.

        Parameters
            deviceGroupObj: <str>|<list>: 'all' or a list of Device Group objects.
                             Ex: ['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1']

            action: <str>: 'start'|'stop'
        """
        if deviceGroupObjList == 'all':
            if action == 'stop':
                self.ixNetwork.Topology.find.DeviceGroup.find().Stop()
            else:
                self.ixNetwork.Topology.find.DeviceGroup.find().Start()
        else:
            if action == 'stop':
                deviceGroupObjList.Stop()
            else:
                deviceGroupObjList.Start()
        time.sleep(3)

    def verifyProtocolSessionsNgpf(self, protocolObjList=None, timeout=90):
        """
        Description
            Either verify the user specified protocol list to verify for session UP or verify
            the default object's self.configuredProtocols list that accumulates the emulation protocol object
            when it was configured.
            When verifying IPv4, this API will verify ARP failures and return you a list of IP interfaces
            that failed ARP.

        Parameters
            protocolObjList: <list>: A list of protocol objects.  Default = None.  The class will automatically verify
            all of the configured protocols.
                         Ex: ['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/ospfv2/1',]

            timeout: <int>: Total wait time for all the protocols in the provided list to come up.

        Syntaxes
            GET:  http://10.219.117.103:11009/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1
            RESPONSE:  [u'notStarted', u'notStarted', u'notStarted', u'notStarted', u'notStarted', u'notStarted']
            GET:  http://10.219.117.103:11009/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
            RESPONSE:  [u'up', u'up', u'up', u'up', u'up', u'up', u'up', u'up']
            GET:  http://10.219.117.103:11009/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
            /bgpIpv4Peer/1
        """
        timerStop = timeout
        if protocolObjList is None:
            protocolObjList = self.configuredProtocols

        for eachProtocol in protocolObjList:
            # notStarted, up or down
            protocolName = eachProtocol.href.split('/')[-2]
            for timer in range(1, timerStop+1):
                sessionStatus = self.getSessionStatus(eachProtocol)
                protocolSessionStatus = eachProtocol.Status

                self.ixnObj.logInfo('\nVerifyProtocolSessions: %s\n' % eachProtocol, timestamp=False)
                self.ixnObj.logInfo('\tprotocolSessionStatus: %s' % protocolSessionStatus, timestamp=False)
                self.ixnObj.logInfo('\tsessionStatusResponse: %s' % sessionStatus, timestamp=False)
                if timer < timerStop:
                    if protocolSessionStatus != 'started':
                        self.ixnObj.logInfo('\tWait %s/%s seconds' % (timer, timerStop), timestamp=False)
                        time.sleep(1)
                        continue

                    # Started
                    if 'up' not in sessionStatus:
                        self.ixnObj.logInfo('\tProtocol session is down: Wait %s/%s seconds' % (timer, timerStop),
                                            timestamp=False)
                        time.sleep(1)
                        continue

                    if 'up' in sessionStatus:
                        self.ixnObj.logInfo('Protocol sessions are all up: {0}'.format(protocolName))
                        break

                if timer == timerStop:
                    if 'notStarted' in protocolSessionStatus:
                        raise IxNetRestApiException('\tverifyProtocolSessions: {0} session failed to start'.format(protocolName))
                        
                    if protocolSessionStatus == 'started' and 'down' in sessionStatus:
                        # Show ARP failures
                        if protocolName == 'ipv4':
                            ipInterfaceIndexList = []
                            index = 0
                            for eachSessionStatus in sessionStatus:
                                self.ixnObj.logInfo('eachSessionStatus index: {0} {1}'.format(eachSessionStatus, index),
                                                    timestamp=False)
                                if eachSessionStatus == 'down':
                                    ipInterfaceIndexList.append(index)
                                index += 1
                            ipMultivalue = eachProtocol.Address
                            ipAddressList = self.ixnObj.getMultivalueValues(ipMultivalue, silentMode=True)
                            self.ixnObj.logWarning('ARP failed on IP interface:')
                            for eachIpIndex in ipInterfaceIndexList:
                                self.ixnObj.logInfo('\t{0}'.format(ipAddressList[eachIpIndex]), timestamp=False)
                        else:
                            self.ixnObj.logWarning('\tverifyProtocolSessions: {0} session failed'.format(protocolName))

                        raise IxNetRestApiException('Verify protocol sessions failed: {0}'.format(protocolName))

    def verifyAllProtocolSessionsInternal(self, protocol, timeout=120, silentMode=True):
        """
        Description
            Verify protocol sessions for UP state.
            Initially created for verifyAllProtocolSessionsNgpf(), but this API will also work
            by passing in a protocol object.

        Parameters
           protocol: <str>: The protocol object to verify the session state.
           timeout: <int>: The timeout value for declaring as failed. Default = 120 seconds.
           silentMode: <bool>: True to not display less on the terminal.  False for debugging purpose.
        """
        sessionDownList = ['down', 'notStarted']

        protocolActiveMultivalue = protocol.Active
        response = self.getMultivalueValues(protocolActiveMultivalue)
        self.ixnObj.logInfo('\t%s' % protocol, timestamp=False)
        self.ixnObj.logInfo('\tProtocol is enabled: %s\n' % response[0], timestamp=False)
        if response[0] == 'false':
            return

        for timer in range(1, timeout+1):
            currentStatus = self.getSessionStatus(protocol)
            self.ixnObj.logInfo('\n%s' % protocol, timestamp=False)
            self.ixnObj.logInfo('\tTotal sessions: %d' % len(currentStatus), timestamp=False)
            totalDownSessions = 0
            for eachStatus in currentStatus:
                if eachStatus != 'up':
                    totalDownSessions += 1
            self.ixnObj.logInfo('\tTotal sessions Down: %d' % totalDownSessions, timestamp=False)
            self.ixnObj.logInfo('\tCurrentStatus: %s' % currentStatus, timestamp=False)

            if timer < timeout and [element for element in sessionDownList if element in currentStatus] == []:
                self.ixnObj.logInfo('Protocol sessions are all up')
                break

            if timer < timeout and [element for element in sessionDownList if element in currentStatus] != []:
                self.ixnObj.logInfo('\tWait %d/%d seconds' % (timer, timeout), timestamp=False)
                time.sleep(1)
                continue

            if timer == timeout and [element for element in sessionDownList if element in currentStatus] != []:
                raise IxNetRestApiException('\nError: Protocols failed')

    def verifyAllProtocolSessionsNgpf(self, timeout=120, silentMode=False):
        """
        Description
            Loop through each Topology Group and its enabled Device Groups and verify
            all the created and activated protocols for session up.
            Applies to Ethernet, IPv4 and IPv6.

        Parameters
           timeout: <int>: The timeout value for declaring as failed. Default = 120 seconds.
           silentMode: <bool>: True to not display less on the terminal.  False for debugging purpose.            
        """
        l2ProtocolList = ['isisL3', 'lacp', 'mpls']
        l3ProtocolList = ['ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
                          'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
                          'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
                          'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp', 'ipv6sr',
                          'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3', 'ovsdbcontroller', 'ovsdbserver',
                          'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp', 'rsvpteIf',
                          'rsvpteLsps', 'tag', 'vxlan']

        for protocol in l2ProtocolList:
            self.verifyAllProtocolSessionsInternal(protocol)

        for protocol in l3ProtocolList:
            self.verifyAllProtocolSessionsInternal(protocol)

    def getIpObjectsByTopologyObject(self, topologyObj, ipType='ipv4'):
        """
        Description
           Get all the Topology's IPv4 or IPv6 objects based on the specified topology object.

        Parameters
           ipType = ipv4 or ipv6
        """
        ipObjList = [] 
        ipObjList = topologyObj.DeviceGroup.find().Ethernet.find().Ipv4.find()
        return ipObjList

    def getAllTopologyList(self):
        """
        Description
           If Topology exists: Returns a list of created Topologies.

        Return
           If no Topology exists: Returns []
        """
        topologyList = self.ixNetwork.Topology.find()
        return topologyList

    def clearAllTopologyVports(self):
        topologyList = self.ixNetwork.Topology.find()
        for topology in topologyList:
            topology.ClearPortsAndTrafficStats()


    def modifyTopologyPortsNgpf(self, topologyObj, portList, topologyName=None):
        """
        Description
           Add/remove Topology ports.

        Parameters
           topologyObj: <str>: The Topology Group object.
           portList: <list>: A list of all the ports that you want for the Topology even if the port exists in
                             the Topology.

           topologyName: <st>: The Topology Group name to modify.
           
        Requirements:
            1> You must have already connected all the required ports for your configuration. Otherwise,
               adding additional port(s) that doesn't exists in your configuration's assigned port list
               will not work.

            2> This API requires getVports()

        Examples
           topologyObj = '/api/v1/sessions/1/ixnetwork/topology/1'

           portList format = [(str(chassisIp), str(slotNumber), str(portNumber))]
               Example 1: [ ['192.168.70.10', '1', '1'] ]
               Example 2: [ ['192.168.70.10', '1', '1'], ['192.168.70.10', '2', '1'] ]
        """
        if topologyName != None and topologyObj is None:
            topologyObj = self.ixNetwork.Topology.find(Name=topologyName)
        else:
            topologyObj.update(Ports=portList) 

    def getTopologyPorts(self, topologyObj):
        """
        Description
            Get all the configured ports in the Topology.

        Parameter
            topologyObj: <str>: /api/v1/sessions/1/ixnetwork/topology/1

        Returns
            A list of ports: [('192.168.70.10', '1', '1') ('192.168.70.10', '1', '2')]
        """
        portList = topologyObj.ports
        return portList

    def sendArpNgpf(self, ipv4ObjList):
        """
        Description
            Send ARP out of all the IPv4 objects that you provide in a list.

        ipv4ObjList: <str>:  Provide a list of one or more IPv4 object handles to send arp.
                      Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1"]
        """
        if type(ipv4ObjList) != list:
            raise IxNetRestApiException('sendArpNgpf error: The parameter ipv4ObjList must be a list of objects.')

        for ipv4Obj in ipv4ObjList:
            ipv4Obj.SendArp()

    def sendPing(self, srcIpList=None, destIp=None):
        """
        Description
            Send PING from the the list of srcIp to destIp.  This function will query for the IPv4
            object that has the srcIp address.

        Parameters
            srcIpList: <list>: The srcIp addresses in a list.  Could be 1 or more src IP addresses, but must
                       be in a list.  This API will look up the IPv4 object that has the srcIp.
            destIp: <str>: The destination IP to ping.

        Returns
            Success: 1 requests sent, 1 replies received.
            Failed: Ping: 1.1.1.1 -> 1.1.1.10 failed - timeout
            0: Returns 0 if no src IP address found in the srcIpList.
        """
        ipv4ObjSessionList = self.ixNetwork.Topology.find.DeviceGroup.find().Ethernet.find().Ipv4.find()
        ipv4ObjList = [ipv4Obj for ipv4Obj in ipv4ObjSessionList if ipv4Obj.Address.Values in srcIpList]

        if ipv4ObjList == []:
            raise IxNetRestApiException('No srcIp addresses found in configuration: {0}'.format(srcIpList))

        for ipv4Obj in ipv4ObjList:
            ipv4Obj.SendPing(destIp)

    def verifyNgpfProtocolStarted(self, protocolObj, ignoreFailure=False, timeout=30):
        """
        Description
           Verify if NGPF protocol started.

        Parameter
           protocolObj: <str>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
           timeout: <int>: The timeout value. Default=30 seconds.
        """
        for counter in range(1, timeout+1):
            # sessionStatus is a list of status for each 'session' (host)
            sessionStatus = self.getSessionStatus(protocolObj)
            self.ixnObj.logInfo('\nVerifyNgpfProtocolStarted: %s' % protocolObj, timestamp=False)

            if counter < timeout:
                count = 0
                for session in sessionStatus:
                    if session in ['notStarted', 'down']:
                        count += 1
                self.ixnObj.logInfo('\t{0} out of {1} sessions are still down'.format(count, len(sessionStatus)),
                                    timestamp=False)
                self.ixnObj.logInfo('\tWait %d/%d seconds' % (counter, timeout), timestamp=False)
                time.sleep(1)

            if counter == timeout:
                count = 0
                for session in sessionStatus:
                    if session in ['notStarted', 'down']:
                        count += 1
                
                if count != 0:
                    errMsg = '{0} out of {1} sessions failed to start'.format(count, len(sessionStatus))
                    self.ixnObj.logError(errMsg)
                    if not ignoreFailure:
                        raise IxNetRestApiException(errMsg)
                    else:
                        return 1

            if counter < timeout:
                flag = 0
                for session in sessionStatus:
                    if session in ['notStarted', 'down']:
                        flag = 1
                if flag == 0:
                    self.ixnObj.logInfo('\tTotal of {0} sessions started'.format(len(sessionStatus)), timestamp=False)
                    return 0

    def deviceGroupProtocolStackNgpf(self, deviceGroupObj, ipType, arpTimeout=3, silentMode=True):
        """
        Description
            This API is an internal API for VerifyArpNgpf.
            It's created because each deviceGroup has IPv4/IPv6 and
            a deviceGroup could have inner deviceGroup that has IPv4/IPv6.
            Therefore, you can loop device groups.

        Parameters
            deviceGroupObj: <str>: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
            ipType: <str>: ipv4|ipv6
            arpTimeout:  <int>: Timeout value. Default=60 seconds.
            silentMode: <bool>: True to show less display on the terminal. False for debugging purposes.

        Requires
            self.verifyNgpfProtocolStarted()
        """
        unresolvedArpList = []
        deviceGroupObjList = [deviceGroupObj]
        if deviceGroupObj.DeviceGroup.find():
            deviceGroupObjList.append(deviceGroupObj.DeviceGroup.find())
        for eachDeviceGroup in deviceGroupObjList:
            ethernetObjList = eachDeviceGroup.Ethernet.find()
            for ethernetObj in ethernetObjList:
                ipProtocolList = eval('ethernetObj.' + ipType + '.find()')
                if not ipProtocolList:
                    self.ixnObj.logWarning('{0} is not configured in {1}'.format(ipType, ethernetObj))
                    raise IxNetRestApiException('Layer3 is not configured in {0}'.format(ethernetObj))

                for ipProtocol in ipProtocolList:
                    match = re.match('.*(/topology.*)', ipProtocol)
                    result = self.verifyNgpfProtocolStarted(ipProtocol, ignoreFailure=True)

                    for counter in range(1, arpTimeout+1):
                        sessionStatus = self.getSessionStatus(ipProtocol)
                        if counter < arpTimeout and 'down' in sessionStatus:
                            self.ixnObj.logInfo('\tARP is not resolved yet. Wait {0}/{1}'.format(counter, arpTimeout),
                                                timestamp=False)
                            time.sleep(1)
                            continue
                        if counter < arpTimeout and 'down' not in sessionStatus:
                            break
                        if counter == arpTimeout and 'down' in sessionStatus:
                            pass

                    resolvedGatewayMac = ipProtocol.ResolvedGatewayMac
                    for index in range(0, len(resolvedGatewayMac)):
                        if bool(re.search('.*Unresolved.*', resolvedGatewayMac[index])):
                            multivalue = ipProtocol.Address
                            multivalueResponse = self.ixnObj.getMultivalueValues(multivalue, silentMode=silentMode)
                            srcIpAddrNotResolved = multivalueResponse[index]
                            gatewayMultivalue = ipProtocol.GatewayIp
                            response = self.ixnObj.getMultivalueValues(gatewayMultivalue, silentMode=silentMode)
                            gatewayIp = response[index]
                            self.ixnObj.logError('Failed to resolve ARP: srcIp:{0} gateway:{1}'.format(srcIpAddrNotResolved,
                                                                                                       gatewayIp))
                            unresolvedArpList.append((srcIpAddrNotResolved, gatewayIp))

            if not unresolvedArpList:
                self.ixnObj.logInfo('ARP is resolved')
                return 0
            else:
                return unresolvedArpList

    def verifyArp(self, ipType='ipv4', deviceGroupName=None, silentMode=True):
        """
        Description
            Verify for ARP resolvement on every enabled Device Group including inner Device Groups.
            If device group name is specified , verify ARP on specified device group
            How it works:
               Each device group has a list of $sessionStatus: up, down or notStarted.
               If the deviceGroup has sessionStatus as "up", then ARP will be verified.
               It also has a list of $resolvedGatewayMac: MacAddress or removePacket[Unresolved]
               These two $sessionStatus and $resolvedGatewayMac lists are aligned.
               If lindex 0 on $sessionSatus is up, then $resolvedGatewayMac on index 0 expects
               to have a mac address.  Not removePacket[Unresolved].
               If not, then arp is not resolved.

        Requires
           self.deviceGroupProtocolStacksNgpf() 
           self.verifyNgpfProtocolStarted()

        Parameter
            ipType: <str>: ipv4 or ipv6
            deviceGroupName: <str>: Name of the device group to send arp request
            silentMode: <bool>: True to show less display on the terminal. False for debugging purposes.
        """
        self.ixnObj.logInfo('Verify ARP: %s' % ipType)
        unresolvedArpList = []
        startFlag = 0
        deviceGroupStatus = None
        for topology in self.ixNetwork.Topology.find():
            for deviceGroup in topology.DeviceGroup.find():
                deviceName = deviceGroup.Name
                if deviceGroupName:
                    if deviceName == deviceGroupName:
                        pass
                    else:
                        continue
                enabledMultivalue = deviceGroup.Enabled
                response = self.getMultivalueValues(enabledMultivalue, silentMode=silentMode)
                if response[0] == 'false':
                    continue

                timeout = 30
                for counter in range(1, timeout+1):
                    deviceGroupStatus = deviceGroup.Status
                    if deviceGroupStatus == 'notStarted':
                        raise IxNetRestApiException('\nDevice Group is not started: {0}.'.format(deviceGroup))

                    if counter < timeout and deviceGroupStatus == 'starting':
                        self.ixnObj.logInfo('\tWait %d/%d' % (counter, timeout), timestamp=False)
                        time.sleep(1)
                        continue
                    if counter < timeout and deviceGroupStatus in ['started', 'mixed']:
                        break
                    if counter == timeout and deviceGroupStatus not in ['started', 'mixed']:
                        raise IxNetRestApiException('\nDevice Group failed to come up: {0}.'.format(deviceGroup))

                if deviceGroupStatus in ['started', 'mixed']:
                    startFlag = 1
                    arpResult = self.deviceGroupProtocolStackNgpf(deviceGroup, ipType, silentMode=silentMode)
                    if arpResult != 0:
                        unresolvedArpList = unresolvedArpList + arpResult
                    innerDeviceGroup = deviceGroup.DeviceGroup.find()
                    if innerDeviceGroup:
                        innerDeviceGroupObj = innerDeviceGroup
                        self.ixnObj.logInfo('%s' % innerDeviceGroupObj, timestamp=False)
                        deviceGroupStatus1 = innerDeviceGroupObj.Status
                        self.ixnObj.logInfo('\tdeviceGroup Status: %s' % deviceGroupStatus1, timestamp=False)

                        if deviceGroupStatus1 == 'started':
                            arpResult = self.deviceGroupProtocolStackNgpf(innerDeviceGroupObj, ipType,
                                                                          silentMode=silentMode)
                            if arpResult != 0:
                                unresolvedArpList = unresolvedArpList + arpResult

        if unresolvedArpList == [] and startFlag == 0:
            raise IxNetRestApiException("\nError: Device Group is not started. It must've went down. Can't verify arp.")

        if unresolvedArpList != [] and startFlag == 1:
            print()
            raise IxNetRestApiException('\nError: Unresolved ARP: {0}'.format(unresolvedArpList))

    def getNgpfGatewayIpMacAddress(self, gatewayIp):
        """
        Description
            Get the NGPF gateway IP Mac Address. The IPv4
            session status must be UP.

        Parameter
            gatewayIp: <str>: The gateway IP address.

        Return:
            - 0: No Gateway IP address found.
            - removePacket[Unresolved]
            - The Gateway IP's Mac Address.
        """
        ipv4Obj = None
        ipv4Obj = self.ixNetwork.Topology.find().DeviceGroup.find().Ipv4.find(gatewayip=gatewayIp)
        if ipv4Obj is not None:
            return ipv4Obj.ResolvedGatewayMac
        else:
            return None

    def getDeviceGroupSrcIpGatewayIp(self, srcIpAddress):
        """
        Description
            Search each Topology's Device Group for the provided srcIpAddress.
            If found, get the gateway IP address.

        Parameter
           srcIpAddress: <str>: The source IP address.

        Returns
            0: Failed. No srcIpAddress found in any Device Group.
            Gateway IP address
        """
        ipv4ObjSessionList = self.ixNetwork.Topology.find.DeviceGroup.find().Ethernet.find().Ipv4.find()
        ipv4Obj = [ipv4Obj for ipv4Obj in ipv4ObjSessionList if ipv4Obj.Address.Values == srcIpAddress]
        if ipv4Obj is not None:
            return ipv4Obj.gatewayip
        else:
            return None

    def getDeviceGroupObjAndIpObjBySrcIp(self, srcIpAddress):
        """
        Description
            Search each Topology/Device Group for the srcIpAddress.
            If found, return the Device Group object and the IPv4|Ipv6 objects.

            if srcIpAddress is IPv6, the format must match what is shown
            in the GUI or API server.  Please verify how the configured
            IPv6 format looks like on either the IxNetwork API server when you
            are testing your script during development.

        Parameter
           srcIpAddress: <str>: The source IP address.

        Returns
            None: If no srcIpAddress is found.
            deviceGroup Object and IPv4|IPv6 object
        """
        ipv4ObjSessionList = self.ixNetwork.Topology.find.DeviceGroup.find().Ethernet.find().Ipv4.find()
        ipv4Obj = [ipv4Obj for ipv4Obj in ipv4ObjSessionList if ipv4Obj.Address.Values == srcIpAddress]
        if ipv4Obj is not None:
            return [ipv4Obj.parent.parent, pv4Obj]
        else:
            return None
          
    def getInnerDeviceGroup(self, deviceGroupObj):
        deviceGroupList = []
        if deviceGroupObj is not None:
            while True:
                try:
                    innerDevGroupObj = deviceGroupObj.DeviceGroup.find()
                    if innerDevGroupObj != " ":
                        print("added innerdeviceGroup Obj to list value is", innerDevGroupObj)
                        deviceGroupList.append(innerDevGroupObj)
                        deviceGroupObj = innerDevGroupObj
                except:
                    break
            return deviceGroupList
    def getTopologyObjAndDeviceGroupObjByPortName(self, portName):
        """
        Description
            Search each Topology Group vport for the portName.
            If found, return the topology object and a list of 
            all its device groups and inner device group within a device group.

        Parameter
            portName: <str>: The port name that you configured for the physical port.

        Returns
            None: If no portName found in any Topology Group.

            Topology object + Device Group list
            Ex 1: ['/api/v1/sessions/1/ixnetwork/topology/2', ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1']]
            Ex 2: ('/api/v1/sessions/1/ixnetwork/topology/1', ['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1', 
                                                               '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/deviceGroup/3'])
        """
        devGrphrefList = []
        for topology in self.ixNetwork.Topology.find():
            if self.ixNetwork.Vport.find(Name=portName).href in topology.Vports:
                devGrpList = topology.DeviceGroup.find()
                break

        for devGrpObj in devGrpList:
            devGrphrefList.append(devGrpObj.href)

        return (topology.href, devGrphrefList)

    def getNetworkGroupObjByIp(self, networkGroupIpAddress):
        """
        Description
            Search each Device Group's Network Group for the networkGroupIpAddress.
            If found, return the Network Group object.
            Mainly used for Traffic Item source/destination endpoints.

            The networkGroupIpAddress cannot be a range. It has to be an actual IP address
            within the range.

        Parameter
           networkGroupIpAddress: <str>: The network group IP address.

        Returns
            None: No ipAddress found in any NetworkGroup.
            network group Object: The Network Group object.
        """
       grpObjList = None
        if '.' in networkGroupIpAddress:
            grpObjList = self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv4PrefixPools.find()
        if ':' in networkGroupIpAddress:
            grpObjList = self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv6PrefixPools.find()

        if grpObjList is not None:
            for grpObj in grpObjList:
                netAddrList = grpObj.NetworkAddress.Values
                if networkGroupIpAddress in netAddrList:
                    return grpObj.parent

        return None
              
    def getIpAddrIndexNumber(self, ipAddress):
        """
        Description
            Get the index ID of the IP address.

        Parameter
            ipAddress: <str>: The IPv4|IPv6 address to search for its index.

        Return
            None or the IP address index number (based one)
        """
        ipObjList = None
        if '.' in ipAddress:
            ipObjList = self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find()
        if ':' in ipAddress:
            ipObjList = self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find()

        if ipObjList is not None:
            for ipObj in ipObjList:
                ipAddrList = ipObj.Address.Values
                if ipAddress in ipAddrList:
                    return ipAddrList.index(ipAddress) + 1

        return None

    def getIpv4ObjByPortName(self, portName=None):
        """
        Description
            Get the IPv4 object by the port name.

        Parameter
            portName: <str>: Optional: The name of the port.  Default=None.
        """
        topologyObj = None
        for topology in self.ixNetwork.Topology.find():
            if self.ixNetwork.Vport.find(Name=portName).href in topology.Ports:
                topologyObj = topology
                break
            else:
                raise IxNetRestApiException('\nNo such vport name: %s\n' % portName)
        ipv4Obj = topologyObj.DeviceGroup.find().Ethernet.find().Ipv4.find()[0]
        if ipv4Obj:
            return ipv4Obj
        return None

    def activateIgmpHostSession(self, portName=None, ipAddress=None, activate=True):
        """
        Description
            Active or deactivate the IGMP host session ID by the portName and IPv4 host address.

        Parameters:
            portName: <str>: The name of the port in which this API will search in all the Topology Groups.
            ipAddress: <str>: Within the Topology Group, the IPv4 address for the IGMP host.
            activate: <bool>: To activate or not to activate.
        """
        ipv4AddressIndex = self.getIpAddrIndexNumber(ipAddress)
        ipv4Obj = self.getIpv4ObjByPortName(portName=portName)
        igmpHostObj = ipv4Obj.IgmpHost.find()
        if not igmpHostObj:
            raise IxNetRestApiException('\nNo IGMP HOST found\n')

        igmpHostActiveMultivalue = igmpHostObj.Active
        valueList = self.getMultivalueValues(igmpHostActiveMultivalue)
        valueList[ipv4AddressIndex-1] = activate
        self.ixnObj.configMultivalue(igmpHostActiveMultivalue, multivalueType='valueList', data={'values': valueList})

    def enableDeviceGroup(self, deviceGroupObj=None, enable=True):
        """
        Description
            Enable or disable a Device Group by the object handle.  A Device Group could contain many interfaces.
            This API will enable or disable all the interfaces.

        Parameters
            deviceGroupObj: The Device Group object handle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1

            enable: True|False
        """
        enabledMultivalue = deviceGroupObj.Enabled
        self.ixnObj.configMultivalue(enabledMultivalue, multivalueType='singleValue', data={'value': enable})

    def getRouteRangeAddressProtocolAndPort(self, routeRangeAddress):
        """
        Description
            Using the specified route range address, return the associated protocol and port.

        Parameter
            routeRangeAddress: The route range address.

        Returns
            [portList, protocolList] ->  (['192.168.70.11:2:1'], ['ospf', 'isisL3'])
        """
        protocolList = []
        portList = []
        for topology in self.ixNetwork.Topology.find():
            portList = self.ixnObj.getPhysicalPortFromVport(topology.Vports)
            for networkGroup in topology.DeviceGroup.find().NetworkGroup.find():
                for ipv4PrefixPool in networkGroup.Ipv4PrefixPools.find():
                    networkAddressList = self.ixnObj.getMultivalueValues(ipv4PrefixPool.NetworkAddress)
                    if routeRangeAddress in networkAddressList:
                        if ipv4PrefixPool.BgpIPRouteProperty.find():
                            protocolList.append('bgp')
                        if ipv4PrefixPool.OspfRouteProperty.find():
                            protocolList.append('ospf')
                        if ipv4PrefixPool.IsisL3RouteProperty.find():
                            protocolList.append('isisL3')
                        if ipv4PrefixPool.LdpFECProperty.find():
                            protocolList.append('ldp')

        return portList, protocolList

    def activateRouterIdProtocol(self, routerId, protocol=None, activate=True):
        """
        Description
            Activate the protocols based on the RouterId.
            This API will disabled all Device Groups within a Topology Group and enable only the
            Device Group that has the specified router ID in it.

        Parameter
            routerId: The router Id address to enable|disable
            activate: True|False. The protocol to activate|disactivate.
            protocol: The protocol to activate.
                      Current choices: bgpIpv4Peer, bgpIpv6Peer, igmpHost, igmpQuerier,
                                       mldHost, mldQuerier, pimV6Interface, ospfv2, ospfv3, isisL3
        """
        if type(routerId) is list:
            routerId = routerId[0]
        protocol = protocol[0:1].capitalize() + protocol[1:]
        protocolList = []
        foundRouterIdFlag = 0
        deviceGroupObj = self.getDeviceGroupByRouterId(routerId)
        routerIdMultivalue = deviceGroupObj.RouterData.find()[0].RouterId
        routerIdList = self.ixnObj.getMultivalueValues(routerIdMultivalue, silentMode=True)
        self.ixnObj.logInfo('activateRouterIdProtocols: Querying DeviceGroup for routerId %s: %s' % (routerId, protocol))
        self.ixnObj.logInfo('routerIdList: {0}'.format(routerIdList))
        if routerId in routerIdList:
            self.ixnObj.logInfo('Found routerId %s' % routerId)
            routerIdIndex = routerIdList.index(routerId)
            self.ixnObj.logInfo('routerId index: %s' % routerIdIndex)
            if protocol == 'IsisL3':
                if eval("deviceGroupObj.Ethernet.find()[0]." + protocol + ".find()"):
                    protocolList.append(eval("deviceGroupObj.Ethernet.find()[0]." + protocol + ".find()[0].Active"))

            try:
                if eval("deviceGroupObj.Ethernet.find().Ipv4.find()." + protocol + ".find()"):
                    protocolList.append(eval("deviceGroupObj.Ethernet.find().Ipv4.find()." + protocol + ".find().Active"))
                if eval("deviceGroupObj.Ethernet.find().Ipv6.find()." + protocol + ".find()"):
                    protocolList.append(eval("deviceGroupObj.Ethernet.find().Ipv6.find()." + protocol + ".find().Active"))
            except:
                pass

            for protocolActiveMultivalue in protocolList:
                try:
                    protocolActiveList = self.ixnObj.getMultivalueValues(protocolActiveMultivalue)
                    self.ixnObj.logInfo('currentValueList: %s' % protocolActiveList)
                    protocolActiveList[routerIdIndex] = str(activate).lower()
                    self.ixnObj.logInfo('updatedValueList: %s' % protocolActiveList)
                    self.ixnObj.configMultivalue(protocolActiveMultivalue, multivalueType='valueList',
                                                 data={'values': protocolActiveList})
                except:
                    pass
            return
        if foundRouterIdFlag == 0:
            raise Exception('\nNo RouterID found in any Device Group: %s' % routerId)

    def activateRouterIdRouteRanges(self, protocol=None, routeRangeAddressList=None, activate=True):
        """
        Description
            Activate the protocols based on the RouterId.

        Parameter
            protocol: The protocol to disable/enable route ranges.
                      Current choices: bgp, ospf, ldp, isis

            routeRangeAddress: A list of two lists grouped in a list:
                               For example: [[[list_of_routerID], [list_of_route_ranges]]]

            activate: True|False

        Examples:
            1> activateRouterIdRouteRanges(routeRangeAddressList=[[['all'], ['all']]], protocol='ospf', activate=True)

            2> activateRouterIdRouteRanges(routeRangeAddressList=[[['all'], ['202.13.0.0', '202.23.0.0', '203.5.0.0']]],
                                                                 protocol='isis', activate=False)

            3> activateRouterIdRouteRanges(routeRangeAddressList=[[['192.0.0.2', '192.0.0.3'], ['202.11.0.0', '202.21.0.0']],
                                                                 [['192.0.0.1'], ['all']]], protocol='ospf', activate=False)

            4> activateRouterIdRouteRanges(routeRangeAddressList=[[['192.0.0.1', '192.0.0.3'], ['202.3.0.0', '202.23.0.0']]],
                                                                 protocol='ospf', activate=False)
        """
        if protocol == 'bgp':
            protocol = 'bgpIPRouteProperty'
        if protocol == 'ospf':
            protocol = 'ospfRouteProperty'
        if protocol == 'isis':
            protocol = 'isisL3RouteProperty'
        if protocol == 'ldp':
            protocol = 'ldpFECProperty'
        protocol = protocol[0:1].capitalize() + protocol[1:]

        # 1: Get all the Device Group objects with the user specified router IDs.
        deviceGroupObjList = []
        allRouterIdList = []
        for topology in self.ixNetwork.Topology.find():
            for deviceGroup in topology.DeviceGroup.find():
                deviceGroupMultiplier = deviceGroup.Multiplier
                routerIdMultivalue = deviceGroup.RouterData.find()[0].RouterId
                routerIdList = self.getMultivalueValues(routerIdMultivalue, silentMode=True)
                deviceGroupObjList.append((deviceGroup, deviceGroupMultiplier, routerIdList))

                for rId in routerIdList:
                    if rId not in allRouterIdList:
                        allRouterIdList.append(rId)

        # 2: For each Device Group, look for the protocol to enable|disable
        #    Enable|disable based on the specified routerId list
        for deviceGroup in deviceGroupObjList:
            deviceGroupObj = deviceGroup[0]
            deviceGroupMultiplier = deviceGroup[1]
            deviceGroupRouterIdList = deviceGroup[2]

            self.ixnObj.logInfo('Searching Device Group: %s' % deviceGroupObj)
            for networkGroup in deviceGroupObj.NetworkGroup.find():
                networkGroupObj = networkGroup
                for ipv4Prefix in networkGroup.Ipv4PrefixPools.find():
                    if eval("ipv4Prefix." + protocol + ".find()"):
                        protocolObj = eval("ipv4Prefix." + protocol + ".find()")
                        ipv4PrefixPoolMultivalue = ipv4Prefix.NetworkAddress
                        ipv4PrefixPool = self.getMultivalueValues(ipv4PrefixPoolMultivalue, silentMode=True)
                        protocolMultivalue = protocolObj.Active
                        protocolActiveList = self.getMultivalueValues(protocolMultivalue, silentMode=True)
                        totalCountForEachRouterId = ipv4Prefix.Count // deviceGroupMultiplier
                        totalRouteRangeCount = ipv4Prefix.Count

                        # Create a dictionary containing routerID starting/ending indexes.
                        routerIdIndexes = {}
                        startingIndex = 0
                        endingIndex = totalCountForEachRouterId
                        for routerId in deviceGroupRouterIdList:
                            routerIdIndexes[routerId, 'startingIndex'] = {}
                            routerIdIndexes[routerId, 'endingIndex'] = {}
                            routerIdIndexes[routerId, 'startingIndex'] = startingIndex
                            routerIdIndexes[routerId, 'endingIndex'] = endingIndex
                            startingIndex += totalCountForEachRouterId
                            endingIndex += totalCountForEachRouterId

                        for key, value in routerIdIndexes.items():
                            print('', key, value)

                        self.ixnObj.logInfo('Current active list: %s' % protocolActiveList)
                        startingIndex = 0
                        endingIndex = totalCountForEachRouterId
                        for eachRouterId in deviceGroupRouterIdList:
                            print(eachRouterId)
                            for item in routeRangeAddressList:
                                currentUserDefinedRouterIdList = item[0]
                                currentUserDefinedRouteRangeList = item[1]

                                if 'all' not in currentUserDefinedRouterIdList:
                                    if eachRouterId not in currentUserDefinedRouterIdList:
                                        continue

                                if 'all' in currentUserDefinedRouteRangeList:
                                    for index in range(routerIdIndexes[eachRouterId, 'startingIndex'],
                                                       routerIdIndexes[eachRouterId, 'endingIndex']):
                                        protocolActiveList[index] = activate

                                if 'all' not in currentUserDefinedRouteRangeList:
                                    for index in range(startingIndex, totalRouteRangeCount):
                                        currentIpv4PrefixPoolsIndex = ipv4PrefixPool[index]
                                        if ipv4PrefixPool[index] in currentUserDefinedRouteRangeList:
                                            protocolActiveList[index] = activate

                                self.ixnObj.logInfo('Modifying: %s' % networkGroupObj)
                                self.ixnObj.configMultivalue(protocolMultivalue, multivalueType='valueList',
                                                             data={'values': protocolActiveList})

    def modifyProtocolRoutes(self, **kwargs):
        """
        Description

        Parameters
            protocol:
            startingAddress:
            endingAddress:

        Example:
            configNetworkGroup(deviceGroupObj2,
                               name='networkGroup2',
                               multiplier = 100,
                               networkAddress = {'start': '180.1.0.0',
                                                 'step': '0.0.0.1',
                                                 'direction': 'increment'},
                               prefixLength = 24)
        """
        response = self.ixnObj.get(self.ixnObj.sessionUrl+networkGroupPrefixPoolObj)
        print(response.json())
        prefixPoolAddressMultivalue = response.json()['networkAddress']
        print('modifyProtocolRoutes:', prefixPoolAddressMultivalue)

        prefixPoolObj = None
        if 'networkGroupObj' not in kwargs:
            networkGroupObj = deviceGroupObj.NetworkGroup.add()

        if 'networkGroupObj' in kwargs:
            networkGroupObj = kwargs['networkGroupObj']

        self.ixnObj.logInfo('configNetworkGroup: %s' % networkGroupObj)
        if 'name' in kwargs:
            networkGroupObj.Name = kwargs['name']

        if 'multiplier' in kwargs:
            networkGroupObj.Multiplier = kwargs['multiplier']

        if 'networkAddress' in kwargs:
            prefixPoolObj = networkGroupObj.Ipv4PrefixPools.add()

            if 'networkAddress' in kwargs:
                multiValue = prefixPoolObj.NetworkAddress
                self.configMultivalue(multiValue, "counter", data={'start': kwargs['networkAddress']['start'],
                                                                   'step': kwargs['networkAddress']['step'],
                                                                   'direction': kwargs['networkAddress']['direction']})
            if 'prefixLength' in kwargs:
                multiValue = prefixPoolObj.PrefixLength
                self.configMultivalue(multiValue, "singleValue", data={'value': kwargs['prefixLength']})
        return prefixPoolObj

    def applyOnTheFly(self):
        """
         Description
            Apply NGPF configuration changes on the fly while Topology protocols are running.
        """
        self.ixNetwork.Globals.Topology.ApplyOnTheFly()

    def getProtocolListByPort(self, port):
        """
        Description
            For IxNetwork Classic Framework only:
            Get all enabled protocolss by the specified port.

        Parameter
            port: (chassisIp, cardNumber, portNumber) -> ('10.10.10.1', '2', '8')
        """
        protocolList = ['bfd', 'bgp', 'cfm', 'eigrp', 'elmi', 'igmp', 'isis', 'lacp', 'ldp', 'linkOam', 'lisp',
                        'mld', 'mplsOam', 'mplsTp', 'openFlow', 'ospf', 'ospfV3', 'pimsm', 'ping', 'rip', 'ripng',
                        'rsvp', 'stp']
        self.ixnObj.logInfo('\ngetProtocolListByPort...')
        chassis = str(port[0])
        card = str(port[1])
        port = str(port[2])
        portObj = chassis + ":" + card + ":" + port
        enabledProtocolList = []
        vport = self.ixNetwork.Vport.find(AssignedTo=portObj)
        for protocol in protocolList:
            currentProtocol = protocol[0].capitalize() + protocol[1:]
            if eval("vport.Protocols.find()." + currentProtocol) and eval("vport.Protocols.find()." + currentProtocol +
                                                                          ".Enabled"):
                enabledProtocolList.append(str(protocol))

        return enabledProtocolList

    def getProtocolListByPortNgpf(self, port=None, portName=None):
        """
        Description
            Based on either the vport name or the physical port, get the Topology
            Group object and all the protocols in each Device Group within the same 
            Topology Group.

        Parameter
            port: [chassisIp, cardNumber, portNumber]
                  Example: ['10.10.10.1', '2', '8']

            portName: <str>: The virtual port name.

        Example usage:
            protocolObj = Protocol(mainObj)
            protocolList = protocolObj.getProtocolListByPortNgpf(port=['192.168.70.120', '1', '2'])

            Subsequently, you could call getProtocolObjFromProtocolList to get any protocol object handle:
            obj = protocolObj.getProtocolObjFromProtocolList(protocolList['deviceGroup'], 'bgpIpv4Peer')
        
        Returns
            {'topology':    '/api/v1/sessions/1/ixnetwork/topology/2',
             'deviceGroup': [['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2/ethernet/1',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2/ethernet/1/ipv4/1',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2/ethernet/1/ipv4/1/bgpIpv4Peer'],

                             ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/3',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/3/ethernet/1',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/3/ethernet/1/ipv4/1',
                              '/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/3/ethernet/1/ipv4/1/ospfv2']
                            ]}
        """
        l3ProtocolList = ['ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
                          'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
                          'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
                          'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp', 'ipv6sr',
                          'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3', 'ovsdbcontroller', 'ovsdbserver',
                          'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp', 'rsvpteIf',
                          'rsvpteLsps', 'tag', 'vxlan']
        
        outputDict = {'topology':"", 'deviceGroup':[]}

        if port != None and portName == None:
            portName = str(port[1]) + '/' + str(port[2])
        
        for topology in self.ixNetwork.Topology.find():
            if self.ixNetwork.Vport.find(Name=portName).href in topology.Vports:
                devGrpList = topology.DeviceGroup.find()
                outputDict['topology']=topology.href
                break
        
        for devGrpObj in devGrpList:
            outPutList = []
            for currentProtocol in l3ProtocolList:
                currentProtocol = currentProtocol[0].capitalize()+currentProtocol[1:]
                try:
                    if eval('devGrpObj.Ethernet.find()'):
                        outPutList.append(eval('devGrpObj.Ethernet.find()').href)
                    if eval('devGrpObj.Ethernet.find().Ipv4.find()'):
                        outPutList.append(eval('devGrpObj.Ethernet.find().Ipv4.find().'+ currentProtocol +'.find()').href)
                        if eval('devGrpObj.Ethernet.find().Ipv4.find().'+ currentProtocol +'.find()'):
                            outPutList.append(eval('devGrpObj.Ethernet.find().Ipv4.find()').href)
                    if eval('devGrpObj.Ethernet.find().Ipv6.find()'):
                        outPutList.append(eval('devGrpObj.Ethernet.find().Ipv6.find()').href)
                        if eval('devGrpObj.Ethernet.find().Ipv6.find().'+ currentProtocol +'.find()'):
                            outPutList.append(eval('devGrpObj.Ethernet.find().Ipv6.find().'+ currentProtocol +'.find()').href)
                except:
                    pass
            if outPutList != []:
                outputDict['deviceGroup'].append(outPutList)
        return outputDict

    def getProtocolListByHostIpNgpf(self, hostIp):
        """
        Description
            Based on the host IP address, will return all the Topology/DeviceGroup and all
            it's protocols within the DeviceGroup.

        Parameter
            hostIp: <str>: The host IP address to search in all the topologies.

        Example usage:
            protocolObj = Protocol(mainObj)
            objectList = protocolObj.getProtocolListByHostIpNgpf('1.1.1.1')

            Subsequently, you could call getProtocolObjFromProtocolList to get any protocol object handle:
            obj = protocolObj.getProtocolObjFromProtocolList(protocolList['deviceGroup'], 'bgpIpv4Peer')
        
        Returns
           # This return example shows that the hostIp was found in one topology group and the hostIP
           # was found in two of the device groups within this topology group.

           [{'topology': '/api/v1/sessions/1/ixnetwork/topology/1',
             'deviceGroup': [['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1'],

                             ['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2/ethernet/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2/ethernet/1/ipv4/1',
                              '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2/ethernet/1/ipv4/1/ospfv2/1']
                            ]
            }]
        """
        container = []
        l3ProtocolList = ['ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent',
                          'dhcpv6relayAgent', 'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier', 'lac',
                          'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
                          'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp', 'ipv6sr',
                          'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3', 'ovsdbcontroller', 'ovsdbserver',
                          'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp', 'rsvpteIf',
                          'rsvpteLsps', 'tag', 'vxlan'
                          ]

        topologyList = self.ixNetwork.Topology.find()
        for topology in topologyList:
            topologyObj = topology
            deviceGroupList = topologyObj.DeviceGroup.find()
            topologyDict = {}
            topology = []
            deviceGroupObjects = []

            for deviceGroup in deviceGroupList:
                deviceGroupObj = deviceGroup
                ethernetList = deviceGroup.Ethernet.find()
                isHostIpFound = False
                for ethernet in ethernetList:
                    ipList = []
                    ethernetObj = ethernet

                    # IPv4
                    if '.' in hostIp:
                        ipList = ethernet.Ipv4.find()

                    if ':' in hostIp:
                        ipList = ethernet.Ipv6.find()

                    if ipList:
                        for ipObj in ipList:
                            multivalue = ipObj.Address
                            ipHostList = self.getMultivalueValues(multivalue)

                            if hostIp in ipHostList:
                                if 'topology' not in topologyDict:
                                    topologyDict = {'topology': topologyObj.href, 'deviceGroup': []}

                                deviceGroupObjects.append(deviceGroupObj.href)
                                deviceGroupObjects.append(ethernetObj.href)
                                deviceGroupObjects.append(ipObj.href)
                                isHostIpFound = True

                        if not isHostIpFound:
                            continue

                        for layer3Ip in ipList:
                            for currentProtocol in l3ProtocolList:
                                currentProtocol = currentProtocol[0].capitalize() + currentProtocol[1:]
                                try:
                                    if eval('layer3Ip.' + currentProtocol + '.find()'):
                                        deviceGroupObjects.append(eval('layer3Ip.' + currentProtocol + '.find()').href)
                                except:
                                    pass

                # Done with the current Device Group. Reset deviceGroupObjects for the next DG.
                if isHostIpFound:
                    topologyDict['deviceGroup'].insert(len(topologyDict['deviceGroup']), deviceGroupObjects)
                    deviceGroupObjects = []

            # 'deviceGroup' exists if the ipHost is found.
            # If exists, append it to the current Topology.
            if 'deviceGroup' in topologyDict:
                container.append(topologyDict)

        return container

    def getEndpointObjByDeviceGroupName(self, deviceGroupName, endpointObj):
        """
        Description
            Based on the Device Group name, return the specified endpointObj object handle.
            The endpointObj is the NGPF endpoint: topology, deviceGroup, networkGroup, ethernet, ipv4|ipv6,
            bgpIpv4Peer, ospfv2, igmpHost, etc.  The exact endpoint name could be found in the
            IxNetwork API Browser.

        Parameter
            deviceGroupName: <str>: The Device Group name.
            endpointObj: <str>: The NGPF endpoint object handle to get.
            
        Example usage:
            # This example shows how to get the bgp object handle from the Device Group named DG-2.

            protocolObj = Protocol(mainObj)
            obj = protocolObj.getEndpointObjByDeviceGroupName('DG-2', 'bgpIpv4Peer')
            returns: ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer']

            obj = protocolObj.getEndpointObjByDeviceGroupName('DG-2', 'topology')
            returns: ['/api/v1/sessions/1/ixnetwork/topology/2']

        Returns
           []|The NGPF endpoint object handle(s) in a list.
        """
        devGrpObj = self.ixNetwork.Topology.find().DeviceGroup.find(Name=deviceGroupName)
        try:
            if eval('devGrpObj.Ethernet.find().Ipv4.find().'+ endpointObj +'.find()'):
                obj = eval('devGrpObj.Ethernet.find().Ipv4.find().'+ endpointObj +'.find()')
                print("returning obj", obj)
                return obj
        except:
            return []

    def getProtocolObjFromProtocolList(self, protocolList, protocol, deviceGroupName=None):
        """
        Description
           This is an internal API used after calling self.getProtocolListByPortNgpf().
           self.getProtocolListByPortNgpf() returns a dict containing a key called deviceGroup
           that contains all the device group protocols in a list.

           Use this API to get the protocol object handle by passing in the deviceGroup list and
           specify the NGPF protocol endpoint name.

        Parameters
           protocolList: <list>:
           protocol: <str>: The NGPF endpoint protocol name. View below:
           deviceGroupName: <str>: If there are multiple Device Groups within the Topology, filter
                            the Device Group by its name.

         NGPF endpoint protocol names:
            'ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
            'dhcpv4server', 'dhcpv6server', 'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
            'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
            'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp',
            'ipv6sr', 'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3',  'ovsdbcontroller',
            'ovsdbserver', 'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp',
            'rsvpteIf', 'rsvpteLsps', 'tag', 'vxlan'

        Example usage:
            protocolObj = Protocol(mainObj)
            protocolList = protocolObj.getProtocolListByPortNgpf(port=['192.168.70.120', '1', '2'])
            obj = protocolObj.getProtocolObjFromProtocolList(protocolList['deviceGroup'], 'bgpIpv4Peer')

            If you expect multiple Device Groups in your Topology, you could filter by the Device Group name:
            obj = protocolObj.getProtocolObjFromProtocolList(protocolList['deviceGroup'], 'ethernet', deviceGroupName='DG2')

        Returns
            The protocol object handle in a list. For example:
            ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2/ethernet/1/ipv4/1/bgpIpv4Peer']
        """
        protoReturnList = []
        if deviceGroupName is None:
            vportList = self.ixNetwork.Vport.find()
            
            for vportObj in vportList:
                protocolList = self.getProtocolListByPortNgpf(portName=vportObj.Name)
                protoList = protocolList['deviceGroup'][0]
                for protoHref in protoList:
                    if protocol in protoHref:
                        print("comparing " + protocol + "with" + protoHref)
                        return protoHref
        else:
            if eval('self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv4.find().'+ protocol +'.find()'):
                protoObj = 'self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv4.find().'+ protocol +'.find()'
                protoReturnList.append(protoObj)
            if eval('self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv6.find().'+ protocol +'.find()'):
                protoObj = 'self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv6.find().'+ protocol +'.find()'
                protoReturnList.append(protoObj)
            if eval('self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().'+ protocol +'.find()'):
                protoObj = 'self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().'+ protocol +'.find()'
                protoReturnList.append(protoObj)

            return protoReturnList

    def getProtocolObjFromHostIp(self, topologyList, protocol):
        """
        Description
           This is an internal API used after calling self.getProtocolListByHostIpNgpf().
           self.getProtocolListByHostIpNgpf() returns a list of Dicts containing all the topologies
           and its device group(s) that has a hostIp configured.
        
           Use this API to get the protocol object handle by passing in the NGPF endpoint protocol name.

        Parameters
           topologyList: <list>:  A returned list of Dicts from self.getProtocolListByHostIpNgpf(.
           protocol: <str>: The NGPF endpoint protocol name. View below:
        
         protocol (These are the NGPF endpoint objects):
            'ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
            'dhcpv4server', 'dhcpv6server', 'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
            'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
            'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp',
            'ipv6sr', 'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3',  'ovsdbcontroller',
            'ovsdbserver', 'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp',
            'rsvpteIf', 'rsvpteLsps', 'tag', 'vxlan'

        Example usage:
            protocolObj = Protocol(mainObj)
            x = protocolObj.getProtocolListByHostIpNgpf('1.1.1.1')
            objHandle = protocolObj.getProtocolObjFromHostIp(x, protocol='bgpIpv4Peer')

        Returns
            This API returns a list of object handle(s).

            Example 1:
            The protocol object handle in a list. For example:
               ['/api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/2/ethernet/1/ipv4/1/bgpIpv4Peer']

            Example 2:
                If there are multiple device groups and you want to get all the IPv4 endpoints that has the hostIp,
                this API will return you a list:
                   ['/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1',
                    '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/2/ethernet/1/ipv4/1']   
        """
        objectHandle = []
        for element in topologyList:
            if protocol == 'topology':
                objectHandle.append(element['topology'])
                return objectHandle

            for eachDeviceGroup in element['deviceGroup']:
                # Example: deviceGroupEndpoint are:
                #    /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
                #    /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1
                #    /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1
                #    /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1
                #    /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/2/ldpv6ConnectedInterface/1
                for deviceGroupEndpoint in eachDeviceGroup:
                    if protocol in ['deviceGroup', 'networkGroup', 'ethernet', 'ipv4', 'ipv6']:
                        match = re.search(r'(/api/v1/sessions/[0-9]+/ixnetwork/topology/[0-9]+.*%s/[0-9]+)$' % protocol,
                                          deviceGroupEndpoint.href)
                        if match:
                            objectHandle.append(deviceGroupEndpoint)
                    else:
                        if protocol in deviceGroupEndpoint:
                            objectHandle.append(deviceGroupEndpoint)

        if objectHandle:
            # self.ixnObj.logInfo('\nObject handles: {0}'.format(str(objectHandle)), timestamp=False)
            return objectHandle

    def getPortsByProtocolNgpf(self, ngpfEndpointName):
        """
        Description
            For IxNetwork NGPF only:
            Based on the specified NGPF endpoint name, return all ports associated with the protocol.

        Parameter
            ngpfEndpointName: <str>: See below for all the NGPF endpoint protocol names.

         Returns
            [chassisIp, cardNumber, portNumber]
            Example: [['10.219.117.101', '1', '1'], ['10.219.117.101', '1', '2']]

            Returns [] if no port is configured with the specified ngpfEndpointName

         ngpfEndpointName options:
            'ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
            'dhcpv4server', 'dhcpv6server', 'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
            'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
            'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp',
            'ipv6sr', 'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3',  'ovsdbcontroller',
            'ovsdbserver', 'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp',
            'rsvpteIf', 'rsvpteLsps', 'tag', 'vxlan'
        """
        portList = []
        topologyList = self.ixNetwork.Topology.find()
        for topology in topologyList:
            deviceGroupList = topology.DeviceGroup.find()
            for deviceGroup in deviceGroupList:
                ethernetList = deviceGroup.Ethernet.find()
                for ethernet in ethernetList:
                    ipv4List = ethernet.Ipv4.find()
                    ipv6List = ethernet.Ipv6.find()
                    for layer3Ip in ipv4List+ipv6List:
                        ngpfEndpointName = ngpfEndpointName[0:1].capitalize() + ngpfEndpointName[1:]
                        ngpfEndpointObj = eval("layer3Ip." + ngpfEndpointName + ".find()")
                        if not ngpfEndpointObj:
                            continue
                        vportList = topology.Vports
                        vports = self.ixNetwork.Vport.find()
                        for vport in vports:
                            if vport.href == vportList[0]:
                                assignedTo = vport.AssignedTo
                                currentChassisIp = assignedTo.split(':')[0]
                                currentCardNumber = assignedTo.split(':')[1]
                                currentPortNumber = assignedTo.split(':')[2]
                                currentPort = [currentChassisIp, currentCardNumber, currentPortNumber]
                                portList.append(currentPort)
                                self.ixnObj.logInfo('\tFound port configured: %s' % currentPort)
        return portList

    def flapBgp(self, topologyName=None, bgpName=None, enable=True, ipInterfaceList='all', upTimeInSeconds=0,
                downTimeInSeconds=0):
        """
        Description
           Enable/Disable BGP flapping.

        Parameters
           topologyName: <str>: Mandatory: The Topolgy Group name where the BGP stack resides in.
           bgpName: <str>: Mandatory. The name of the BGP stack.
           enable: <bool>: To enable or disable BGP flapping.
           ipInterfaceList: <list>: A list of the local BGP IP interface to configure for flapping.
           upTimeInSeconds: <int>: The up time for BGP to remain up before flapping it down.
           downTimeInSeconds: <int>: The down time for BGP to remain down before flapping it back up.
        """
        bgpObject = None

        topologyObj = self.ixNetwork.Topology.find(Name=topologyName)

        if topologyObj is None:
            raise IxNetRestApiException('\nNo such Topology Group name found %s' % topologyName)
            
        try:
            bgpIpv4PeerObj = topologyObj.DeviceGroup.find().Ethernet.find().Ipv4.find().BgpIpv4Peer.find()
            if bgpName == bgpIpv4PeerObj.Name:
                bgpObject = bgpIpv4PeerObj
        except:
            bgpIpv6PeerObj = topologyObj.DeviceGroup.find().Ethernet.find().Ipv4.find().BgpIpv6Peer.find()
            if bgpName == bgpIpv6PeerObj.Name:
                bgpObject = bgpIpv6PeerObj
        
        if bgpObject is None:
            raise IxNetRestApiException('\nNo such bgp name found %s' % bgpName)
        
        self.flapBgpPeerNgpf(bgpObjHandle=bgpObject, enable=enable, flapList=ipInterfaceList,
                             uptime=upTimeInSeconds, downtime=downTimeInSeconds)

    def flapBgpPeerNgpf(self, bgpObjHandle, enable=True, flapList='all', uptime=0, downtime=0):
        """
        Description
           Enable or disable BGP flapping on either all or a list of IP interfaces.

        Parameters
            bgpObjHandle: The bgp object handle.
                         /api/v1/sessions/<int>/ixnetwork/topology/<int>/deviceGroup/<int>/ethernet/<int>/ipv4/<int>/bgpIpv4Peer/<int>
            enable: <bool>: Default = True
            flapList: 'all' or a list of IP addresses to enable/disable flapping.
                      [['10.10.10.1', '10.10.10.8', ...]
                      Default = 'all'
            uptime: <int>: In seconds. Defaults = 0
            downtime: <int>: In seconds. Defaults = 0

        Syntax
           POST = /api/v1/sessions/<int>/ixnetwork/topology/<int>/deviceGroup/<int>/ethernet/<int>/ipv4/<int>/
           bgpIpv4Peer/<int>
        """
        if flapList != 'all' and type(flapList) != list:
            flapList = flapList.split(' ')
        # Get the IP object from the bgpObjHandle
        match = re.match('(/api.*)/bgp', bgpObjHandle.href)
        ipObj = match.group(1)
        for eachIpObj in self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find():
            if eachIpObj.href == ipObj:
                ipObj = eachIpObj
        ipAddressList = self.getIpAddresses(ipObj)
        count = len(ipAddressList)

        # Recreate an index list based on user defined ip address to enable/disable
        indexToFlapList = []
        if flapList != 'all':
            for ipAddress in flapList:
                # A custom list of indexes to enable/disable flapping based on the IP address index number.
                indexToFlapList.append(ipAddressList.index(ipAddress))

        # Copy the same index list for uptime and downtime
        enableFlappingMultivalue = bgpObjHandle.Flap
        upTimeMultivalue = bgpObjHandle.UptimeInSec
        downTimeMultivalue = bgpObjHandle.DowntimeInSec

        flappingResponse = self.getMultivalueValues(enableFlappingMultivalue)
        uptimeResponse = self.getMultivalueValues(upTimeMultivalue)
        downtimeResponse = self.getMultivalueValues(downTimeMultivalue)

        # Flapping IP addresses
        flapOverlayList = []
        uptimeOverlayList = []
        downtimeOverlayList = []
        # Build a valueList of either "true" or "false"
        if flapList == 'all':
            for counter in range(0, count):
                if enable:
                    flapOverlayList.append("true")
                if not enable:
                    flapOverlayList.append("false")
                uptimeOverlayList.append(str(uptime))
                downtimeOverlayList.append(str(downtime))

        if flapList != 'all':
            # ['true', 'true', 'true']
            currentFlappingValueList = flappingResponse
            # ['10', '10', '10']
            currentUptimeValueList = uptimeResponse
            # ['20', '20', '20']
            currentDowntimeValueList = downtimeResponse

            indexCounter = 0
            for (eachFlapValue, eachUptimeValue, eachDowntimeValue) in zip(currentFlappingValueList,
                                                                           currentUptimeValueList,
                                                                           currentDowntimeValueList):
                if indexCounter not in indexToFlapList:
                    flapOverlayList.append(eachFlapValue)
                    uptimeOverlayList.append(eachUptimeValue)
                    downtimeOverlayList.append(eachDowntimeValue)
                else:
                    # Change the value on this index position.
                    if enable:
                        flapOverlayList.append("true")
                    else:
                        flapOverlayList.append("false")

                    uptimeOverlayList.append(str(uptime))
                    downtimeOverlayList.append(str(downtime))
                indexCounter += 1
        self.configMultivalue(enableFlappingMultivalue, 'valueList', data={'values': flapOverlayList})
        self.configMultivalue(upTimeMultivalue, 'valueList', data={'values': uptimeOverlayList})
        self.configMultivalue(downTimeMultivalue, 'valueList', data={'values': downtimeOverlayList})

    def flapBgpRoutesNgpf(self, prefixPoolObj, enable=True, ipRouteListToFlap='all', uptime=0, downtime=0, ip='ipv4'):
        """
        Description
           This API will enable or disable flapping on either all or a list of BGP IP routes.
           If you are configuring routes to enable, you could also set the uptime and downtime in seconds.

        Parameters
            prefixPoolObj = The Network Group PrefixPool object that was returned by configNetworkGroup()
                            /api/v1/sessions/<int>/ixnetwork/topology/<int>/deviceGroup/<int>/networkGroup/<int>/ipv4PrefixPools/<int>
            enable: True or False
                - Default = True
            ipRouteListToFlap: 'all' or a list of IP route addresses to enable/disable.
                                 [['160.1.0.1', '160.1.0.2',...]
                - Default = 'all'
            upTime: In seconds.
                - Defaults = 0
            downTime: In seconds.
                - Defaults = 0
            ip: ipv4 or ipv6
                - Defaults = ipv4

        Syntax
           POST = For IPv4: http://{apiServerIp:port}/api/v1/sessions/<int>/ixnetwork/topology/<int>/deviceGroup/<int>/
           networkGroup/<int>/ipv4PrefixPools/<int>/bgpIPRouteProperty

                  For IPv6: http://{apiServerIp:port}/api/v1/sessions/<int>/ixnetwork/topology/<int>/deviceGroup/<int>/
                  networkGroup/<int>/ipv4PrefixPools/<int>/bgpV6IPRouteProperty
        """
        routePropertyObj = None
        if ipRouteListToFlap != 'all' and type(ipRouteListToFlap) != list:
            ipRouteListToFlap = ipRouteListToFlap.split(' ')

        # Get a list of configured IP route addresses
        networkAddressList = prefixPoolObj.LastNetworkAddress
        count = len(networkAddressList)

        # Recreate an index list based on user defined ip route to enable/disable
        indexToFlapList = []
        if ipRouteListToFlap != 'all':
            for ipRouteAddress in ipRouteListToFlap:
                # A custom list of indexes to enable/disable flapping based on the IP address index number.
                indexToFlapList.append(networkAddressList.index(ipRouteAddress))

        if ip == 'ipv4':
            routePropertyObj = prefixPoolObj.BgpIPRouteProperty.find()
        if ip == 'ipv6':
            routePropertyObj = prefixPoolObj.BgpV6IPRouteProperty.find()

        enableFlappingMultivalue = routePropertyObj.EnableFlapping
        upTimeMultivalue = routePropertyObj.Uptime
        downTimeMultivalue = routePropertyObj.Downtime
        flappingResponse = self.ixnObj.getMultivalueValues(enableFlappingMultivalue)
        uptimeResponse = self.ixnObj.getMultivalueValues(upTimeMultivalue)
        downtimeResponse = self.ixnObj.getMultivalueValues(downTimeMultivalue)

        # Flapping IP addresses
        flapOverlayList = []
        uptimeOverlayList = []
        downtimeOverlayList = []
        # Build a valueList of either "true" or "false"
        if ipRouteListToFlap == 'all':
            for counter in range(0,count):
                if enable:
                    flapOverlayList.append("true")
                if not enable:
                    flapOverlayList.append("false")
                uptimeOverlayList.append(str(uptime))
                downtimeOverlayList.append(str(downtime))

        if ipRouteListToFlap != 'all':
            currentFlappingValueList = flappingResponse[0]
            currentUptimeValueList = uptimeResponse[0]
            currentDowntimeValueList = downtimeResponse[0]

            indexCounter = 0
            for (eachFlapValue, eachUptimeValue, eachDowntimeValue) in zip(currentFlappingValueList,
                                                                           currentUptimeValueList,
                                                                           currentDowntimeValueList):
                # Leave the setting alone on this index position. User did not care to change this value.
                if indexCounter not in indexToFlapList:
                    flapOverlayList.append(eachFlapValue)
                    uptimeOverlayList.append(eachUptimeValue)
                    downtimeOverlayList.append(eachDowntimeValue)
                else:
                    # Change the value on this index position.
                    if enable:
                        flapOverlayList.append("true")
                    else:
                        flapOverlayList.append("false")
                    uptimeOverlayList.append(str(uptime))
                    downtimeOverlayList.append(str(downtime))
                indexCounter += 1
        self.configMultivalue(enableFlappingMultivalue, 'valueList', data={'values': flapOverlayList})
        self.configMultivalue(upTimeMultivalue, 'valueList', data={'values': uptimeOverlayList})
        self.configMultivalue(downTimeMultivalue, 'valueList', data={'values': downtimeOverlayList})

    def enableProtocolRouteRange(self, routerId, protocol, enable=False):
        """
        Description
            Enable or disable route range for protocols: ospf, bgp, isis, etc.

        Parameters
            routerId: all|List of routerId
            enable: True|False
        """
        topologyObj = None
        vport = None
        deviceGroupObj = self.getDeviceGroupByRouterId(routerId)
        for topology in self.ixNetwork.Topology.find():
            for deviceGroup in topology.DeviceGroup.find():
                if deviceGroup.href == deviceGroupObj.href:
                    topologyObj = topology
                    break
        for eachVport in self.ixNetwork.Vport.find():
            if eachVport.href in topologyObj.Ports:
                vport = eachVport
                break

        RouterInstanceList = self.classicProtocolObj.getRouterInstanceByPortAndProtocol(protocol=protocol, vport=vport)
        if not RouterInstanceList:
            raise IxNetRestApiException('No Router instance exists in protocol {0}'.format(protocol))
        routerDataObj = deviceGroupObj.RouterData.find()
        routerIdMultivalue = routerDataObj.RouterId
        routerIdList = self.ixnObj.getMultivalueValues(routerIdMultivalue)
        for eachRouterInstance in RouterInstanceList:
            RouteRangeInstanceList = eachRouterInstance.RouteRange.find()
            for eachRouteRange in RouteRangeInstanceList:
                eachRouteRange.Enabled = enable
        print(routerIdList)
        print(deviceGroupObj)

    def startStopIpv4Ngpf(self, ipv4ObjList, action='start'):
        """
        Description
           Start or stop IPv4 header.

        Parameters
            ipv4ObjList: Provide a list of one or more IPv4 object handles to start or stop.
                 Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1", ...]

            action: start or stop
        """
        if type(ipv4ObjList) != list:
            raise IxNetRestApiException('startStopIpv4Ngpf error: The parameter ipv4ObjList must be a list of objects.')
        self.ixnObj.logInfo('startStopIpv4Ngpf: {0}'.format(action))
        for eachIpv4Obj in ipv4ObjList:
            if action == 'start':
                eachIpv4Obj.Start()
            if action == 'stop':
                eachIpv4Obj.Stop()

    def startStopBgpNgpf(self, bgpObjList, action='start'):
        """
        Description
            Start or stop BGP protocol

        Parameters
            bgpObjList: Provide a list of one or more BGP object handles to start or stop.
                 Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1", ...]

            action: start or stop
        """
        if type(bgpObjList) != list:
            raise IxNetRestApiException('startStopBgpNgpf error: The parameter bgpObjList must be a list of objects.')
        self.ixnObj.logInfo('startStopBgpNgpf: {0}'.format(action))
        for eachBgpObj in bgpObjList:
            if action == 'start':
                eachBgpObj.Start()
            if action == 'stop':
                eachBgpObj.Stop()

    def startStopOspfNgpf(self, ospfObjList, action='start'):
        """
        Description
            Start or stop OSPF protocol

        Parameters
            bgpObjList: Provide a list of one or more OSPF object handles to start or stop.
                 Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/ospfv2/1", ...]

            action: start or stop
        """
        if type(ospfObjList) != list:
            raise IxNetRestApiException('startStopOspfNgpf error: The parameter ospfObjList must be a list of objects.')
        self.ixnObj.logInfo('startStopOspfNgpf: {0}'.format(action))
        for eachOspfObj in ospfObjList:
            if action == 'start':
                eachOspfObj.Start()
            if action == 'stop':
                eachOspfObj.Stop()

    def startStopIgmpHostNgpf(self, igmpHostObjList, action='start'):
        """
        Description
            Start or stop IGMP Host protocol

        Parameters
            igmpHostObjList: Provide a list of one or more IGMP host object handles to start or stop.
                 Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/igmpHost/1", ...]

        action: start or stop
        """
        if type(igmpHostObjList) != list:
            raise IxNetRestApiException('igmpHostObjNgpf error: The parameter igmpHostObjList must be a '
                                        'list of objects.')
        self.ixnObj.logInfo('startStopIgmpHostNgpf: {0}'.format(action))
        for eachIgmpHostObj in igmpHostObjList:
            if action == 'start':
                eachIgmpHostObj.Start()
            if action == 'stop':
                eachIgmpHostObj.Stop()

    def startStopPimV4InterfaceNgpf(self, pimV4ObjList, action='start'):
        """
        Description
            Start or stop PIM IPv4 interface.

        Parameters
            pimV4ObjList: Provide a list of one or more PIMv4 object handles to start or stop.
                       Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/pimV4Interface/1", ...]

            action: start or stop
        """
        if type(pimV4ObjList) != list:
            raise IxNetRestApiException('startStopPimV4InterfaceNgpf error: The parameter pimv4ObjList must be a '
                                        'list of objects.')
        self.ixnObj.logInfo('startStopPimV4InterfaceNgpf: {0}'.format(action))
        self.ixnObj.logInfo('\t%s' % pimV4ObjList)
        for eachPimV4Obj in pimV4ObjList:
            if action == 'start':
                eachPimV4Obj.Start()
            if action == 'stop':
                eachPimV4Obj.Stop()

    def startStopMldHostNgpf(self, mldHostObjList, action='start'):
        """
        Description
            Start or stop MLD Host.  For IPv6 only.

        Parameters
            mldHostObjList: Provide a list of one or more mldHost object handles to start or stop.
                         Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/2/mldHost/1", ...]

            action: start or stop
        """
        if type(mldHostObjList) != list:
            raise IxNetRestApiException('startStopMldHostNgpf error: The parameter mldHostObjList must be a '
                                        'list of objects.')
        self.ixnObj.logInfo('startStopMldHostNgpf: {0}'.format(action))
        self.ixnObj.logInfo('\t%s' % mldHostObjList)
        for eachMldHostObj in mldHostObjList:
            if action == 'start':
                eachMldHostObj.Start()
            if action == 'stop':
                eachMldHostObj.Stop()

    def startStopIsisL3Ngpf(self, isisObjList, action='start'):
        """
        Description
            Start or stop ISIS protocol.

        Parameters
            isisObjList: Provide a list of one or more mldHost object handles to start or stop.
                      Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/isisL3/3", ...]

        action = start or stop
        """
        if type(isisObjList) != list:
            raise IxNetRestApiException('startStopIsisL3Ngpf error: The parameter isisObjList must be a '
                                        'list of objects.')
        self.ixnObj.logInfo('startStopIsisL3Ngpf: {0}'.format(action))
        self.ixnObj.logInfo('\t%s' % isisObjList)
        for eachIsisObj in isisObjList:
            if action == 'start':
                eachIsisObj.Start()
            if action == 'stop':
                eachIsisObj.Stop()

    def startStopLdpBasicRouterNgpf(self, ldpObjList, action='start'):
        """
        Description
            Start or stop LDP Basic Router protocol.

        Parameters
            ldpObjList: Provide a list of one or more ldpBasicRouter object handles to start or stop.
                      Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ldpBasicRouter/3", ...]

        action = start or stop
        """
        if type(ldpObjList) != list:
            raise IxNetRestApiException('startStopLdpBasicRouterNgpf error: The parameter ldpObjList must be a '
                                        'list of objects.')
        for eachLdpObj in ldpObjList:
            if action == 'start':
                eachLdpObj.Start()
            if action == 'stop':
                eachLdpObj.Stop()

    def enableDisableIgmpGroupRangeNgpf(self, protocolSessionUrl, groupRangeList, action='disable'):
        """
         Description:
             To enable or disable specific multicast group range IP addresses by using overlay.

             1> Get a list of all the Multicast group range IP addresses.
             2> Get the multivalue list of ACTIVE STATE group ranges.
             3> Loop through the user list "groupRangeList" and look
                for the index position of the specified group range IP address.
             4> Using overlay to enable|disable the index value.

             Note: If an overlay is not created, then create one by:
                   - Creating a "ValueList" for overlay pattern.
                   - And add an Overlay.

        Parameters
            protocolSessionUrl: http://{apiServerIp:port}/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/igmpHost/1
            groupRangeList: A list of multicast group range addresses to disable.
                                Example: ['225.0.0.1', '225.0.0.5']
            action: disable or enable

        """
        if action == 'disable':
            enableDisable = 'false'
        else:
            enableDisable = 'true'
        igmpMcastIPv4GroupListObj = protocolSessionUrl.IgmpMcastIPv4GroupList
        groupRangeAddressMultivalue = igmpMcastIPv4GroupListObj.StartMcastAddr
        activeMultivalue = igmpMcastIPv4GroupListObj.Active
        groupRangeValues = self.ixnObj.getMultivalueValues(groupRangeAddressMultivalue)
        print('\nConfigured groupRangeValues:', groupRangeValues)

        listOfIndexesToDisable = []
        # Loop through user list of specified group ranges to disable.
        for groupRangeIp in groupRangeList:
            index = groupRangeValues.index(groupRangeIp)
            listOfIndexesToDisable.append(index)

        if not listOfIndexesToDisable:
            raise IxNetRestApiException('disableIgmpGroupRangeNgpf Error: No multicast group range ip address found '
                                        'on your list')

        for index in listOfIndexesToDisable:

            self.ixnObj.logInfo('enableDisableIgmpGroupRangeNgpf: %s: %s' % (action, groupRangeValues[index]))
            currentOverlayUrl = activeMultivalue.Overlay(index+1, enableDisable)

    def enableDisableMldGroupNgpf(self, protocolSessionUrl, groupRangeList, action='disable'):
        """
         Description:
             For IPv6 only. To enable or disable specific multicast group range IP addresses by using
             overlay.

             1> Get a list of all the Multicast group range IP addresses.
             2> Get the multivalue list of ACTIVE STATE group ranges.
             3> Loop through the user list "groupRangeList" and look
                for the index position of the specified group range IP address.
             4> Using overlay to enable|disable the index value.

             Note: If an overlay is not created, then create one by:
                   - Creating a "ValueList" for overlay pattern.
                   - And add an Overlay.

        Parameters
            protocolSessionUrl: http://{apiServerIp:port}/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/
            1/ipv4/1/igmpHost/1
            groupRangeList: A list of multicast group range addresses to disable.
                                Example: ['ff03::1', 'ff03::2']
            action: disable or enable
        """
        if action == 'disable':
            enableDisable = 'false'
        else:
            enableDisable = 'true'
        mldMcastIPv6GroupListObj = protocolSessionUrl.MldMcastIPv6GroupList
        groupRangeAddressMultivalue = mldMcastIPv6GroupListObj.StartMcastAddr
        activeMultivalue = mldMcastIPv6GroupListObj.Active
        groupRangeValues = self.getMultivalueValues(groupRangeAddressMultivalue)

        self.ixnObj.logInfo('Configured groupRangeValues: %s' % groupRangeValues)

        listOfIndexesToDisable = []
        # Loop through user list of specified group ranges to disable.
        for groupRangeIp in groupRangeList:
            index = groupRangeValues.index(groupRangeIp)
            listOfIndexesToDisable.append(index)

        if not listOfIndexesToDisable:
            raise IxNetRestApiException('disableMldGroupNgpf Error: No multicast group range ip address '
                                        'found on your list')

        for index in listOfIndexesToDisable:
            self.ixnObj.logInfo('enableDisableMldGroupNgpf: %s: %s' % (action, groupRangeValues[index]))
            currentOverlayUrl = activeMultivalue.Overlay(index + 1, enableDisable)

    def sendIgmpJoinLeaveNgpf(self, routerId=None, igmpHostUrl=None, multicastIpAddress=None, action='join'):
        """
        Description
            Send IGMP joins or leaves.

            A IGMP host object is acceptable.  If you don't know the IGMP host object, use Device Group RouterID.
            Since a Device Group could have many routerID, you could state one of them.

            If multicastIpAddress is 'all', this will send IGMP join on all multicast addresses.
            Else, provide a list of multicast IP addresses to send join.

        Parameters
            routerId: The Device Group Router ID address.
            igmpHostUrl: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/igmpHost/1'
            multicastIpAddress: 'all' or a list of multicast IP addresses to send join.
                                 Example: ['225.0.0.3', '225.0.0.4']
            action: join|leave
        """
       
        if routerId:
            deviceGroupObj = self.getDeviceGroupByRouterId(routerId=routerId)
            if deviceGroupObj == 0:
                raise IxNetRestApiException('No Device Group found for router ID: %s' % routerId)

            routerDataObj = deviceGroupObj.RouterData.find()
            routerIdMultivalue = routerDataObj.RouterId
            routerIdList = self.getMultivalueValues(routerIdMultivalue)
            if routerId in routerIdList:
                igmpHostUrl = deviceGroupObj.Ethernet.find().Ipv4.find().IgmpHost.find()
        igmpMcastIPv4GroupListObj = igmpHostUrl.IgmpMcastIPv4GroupList
        startMcastAddrMultivalue = igmpMcastIPv4GroupListObj.StartMcastAddr
        listOfConfiguredMcastIpAddresses = self.ixnObj.getMultivalueValues(startMcastAddrMultivalue)

        self.ixnObj.logInfo('sendIgmpJoinNgpf: List of configured Mcast IP addresses: %s'
                            % listOfConfiguredMcastIpAddresses)
        if not listOfConfiguredMcastIpAddresses:
            raise IxNetRestApiException('sendIgmpJoinNgpf: No Mcast IP address configured')

        if multicastIpAddress == 'all':
            listOfMcastAddresses = listOfConfiguredMcastIpAddresses
        else:
            listOfMcastAddresses = multicastIpAddress

        # Note: Index position is not zero based.
        indexListToSend = []
        for eachMcastAddress in listOfMcastAddresses:
            index = listOfConfiguredMcastIpAddresses.index(eachMcastAddress)
            indexListToSend.append(index+1)
        self.ixnObj.logInfo('\t%s' % multicastIpAddress)
        if action == 'join':
            igmpMcastIPv4GroupListObj.IgmpJoinGroup(indexListToSend)
        if action == 'leave':
            igmpMcastIPv4GroupListObj.IgmpLeaveGroup(indexListToSend)

    def sendPimV4JoinLeaveNgpf(self, routerId=None, pimObj=None, multicastIpAddress=None, action='join'):
        """
        Description
            Send PIMv4 joins or leaves.

            A PIM host object is acceptable.  If you don't know the PIM host object, use Device Group RouterID.
            Since a Device Group could have many routerID, you could state one of them.

            If multicastIpAddress is 'all', this will send join on all multicast addresses.
            Else, provide a list of multicast IP addresses to send join|leave.

        NOTE:
           Current support:  Each IP host multicast group address must be unique. IP hosts could send the same
                             multicast group address, but this API only supports unique multicast group address.
  
        Parameters
            routerId: The Device Group Router ID address.
            pimObj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/pimV4Interface/1/pimV4JoinPruneList'
            multicastIpAddress: 'all' or a list of multicast IP addresses to send join.
                                 Example: ['225.0.0.3', '225.0.0.4']
            action: join|leave
        """
      
        if routerId:
            deviceGroupObj = self.getDeviceGroupByRouterId(routerId=routerId)
            if deviceGroupObj == 0:
                raise IxNetRestApiException('No Device Group found for router ID: %s' % routerId)

            routerDataObj = deviceGroupObj.RouterData.find()
            routerIdMultivalue = routerDataObj.RouterId
            routerIdList = self.getMultivalueValues(routerIdMultivalue)
            if routerId in routerIdList:
                pimObj = deviceGroupObj.Ethernet.find().Ipv4.find().PimV4Interface.find()
        pimV4JoinPruneList = pimObj.PimV4JoinPruneList

        startMcastAddrMultivalue = pimV4JoinPruneList.groupV4Address
        listOfConfiguredMcastIpAddresses = self.ixnObj.getMultivalueValues(startMcastAddrMultivalue)

        self.ixnObj.logInfo('sendPimV4JoinNgpf: List of configured Mcast IP addresses: %s' %
                            listOfConfiguredMcastIpAddresses)
        if not listOfConfiguredMcastIpAddresses:
            raise IxNetRestApiException('sendPimV4JoinNgpf: No Mcast IP address configured')

        if multicastIpAddress == 'all':
            listOfMcastAddresses = listOfConfiguredMcastIpAddresses
        else:
            listOfMcastAddresses = multicastIpAddress

        # Note: Index position is not zero based.
        indexListToSend = []
        for eachMcastAddress in listOfMcastAddresses:
            index = listOfConfiguredMcastIpAddresses.index(eachMcastAddress)
            indexListToSend.append(index+1)
        self.ixnObj.logInfo('\t%s' % multicastIpAddress)
        if action == 'join':
            pimV4JoinPruneList.Join(indexListToSend)
        if action == 'leave':
            pimV4JoinPruneList.Leave(indexListToSend)

    def sendMldJoinNgpf(self, mldObj, ipv6AddressList):
        """
        Description
            For IPv6 only.
            This API will take the MLD object and loop through all the configured ports
            looking for the specified ipv6Address to send a join.

        Parameter
            ipv6AddressList: 'all' or a list of IPv6 addresses that must be EXACTLY how it is configured on the GUI.
        """
        mldMcastIPv6GroupListObj = mldObj.MldMcastIPv6GroupList
        startMcastAddrMultivalue = mldMcastIPv6GroupListObj.StartMcastAddr
        listOfConfiguredGroupIpAddresses = self.getMultivalueValues(startMcastAddrMultivalue)
        if ipv6AddressList == 'all':
            listOfGroupAddresses = listOfConfiguredGroupIpAddresses
        else:
            listOfGroupAddresses = ipv6AddressList

        indexListToSend = []
        for eachSpecifiedIpv6Addr in listOfGroupAddresses:
            index = listOfConfiguredGroupIpAddresses.index(eachSpecifiedIpv6Addr)
            indexListToSend.append(index + 1)
        mldMcastIPv6GroupListObj.MldJoinGroup(indexListToSend)

    def sendMldLeaveNgpf(self, mldObj, ipv6AddressList):
        """
        Description
            For IPv6 only.
            This API will take the mld sessionUrl object and loop through all the configured ports
            looking for the specified ipv6Address to send a leave.

        Parameters
            mldObj: http://{apiServerIp:port}/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/2
            /mldHost/1
            ipv6AddressList: 'all' or a list of IPv6 addresses that must be EXACTLY how it is configured on the GUI.
        """
        mldMcastIPv6GroupListObj = mldObj.MldMcastIPv6GroupList
        startMcastAddrMultivalue = mldMcastIPv6GroupListObj.StartMcastAddr
        listOfConfiguredGroupIpAddresses = self.getMultivalueValues(startMcastAddrMultivalue)
        if ipv6AddressList == 'all':
            listOfGroupAddresses = listOfConfiguredGroupIpAddresses
        else:
            listOfGroupAddresses = ipv6AddressList

        indexListToSend = []
        for eachSpecifiedIpv6Addr in listOfGroupAddresses:
            index = listOfConfiguredGroupIpAddresses.index(eachSpecifiedIpv6Addr)
            indexListToSend.append(index + 1)
        mldMcastIPv6GroupListObj.MldLeaveGroup(indexListToSend)

    def getSessionStatus(self, protocolObj):
        """
        Description
           Get the object's session status.

        Parameter
           protocolObj: (str): The protocol object.
                        /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/bgpIpv4Peer/1
        Returns
           Success: A list of up|down session status.
           Failed:  An empty list
        """
        return protocolObj.SessionStatus

    def getIpAddresses(self, ipObj):
        """
        Description
           Get the configured ipv4|ipv6 addresses in a list.
        
        Parameter
           ipObj: <str>: The IPv4|Ipv6 object: /api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1/ethernet/1/ipv4/1
        """
        multivalueObj = ipObj.Address
        response = self.getMultivalueValues(multivalueObj)
        return response

    def showTopologies(self):
        """
        Description
            Show the NGPF configuration: Topology Groups, Device Groups, Mac Addreseses, VLAN ID,
                                         IPv4, IPv6, protocol sessions.
        """
        topologyList = self.ixNetwork.Topology.find()
        self.ixnObj.logInfo('', timestamp=False)
        for (index, topology) in enumerate(topologyList):
            self.ixnObj.logInfo('TopologyGroup: {0}   Name: {1}'.format(index+1, topology.Name), timestamp=False)
            self.ixnObj.logInfo('    Status: {0}'.format(topology.Status), timestamp=False)

            vportObjList = []
            for eachVport in self.ixNetwork.Vport.find():
                if eachVport.href in topology.Ports:
                    vportObjList.append(eachVport)
            for (index, vportObj) in enumerate(vportObjList):

                self.ixnObj.logInfo('    VportId: {0} Name: {1}  AssignedTo: {2}  State: {3}'.format(index+1,
                                                                                                     vportObj.Name,
                                                                                                     vportObj.AssignedTo,
                                                                                                     vportObj.State),
                                    timestamp=False)
            self.ixnObj.logInfo('\n', end='', timestamp=False)
            deviceGroupObjList = topology.DeviceGroup.find()
            for (index, deviceGroup) in enumerate(deviceGroupObjList):
                self.ixnObj.logInfo('    DeviceGroup:{0}  Name:{1}'.format(index+1, deviceGroup.Name), timestamp=False)
                self.ixnObj.logInfo('\tStatus: {0}'.format(deviceGroup.Status), end='\n\n', timestamp=False)
                ethernetObjList = deviceGroup.Ethernet.find()
                for (index, ethernet) in enumerate(ethernetObjList):
                    ethernetSessionStatus = self.getSessionStatus(ethernet)
                    self.ixnObj.logInfo('\tEthernet:{0}  Name:{1}'.format(index+1, ethernet.Name), timestamp=False)
                    self.ixnObj.logInfo('\t    Status: {0}'.format(ethernet.Status), timestamp=False)
                    enableVlansMultivalue = ethernet.EnableVlans
                    enableVlansValues = self.getMultivalueValues(enableVlansMultivalue, silentMode=True)[0]
                    self.ixnObj.logInfo('\t    Vlan enabled: %s\n' % enableVlansValues, timestamp=False)
                    ipv6List = []
                    if not ethernet.Ipv6.find():
                        ipv6List.insert(0, None)

                    for (index, mac, vlan, ipv4, ipv6) in enumerate(zip(ethernet.Mac, ethernet.Vlan.find(),
                                                                        ethernet.Ipv4.find(), ethernet.Ipv6.find())):
                        ipv4Obj = ipv4
                        ipv4SessionStatus = self.getSessionStatus(ipv4Obj)
                        self.ixnObj.logInfo('\tIPv4:{0} Status: {1}'.format(index+1, ipv4.Status), timestamp=False)
                        macResponse = mac
                        macAddress = self.getMultivalueValues(macResponse, silentMode=True)
                        vlanResponse = vlan.VlanId
                        vlanId = self.getMultivalueValues(vlanResponse, silentMode=True)
                        priorityResponse = vlan.Priority
                        vlanPriority = self.getMultivalueValues(priorityResponse, silentMode=True)
                        ipResponse = ipv4.Address
                        ipAddress = self.getMultivalueValues(ipResponse, silentMode=True)
                        gatewayResponse = ipv4.GatewayIp
                        gateway = self.getMultivalueValues(gatewayResponse, silentMode=True)
                        prefixResponse = ipv4.Prefix
                        prefix = self.getMultivalueValues(prefixResponse, silentMode=True)

                        index = 1
                        self.ixnObj.logInfo('\t    {0:8} {1:14} {2:7} {3:9} {4:12} {5:16} {6:12} {7:7} {8:7}'.
                                            format('Index', 'MacAddress', 'VlanId', 'VlanPri', 'EthSession',
                                                   'IPv4Address', 'Gateway', 'Prefix', 'Ipv4Session'), timestamp=False)
                        self.ixnObj.logInfo('\t    {0}'.format('-'*104), timestamp=False)
                        for mac, vlanId, vlanPriority, ethSession, ip, gateway, prefix, ipv4Session in zip(macAddress,
                                                                                                           vlanId,
                                                                                                           vlanPriority,
                                                                                                           ethernetSessionStatus,
                                                                                                           ipAddress,
                                                                                                           gateway,
                                                                                                           prefix,
                                                                                                           ipv4SessionStatus):
                            self.ixnObj.logInfo('\t    {0:^5} {1:18} {2:^6} {3:^9} {4:13} {5:<15} {6:<13} {7:6} {8:7}'
                                                .format(index, mac, vlanId, vlanPriority, ethSession, ip, gateway,
                                                        prefix, ipv4Session), timestamp=False)
                            index += 1

                        # IPv6
                        if None not in ipv6List:
                            ipResponse = ipv6.Address
                            ipAddress = self.getMultivalueValues(ipResponse, silentMode=True)
                            gatewayResponse = ipv6.GatewayIp
                            gateway = self.getMultivalueValues(gatewayResponse, silentMode=True)
                            prefixResponse = ipv6.Prefix
                            prefix = self.getMultivalueValues(prefixResponse, silentMode=True)
                            ipv6SessionStatus = self.getSessionStatus(ipv6)
                            index1 = 1
                            self.ixnObj.logInfo('\tIPv6:{0} Status: {1}'.format(index1+1, ipv6.Status), timestamp=False)
                            self.ixnObj.logInfo('\t    {0:8} {1:14} {2:7} {3:9} {4:12} {5:19} {6:18} {7:7} {8:7}'
                                                .format('Index', 'MacAddress', 'VlanId', 'VlanPri', 'EthSession',
                                                        'IPv6Address', 'Gateway', 'Prefix', 'Ipv6Session'),
                                                timestamp=False)
                            self.ixnObj.logInfo('\t   %s' % '-'*113)
                            for mac, vlanId, vlanPriority, ethSession, ip, gateway, prefix, ipv4Session in zip(macAddress,
                                                                            vlanId, vlanPriority,
                                                                            ethernetSessionStatus,
                                                                            ipAddress, gateway,
                                                                            prefix, ipv6SessionStatus):
                                self.ixnObj.logInfo('\t    {0:^5} {1:18} {2:^6} {3:^9} {4:13} {5:<15} '
                                                    '{6:<13} {7:8} {8:7}'.format(index, mac, vlanId, vlanPriority,
                                                                                 ethSession, ip, gateway, prefix,
                                                                                 ipv4Session), timestamp=False)
                                index += 1

                        self.ixnObj.logInfo('\n', end='', timestamp=False)
                        if ipv4.BgpIpv4Peer.find():
                            for (index, bgpIpv4Peer) in enumerate(ipv4.BgpIpv4Peer.find()):
                                bgpIpv4PeerSessionStatus = self.getSessionStatus(bgpIpv4Peer)

                                self.ixnObj.logInfo('\tBGPIpv4Peer:{0}  Name:{1}'.format(index+1, bgpIpv4Peer.Name,
                                                                                         bgpIpv4Peer.Status), timestamp=False)
                                dutIpResponse = bgpIpv4Peer.DutIp
                                dutIp = self.getMultivalueValues(dutIpResponse, silentMode=True)
                                typeMultivalue = bgpIpv4Peer.Type
                                bgpType = self.getMultivalueValues(typeMultivalue, silentMode=True)
                                localAs2BytesMultivalue = bgpIpv4Peer.LocalAs2Bytes
                                localAs2Bytes = self.getMultivalueValues(localAs2BytesMultivalue, silentMode=True)
                                flapResponse = bgpIpv4Peer.Flap
                                flap = self.getMultivalueValues(flapResponse, silentMode=True)
                                uptimeResponse = bgpIpv4Peer.UptimeInSec
                                uptime = self.getMultivalueValues(uptimeResponse, silentMode=True)
                                downtimeResponse = bgpIpv4Peer.DowntimeInSec
                                downtime = self.getMultivalueValues(downtimeResponse, silentMode=True)
                                self.ixnObj.logInfo('\t    Type: {0}  localAs2Bytes: {1}'.format(bgpType[0],
                                                                                                 localAs2Bytes[0]),
                                                    timestamp=False)
                                self.ixnObj.logInfo('\t    Status: {0}'.format(bgpIpv4Peer.Status), timestamp=False)
                                index = 1

                                for dutIp, bgpSession, flap, uptime, downtime in zip(dutIp,
                                                                                     bgpIpv4PeerSessionStatus,
                                                                                     flap,
                                                                                     uptime,
                                                                                     downtime):
                                    self.ixnObj.logInfo('\t\t{0}: DutIp:{1}  SessionStatus:{2}  Flap:{3}  upTime:{4}  '
                                                        'downTime:{5}'.format(index, dutIp, bgpSession, flap, uptime,
                                                                              downtime), timestamp=False)
                                    index += 1

                        for (index, ospfv2) in enumerate(ipv4.Ospfv2.find()):
                            self.ixnObj.logInfo('\t    OSPFv2:{0}  Name:{1}'.format(index+1, ospfv2.Name,
                                                                                    ospfv2.Status), timestamp=False)
                            self.ixnObj.logInfo('\t\tStatus: {0}'.format(ospfv2.Status), end='\n\n', timestamp=False)

                        for (index, igmpHost) in enumerate(ipv4.IgmpHost.find()):
                            self.ixnObj.logInfo('\t    igmpHost:{0}  Name:{1}'.format(index+1, igmpHost.Name,
                                                                                      igmpHost.Status), timestamp=False)
                            self.ixnObj.logInfo('\t\tStatus: {0}'.format(igmpHost.Status), end='\n\n', timestamp=False)
                        for (index, igmpQuerier) in enumerate(ipv4.IgmpQuerier.find()):
                            self.ixnObj.logInfo('\t    igmpQuerier:{0}  Name:{1}'.format(index+1, igmpQuerier.Name,
                                                                                         igmpQuerier.Status),
                                                timestamp=False)
                            self.ixnObj.logInfo('\t\tStatus: {0}'.format(igmpQuerier.Status), end='\n\n',
                                                timestamp=False)
                        for (index, vxlan) in enumerate(ipv4.Vxlan.find()):
                            self.ixnObj.logInfo('\t    vxlan:{0}  Name:{1}'.format(index+1, vxlan.Name, vxlan.Status),
                                                timestamp=False)
                            self.ixnObj.logInfo('\tStatus: {0}'.format(vxlan.Status), end='\n\n, timestamp=False')

                for (index, networkGroup) in enumerate(deviceGroup.NetworkGroup.find()):
                    self.ixnObj.logInfo('\n\tNetworkGroup:{0}  Name:{1}'.format(index+1, networkGroup.Name),
                                        timestamp=False)
                    self.ixnObj.logInfo('\t    Multiplier: {0}'.format(networkGroup.Multiplier), timestamp=False)
                    ipv4PrefixPoolsObj = networkGroup.Ipv4PrefixPools.find()
                    startingAddressMultivalue = ipv4PrefixPoolsObj.NetworkAddress
                    startingAddress = self.getMultivalueValues(startingAddressMultivalue, silentMode=True)[0]
                    endingAddress = self.getMultivalueValues(startingAddressMultivalue, silentMode=True)[-1]
                    prefixLengthMultivalue = ipv4PrefixPoolsObj.PrefixLength
                    prefixLength = self.getMultivalueValues(prefixLengthMultivalue)[0]
                    self.ixnObj.logInfo('\t    StartingAddress:{0}  EndingAddress:{1}  Prefix:{2}'.format(
                        startingAddress, endingAddress, prefixLength), timestamp=False)
                    if None not in ethernet.Ipv6.find():
                        for (index, ipv6) in enumerate(ethernet.Ipv6.find()):
                            self.ixnObj.logInfo('\t    IPv6:{0}  Name:{1}'.format(index+1, ipv6.Name), timestamp=False)
                            for (index, bgpIpv6Peer) in enumerate(ipv6.BgpIpv6Peer.find()):
                                self.ixnObj.logInfo('\t    BGPIpv6Peer:{0}  Name:{1}'.format(index+1, bgpIpv6Peer.Name),
                                                    timestamp=False)
                            for (index, ospfv3) in enumerate(ipv6.Ospfv3.find()):
                                self.ixnObj.logInfo('\t    OSPFv3:{0}  Name:{1}'.format(index+1, ospfv3.Name),
                                                    timestamp=False)
                            for (index, mldHost) in enumerate(ipv6.MldHost.find()):
                                self.ixnObj.logInfo('\t    mldHost:{0}  Name:{1}'.format(index+1, mldHost.Name),
                                                    timestamp=False)
                            for (index, mldQuerier) in ipv6.MldQuerier.find():
                                self.ixnObj.logInfo('\t    mldQuerier:{0}  Name:{1}'.format(index+1, mldQuerier.Name),
                                                    timestamp=False)
            self.ixnObj.logInfo('\n', timestamp=False)

    def getBgpObject(self, topologyName=None, bgpAttributeList=None):
        """
        Description
            Get the BGP object from the specified Topology Group name and return the specified attributes

        Parameters
            topologyName: The Topology Group name
            bgpAttributeList: The BGP attributes to get.


        Example:
            bgpAttributeMultivalue = restObj.getBgpObject(topologyName='Topo1', bgpAttributeList=['flap',
            'uptimeInSec', 'downtimeInSec'])
            restObj.configMultivalue(bgpAttributeMultivalue['flap'],          multivalueType='valueList',
            data={'values': ['true', 'true']})
            restObj.configMultivalue(bgpAttributeMultivalue['uptimeInSec'],   multivalueType='singleValue',
            data={'value': '60'})
            restObj.configMultivalue(bgpAttributeMultivalue['downtimeInSec'], multivalueType='singleValue',
            data={'value': '30'})
        """
        queryData = {'from': '/',
                     'nodes': [{'node': 'topology',    'properties': ['name'], 'where': [{'property': 'name',
                                                                                          'regex': topologyName}]},
                               {'node': 'deviceGroup', 'properties': [], 'where': []},
                               {'node': 'ethernet',    'properties': [], 'where': []},
                               {'node': 'ipv4',        'properties': [], 'where': []},
                               {'node': 'bgpIpv4Peer', 'properties': bgpAttributeList, 'where': []}]
                     }
        queryResponse = self.ixnObj.query(data=queryData)
        try:
            bgpHostAttributes = queryResponse.json()['result'][0]['topology'][0]['deviceGroup'][0]['ethernet'][0]
            ['ipv4'][0]['bgpIpv4Peer'][0]
            return bgpHostAttributes
        except IndexError:
            raise IxNetRestApiException('\nVerify the topologyName and bgpAttributeList input: {0} / {1}\n'
                                        .format(topologyName, bgpAttributeList))

    def isRouterIdInDeviceGroupObj(self, routerId, deviceGroupObj):
        routerIdMultivalue = deviceGroup['routerData'][0]['routerId']
        routerIdList = self.ixnObj.getMultivalueValues(routerIdMultivalue, silentMode=True)

    def configBgpNumberOfAs(self, routerId, numberOfAs):
        """
        Description
            Set the total number of BGP AS # List.
            In the GUI, under NetworkGroup, BGP Route Range tab, bottom tab ASPathSegments, enter number of AS
            # Segments.

            NOTE! 
                Currently, this API will get the first Network Group object even if there are multiple
                Network Groups. Network Groups could be filtered by the name or by the first route range 
                address.  Haven't decided yet. Don't want to filter by name because in a situation 
                where customers are also using Spirent, Spirent doesn't go by name.

        Parameters
            routerId: The Device Group router ID
            numberOfAs: The total number of AS list to create.

        Requirements
            getDeviceGroupByRouterId()
        """
        deviceGroupObj = self.getDeviceGroupByRouterId(routerId=routerId)
        if deviceGroupObj == 0:
            raise IxNetRestApiException('No Device Group found for router ID: %s' % routerId)

        queryData = {'from': deviceGroupObj,
                     'nodes': [{'node': 'networkGroup',    'properties': [], 'where': []},
                               {'node': 'ipv4PrefixPools', 'properties': [], 'where': []},
                               {'node': 'bgpIPRouteProperty', 'properties': [], 'where': []},
                               {'node': 'bgpAsPathSegmentList', 'properties': [], 'where': []}
                               ]}
        queryResponse = self.ixnObj.query(data=queryData)
        try:
            bgpStack = queryResponse.json()['result'][0]['networkGroup'][0]['ipv4PrefixPools'][0]['bgpIPRouteProperty'][0]['bgpAsPathSegmentList']
        except:
            raise IxNetRestApiException('No object found in DeviceGroup object:  deviceGroup/networkGroup/'
                                        'ipv4PrefixPools/bgpIPRouteProperty/bgpAsPathSegmentList: %s' % deviceGroupObj)

        if not bgpStack:
            return IxNetRestApiException('No ipv4PrefixPools bgpIPRouteProperty object found.')

        bgpRouteObj = bgpStack[0]['href']
        response = self.ixnObj.get(self.ixnObj.httpHeader+bgpRouteObj)
        asNumberInSegmentMultivalue = response.json()['numberOfAsNumberInSegment']
        self.ixnObj.patch(self.ixnObj.httpHeader+bgpRouteObj, data={'numberOfAsNumberInSegment': numberOfAs})

    def configBgpAsPathSegmentListNumber(self, routerId, asNumber, indexAndAsNumber):
        """
        Description
            Set BGP AS numbers in the route range. 
            If there are 5 AS# created under "Number of AS# In Segment-1", the asNumberList is
            the AS# that you want to modify for all route ranges (Device Group multiplier). 
            The indexAndAsNumber is the route range index and value: [3, 300].
            3 = the 2nd route range (zero based) and 300 is the value.

            NOTE! 
                Currently, this API will get the first Network Group object even if there are multiple
                Network Groups. Network Groups could be filtered by the name or by the first route range 
                address.  Haven't decided yet. Don't want to filter by name because in a situation 
                where customers are also using Spirent, Spirent doesn't go by name.

        Parameters
            routerId: The Device Group router ID where the BGP is configured.
            asListNumber: 1|2|3|...|6|..:  The AS# to modify.
                          (On GUI, click NetworkGroup, on bottom tab asPathSegment,
                           and on top tab, use the "Number of AS# In Segment-1" to set number of AS#1 or AS#2 or AS#3.)
            indexAndAsNumber: all|a list of indexes with as# -> [[1, 100], [3, 300], ...]

        Example:
            protocolObj.configBgpAsPathSegmentListNumber(routerid='195.0.0.2', 3, [[0,28], [3,298], [4, 828]])

        Requirements:
            getDeviceGroupByRouterId()
            getMultivalues()
            configMultivalues()
        """
        deviceGroupObj = self.getDeviceGroupByRouterId(routerId=routerId)
        if deviceGroupObj == 0:
            raise IxNetRestApiException('No Device Group found for router ID: %s' % routerId)

        queryData = {'from': deviceGroupObj,
                     'nodes': [{'node': 'networkGroup',    'properties': [], 'where': []},
                               {'node': 'ipv4PrefixPools', 'properties': [], 'where': []},
                               {'node': 'bgpIPRouteProperty', 'properties': [], 'where': []},
                               {'node': 'bgpAsPathSegmentList', 'properties': [], 'where': []},
                               {'node': 'bgpAsNumberList', 'properties': [], 'where': []}
                               ]}
        queryResponse = self.ixnObj.query(data=queryData)
        try:
            bgpStack = queryResponse.json()['result'][0]['networkGroup'][0]['ipv4PrefixPools'][0]['bgpIPRouteProperty'][0]['bgpAsPathSegmentList'][0]['bgpAsNumberList'][int(asNumber)-1]
        except:
            raise IxNetRestApiException('No object found in DeviceGroup object:  deviceGroup/networkGroup/'
                                        'ipv4PrefixPools/bgpIPRouteProperty/bgpAsPathSegmentList/bgpAsNumberlist: %s'
                                        % deviceGroupObj)

        if not bgpStack:
            return IxNetRestApiException('No ipv4PrefixPools bgpIPRouteProperty object found.')

        bgpRouteObj = bgpStack['href']
        response = self.ixnObj.get(self.ixnObj.httpHeader+bgpRouteObj)
        asNumberMultivalue = response.json()['asNumber']
        asNumberValueList = self.ixnObj.getMultivalueValues(asNumberMultivalue)
        try:
            for eachIndexAsNumber in indexAndAsNumber:
                index = eachIndexAsNumber[0]
                asNumber = eachIndexAsNumber[1]
                asNumberValueList[index] = str(asNumber)
        except:
            raise IxNetRestApiException('The index that you indicated is out of range for the current AS list')
 
        self.ixnObj.logInfo('Configuruing: %s' % bgpRouteObj)
        self.ixnObj.configMultivalue(asNumberMultivalue, 'valueList', {'values': asNumberValueList})

    def configBgpAsSetMode(self, routerId, asSetMode):
        """
        Description
            Configure BGP Route Range AS Path: AS # Set Mode. This API will change all
            indexes to the specified asSetMode
            Note: In GUI, under Route Range, BGP IP Route Range.

        Parameters
            asSetMode:
                Options: "dontincludelocalas",
                         "includelocalasasasseq",
                         "includelocalasasasset",
                         "includelocalasasasseqconfederation",
                         "includelocalasasassetconfederation",
                         "prependlocalastofirstsegment"
        """
        deviceGroupObj = self.getDeviceGroupByRouterId(routerId=routerId)
        if deviceGroupObj is None:
            raise IxNetRestApiException('No Device Group found for router ID: %s' % routerId)

        queryData = {'from': deviceGroupObj,
                     'nodes': [{'node': 'networkGroup',    'properties': [], 'where': []},
                               {'node': 'ipv4PrefixPools', 'properties': [], 'where': []},
                               {'node': 'bgpIPRouteProperty', 'properties': [], 'where': []}]
                     }
        queryResponse = self.ixnObj.query(data=queryData)
        bgpStack = queryResponse.json()['result'][0]['networkGroup'][0]['ipv4PrefixPools'][0]['bgpIPRouteProperty']
        if not bgpStack:
            return IxNetRestApiException('No ipv4PrefixPools bgpIPRouteProperty object found.')

        bgpRouteObj = bgpStack[0]['href']
        response = self.ixnObj.get(self.ixnObj.httpHeader+bgpRouteObj)        
        asSetModeMultivalue = response.json()['asSetMode']
        count = response.json()['count']
        newList = [asSetMode for counter in range(0, count)]
        self.ixnObj.configMultivalue(asSetModeMultivalue, 'valueList', {'values': newList})

    def getObject(self, keys, ngpfEndpointName=None):
        """
        Description
            This is an internal function usage for getNgpfObjectHandleByName() only.
        """
        for key, value in keys.items():
            if type(value) is list:
                for keyValue in value:
                    for key, value in keyValue.items():
                        if key == 'name' and value == ngpfEndpointName:
                            return keyValue['href']

                    object = self.getObject(keys=keyValue, ngpfEndpointName=ngpfEndpointName)
                    if object is not None:
                        return object
        return None

    def getNgpfObjectHandleByName(self, ngpfEndpointObject=None, ngpfEndpointName=None):
        """
        Description
           Get the NGPF object handle filtering by the NGPF component name.
           The NGPF object name is something that you could configure for each NGPF stack.
           Stack meaning: topology, deviceGroup, ethernet, ipv44, bgpIpv4Peer, etc

        Parameters
           ngpfEndpointObject: See below ngpfL2ObjectList and ngpfL3ObjectList. 
           ngpfEndpointName:   The name of the NGPF component object.

        Examples:
           protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='topology', ngpfEndpointName='Topo2')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/2

           protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='ipv4', ngpfEndpointName='IPv4 1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1

           protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='bgpIpv4Peer', ngpfEndpointName='bgp_2')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1/
                 bgpIpv4Peer/2

           protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='networkGroup', ngpfEndpointName='networkGroup1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1

           protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='ipv4PrefixPools',
           ngpfEndpointName='Basic IPv4 Addresses 1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/
                 networkGroup1/ipv4PrefixPools/1
        """
        ngpfMainObjectList = ['topology', 'deviceGroup', 'ethernet', 'ipv4', 'ipv6',
                      'networkGroup', 'ipv4PrefixPools', 'ipv6PrefixPools']
        ngpfL2ObjectList = ['isisL3', 'lacp', 'mpls']
        ngpfL3ObjectList = ['ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
                    'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
                    'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
                    'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp', 'ipv6sr',
                    'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3', 'ovsdbcontroller', 'ovsdbserver',
                    'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp', 'rsvpteIf',
                    'rsvpteLsps', 'tag', 'vxlan'
                ]

        if ngpfEndpointObject not in ngpfL2ObjectList+ngpfL3ObjectList+ngpfMainObjectList:
            raise IxNetRestApiException('\nError: No such ngpfEndpointObject: %s' % ngpfEndpointObject)

        if ngpfEndpointObject in ngpfL2ObjectList:
            ngpfEndpointObject = ngpfEndpointObject[0:1].capitalize() + ngpfEndpointObject[1:]
            nodesObjList = self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find()
            Obj = eval("nodesObjList." + ngpfEndpointObject + ".find(Name=ngpfEndpointName)")
            self.ixnObj.logInfo('getNgpfObjectHandleByName: %s' % Obj)
            return Obj
        elif ngpfEndpointObject in ngpfL3ObjectList:
            ngpfEndpointObject = ngpfEndpointObject[0:1].capitalize() + ngpfEndpointObject[1:]
            nodesIpv4ObjList = self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find()
            nodesIpv6ObjList = self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find()
            try:
                Obj = eval("nodesIpv4ObjList." + ngpfEndpointObject + ".find(Name=ngpfEndpointName)")
                self.ixnObj.logInfo('getNgpfObjectHandleByName: %s' % Obj)
                return Obj
            except:
                Obj = eval("nodesIpv6ObjList." + ngpfEndpointObject + ".find(Name=ngpfEndpointName)")
                self.ixnObj.logInfo('getNgpfObjectHandleByName: %s' % Obj)
                return Obj
        else:
            obj = self.ixNetwork
            ngpfEndpointIndex = ngpfMainObjectList.index(ngpfEndpointObject)

        for eachNgpfEndpoint in ngpfMainObjectList[:ngpfEndpointIndex+1]:
            # topology, deviceGroup, ethernet, ipv4, ipv6, networkGroup ...
            if eachNgpfEndpoint != ngpfEndpointObject:
                eachNgpfEndpoint = eachNgpfEndpoint[0:1].capitalize() + eachNgpfEndpoint[1:]
                obj = eval('obj.' + eachNgpfEndpoint + ".find()")
            else:
                eachNgpfEndpoint = eachNgpfEndpoint[0:1].capitalize() + eachNgpfEndpoint[1:]
                obj = eval('obj.' + eachNgpfEndpoint + ".find(Name=ngpfEndpointName)")
        self.ixnObj.logInfo('getNgpfObjectHandleByName: %s' % obj)
        return obj

    def getNgpfObjectHandleByRouterId(self, ngpfEndpointObject, routerId):
        """
        Description
           Get the NGPF object handle filtering by the routerId.
           All host interface has a router ID by default and the router ID is located in the
           Device Group in the IxNetwork GUI.  The API endpoint is: /topology/deviceGroup/routerData
        
           Note: Router ID exists only if there are protocols configured.

        Parameters
           ngpfEndpointObject: <str>: The NGPF endpoint. Example:
                               deviceGroup, ethernet, ipv4, ipv6, bgpIpv4Peer, ospfv2, etc.
                               These endpoint object names are the IxNetwork API endpoints and you could
                               view them in the IxNetwork API browser.

           routerId: <str>: The router ID IP address.

        Example:
              protocolObj.getNgpfObject(ngpfEndpointObject='ipv4', routerId='192.0.0.1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv4/1

              protocolObj.getNgpfObject(ngpfEndpointObject='bgpIpv4Peer', routerId='193.0.0.1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/2/deviceGroup/1/ethernet/1/ipv4/1/
                 bgpIpv4Peer/2

              protocolObj.getNgpfObject(ngpfEndpointObject='networkGroup', routerId='193.0.0.1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup/1

              protocolObj.getNgpfObject(ngpfEndpointObject='ipv4PrefixPools', routerId='193.0.0.1')
                 return objectHandle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/networkGroup1/
                 ipv4PrefixPools/1
        """
        ngpfMainObjectList = ['topology', 'deviceGroup', 'ethernet', 'networkGroup', 'ipv4PrefixPools',
                            'ipv6PrefixPools']

        ngpfL2ObjectList = ['isisL3', 'lacp', 'mpls', 'ipv4', 'ipv6',]

        ngpfL3ObjectList = ['ancp', 'bfdv4Interface', 'bgpIpv4Peer', 'bgpIpv6Peer', 'dhcpv4relayAgent', 'dhcpv6relayAgent',
                            'geneve', 'greoipv4', 'greoipv6', 'igmpHost', 'igmpQuerier',
                            'lac', 'ldpBasicRouter', 'ldpBasicRouterV6', 'ldpConnectedInterface', 'ldpv6ConnectedInterface',
                            'ldpTargetedRouter', 'ldpTargetedRouterV6', 'lns', 'mldHost', 'mldQuerier', 'ptp', 'ipv6sr',
                        'openFlowController', 'openFlowSwitch', 'ospfv2', 'ospfv3', 'ovsdbcontroller', 'ovsdbserver',
                            'pcc', 'pce', 'pcepBackupPCEs', 'pimV4Interface', 'pimV6Interface', 'ptp', 'rsvpteIf',
                            'rsvpteLsps', 'tag', 'vxlan'
                            ]
        
        if ngpfEndpointObject not in ngpfL2ObjectList + ngpfL3ObjectList + ngpfMainObjectList:
            raise IxNetRestApiException('\nError: No such ngpfEndpointObject: %s' % ngpfEndpointObject)
        deviceGroupObjByRouterId = self.getDeviceGroupByRouterId(routerId=routerId)
        for topology in self.ixNetwork.Topology.find():
            deviceGroupList = []
            for deviceGroupObj in topology.DeviceGroup.find():
                deviceGroupList.append(deviceGroupObj)

            for deviceGroupObj in deviceGroupList:
                if deviceGroupObj == deviceGroupObjByRouterId:
                    if ngpfEndpointObject == 'topology':
                        return topology
                    if ngpfEndpointObject == 'deviceGroup':
                        return deviceGroupObj
                    ethernetList = deviceGroupObj.Ethernet.find()
                    if not ethernetList:
                        continue

                    if ngpfEndpointObject == 'ethernet':
                        for eachEthernetObj in ethernetList:
                            match = re.match('(/api.*)', eachEthernetObj.href)
                            if match:
                                return eachEthernetObj

                    if ngpfEndpointObject == 'networkGroup':
                        networkGroupList = deviceGroupObj.NetworkGroup.find()
                        for eachNetworkGroupObj in networkGroupList:
                            match = re.match('(/api.*)', eachNetworkGroupObj.href)
                            if match:
                                return eachNetworkGroupObj

                    for ethernet in ethernetList:
                        # Dynamically get all Ethernet child endpoints
                        if ngpfEndpointObject in ngpfL2ObjectList:
                            endpointObject = ngpfEndpointObject[0:1].capitalize() + ngpfEndpointObject[1:]
                            Obj = eval("ethernet." + endpointObject + ".find()")
                            return Obj
                        elif ngpfEndpointObject in ngpfL3ObjectList:
                            endpointObject = ngpfEndpointObject[0:1].capitalize() + ngpfEndpointObject[1:]
                            nodesIpv4ObjList = ethernet.Ipv4.find()
                            nodesIpv6ObjList = ethernet.Ipv6.find()
                            try:
                                Obj = eval("nodesIpv4ObjList." + endpointObject + ".find()")
                                return Obj
                            except:
                                Obj = eval("nodesIpv6ObjList." + endpointObject + ".find()")
                                return Obj
                        else:
                            return None

    def getDeviceGroupByRouterId(self, routerId=None, queryDict=None, runQuery=True):
        """
        Description
            Get the Device Group object handle for the routerId.

            Note:
               A Device Group could have many IP host (sessions). This is configured as multipliers in
               a Device Group.  If multiplier = 5, there will be 5 IP host. Each host will
               have a unique router ID identifier.
               To get the Device Group that has a specific router ID, pass in the router ID for the
               parameter routerId.

        Parameter
            routerId: <str>: The router ID in the format of 192.0.0.1.
            queryDict: <dict>: Ignore this parameter. This parameter is only used internally. 
            runQuery: Ignore this parameter.  <bool>: This parameter is only used internally.

        Example:
            obj = mainObj.getDeviceGroupByRouterId(routerId='192.0.0.3')

           How to getMac:
               Step 1> Get the Device Group that has routerId
                       deviceGroupObjHandle = self.getDeviceGroupByRouterId(routerId=routerId)
               Step 2> Append the /ethernet/1 endpoint object to the Device Group object.
                       ethernetObjHandle = deviceGroupObjHandle + '/ethernet/1'
               Step 3> Get the mac address using the ethernetObjHandle
                       return self.getObjAttributeValue(ethernetObjHandle, 'mac')

        Return
            - deviceGroup object handle: /api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1
            - None if routerid is not found
        """
        deviceGroupObj = None
        routerDataObj = self.ixNetwork.Topology.find().DeviceGroup.find().RouterData.find()
        for eachRouterDataObj in routerDataObj:
            routerIdValues = self.getMultivalueValues(eachRouterDataObj.RouterId)
            if routerId in routerIdValues:
                match = re.match('(/api.*)/routerData', eachRouterDataObj.href)
                deviceGroupObj = match.group(1)
        deviceGroupObjectList = self.ixNetwork.Topology.find().DeviceGroup.find()
        for eachDeviceGroupObject in deviceGroupObjectList:
            if eachDeviceGroupObject.href == deviceGroupObj:
                return eachDeviceGroupObject
        return deviceGroupObj

    def getEthernetPropertyValue(self, routerId=None, ngpfEndpointName=None, property=None):
        """
        Description
            Get any NGPF Ethernet property value based on the router ID or by the NGPF 
            component name.

        Parameters
            routerId: <str>: The router ID IP address.
            ngpfEndpointName: <str>: The NGPF endpoint name.
            property: <str>: The NGPF Ethernet property.
                      Choices: name, mac, mtu, status, vlanCount, enableVlans 
        """
        ethernetObj = None
        ethernetProperties = ['name', 'mac', 'mtu', 'status', 'vlanCount', 'enableVlans']
        if property not in ethernetProperties:
            raise IxNetRestApiException('\nError: No such Ethernet property: %s.\n\nAvailable NGPF Ethernet properies:'
                                        ' %s' % (property, ethernetProperties))

        if routerId:
            ethernetObj = self.getNgpfObjectHandleByRouterId(routerId=routerId, ngpfEndpointObject='ethernet')
        
        if ngpfEndpointName:
            ethernetObj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName,
                                                         ngpfEndpointObject='ethernet')
        attribute = property[0:1].capitalize() + property[1:]

        return self.ixnObj.getObjAttributeValue(ethernetObj, attribute)

    def sendNsNgpf(self, ipv6ObjList):
        """
        Description
            Send NS out of all the IPv6 objects that you provide in a list.
        
        Parameter
            ipv6ObjList: <str>:  Provide a list of one or more IPv6 object handles to send arp.
                         Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/1"]
        """
        if type(ipv6ObjList) != list:
            raise IxNetRestApiException('sendNsNgpf error: The parameter ipv6ObjList must be a list of objects.')
        self.ixNetwork.Topology.DeviceGroup.Ethernet.Ipv6.SendNs(ipv6ObjList)

    def configIpv6Ngpf(self, obj=None, port=None, portName=None, ngpfEndpointName=None, **kwargs):
        """
        Description
            Create or modify NGPF IPv6.
            To create a new IPv6 stack in NGPF, pass in the Ethernet object.
            If modifying, there are four options. 2-4 will query for the IP object handle.

               1> Provide the BGP object handle using the obj parameter.
               2> Set port: The physical port.
               3> Set portName: The vport port name.
               4> Set NGPF IP name that you configured.

        Parameters
            obj: <str>: None or Ethernet obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1'
                                IPv6 obj: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ethernet/1/ipv6/1'

            port: <list>: Format: [ixChassisIp, str(cardNumber), str(portNumber)]
            portName: <str>: The virtual port name.
            ngpfEndpointName: <str>: The name that you configured for the NGPF BGP.

            kwargs:
               ipv6Address: <dict>: {'start': '2000:0:0:1:0:0:0:1', 'direction': 'increment',
               'step': '0:0:0:0:0:0:0:1'},
               ipv6AddressPortStep: <str>|<dict>:  disable|0:0:0:0:0:0:0:1
                                    Incrementing the IP address on each port based on your input.
                                    0:0:0:0:0:0:0:1 means to increment the last octet on each port.

               gateway: <dict>: {'start': '2000:0:0:1:0:0:0:2', 'direction': 'increment', 'step': '0:0:0:0:0:0:0:1'},
               gatewayPortStep:  <str>|<dict>:  disable|0:0:0:0:0:0:0:1
                                 Incrementing the IP address on each port based on your input.
                                 0:0:0:0:0:0:0:1 means to increment the last octet on each port.

               prefix: <int>:  Example: 64
               resolveGateway: <bool>
        Syntax
            POST:  /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6
            PATCH: /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}

        Example to create a new IPv6 object:
             ipv6Obj = configIpv4Ngpf(ethernetObj1,
                                      ipv6Address={'start': '2000:0:0:1:0:0:0:1',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:1'},
                                      ipv6AddressPortStep='disabled',
                                      gateway={'start': '2000:0:0:1:0:0:0:2',
                                               'direction': 'increment',
                                               'step': '0:0:0:0:0:0:0:0'},
                                      gatewayPortStep='disabled',
                                      prefix=64,
                                      resolveGateway=True)

        Return
            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}
        """
        if obj is not None:
            if 'ipv6' in obj.href:
                ipv6Obj = obj
            else:
                self.ixnObj.logInfo('Creating new IPv6 in NGPF')
                ipv6Obj = obj.Ipv6.add()
                
        # To modify
        if ngpfEndpointName:
            ipv6Obj = self.getNgpfObjectHandleByName(ngpfEndpointName=ngpfEndpointName, ngpfEndpointObject='ipv6')
            createNewIpv6Obj = False

        # To modify
        if port:
            x = self.getProtocolListByPortNgpf(port=port)
            ipv6Obj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ipv6')[0]
            createNewIpv6Obj = False

        # To modify
        if portName:
            x = self.getProtocolListByPortNgpf(portName=portName)
            ipv6Obj = self.getProtocolObjFromProtocolList(x['deviceGroup'], 'ipv6')[0]
            createNewIpv6Obj = False

        if 'name' in kwargs:
            ipv6Obj.Name = kwargs['name']

        if 'multiplier' in kwargs:
            ipv6Obj.Multiplier = kwargs['multiplier']

        # Config IPv6 address
        if 'ipv6Address' in kwargs:
            self.ixnObj.logInfo('Configuring IPv6 address. Attribute for multivalueId = jsonResponse["address"]')
            addrObj = ipv6Obj.Address
            # Default to counter
            multivalueType = 'counter'
            data = kwargs['ipv6Address']
            if 'ipv6AddressMultivalueType' in kwargs:
                multivalueType = kwargs['ipv6AddressMultivalueType']
            if multivalueType == 'random':
                addrObj.Random()
            else:
                self.configMultivalue(addrObj, multivalueType, data)
            # Config IPv6 port step
            if 'ipv6AddressPortStep' in kwargs:
                portStepMultivalue = addrObj.Steps.find()
                self.ixnObj.logInfo('Configure IPv6 address port step')
                if kwargs['ipv6AddressPortStep'] != 'disabled':
                    portStepMultivalue.Step = kwargs['ipv6AddressPortStep']
                if kwargs['ipv6AddressPortStep'] == 'disabled':
                    portStepMultivalue.Enabled = False
        # Config Gateway
        if 'gateway' in kwargs:
            gatewayObj = ipv6Obj.find().GatewayIp
            self.ixnObj.logInfo('Configure IPv6 gateway. Attribute for multivalueId = jsonResponse["gatewayIp"]')
            # Default to counter
            multivalueType = 'counter'
            data = kwargs['gateway']
            if 'gatewayMultivalueType' in kwargs:
                multivalueType = kwargs['ipv6AddressMultivalueType']
            if multivalueType == 'random':
                gatewayObj.Random()
            else:
                self.configMultivalue(gatewayObj, multivalueType, data)
            # Config Gateway port step
            if 'gatewayPortStep' in kwargs:
                portStepMultivalue = gatewayObj.Steps.find()
                self.ixnObj.logInfo('Configure IPv6 gateway port step')
                if kwargs['gatewayPortStep'] != 'disabled':
                    portStepMultivalue.Step = kwargs['gatewayPortStep']
                if kwargs['gatewayPortStep'] == 'disabled':
                    portStepMultivalue.Enabled = False
        # Config resolve gateway
        if 'resolveGateway' in kwargs:
            resolveGatewayObj = ipv6Obj.find().ResolveGateway
            self.configMultivalue(resolveGatewayObj, 'singleValue', data={'value': kwargs['resolveGateway']})
        if 'prefix' in kwargs:
            prefixObj = ipv6Obj.find().Prefix
            self.ixnObj.logInfo('Configure IPv6 prefix. Attribute for multivalueId = jsonResponse["prefix"]')
            self.configMultivalue(prefixObj, 'singleValue', data={'value': kwargs['prefix']})

        if ipv6Obj not in self.configuredProtocols:
            self.configuredProtocols.append(ipv6Obj)
        return ipv6Obj

    def configDeviceGroupMultiplier(self, objectHandle, multiplier, applyOnTheFly=False):
        """
        Description
           Configure a Device Group multiplier.  Pass in a NGPF object handle and
           this API will parse out the Device Group object to use for configuring 
           the multiplier.
        
        Parameter
           objectHandle: <str>: A NGPF object handle.
           multiplier: <int>: The number of multiplier.
           applyOnTheFly: <bool>: Default to False. applyOnTheFly is for protocols already running.
        """
        deviceGroup = None
        deviceGroupObject = re.search("(.*deviceGroup/\d).*", objectHandle.href)
        deviceGroupObjectList = self.ixNetwork.Topology.find().DeviceGroup.find()
        for eachDeviceGroupObject in deviceGroupObjectList:
            if eachDeviceGroupObject.href == deviceGroupObject.group(1):
                deviceGroup = eachDeviceGroupObject
                break
        deviceGroup.Multiplier = int(multiplier)
        if applyOnTheFly:
            self.applyOnTheFly()

    def startStopLdpBasicRouterV6Ngpf(self, ldpV6ObjList, action='start'):
        """
        Description
            Start or stop LDP Basic Router V6 protocol.

        Parameters
            ldpV6ObjList: <list>: Provide a list of one or more ldpBasicRouterV6 object handles to start or stop.
                      Ex: ["/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/1/ldpBasicRouterV6/1", ...]
            action: <str>: start or stop
        """
        if type(ldpV6ObjList) != list:
            raise IxNetRestApiException('startStopLdpBasicRouterV6Ngpf error: The parameter ldpV6ObjList '
                                        'must be a list of objects.')
        for eachLdpV6Obj in ldpV6ObjList:
            if action == 'start':
                eachLdpV6Obj.Start()
            if action == 'stop':
                eachLdpV6Obj.Stop()

    def startStopLdpConnectedInterfaceNgpf(self, ldpConnectedIntObjList, action='start'):
        """
        Description
            Start or stop LDP Basic Router Connected Interface protocol.

        Parameters
            ldpConnectedIntObjList: <list>: Provide a list of one or more ldpBasicRouter
                                    object handles to start or stop.
                Ex: ["/api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv4/{id}/
                ldpConnectedInterface/{id}", ...]
            action: <str>: start or stop
        """
        if type(ldpConnectedIntObjList) != list:
            raise IxNetRestApiException('startStopLdpConnectedInterfaceNgpf error: The parameter ldpObjList'
                                        ' must be a list of objects.')
        for eachLdpConnectedIntObj in ldpConnectedIntObjList:
            if action == 'start':
                eachLdpConnectedIntObj.Start()
            if action == 'stop':
                eachLdpConnectedIntObj.Stop()

    def startStopLdpV6ConnectedInterfaceNgpf(self, ldpV6ConnectedIntObjList, action='start'):
        """
        Description
            Start or stop LDP Basic Router V6 Connected Interface protocol.

        Parameters
            ldpV6ConnectedIntObjList: <list>:  Provide a list of one or more ldpBasicRouter object handles to start or
            stop.
                      Ex: ["/api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}/ipv6/{id}/l
                      dpConnectedInterface/{id}", ...]
            action = start or stop
        """
        if type(ldpV6ConnectedIntObjList) != list:
            raise IxNetRestApiException('startStopLdpV6ConnectedInterfaceNgpf error: The parameter ldpV6ConnectedIntObj'
                                        'List must be a list of objects.')

        for eachLdpV6ConnectedIntObj in ldpV6ConnectedIntObjList:
            if action == 'start':
                eachLdpV6ConnectedIntObj.Start()
            if action == 'stop':
                eachLdpV6ConnectedIntObj.Stop()

    def verifyDhcpClientBind(self, deviceGroupName=None, protocol=None, **kwargs):
        """
        Description
            Check DHCP Client Bound/Idle and DHCP Client Bound Count.

        Parameters
            deviceGroupName: <str>: Name of deviceGroup, if value None check for all deviceGroups
                             Example: deviceGroupName = 'Device Group 4'
            protocol: <str>: ipv4,ipv6. If value None check for ipv4 and ipv6
                      Example: protocol = 'ipv4'
            kwargs:
                  portName: <str>: The virtual port name.
                            Example: portName = '1/2/9'

        Examples:
            protocolObj.verifyDhcpClientBind(deviceGroupName="DHCPv6 Client")
            protocolObj.verifyDhcpClientBind(protocol="ipv4")
            protocolObj.verifyDhcpClientBind(portName="1/2/9")

        Returns:
              Dictionary {'Idle': {'Device Group 4': {'Client2': [1, 2, 3, 4]}, 'DHCPv6 Client': {'Client1': [3]}},
                          'Bound': {'DHCPv6 Client': {'Client1': [1, 2, 4]}},   'boundCount': 3}

        """
        portName = kwargs.get('portName', None)
        if protocol is None:
            protocols = ['ipv4', 'ipv6']
        else:
            protocols = [protocol]

        boundCount = 0
        idleBoundDict = {}
        ibList = []

        for protocol in protocols:
            self.ixnObj.logInfo('Verifying DHCP IDLE/BOUND/NOTSTARTED for {0} protocol'.format(protocol))
            deviceList = []

            if portName:
                protocolList = self.getProtocolListByPortNgpf(portName=portName)
                topology = protocolList['deviceGroup'][0][0].split("deviceGroup")[0]
                deviceGroupObjList = topology.DeviceGroup.find()
                for deviceGroupObj in deviceGroupObjList:
                    deviceList.append(deviceGroupObj.Name)
            elif deviceGroupName is None:
                # Get all deviceGroups in all topology lists
                topologyList = self.getAllTopologyList()
                for topology in topologyList:
                    deviceGroupObjList = topology.DeviceGroup.find()
                    for deviceGroupObj in deviceGroupObjList:
                        deviceList.append(deviceGroupObj.Name)
            else:
                deviceList.append(deviceGroupName)
                ethObjList = self.getEndpointObjByDeviceGroupName(deviceGroupName, 'ethernet')
                if not ethObjList:
                    raise IxNetRestApiException("Device Group not configured")

            for eachDevice in deviceList:
                dhcpClientObjList = []
                ethObjList = self.getEndpointObjByDeviceGroupName(eachDevice, 'ethernet')

                for ethObj in ethObjList:
                    if protocol == 'ipv6':
                        dhcpClientList = ethObj.Dhcpv6client.find()
                    else:
                        dhcpClientList = ethObj.Dhcpv4client.find()

                    for dhcpClient in dhcpClientList:
                        dhcpClientObjList.append(dhcpClient)

                for dhcpClientObj in dhcpClientObjList:
                    idleDhcpDict = {}
                    boundDhcpDict = {}
                    dhcpObjName = str(dhcpClientObj.Name)
                    dhcpClientObjDeviceCount = dhcpClientObj.Count
                    discoveredAddressList = dhcpClientObj.DiscoveredAddresses

                    idleList = [count+1 for count in range(dhcpClientObjDeviceCount) if('[Unresolved]' in
                                                                                        discoveredAddressList[count])]
                    boundList = [count+1 for count in range(dhcpClientObjDeviceCount) if('[Unresolved]' not in
                                                                                         discoveredAddressList[count])]

                    if idleList:
                        idleDhcpDict[dhcpObjName] = idleList
                        ibList.append(["Idle", eachDevice, idleDhcpDict])
                    if boundList:
                        boundDhcpDict[dhcpObjName] = boundList
                        ibList.append(["Bound", eachDevice, boundDhcpDict])

                    boundCount += len(boundList)

        idleBoundDict['Idle'] = {str(ele[1]): ele[2] for ele in filter(lambda x: x[0] == 'Idle', ibList)}
        idleBoundDict['Bound'] = {str(ele[1]): ele[2] for ele in filter(lambda x: x[0] == 'Bound', ibList)}
        idleBoundDict['boundCount'] = boundCount

        return idleBoundDict
