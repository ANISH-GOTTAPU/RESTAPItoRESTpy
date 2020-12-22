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

bgpObj1 = protocolObj.configBgp(ipv4Obj1,
                                    name = 'bgp_1',
                                    enableBgp = False,
                                    holdTimer = 90,
                                    dutIp={'start': '1.1.1.1', 'direction': 'increment', 'step': '0.0.0.1'},
                                    localAs2Bytes = 101,
                                    localAs4Bytes = 108,
                                    enable4ByteAs = True,
                                    enableGracefulRestart = False,
                                    restartTime = 45,
                                    type = 'internal',
                                    enableBgpIdSameasRouterId = True)

# print(protocolObj.getBgpObject(bgpAttributeList=['flap', 'uptimeInSec', 'downtimeInSec']))
# print(protocolObj.getBgpObject(bgpAttributeList=['name', 'dutIp', 'type']))
# protocolObj.configNetworkGroup(create=deviceGroupObj1, networkAddress={'start':'200.0.0.1', 'direction':'increment', 'step':'0.0.0.1'})
# networkObj, prefixObj = protocolObj.configNetworkGroup(create=deviceGroupObj1)
# networkObj, prefixObj = protocolObj.configNetworkGroup(modify=networkObj, networkAddress={'start':'200.0.0.1', 'direction':'increment', 'step':'0.0.0.1'})
# protocolObj.configBgpNumberOfAs(routerId='192.0.0.1', numberOfAs=25)
protocolObj.configNetworkGroupWithTopology(create=deviceGroupObj1)

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
#
# ipv6Obj2 = protocolObj.configIpv6Ngpf(ethernetObj2,
#                                           ipv6Address={'start': '2001:0:0:1:0:0:0:2',
#                                                        'direction': 'increment',
#                                                        'step': '0:0:0:0:0:0:0:1'},
#                                           ipv6AddressPortStep='2000::1',
#                                           gateway={'start': '2001:0:0:1:0:0:0:2',
#                                                    'direction': 'increment',
#                                                    'step': '0:0:0:0:0:0:0:0'},
#                                           gatewayPortStep='disabled',
#                                           prefix=128,
#                                           resolveGateway=False)

# protocolObj.showTopologies()