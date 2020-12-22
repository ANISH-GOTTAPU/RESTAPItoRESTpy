import json
import re
import time
import csv
import datetime
import requests
import sys
import os
import tabulate

sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules")
import IxNetRestApi, IxNetRestApiProtocol, \
     IxNetRestApiStatistics, IxNetRestApiFileMgmt, IxNetRestApiPortMgmt, \
     IxNetRestApiTraffic

from IxNetRestApiTraffic import Traffic

from ixia_ixnetwork import IxNetwork

# Import Restpy library
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy.files import Files

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

    def new_blank_config(self):
        """
        Upload a blank config file before loading a new config file
        """
        self.ixNetwork.NewConfig()

mainObj = IXIA(server_ip="127.0.0.1")
mainObj.new_blank_config()

portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(mainObj)
protocolObj = IxNetRestApiProtocol.Protocol(mainObj)
#
ixChassisIp = '10.39.70.159'
portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
#
portMgmtObj.assignPorts(portList)
topologyObj1 = protocolObj.createTopologyNgpf(portList=[portList[0]], topologyName="Topo1")
# topologyObj2 = protocolObj.createTopologyNgpf(portList=[portList[1]], topologyName="Topo2")

# print("******************************* TEST 1 *******************************")
# deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG1')
                                                       
# deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG2')

# ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
#                                                ethernetName='MyEth1',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled')             

# ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
#                                              ethernetName='MyEth2',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='disabled')

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
#                                        resolveGateway=False)

# ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj2,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.0'},
#                                        ipv4AddressPortStep='disabled',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=24,
#                                        resolveGateway=False)

# print("******************************* TEST 2 *******************************")
# deviceGroupObj3 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG3')
                                                       
# deviceGroupObj4 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG4')

# ethernetObj3 = protocolObj.configEthernetNgpf(deviceGroupObj3,
#                                                ethernetName='MyEth3',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled')             

# ethernetObj4 = protocolObj.configEthernetNgpf(deviceGroupObj4,
#                                              ethernetName='MyEth4',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='disabled')

# ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj3,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.1'},
#                                        ipv4AddressPortStep='disabled',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=16,
#                                        resolveGateway=True)

# ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj4,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.0'},
#                                        ipv4AddressPortStep='disabled',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=32,
#                                        resolveGateway=True)

# print("******************************* TEST 3 *******************************")
# deviceGroupObj3 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG3')
                                                       
# deviceGroupObj4 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG4')

# ethernetObj3 = protocolObj.configEthernetNgpf(deviceGroupObj3,
#                                                ethernetName='MyEth3',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='01:00:00:00:00:01')             

# ethernetObj4 = protocolObj.configEthernetNgpf(deviceGroupObj4,
#                                              ethernetName='MyEth4',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='02:00:00:00:00:02')

# ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj3,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.1'},
#                                        ipv4AddressPortStep='11.11.11.11',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=16,
#                                        resolveGateway=True)

# ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj4,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.0'},
#                                        ipv4AddressPortStep='10.10.10.10',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=32,
#                                        resolveGateway=True)

# print("******************************* TEST 4 *******************************")
# deviceGroupObj3 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG3')
                                                       
# deviceGroupObj4 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG4')

# ethernetObj3 = protocolObj.configEthernetNgpf(deviceGroupObj3,
#                                                ethernetName='MyEth3',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='01:00:00:00:00:01')             

# ethernetObj4 = protocolObj.configEthernetNgpf(deviceGroupObj4,
#                                              ethernetName='MyEth4',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='02:00:00:00:00:02')

# ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj3,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.1'},
#                                        ipv4AddressPortStep='11.11.11.11',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=16,
#                                        resolveGateway=True)

# ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj4,
#                                        ipv4Address={'start': '1.1.1.1',
#                                                     'direction': 'increment',
#                                                     'step': '0.0.0.0'},
#                                        ipv4AddressPortStep='10.10.10.10',
#                                        gateway={'start': '1.1.1.2',
#                                                 'direction': 'increment',
#                                                 'step': '0.0.0.0'},
#                                        gatewayPortStep='disabled',
#                                        prefix=32,
#                                        resolveGateway=True)

print("******************************* TEST 5 *******************************")
deviceGroupObj3 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG3')
                                                       
ethernetObj3 = protocolObj.configEthernetNgpf(deviceGroupObj3,
                                               ethernetName='MyEth3',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='01:00:00:00:00:01')             

ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj3,
                                       ipv4Address={'start': '1.1.1.1',
                                                    'direction': 'increment',
                                                    'step': '0.0.0.0'},
                                       ipv4AddressPortStep='10.10.10.10',
                                       gateway={'start': '1.1.1.2',
                                                'direction': 'increment',
                                                'step': '0.0.0.0'},
                                       gatewayPortStep='disabled',
                                       prefix=32,
                                       resolveGateway=True)
ipv4Obj3 = protocolObj.configIpv4Ngpf(ipv4Obj2, name='Ipv4Renaming')
time.sleep(5)
ipv4Obj3 = protocolObj.configIpv4Ngpf(ipv4Obj2, port=portList[0], name='Ipv4Renaming_withPort')
time.sleep(5)
ipv4Obj3 = protocolObj.configIpv4Ngpf(ipv4Obj2, portName='2/1', name='Ipv4Renaming_withPortName')