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

print("******************************* TEST 2 *******************************")
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj2,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                             ethernetName='MyEth2',
                                             macAddress={'start': '00:01:02:00:00:01',
                                                         'direction': 'increment',
                                                         'step': '00:00:00:00:00:01'},
                                             macAddressPortStep='disabled')

ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj1,
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

dhcpServerObj= protocolObj.configDhcpServerV4(ipv4Obj1,
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
                                              poolSize=10
                                          )
dhcpServerObj= protocolObj.configDhcpServerV4(dhcpServerObj,
                                              name='DHCP-Server_Renamed')

# mainObj.ixNetwork.LoadConfig('C:/Keysight/RestPy_Migration/GIT_Repo/RestAPI_To_Restpy_Verification/RestAPI/DhcpServer.ixncfg')
# dhcpServerObj = protocolObj.getEndpointObjByDeviceGroupName('DG 1', 'Dhcpv4server')
# print("printing dhcpServerObj", dhcpServerObj)

# idhcpServerObj= protocolObj.configDhcpServerV4(dhcpServerObj,
#                                               name='DHCP-Server_Renamed')