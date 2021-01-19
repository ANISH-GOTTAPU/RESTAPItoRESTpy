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

# bgpObj1 = protocolObj.configBgp(ipv4Obj1,
#                                     name = 'bgp_1',
#                                     enableBgp = False,
#                                     holdTimer = 90,
#                                     dutIp={'start': '1.1.1.1', 'direction': 'increment', 'step': '0.0.0.1'},
#                                     localAs2Bytes = 101,
#                                     localAs4Bytes = 108,
#                                     enable4ByteAs = True,
#                                     enableGracefulRestart = False,
#                                     restartTime = 45,
#                                     type = 'internal',
#                                     enableBgpIdSameasRouterId = True)
ospfObj1 = protocolObj.configOspf(ipv4Obj1,
                                      name = 'ospf_1',
                                      areaId = '0',
                                      neighborIp = '1.1.1.2',
                                      helloInterval = '10',
                                      areaIdIp = '0.0.0.0',
                                      networkType = 'pointtomultipoint',
                                      deadInterval = '40')

networkObj, prefixObj = protocolObj.configNetworkGroup(create=deviceGroupObj1)
networkObj, prefixObj = protocolObj.configNetworkGroup(modify=networkObj, networkAddress={'start':'200.0.0.1', 'direction':'increment', 'step':'0.0.0.1'})

networkObj.remove()
print("******************************* TEST 2 *******************************")
networkGrpObj, networkTopoObj = protocolObj.configNetworkGroupWithTopology(create=deviceGroupObj2)
networkGrpObj, networkTopoObj = protocolObj.configNetworkGroupWithTopology(topoType='Ring', modify=networkGrpObj)
print("******************************* TEST 3 *******************************")
networkGrpObj, networkTopoObj = protocolObj.configNetworkGroupWithTopology(create=deviceGroupObj1)
protocolObj.configNetworkTopologyProperty(networkGrpObj, 'OspfPseudoRouter', routerId={'start':'192.0.0.1',
                                                                                       'direction':'increment',
                                                                                       'step':'0.0.0.1'})
