import time
import sys

sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules")
import IxNetRestApi, IxNetRestApiProtocol, IxNetRestApiPortMgmt

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

print("******************************* TEST 1 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
                                                       multiplier=1,
                                                       deviceGroupName='DG2')

ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled')

ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
                                             ethernetName='MyEth2',
                                             macAddress={'start': '00:01:02:00:00:01',
                                                         'direction': 'increment',
                                                         'step': '00:00:00:00:00:01'},
                                             macAddressPortStep='disabled')

ipv6Obj1 = protocolObj.configIpv6Ngpf(ethernetObj1,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:1',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='disabled',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=64,
                                          resolveGateway=True)

ipv6Obj2 = protocolObj.configIpv6Ngpf(ethernetObj2,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:2',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='2000::1',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=128,
                                          resolveGateway=False)

# print("******************************* TEST 2 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
                                                       multiplier=1,
                                                       deviceGroupName='DG2')

ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled')

ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
                                             ethernetName='MyEth2',
                                             macAddress={'start': '00:01:02:00:00:01',
                                                         'direction': 'increment',
                                                         'step': '00:00:00:00:00:01'},
                                             macAddressPortStep='disabled')

ipv6Obj1 = protocolObj.configIpv6Ngpf(ethernetObj1,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:1',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='disabled',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=64,
                                          resolveGateway=True)

ipv6Obj2 = protocolObj.configIpv6Ngpf(ethernetObj2,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:2',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='2000::1',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=128,
                                          resolveGateway=False)

ospfObj1 = protocolObj.configOspfv3(ipv6Obj1,
                                      name = 'ospf_1',
                                      areaId = '0',
                                      helloInterval = '10',
                                      areaIdIp = '193.0.0.1',
                                      networkType = 'broadcast',
                                      deadInterval = '40')

ospfObj2 = protocolObj.configOspfv3(ipv6Obj2,
                                      name = 'ospf_2',
                                      areaId = '0',
                                      helloInterval = '30',
                                      areaIdIp = '192.0.0.1',
                                      networkType = 'pointtopoint',
                                      deadInterval = '40')

# print("******************************* TEST 3 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
                                                       multiplier=1,
                                                       deviceGroupName='DG2')

ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled')

ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
                                             ethernetName='MyEth2',
                                             macAddress={'start': '00:01:02:00:00:01',
                                                         'direction': 'increment',
                                                         'step': '00:00:00:00:00:01'},
                                             macAddressPortStep='disabled')

ipv6Obj1 = protocolObj.configIpv6Ngpf(ethernetObj1,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:1',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='disabled',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=64,
                                          resolveGateway=True)

ipv6Obj2 = protocolObj.configIpv6Ngpf(ethernetObj2,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:2',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='2000::1',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=128,
                                          resolveGateway=False)

ospfObj1 = protocolObj.configOspfv3(ipv6Obj1,
                                      name = 'ospf_1',
                                      areaId = '45',
                                      helloInterval = '10',
                                      areaIdIp = '193.0.0.1',
                                      networkType = 'pointtopoint',
                                      deadInterval = '40')

ospfObj2 = protocolObj.configOspfv3(ipv6Obj2,
                                      name = 'ospf_2',
                                      areaId = '23',
                                      helloInterval = '39',
                                      areaIdIp = '193.0.0.2',
                                      networkType = 'broadcast',
                                      deadInterval = '140')

print("******************************* TEST 4 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')
                                                       
ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled')

ipv6Obj1 = protocolObj.configIpv6Ngpf(ethernetObj1,
                                          ipv6Address={'start': '2001:0:0:1:0:0:0:1',
                                                       'direction': 'increment',
                                                       'step': '0:0:0:0:0:0:0:1'},
                                          ipv6AddressPortStep='disabled',
                                          gateway={'start': '2001:0:0:1:0:0:0:2',
                                                   'direction': 'increment',
                                                   'step': '0:0:0:0:0:0:0:0'},
                                          gatewayPortStep='disabled',
                                          prefix=64,
                                          resolveGateway=True)

ospfObj1 = protocolObj.configOspfv3(ipv6Obj1,
                                      name = 'ospf_1',
                                      areaId = '45',
                                      helloInterval = '10',
                                      areaIdIp = '193.0.0.1',
                                      networkType = 'pointtopoint',
                                      deadInterval = '40')

ospfObj3 = protocolObj.configOspfv3(ospfObj1, routerId='193.0.0.1', name ='Ospf_withRouterID')
time.sleep(5)

ospfObj3 = protocolObj.configOspfv3(ospfObj3, port=portList[0], name ='Ospf_withPort')
time.sleep(5)

ospfObj3 = protocolObj.configOspfv3(ospfObj3, portName='2/1', name ='Ospf_withPortName')
time.sleep(5)

ospfObj3 = protocolObj.configOspfv3(ospfObj3, ngpfEndpointName='topology' , name ='Ospf_withPortName')
time.sleep(5)

ospfObj3 = protocolObj.configOspfv3(ospfObj3, hostIp='2001:0:0:1:0:0:0:1' , name ='Ospf_withPortName')

print("******************************* TEST 5 *******************************")
# deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
#                                                     multiplier=1,
#                                                     deviceGroupName='DG1')
#
# ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
#                                                ethernetName='MyEth1',
#                                                macAddress={'start': '00:01:01:00:00:01',
#                                                            'direction': 'increment',
#                                                            'step': '00:00:00:00:00:01'},
#                                                macAddressPortStep='disabled')
#
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
# bgpObj2 = protocolObj.configBgpIpv6(ipv6Obj1,
#                                         name = 'bgp_2',
#                                         active = True,
#                                         holdTimer = 90,
#                                         dutIp={'start': '2001:0:0:1:0:0:0:1', 'direction': 'increment', 'step': '0:0:0:0:0:0:0:0'},
#                                         localAs2Bytes = 101,
#                                         enableGracefulRestart = False,
#                                         restartTime = 45,
#                                         type = 'internal',
#                                         enableBgpIdSameasRouterId = True)