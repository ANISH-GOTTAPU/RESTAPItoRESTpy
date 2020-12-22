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

# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', apiKey='394adace38574cf0b9d94d160e184819', sessionId=3)
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin', sessionId=3)
mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")

mainObj.newBlankConfig()

portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(mainObj)
protocolObj = IxNetRestApiProtocol.Protocol(mainObj)
#
ixChassisIp = '10.39.70.159'
portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
#
portMgmtObj.assignPorts(portList)
topologyObj1 = protocolObj.createTopologyNgpf(portList=[portList[0]], topologyName="Topo1")
topologyObj2 = protocolObj.createTopologyNgpf(portList=[portList[1]], topologyName="Topo2")
#
# print("******************************* TEST 1 *******************************")
# deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG1')
#
# deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG2')
#
# ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
#                                                ethernetName='MyEth1',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled',
#                                                vlanId={'start': 103,
#                                                        'direction': 'increment',
#                                                        'step':0})
#
# ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
#                                              ethernetName='MyEth2',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='disabled',
#                                              vlanId={'start': 103,
#                                                      'direction': 'increment',
#                                                      'step':0})
#
# print("******************************* TEST 2 *******************************")
#
# deviceGroupObj3 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=6,
#                                                     deviceGroupName='DG3')
#
# deviceGroupObj4 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=3,
#                                                        deviceGroupName='DG4')
#
# ethernetObj3 = protocolObj.configEthernetNgpf(deviceGroupObj3,
#                                                ethernetName='MyEth-3',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'decrement',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled',
#                                                vlanId={'start': 103,
#                                                        'direction': 'decrement',
#                                                        'step':5})
#
# ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
#                                              ethernetName='MyEth2',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='disabled',
#                                              vlanId={'start': 103,
#                                                      'direction': 'decrement',
#                                                      'step':4})
#
# print("******************************* TEST 3 *******************************")
#
# deviceGroupObj5 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG5')
#
# deviceGroupObj6 = protocolObj.createDeviceGroupNgpf(topologyObj2,
#                                                        multiplier=1,
#                                                        deviceGroupName='DG6')
#
# ethernetObj5 = protocolObj.configEthernetNgpf(deviceGroupObj5,
#                                                ethernetName='MyEth-3',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'decrement',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='00:00:00:00:00:01')
#
# ethernetObj6 = protocolObj.configEthernetNgpf(deviceGroupObj6,
#                                              ethernetName='MyEth2',
#                                              macAddress={'start': '00:01:02:00:00:01',
#                                                          'direction': 'increment',
#                                                          'step': '00:00:00:00:00:01'},
#                                              macAddressPortStep='00:00:00:00:00:02')

print("******************************* TEST 4 *******************************")
deviceGroupObj5 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG5')

ethernetObj5 = protocolObj.configEthernetNgpf(deviceGroupObj5,
                                               ethernetName='MyEth-3',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'decrement',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='00:00:00:00:00:01')
ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj5, portName='2/1', ethernetName='Eth_WithPortName')
ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj1, port=portList[0], ethernetName='Eth_WithPort')
ethernetObj1 = protocolObj.configEthernetNgpf(ethernetObj1, ngpfEndpointName='Topo1', ethernetName='EthRenamed_WithEndPoint')