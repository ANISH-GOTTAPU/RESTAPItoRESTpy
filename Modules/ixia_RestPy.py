#**************************************************
# Copyright (c) 2017 Cisco Systems, Inc.
# All rights reserved.
#**************************************************
'''
IXIA lib
'''
import json
import re
import time
import csv
import datetime
import requests
import sys
import os
import tabulate
'''
from logger.cafylog import CafyLog
from utils.cafyexception import CafyException
from utils.timer import Timer
from utils.helper import Helper

from tgn.base import TGN
from tgn.ixia_ixnetwork import IxNetwork, TrafficStats, TgenDevice, NewTrafficItem
from tgn.ixia_resthttp import RestHttp, IxiaConfigException, \
    IxiaOperationException, IxiaStatsException
log = CafyLog("ixia")
'''
Import IxNetRestApi Modules
#sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/RESTAPItoRESTpy/Modules")
sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules")
# import ixnetwork_restpy
import IxNetRestApi, IxNetRestApiProtocol, \
     IxNetRestApiStatistics, IxNetRestApiFileMgmt, IxNetRestApiPortMgmt, \
     IxNetRestApiTraffic

from IxNetRestApiTraffic import Traffic

# Hubert's notes: This is another Ixia library file that this library file calls
from ixia_ixnetwork import IxNetwork, Traffic, TrafficStats, TgenDevice, NewTrafficItem
from ixia_ixnetwork import IxNetwork

# Import Restpy library
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy.files import Files

