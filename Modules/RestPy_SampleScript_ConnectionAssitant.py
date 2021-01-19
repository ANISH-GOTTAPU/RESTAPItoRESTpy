import sys

sys.path.append("C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules")
# import IxNetRestApi, IxNetRestApiProtocol, \
#      IxNetRestApiStatistics, IxNetRestApiFileMgmt, IxNetRestApiPortMgmt, \
#      IxNetRestApiTraffic
from ixnetwork_restpy import TestPlatform
import IxNetRestApi, IxNetRestApiPortMgmt, IxNetRestApiProtocol
# from IxNetRestApiTraffic import Traffic
#
# from ixia_ixnetwork import IxNetwork
#
# # Import Restpy library
# from ixnetwork_restpy.testplatform.testplatform import TestPlatform
# from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
# from ixnetwork_restpy.files import Files

## Test Case 1
## Connects to Linux API server using apiKey, and specific sessionId
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', apiKey='394adace38574cf0b9d94d160e184819', sessionId=3)
# print("session 3 mainObj", mainObj)

## Test Case 2
## Creates a new session in Linux API server
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# print("session 3 mainObj", mainObj)

## Test Case 3
## Connects to Linux API server using username and password and connects to session
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin', sessionId=4)
# print("session 4 mainObj", mainObj)

## Test Case 4:
## Connects to windows API server, to an existing session
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("windows session", mainObj)

## Test Case 5
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# print("windows session", mainObj)
# mainObj.deleteSession()

## Test Case 6
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("windows session", mainObj)
# print("printing ixNetwork version::", mainObj.getIxNetworkVersion())

## Test Case 7
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("windows session", mainObj)
# print("printing session details::", mainObj.getAllSessionId())

## Test Case 8
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# print("windows session", mainObj)
# print("printing session details::", mainObj.getAllSessionId())

## Test Case 9
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# mainObj.connectToLinuxIxosChassis(chassisIp='10.39.70.159', username='admin', password='admin')


## Test Case 10
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj.connectToLinuxIxosChassis(chassisIp='10.39.70.159', username='admin', password='admin')
## Giving below exception:
    # File "C:/Keysight/RestPy_Migration/GIT_Repo/ReadyToCommit/RESTAPItoRESTpy/Modules/RestPy_SampleScript_ConnectionAssitant.py", line 65, in <module>
    #     mainObj.connectToLinuxIxosChassis(chassisIp='10.39.70.159', username='admin', password='admin')
    #   File "C:\Keysight\RestPy_Migration\GIT_Repo\ReadyToCommit\RESTAPItoRESTpy\Modules\IxNetRestApi.py", line 529, in connectToLinuxIxosChassis
    #     self.ixNetwork.ConnectToChassis(chassisIp)
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\testplatform\sessions\ixnetwork\ixnetwork.py", line 515, in ConnectToChassis
    #     return self._execute('connectToChassis', payload=payload, response_object=None)
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\base.py", line 318, in _execute
    #     raise notFoundError
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\base.py", line 311, in _execute
    #     response = self._connection._execute(url, payload)
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\connection.py", line 211, in _execute
    #     return self._send_recv('POST', url, payload)
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\connection.py", line 444, in _send_recv
    #     self._process_response_status_code(url, headers, response)
    #   File "C:\Keysight\RestPy_Migration\IxNetwork-master\venv\lib\site-packages\ixnetwork_restpy\connection.py", line 354, in _process_response_status_code
    #     raise NotFoundError(message, response.status_code)
    # ixnetwork_restpy.errors.NotFoundError: connecttochassis is not a valid operation

## Test Case 11
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# print("Linux server global license", mainObj.linuxServerGetGlobalLicense(linuxServerIp='10.39.70.140'))

## Test Case 12
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("Linux server global license", mainObj.linuxServerGetGlobalLicense(linuxServerIp='127.0.0.1'))

## Test Case 13
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj.configLicenseServerDetails(licenseServer='10.39.70.159', licenseMode='subscription', licenseTier='tier3')

## Test Case 14
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("License details before changing")
# mainObj.showLicenseDetails()
# print("License details after changing")
# mainObj.configLicenseServerDetails(licenseServer='10.39.70.159', licenseMode='subscription', licenseTier='tier3')

## Test Case 15
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# print("active session Ids", mainObj.getAllOpenSessionIds())

## Test Case 16
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# print("active session Ids", mainObj.getAllOpenSessionIds())

## Test Case 17
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', apiKey='394adace38574cf0b9d94d160e184819', sessionId=18)
# mainObj.linuxServerStopAndDeleteSession()

## Test Case 18
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj.linuxServerStopAndDeleteSession()

## Test Case 19
# firstSession = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# secondSession = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# firstSession.linuxServerStopAndDeleteSession()

## Test Case 20
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', apiKey='394adace38574cf0b9d94d160e184819', sessionId=33)
# mainObj.linuxServerWaitForSuccess('/api/v1/sessions/33')

## Test Case 21
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj.linuxServerWaitForSuccess('/api/v1/sessions/41')

## Test Case 21
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# mainObj.linuxServerWaitForSuccess('/api/v1/sessions/31')

## Test Case 21
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# mainObj.linuxServerWaitForSuccess('/api/v1/sessions/1')

## Test Case 21
# mainObj = IxNetRestApi.Connect(apiServerIp="127.0.0.1")
# mainObj.newBlankConfig()
# portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(mainObj)
# protocolObj = IxNetRestApiProtocol.Protocol(mainObj)
# #
# ixChassisIp = '10.39.70.159'
# portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
# #
# portMgmtObj.assignPorts(portList)
# chassis = TestPlatform('127.0.0.1').Sessions.find().Ixnetwork.AvailableHardware.Chassis.find()
# print("refresh hardware")
# mainObj.refreshHardware(chassis)

## Test Case 22
# mainObj = IxNetRestApi.Connect(apiServerIp="10.39.70.140", serverOs='linux', username='admin', password='admin')
# portMgmtObj = IxNetRestApiPortMgmt.PortMgmt(mainObj)
# protocolObj = IxNetRestApiProtocol.Protocol(mainObj)
# #
# ixChassisIp = '10.39.70.159'
# portList = [[ixChassisIp, '2', '1'], [ixChassisIp, '2', '2']]
# #
# portMgmtObj.assignPorts(portList)
# chassis = mainObj.session.Ixnetwork.AvailableHardware.Chassis.find(Hostname="10.39.70.159")
# mainObj.refreshHardware(chassis)

## Test Case 23
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
deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                               ethernetName='MyEth1',
                                               macAddress={'start': '00:01:01:00:00:01',
                                                           'direction': 'increment',
                                                           'step': '00:00:00:00:00:01'},
                                               macAddressPortStep='disabled',
                                               vlanId={'start': 103,
                                                       'direction': 'increment',
                                                       'step':0})
vlanObj = ethernetObj1.Vlan.find()
vlanValue = mainObj.getObjAttributeValue(vlanObj, 'vlanId')
print("vlan values from getObjAttributeValue", vlanValue)

nameValue = mainObj.getObjAttributeValue(ethernetObj1, "Name")
print("name values from getObjAttributeValue", nameValue)
