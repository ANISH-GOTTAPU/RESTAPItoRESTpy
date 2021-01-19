import time
import sys

sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules")
import IxNetRestApi, IxNetRestApiProtocol, IxNetRestApiPortMgmt

from ixia_ixnetwork import IxNetwork

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

bgpObj1 = protocolObj.configBgp(ipv4Obj1,
                                    name = 'bgp_1',
                                    enableBgp = True,
                                    holdTimer = 90,
                                    dutIp={'start': '1.1.1.1', 'direction': 'increment', 'step': '0.0.0.1'},
                                    localAs2Bytes = 101,
                                    localAs4Bytes = 108,
                                    enable4ByteAs = True,
                                    enableGracefulRestart = False,
                                    restartTime = 45,
                                    type = 'internal',
                                    enableBgpIdSameasRouterId = True)

bgpObj2 = protocolObj.configBgp(ipv4Obj2,
                                    name = 'bgp_2',
                                    enableBgp = False,
                                    holdTimer = 60,
                                    dutIp={'start': '2.2.2.2', 'direction': 'increment', 'step': '0.0.0.2'},
                                    localAs2Bytes = 121,
                                    localAs4Bytes = 128,
                                    enable4ByteAs = True,
                                    enableGracefulRestart = False,
                                    restartTime = 65,
                                    type = 'external',
                                    enableBgpIdSameasRouterId = True)

print("******************************* TEST 2 *******************************")
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

bgpObj2 = protocolObj.configBgp(ipv4Obj2,
                                    name = 'bgp_2',
                                    enableBgp = False,
                                    holdTimer = 60,
                                    dutIp={'start': '2.2.2.2', 'direction': 'increment', 'step': '0.0.0.2'},
                                    localAs2Bytes = 121,
                                    localAs4Bytes = 128,
                                    enable4ByteAs = True,
                                    enableGracefulRestart = False,
                                    restartTime = 65,
                                    type = 'external',
                                    enableBgpIdSameasRouterId = True)

print("******************************* TEST 3 *******************************")
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

bgpObj1 = protocolObj.configBgp(bgpObj1, name='BGPRenaming')
time.sleep(5)
bgpObj1 = protocolObj.configIpv4Ngpf(bgpObj1, port=portList[0], name='BgpRenaming_withPort')
time.sleep(5)
bgpObj1 = protocolObj.configIpv4Ngpf(bgpObj1, portName='2/1', name='BgpRenaming_withPortName')
time.sleep(5)
bgpObj1 = protocolObj.configBgp(bgpObj1, routerId='192.0.0.1', name='BgpRenaming_withRouterID')
time.sleep(5)
bgpObj1 = protocolObj.configBgp(bgpObj1, hostIp='1.1.1.1', name='BgpRenaming_withLocalIp')

# input()
# topologyObj1.remove()
# topologyObj2.remove()