#class IXIA(TGN):
class IXIA():
    '''
    IXIA lib
    '''
    def get_handles(self):
        '''
        get handles
        '''
        return list()
    def __init__(self, tgn_server_type='windows', server_ip=None, debug_print=False,
                 time_factor=1.0, verbose=True, **kwargs):
        """
        Initialize the REST API wrapper object.
        IxNetwork version should be 8.0 or above for REST api's to work.
        If the port to connect to is not specified by the port argument,then
        try connecting on the default port, 11009
        :param tgn_server_type (str): The type of IXIA lab server to be used
            e.g. 'windows', 'linux', 'windows_cm' (windows connection manager)
        :param use server_ip same as spirent lib
                server: Ixia REST Tcl server to connect to.
                    if None, raise IxiaConfigException
        :param port: HTTP port to connect to server on.
                    Default is '11009'
        :param debug_print: if True, enable debug print statements
        :param Use time_factor same as spirent lib
                    timer_scale_factor: multiplication factor for the methods using
                    timer_ticks arg. For example:
                    start_traffic() takes 60s default timer_ticks arg.
                    timeout = timer_ticks * timer_scale_factor = 60*1.0=60s
                    If a user wants this method to use 120s timeout,then the
                    timer_scale_factor can be adjusted to 2.0
        :param verbose: verbose
        """
        self.tgn_server_type = tgn_server_type
        if self.tgn_server_type == 'windows':
            self.port = kwargs.get('port', 11009)
        elif self.tgn_server_type == 'linux':
            self.port = kwargs.get('port', 443)
        self.tgn_server_user = kwargs.get('tgn_server_user', 'admin')
        self.tgn_server_pw = kwargs.get('tgn_server_pw', 'admin')

        if ':' in server_ip:
            self.port = server_ip.split(':')[1]
            self.server_ip = server_ip.split(':')[0]
        else:
            self.server_ip = server_ip
        #debug_print = True
        #Connection for internal library
        # Hubert commented out
        '''
        self._rest = RestHttp(server_ip=self.server_ip,
                              port=self.port,
                              timer_factor=time_factor,
                              debug_print=debug_print)
        '''

        if self.tgn_server_type == 'windows':
            #self.ixnObj = IxNetRestApi.Connect(apiServerIp=self.server_ip, serverIpPort=self.port)
            self.testPlatform = TestPlatform(ip_address=self.server_ip, rest_port=self.port, platform='windows', log_file_name='restpy.log')

        elif self.tgn_server_type == 'linux':
            self.testPlatform = TestPlatform(ip_address=self.server_ip, rest_port=self.port, platform='linux', log_file_name='restpy.log')
            self.testPlatform.Authenticate(self.tgn_server_user, self.tgn_server_pw)

        '''
            self.ixnObj = IxNetRestApi.Connect(apiServerIp=self.server_ip,
                                               serverIpPort=self.port,
                                               username=self.tgn_server_user,
                                               password=self.tgn_server_pw,
                                               serverOs=self.tgn_server_type,
                                               deleteSessionAfterTest=False)
        elif self.tgn_server_type == 'windows_cm':
            msg = 'Windows Connection Manager is not yet supported.'
            self._rest.log.info('\n %s' %msg)
            raise IxiaConfigException(msg)
        else:
            msg = 'Invalid IXIA lab server type. Please use windows or linux'
            self._rest.log.info('\n %s %s' % (msg, self.tgn_server_type))
            raise IxiaConfigException(msg)

        self._rest.session_url = self._rest.server_url + '/api/v1/sessions/' + \
                                 str(self.ixnObj.sessionId.rsplit('/')[-1]) + '/ixnetwork'

        # Instantiate all relevant objects from the IxNetRestApi (IXIA Contact: Hubert Gee) library
        #self.ixnObj = IxNetRestApi.Connect(apiServerIp=self.server_ip, serverIpPort=self.port)
        self.protocolObj = IxNetRestApiProtocol.Protocol(self.ixnObj)
        self.portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(self.ixnObj)
        self.trafficObj = IxNetRestApiTraffic.Traffic(self.ixnObj)
        self.statisticsObj = IxNetRestApiStatistics.Statistics(self.ixnObj)
        '''

        # RestPy main entry point object self.ixNetwork
        session = self.testPlatform.Sessions.add()

        self.ixNetwork = session.Ixnetwork
        self.ixNetworkSession = self.testPlatform.Sessions
        self.pxe = list()
        self.interfaces_info = kwargs.get('interfaces', [])
        self.interfaces = dict()
        self.interfaces_by_alias = dict()
        self.interfaces_in_zap = dict()
        self.links = dict()
        self.power_cycle_info = list()

        self.config_file = None
        self.timer_scale_factor = time_factor# default timer  of 1s
        self.verbose = verbose
        self.device_type = kwargs.get('type')
        self.name = kwargs.get('name')
        self.alias = kwargs.get('alias')
        self.platform = kwargs.get('platform')
        self.chassis_ip = kwargs.get('chassis_ip')
        self.slave_chassis = kwargs.get('slave_chassis')

        #
        #self.ixnetwork = IxNetwork(self._rest)
        '''
        self.IxNet = IxNetRestMain(serverIp=self.server_ip,
                                   serverPort=self.port)
        '''

        # RestPy Notes: Instantiate an object to another Ixia library file and pass the restPy object
        self.ixnetwork = IxNetwork(self.ixNetwork)
        
        # self.protoNameToRespyObjDict = {
        #     'isisL3': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().IsisL3,
        #     'lacp': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Lacp,
        #     'mpls': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Mpls,
        #     'ancp': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Ancp,
        #     'bfdv4Interface': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Bfdv4Interface,
        #     'bgpIpv4Peer': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().BgpIpv4Peer,
        #     'bgpIpv6Peer': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().BgpIpv6Peer,
        #     'dhcpv4relayAgent': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Dhcpv4relayAgent,
        #     'dhcpv6relayAgent': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Dhcpv6relayAgent,
        #     'geneve': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Geneve,
        #     'greoipv4': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Greoipv4,
        #     'greoipv6': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Greoipv6,
        #     'igmpHost': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().IgmpHost,
        #     'igmpQuerier': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().IgmpQuerier,
        #     'lac': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Lac,
        #     'ldpBasicRouter': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().LdpBasicRouter,
        #     'ldpBasicRouterV6': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().LdpBasicRouterV6,
        #     'ldpConnectedInterface': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().LdpBasicRouterV6,
        #     'ldpv6ConnectedInterface': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Ldpv6ConnectedInterface,
        #     'ldpTargetedRouter': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().LdpTargetedRouter,
        #     'ldpTargetedRouterV6': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().LdpTargetedRouterV6,
        #     'lns': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Lns,
        #     'mldHost': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().MldHost,
        #     'mldQuerier': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().MldQuerier,
        #     'ptp': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Ptp,
        #     'ipv6sr': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Ipv6sr,
        #     'openFlowController': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().OpenFlowController,
        #     'openFlowSwitch': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().OpenFlowSwitch,
        #     'ospfv2': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Ospfv2,
        #     'ospfv3': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().Ospfv3,
        #     'ovsdbcontroller': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Ovsdbcontroller,
        #     'ovsdbserver': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Ovsdbserver,
        #     'pcc': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Pcc,
        #     'pce': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Pce,
        #     'pcepBackupPCEs':"",
        #     'pimV4Interface': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().PimV4Interface,
        #     'pimV6Interface': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6.find().PimV6Interface,
        #     'rsvpteIf': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().RsvpteIf,
        #     'rsvpteLsps': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().RsvpteLsps,
        #     'tag': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find().Tag,
        #     'vxlan': self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4.find() .Vxlan
        # }
        
        # self.mainObjectToRespyObjDict = {
        #     'topology' : self.ixNetwork.Topology,
        #     'deviceGroup' : self.ixNetwork.Topology.find().DeviceGroup,
        #     'ethernet' : self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet,
        #     'ipv4' : self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv4,
        #     'ipv6' : self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find().Ipv6,
        #     'networkGroup' : self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup,
        #     'ipv4PrefixPools': self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv4PrefixPools,
        #     'ipv6PrefixPools' : self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv6PrefixPools
        # }
        
    
    def new_blank_config(self):
        """
        Upload a blank config file before loading a new config file
        """
        self.ixNetwork.NewConfig()
        
    def getInnerDeviceGroup(self, deviceGroupObj):
            # response = self.ixnObj.get(self.ixnObj.httpHeader + deviceGroupObj + '/deviceGroup')
            # if response.json():
            #     for innerDeviceGroup in response.json()[0]['links']:
            #         innerDeviceGroupObj = innerDeviceGroup['href']
            #         deviceGroupList.append(innerDeviceGroupObj)
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
        topoObj = None
        devGrphrefList = []
        for topology in self.ixNetwork.Topology.find():
            if self.ixNetwork.Vport.find(Name=portName).href in topology.Vports:
                devGrpList = topology.DeviceGroup.find()
        
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
        # queryData = {'from': '/',
        #             'nodes': [{'node': 'topology',    'properties': [], 'where': []},
        #                       {'node': 'deviceGroup', 'properties': [], 'where': []},
        #                       {'node': 'networkGroup',  'properties': [], 'where': []},
        #                       {'node': 'ipv4PrefixPools',  'properties': ['networkAddress'], 'where': []},
        #                       {'node': 'ipv6PrefixPools',  'properties': ['networkAddress'], 'where': []}
        #                       ]}

        # queryResponse = self.ixnObj.query(data=queryData, silentMode=False)

        if '.' in networkGroupIpAddress:
            prefixPoolType = 'ipv4PrefixPools'
        if ':' in networkGroupIpAddress:
            prefixPoolType = 'ipv6PrefixPools'

        # for topology in queryResponse.json()['result'][0]['topology']:
        #     for deviceGroup in topology['deviceGroup']:
        #         for networkGroup in deviceGroup['networkGroup']:
        #             for prefixPool in networkGroup[prefixPoolType]:
        #                 prefixPoolRangeMultivalue = prefixPool['networkAddress']
        #                 response = self.ixnObj.getMultivalueValues(prefixPoolRangeMultivalue)
        #                 if networkGroupIpAddress in response:
        #                     return networkGroup['href']
        grpObj = None
        if prefixPoolType == 'ipv4PrefixPools':
            grpObj = self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv4PrefixPools.find()
        elif prefixPoolType == 'ipv6PrefixPools':
            grpObj = self.ixNetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().Ipv6PrefixPools.find()

        if grpObj is not None:
            netAddr = grpObj.LastNetworkAddress
            print("netAddr and grpObj.LastNetworkAddress", str(netAddr[0]), str(networkGroupIpAddress))
            if str(netAddr[0]) == str(networkGroupIpAddress):
                print("matched value of netAddr", netAddr)
                return grpObj.parent
                
            
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
        
        outPutList = []
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
                    if eval('devGrpObj.Ethernet.find().Ipv4.find().'+ currentProtocol +'.find()'):
                        outPutList.append(eval('devGrpObj.Ethernet.find().Ipv4.find().'+ currentProtocol +'.find()').href)
                    if eval('devGrpObj.Ethernet.find().Ipv6.find().'+ currentProtocol +'.find()'):
                        outPutList.append(eval('devGrpObj.Ethernet.find().Ipv6.find().'+ currentProtocol +'.find()').href)
                except:
                    pass
            if outPutList != []:
                outputDict['deviceGroup'].append(outPutList)
        return outputDict
            
    def getProtocolObjFromProtocolList(self, protocolList, protocol, deviceGroupName=None):
        protoReturnList = []
        if deviceGroupName is None:
            vportList = self.ixNetwork.Vport.find()
            
            for vportObj in vportList:
                protocolList = self.getProtocolListByPortNgpf(portName=vportObj.Name)
                protoList = protocolList['deviceGroup'][0]
                for protoHref in protoList:
                    if protocol in protoHref:
                        print("returning", protoHref)
        else:
            #devGroupObj = self.ixNetwork.Topology.find().DeviceGroup.find(Name=deviceGroupName)
            #outputDict['topology']=devGroupObj.parent.href
                   
            if eval('self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find(Name="MyEth1").Ipv4.find().'+ protocol +'.find()'):
                #protoReturnList.append(self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find(Name="MyEth1").Ipv4.find()'.+protocol.+'find())
                print(eval('self.ixNetwork.Topology.find().DeviceGroup.find().Ethernet.find(Name="MyEth1").Ipv4.find().'+ protocol +'.find()'))
            # if eval('self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv6.find().'+ protocol +'.find()'):
                # protoReturnList.append(self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().Ipv6.find().'+ str(protocol).find())
            # if eval('self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().'+ protocol +'.find()'):
                # protoReturnList.append(self.ixNetwork.Topology.find().DeviceGroup.find(deviceGroupName).Ethernet.find().'+ protocol +'.find())
                
            
            
            
                        
