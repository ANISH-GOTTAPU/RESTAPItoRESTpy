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

ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj1,
                                       ipv4Address={'start': '1.1.1.1',
                                                    'direction': 'increment',
                                                    'step': '0.0.0.1'},
                                       ipv4AddressPortStep='disabled',
                                       gateway={'start': '1.1.1.2',
                                                'direction': 'increment',
                                                'step': '0.0.0.0'},
                                       gatewayPortStep='disabled',
                                       prefix=24,
                                       resolveGateway=False)

ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj2,
                                       ipv4Address={'start': '1.1.1.1',
                                                    'direction': 'increment',
                                                    'step': '0.0.0.0'},
                                       ipv4AddressPortStep='disabled',
                                       gateway={'start': '1.1.1.2',
                                                'direction': 'increment',
                                                'step': '0.0.0.0'},
                                       gatewayPortStep='disabled',
                                       prefix=24,
                                       resolveGateway=False)


ospfObj1 = protocolObj.configOspf(ipv4Obj1,
                                      name = 'ospf_1',
                                      areaId = '0',
                                      neighborIp = '1.1.1.2',
                                      helloInterval = '10',
                                      areaIdIp = '0.0.0.0',
                                      networkType = 'pointtomultipoint',
                                      deadInterval = '40')

ospfObj1 = protocolObj.configOspf(ipv4Obj2,
                                      name = 'ospf_2',
                                      areaId = '34',
                                      neighborIp = '1.1.1.2',
                                      helloInterval = '10',
                                      areaIdIp = '0.0.0.0',
                                      networkType = 'pointtopoint',
                                      deadInterval = '40')

print("******************************* TEST 2 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')
                                                       
ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled')             

ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj1,
                                       ipv4Address={'start': '1.1.1.1',
                                                    'direction': 'increment',
                                                    'step': '0.0.0.1'},
                                       ipv4AddressPortStep='disabled',
                                       gateway={'start': '1.1.1.2',
                                                'direction': 'increment',
                                                'step': '0.0.0.0'},
                                       gatewayPortStep='disabled',
                                       prefix=24,
                                       resolveGateway=False)

ospfObj1 = protocolObj.configOspf(ipv4Obj1,
                                      name = 'ospf_1',
                                      areaId = '0',
                                      neighborIp = '1.1.1.2',
                                      helloInterval = '10',
                                      areaIdIp = '0.0.0.0',
                                      networkType = 'pointtomultipoint',
                                      deadInterval = '40')

ospfObj1 = protocolObj.configOspf(ospfObj1, port=portList[0], name = 'ospf_RenameWithPort') 
time.sleep(5)
ospfObj1 = protocolObj.configOspf(ospfObj1, portName='2/1', name = 'ospf_RenameWithPortName')
time.sleep(5)
ospfObj1 = protocolObj.configOspf(ospfObj1, routerId='192.0.0.1', name = 'ospf_RenameWithRouterId')