mainObj = IXIA(server_ip="127.0.0.1")
# mainObj.new_blank_config()

portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(mainObj)
protocolObj = IxNetRestApiProtocol.Protocol(mainObj)

ixChassisIp = '10.39.70.159'
portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
protoList = protocolObj.getProtocolListByPortNgpf(port=portList[0])
print(protoList)
# #
# ixChassisIp = '10.39.70.159'
# portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
# #
# portMgmtObj.assignPorts([portList[0]])
# topologyObj1 = protocolObj.createTopologyNgpf(portList=[portList[0]], topologyName="Topo1")
# #topologyObj2 = protocolObj.createTopologyNgpf(portList=[portList[1]], topologyName="Topo2")
# #
# deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG1')
# #                                                        
# #deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
# #                                                        multiplier=1,
# #                                                        deviceGroupName='DG2')
# #
# ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
#                                                ethernetName='MyEth1',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled',
#                                                vlanId={'start': 103,
#                                                        'direction': 'increment',
#                                                          'step':0})                                                    

# ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj1, portName='2/1', ethernetName='EthRenamed')
# ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj1, port=portList[0], ethernetName='EthRenamed_WithPort')
# ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj1, ngpfEndpointName='Topo1', ethernetName='EthRenamed_WithEndPoint')


# ipv6Obj = protocolObj.configIpv6Ngpf(ethernetObj1)
# ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                              # ethernetName='MyEth1',
                                              # macAddress={'start': '00:02:02:00:00:02',
                                                          # 'direction': 'increment',
                                                          # 'step': '00:00:00:00:00:02'},
                                              # macAddressPortStep='disabled',
                                              # vlanId={'start': 106,
                                                      # 'direction': 'increment',
                                                      # 'step':0})
#ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
#                                              ethernetName='MyEth2',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='disabled',
#                                              vlanId={'start': 103,
#                                                      'direction': 'increment',
#                                                      'step':0})
#                                                      
# ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj1,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.1'},
#                                        ipv4AddressPortStep='disabled',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=24,
#                                        resolveGateway=True)

# ipv6Obj1 = protocolObj.configIpv6Ngpf(ethernetObj1,
#                                           ipv6Address={'start': '2001:0:0:1:0:0:0:1',
#                                                        'direction': 'increment',
#                                                        'step': '0:0:0:0:0:0:0:1'},
#                                           ipv6AddressPortStep='disabled',
#                                           gateway={'start': '2001:0:0:1:0:0:0:2',
#                                                    'direction': 'increment',
#                                                    'step': '0:0:0:0:0:0:0:0'},
#                                           gatewayPortStep='disabled',
#                                           prefix=64,
#                                           resolveGateway=True)

# ospfObj2 = protocolObj.configOspfv3(ipv6Obj1, name='ospfv3_stack')
# dhcpClientObj = protocolObj.configDhcpClientV4(ethernetObj1,
#                                                dhcp4Broadcast=True,
#                                                multiplier = 10,
#                                                dhcp4ServerAddress='1.1.1.11',
#                                                dhcp4UseFirstServer=True,
#                                                dhcp4GatewayMac='00:00:00:00:00:00',
#                                                useRapidCommit=False,
#                                                renewTimer=0
#                                            )


#ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj2,
#                                      ipv4Address={'start': '1.1.1.2',
#                                                   'direction': 'increment',
#                                                   'step': '0.0.0.1'},
#                                      ipv4AddressPortStep='disabled',
#                                      gateway={'start': '1.1.1.1',
#                                               'direction': 'increment',
#                                               'step': '0.0.0.0'},
#                                      gatewayPortStep='disabled',
#                                      prefix=24,
#                                      resolveGateway=True)
# ospfObj1 = protocolObj.configOspf(ipv4Obj1,
#                                   name = 'ospf_1',
#                                   areaId = '0',
#                                   neighborIp = '1.1.1.2',
#                                   helloInterval = '10',
#                                   areaIdIp = '0.0.0.0',
#                                   networkType = 'pointtomultipoint',
#                                   deadInterval = '40')
# bgpObj1 = protocolObj.configBgp(ipv4Obj1,
#                                 name = 'bgp_1',
#                                 enableBgp = True,
#                                 holdTimer = 90,
#                                 dutIp={'start': '1.1.1.2', 'direction': 'increment', 'step': '0.0.0.0'},
#                                 localAs2Bytes = 101,
#                                 localAs4Bytes = 108,
#                                 enable4ByteAs = True,
#                                 enableGracefulRestart = False,
#                                 restartTime = 45,
#                                 type = 'internal',
#                                 enableBgpIdSameasRouterId = True)

# bgpObj2 = protocolObj.configBgp(ipv4Obj2,
                                # name = 'bgp_2',
                                # enableBgp = True,
                                # holdTimer = 90,
                                # dutIp={'start': '1.1.1.1', 'direction': 'increment', 'step': '0.0.0.0'},
                                # localAs2Bytes = 101,
                                # enableGracefulRestart = False,
                                # restartTime = 45,
                                # type = 'internal',
                                # enableBgpIdSameasRouterId = True)

# ospfObj1 = protocolObj.configOspf(ipv4Obj1,
#                                   name = 'ospf_1',
#                                   areaId = '0',
#                                   neighborIp = '1.1.1.2',
#                                   helloInterval = '10',
#                                   areaIdIp = '0.0.0.0',
#                                   networkType = 'pointtomultipoint',
#                                   deadInterval = '40')
#protocolObj.startAllProtocols()
#time.sleep(10)
#trafficObj = Traffic(mainObj)
#trafficStatus = trafficObj.configTrafficItem(mode='create',
#                                             trafficItem = {
#                                                'name': 'Topo1 to Topo2',
#                                                'trafficType': 'ipv4',
#                                                'biDirectional': True,
#                                                'srcDestMesh': 'one-to-one',
#                                                'routeMesh': 'oneToOne',
#                                                'allowSelfDestined': False,
#                                                'trackBy': ['flowGroup0', 'vlanVlanId0']
#                                                },
#                                                endpoints = [{'name': 'Flow-Group-1',
#                                                          'sources': [topologyObj1],
#                                                          'destinations': [topologyObj2]
#                                                }],
#                                                configElements = [{'transmissionType': 'fixedFrameCount',
#                                                               'frameCount': 50000,
#                                                               'frameRate': 88,
#                                                               'frameRateType': 'percentLineRate',
#                                                               'frameSize': 128,
#                                                               'portDistribution': 'applyRateToAll',
#                                                               'streamDistribution': 'splitRateEvenly'
#                                                }])

#trafficObj.startTraffic(regenerateTraffic=True, applyTraffic=True)
#time.sleep(10)
#trafficObj.stopTraffic()

#item = trafficObj.getTrafficItemType(trafficItemName='Topo1 to Topo2')
#print(item)

#item = trafficObj.enableTrafficItemByName(trafficItemName='Topo1 to Topo2')
#print(item)
#deviceGroupObj1 = TestPlatform('127.0.0.1').Sessions.find().Ixnetwork.Topology.find(Name='Topo2').DeviceGroup.find()
#mainObj.getInnerDeviceGroup(deviceGroupObj1)

#topoObj1 = mainObj.getTopologyObjAndDeviceGroupObjByPortName(portName='2/1')
#print(topoObj1)

#val = mainObj.getNetworkGroupObjByIp(networkGroupIpAddress='200.1.0.0')
#print(val)

# obj = protocolObj.getNgpfObjectHandleByName(ngpfEndpointObject='topology', ngpfEndpointName='Topo1')
# print(obj)

# protoList = mainObj.getProtocolListByPortNgpf(port=portList[0])
# print(protoList)

# obj = mainObj.getProtocolObjFromProtocolList(protoList['deviceGroup'], 'Ospfv2', 'DG1')
# print(obj)