import re
import time
from IxNetRestApi import IxNetRestApiException


class Traffic(object):
    def __init__(self, ixnObj=None):
        self.ixnObj = ixnObj
        self.ixNetwork = ixnObj.ixNetwork
        self.httpHeader = ixnObj.split('/api')[0]

    def setMainObject(self, mainObject):
        # For Python Robot Framework support
        self.ixnObj = mainObject

    def configTrafficItem(self, mode=None, obj=None, trafficItem=None, endpoints=None, configElements=None):
        """
        Description
            Create or modify a Traffic Item.

            When creating a new Traffic Item, this API will return 3 object handles:
                 trafficItemObj, endpointSetObjList and configElementObjList

            NOTE:
                Each Traffic Item could create multiple endpoints and for each endpoint.
                you could provide a list of configElements for each endpoint.
                The endpoints and configElements must be in a list.

                - Each endpointSet allows you to configure the highLevelStream, which overrides configElements.
                - If you set bi-directional to True, then there will be two highLevelStreams that you could configure.
                - Including highLevelStream is optional.  Set highLevelStream to None to use configElements.

        Parameters
            mode: craete|modify

            obj: For "mode=modify" only. Provide the object to modify: trafficItemObj|configElementObj|endpointObj

            trafficItem: Traffic Item kwargs.

            endpoints: [list]: A list: [{name: sources:[], destionations:[], highLevelStreams: None,
            (add more endpoints)... ]
                               Scroll down to see example.

            configElements: [list]: Config Element kwargs.
                                    Each item in this list is aligned to the sequential order of your endpoint list.

        If mode is create:
            The required parameters are: mode, trafficItem, endpoints and configElements

        If mode is modify:
            The required parameters are: mode, obj, and one of the objects to modify (trafficIemObj, endpointObj or
             configElementObj).

            You need to provide the right object handle.

               To modify trafficItem:
                  Ex: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/<id>

               To modify endpointSet:
                  Ex: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/endpointSet/<id>

               To modify configElements = configElement object handlex
                  Ex: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/<id>

               Look at sample script l2l3RestNgpy.py

        Traffic Item Parameters
            trafficType options:
               raw, ipv4, ipv4, ethernetVlan, frameRelay, atm, fcoe, fc, hdlc, ppp

            srcDestMesh:
               Defaults to one-to-one
               Options: manyToMany or fullMesh

            routeMesh:
               fullMesh or oneToOne

            allowSelfDestined: True or False

            trackBy: [list]: trackingenabled0, ethernetIiSourceaddress0, ethernetIiDestinationaddress0,
            ethernetIiPfcQueue0, vlanVlanId0, vlanVlanUserPriority0, ipv4SourceIp0, sourceDestValuePair0,
            sourceDestEndpointPair0, ipv4Precedence0, ipv4SourceIp0, flowGroup0, frameSize0

        ConfigElement Parameters
            transmissionType:
               - continuous|fixedFrameCount|fixedDuration
               - custom (for burstPacketCount)

            frameCount: (For continuous and fixedFrameCount traffic)
            burstPacketCount: (For bursty traffic)
            frameSizeType: fixed|random
            frameSize: The packet size.

            frameRate: The rate to transmit packets
            frameRateType: bitsPerSecond|framesPerSecond|interPacketGap|percentLineRate
            frameRateBitRateUnitsType: bitsPerSec|bytesPerSec|kbitsPerSec|kbytesPerSec|mbitsPerSec|mbytesPerSec
            duration: Set fixedDuration
            portDistribution: applyRateToAll|splitRateEvenly.  Default=applyRateToAll
            streamDistribution: splitRateEvenly|applyRateToAll. Default=splitRateEvently
            trackBy: <list>: Some options: flowGroup0, vlanVlanId0, ethernetIiDestinationaddress0,
            ethernetIiSourceaddress0, sourcePort0, sourceDestPortPair0, ipv4DestIp0, ipv4SourceIp0, ipv4Precedence0,
                             ethernetIiPfcQueue0, frameSize0

        If frameSizeType == random
             incrementFrom: Frame size increment from.
             incrementTo: Frame size increment to.

        For bursty packet count,
              transmissionType = 'custom',
              burstPacketCount = 50000,

        Endpoints Parameters
            A list of topology, deviceGroup or protocol objects
                sources: Object in a list.
                destinations: Object in a lsit.

            Example:
               ['/api/v1/sessions/1/ixnetwork/topology/8']
               or a list ['.../topology/1', '.../topology/3']
               ['.../topology/1/deviceGroup/1', '.../topology/2/deviceGroup/1/ethernet/1/ipv4/1']


        USAGE EXAMPLE:
            To modify:
                trafficObj.configTrafficItem(mode='modify',
                                             obj='/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1',
                                             configElements={'transmissionType': 'continuous'})

                trafficObj.configTrafficItem(mode='modify',
                                             obj='/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1',
                                             trafficItem={'trackBy': ['frameSize0', 'ipv4SourceIp0']})

            To create new Traffic Item:

            configTrafficItem(mode='create',
                              trafficItem = {
                                  'name':'Topo1 to Topo2',
                                  'trafficType':'ipv4',
                                  'biDirectional':True,
                                  'srcDestMesh':'one-to-one',
                                  'routeMesh':'oneToOne',
                                  'allowSelfDestined':False,
                                  'trackBy': ['flowGroup0', 'vlanVlanId0']},

                               endpoints = [{'name':'Flow-Group-1',
                                             'sources': [topologyObj1],
                                            'destinations': [topologyObj2],
                                             'highLevelStreamElements': None}],

                               configElements = [{'transmissionType': 'fixedFrameCount',
                                                  'frameCount': 50000,
                                                  'frameRate': 88,
                                                  'frameRateType': 'percentLineRate',
                                                  'frameSize': 128,
                                                  'portDistribution': 'applyRateToAll',
                                                  'streamDistribution': 'splitRateEvenly'
                                                  }]
            )

            To create a new Traffic Item and configure the highLevelStream:

            trafficObj.configTrafficItem(mode='create',
                                         trafficItem = {'name':'Topo3 to Topo4',
                                                       'trafficType':'ipv4',
                                                       'biDirectional':True,
                                                       'srcDestMesh':'one-to-one',
                                                       'routeMesh':'oneToOne',
                                                       'allowSelfDestined':False,
                                                       'trackBy': ['flowGroup0', 'vlanVlanId0']},
                                         endpoints = [{'name':'Flow-Group-1',
                                                        'sources': [topologyObj1],
                                                        'destinations': [topologyObj2],
                                                        'highLevelStreamElements': [
                                                           {
                                                               'transmissionType': 'fixedFrameCount',
                                                               'frameCount': 10000,
                                                               'frameRate': 18,
                                                               'frameRateType': 'percentLineRate',
                                                               'frameSize': 128},
                                                           {
                                                               'transmissionType': 'fixedFrameCount',
                                                               'frameCount': 20000,
                                                               'frameRate': 28,
                                                               'frameRateType': 'percentLineRate',
                                                               'frameSize': 228}
                                                         ]
                                                     }],
                                         configElements = None)


        Return: trafficItemObj, endpointSetObjList, configElementObjList
        """
        # if mode == 'create':
        #     trafficItemUrl = self.ixnObj.sessionUrl+'/traffic/trafficItem'
        if mode == 'modify' and obj is None:
            raise IxNetRestApiException('Modifying Traffic Item requires a Traffic Item object')
        if mode == 'create' and trafficItem is None:
            raise IxNetRestApiException('Creating Traffic Item requires trafficItem kwargs')
        if mode is None:
            raise IxNetRestApiException('configTrafficItem Error: Must include mode: config or modify')

        if mode == 'create' and trafficItem is not None:
            trafficItemObj = self.ixNetwork.Traffic.TrafficItem.add()
            for item in trafficItem.keys():
                if item != 'trackBy':
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("trafficItemObj." + "update(" + itemObj + " =  trafficItem[item])")

            if 'name' in trafficItem:
                trafficItemObj.Name = trafficItem['name']

            if 'trafficType' in trafficItem:
                trafficItemObj.TrafficType = trafficItem['trafficType']

            if 'biDirectional' in trafficItem:
                trafficItemObj.BiDirectional = trafficItem['biDirectional']

            if 'srcDestMesh' in trafficItem:
                trafficItemObj.SrcDestMesh = trafficItem['srcDestMesh']

            if 'routeMesh' in trafficItem:
                trafficItemObj.RouteMesh = trafficItem['routeMesh']

            if 'allowSelfDestined' in trafficItem:
                trafficItemObj.AllowSelfDestined = trafficItem['allowSelfDestined']

            if 'trackBy' in trafficItem:
                # trafficItemObj.find().Tracking.find().TrackBy = trafficItem['trackBy'][0]
                trafficItemObj.Tracking.find().Values = trafficItem['trackBy']

            if endpoints is not None and trafficItemObj is not None:
                # endPointSetValues = endpoints
                for endPoint in endpoints:
                    endPointSetObj = trafficItemObj.EndpointSet.add(Name=endPoint['name'],
                                                                    Sources=endPoint['sources'],
                                                                    Destinations=endPoint['destinations'])

            if configElements != "" and trafficItemObj is not None:
                configElementObj = trafficItemObj.ConfigElement.find()
                configElementsValues = configElements

                for configElementItem in configElementsValues:
                    if 'transmissionType' in configElementItem:
                        configElementObj.TransmissionControl.Type = configElementItem['transmissionType']
                    if 'frameCount' in configElementItem:
                        configElementObj.TransmissionControl.FrameCount = configElementItem['frameCount']
                    if 'frameRate' in configElementItem:
                        configElementObj.FrameRate.update(Rate=configElementItem['frameRate'])
                    if 'frameRateType' in configElementItem:
                        configElementObj.FrameRate.Type = configElementItem['frameRateType']
                    if 'frameSize' in configElementItem:
                        configElementObj.FrameSize.update(FixedSize=configElementItem['frameSize'])
                    if 'portDistribution' in configElementItem:
                        configElementObj.FrameRateDistribution.PortDistribution = configElementItem[
                            'portDistribution']
                    if 'streamDistribution' in configElementItem:
                        configElementObj.FrameRateDistribution.StreamDistribution = configElementItem[
                            'streamDistribution']

        elif mode == 'modify':
            if trafficItem['name'] != "":
                trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItem['name'])
            if trafficItem['trackBy'] != "":
                trafficItemObj.Tracking.find()

        return [trafficItemObj, endPointSetObj, configElementObj]

    def configConfigElements(self, configElementObj, configElements):
        """
        Description
           Configure Traffic Item Config Elements. This function will collect all the ReST API's attributes
           and execute a PATCH in one single command instead of sending a a PATCH for each attribute.
           This avoids dependency breakage because some APIs require the type to be configured first.

           This function also handles high level stream configurations since the attributes are the same. 
           Pass in the highLevelStream obj for the parameter configElementObj

        Parameters
           configElementObj: <str:obj>: The config element object:
                             Ex: /api/v1/sessions/{1}/ixnetwork/traffic/trafficItem/{1}/configElement/{1}
                             highLevelStream obj Ex: /api/v1/sessions/{1}/ixnetwork/traffic/trafficItem/{1}/
                             highLevelStream/{1}
        
           configElements: <dict>: This could also be highLevelStream elements.  
                           configElements = {'transmissionType': 'fixedFrameCount',
                                              'frameCount': 50000,
                                              'frameRate': 88,
                                              'frameRateType': 'percentLineRate',
                                              'frameSize': 128,
                                              'portDistribution': 'applyRateToAll',
                                              'streamDistribution': 'splitRateEvenly'
                                            }
           transmissionType:   fixedFrameCount|continuous|fixedDuration
           incrementFrom:      For frameSizeType = random.  Frame size from size. 
           incrementTo:        For frameSizeType = random. Frame size to size. 
           frameRateType:      bitsPerSecond|percentLineRate|framesPerSecond
           frameRateBitRateUnitsType:    bitsPerSec|bytesPerSec|kbitsPerSec|kbytesPerSec|mbitsPerSec|mbytesPerSec
           portDistribution:   applyRateToAll|splitRateEvenly. Default=applyRateToAll
           streamDistribution: splitRateEvenly|applyRateToAll. Default=splitRateEvently
        """
        for item in configElements.keys():
            if item in ['burstPacketCount', 'duration', 'frameCount', 'interBurstGap', 'interStreamGap',
                        'iterationCount', 'minGapBytes', 'repeatBurst', 'startDelay']:
                itemObj = item[0:1].capitalize() + item[1:]
                eval("trafficitem.TransmissionControl." + "update(" + itemObj + " =  int(configElements[item]))")

            if item in ['enableInterBurstGap', 'enableInterStreamGap', 'interBurstGapUnits',
                        'startDelayUnits', 'type']:
                itemObj = item[0:1].capitalize() + item[1:]
                eval("trafficitem.TransmissionControl." + "update(" + itemObj + " =  str(configElements[item]))")

            if item == 'frameRateType':
                configElementObj.FrameRate.Type = str(configElements[item])

            if item == 'frameRate':
                configElementObj.FrameRate.Rate = float(configElements[item])

            if item == 'frameRateBitRateUnitsType':
                configElementObj.FrameRate.BitRateUnitsType = str(configElements[item])

            if item == 'portDistribution':
                configElementObj.FrameRateDistribution.PortDistribution = configElements[item]

            if item == 'streamDistribution':
                configElementObj.FrameRateDistribution.StreamDistribution = configElements[item]

        # Note: transmissionType is not an attribute in configElement. It is created to be more descriptive than 'type'.
        if 'transmissionType' in configElements:
            configElementObj.TransmissionControl.Type = configElements['transmissionType']
        if 'frameSize' in configElements:
            configElementObj.FrameSize.FixedSize = int(configElements['frameSize'])

        if 'frameSizeType' in configElements:
            configElementObj.FrameSize.Type = configElements['frameSizeType']
            if configElements['frameSizeType'] == 'random':
                configElementObj.FrameSize.IncrementFrom = configElements['incrementFrom']
                configElementObj.FrameSize.IncrementTo = configElements['incrementTo']

    def getConfigElementObj(self, trafficItemObj=None, trafficItemName=None, endpointSetName=None):
        """
        Description
           Get the config element object handle.

           Use case #1: trafficItemName + endpointSetName
           Use case #2: trafficItemObj + endpointSetName

           Use case #3: trafficItemName only (Will assume there is only one configElement object which will be returned)
           Use case #4: trafficItemObj only  (Will assume there is only one configElement object which will be returned)

        Parameters
             
           trafficItemObj: <str obj>: The Traffic Item object.
           trafficItemName: <str>: The Traffic Item name.
           endpointSetName: <str>: The Traffic Item's EndpointSet name.

           How this works:
               - Users could create multiple EndpointSets within a Traffic Item.
               - Each EndpointSet has a unique object ID by default.
               - For each EndpointSet is created, a config element object is also created.
               - Each config element object handle is associated with an EndpointSet ID.
               - To be able to get the right config element object handle, we need to query
                 for the EndpointSet that you need for modifying.
               - Another terminology for EndpointSet is FlowGroup.
               - If you have multiple EndpointSets, you should give each EndpointSet a name
                 to make querying possible.
               - Otherwise, this function will assume there is only one EndpointSet created which will be returned.

        Usage examples:
           trafficObj.getConfigElementObj(trafficItemName='Raw MPLS/UDP', endpointSetName='EndpointSet-2')

           trafficObj.getConfigElementObj(trafficItemName='Raw MPLS/UDP', endpointSetName=None)

           trafficObj.getConfigElementObj(trafficItemObj='/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1', 
                                          trafficItemName=None, endpointSetName=None)

           trafficObj.getConfigElementObj(trafficItemObj='/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1', 
                                          trafficItemName=None, endpointSetName='EndpointSet-2')

        Return
           configElement: /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}/configElement/{id}
        """
        endpointSetObj = None
        if trafficItemObj:
            trafficItemName = self.getTrafficItemName(trafficItemObj)
        if trafficItemName:
            trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)
            if not trafficItemObj:
                raise IxNetRestApiException('\nError: No traffic item name found: {0}'.format(trafficItemName))
            if endpointSetName:
                endpointSetObj = trafficItemObj.EndpointSet.find(Name=endpointSetName)
                if not endpointSetObj:
                    raise IxNetRestApiException(
                        '\nError: No endpointSet name: {0} found in Traffic Item name: {1}'.format(
                            endpointSetName, trafficItemName))
            if endpointSetName is None:
                endpointSetObj = trafficItemObj.EndpointSet.find()
            endpointSetId = endpointSetObj.href.split('/')[-1]
            configElementObj = trafficItemObj.ConfigElement.find(EndpointSetId=endpointSetId)[0]
            print(configElementObj.href)
            return configElementObj

    def getAllConfigElementObj(self, trafficItemObj):
        """
        Description
           Get all config element objects from a traffic item object.

        Parameter
           trafficItemObj:  /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}

        Return
           A list of configElement objects
        """
        configElementObj = trafficItemObj.ConfigElement.find()
        return configElementObj

    def getTransmissionType(self, configElement):
        return configElement.TransmissionControl.Type

    def configTrafficLatency(self, enabled=True, mode='storeForward'):
        latencyObj = self.ixNetwork.Traffic.Statistics.Latency
        latencyObj.Enabled = enabled
        latencyObj.Mode = mode

    def showProtocolTemplates(self, configElementObj):
        """
        Description
           To show all the protocol template options. Mainly used for adding a protocol header
           to Traffic Item packets.

        Parameters
           configElementObj: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}
        """
        protocolTemplateObj = self.ixNetwork.Traffic.ProtocolTemplate.find()
        for (index, eachProtocol) in enumerate(protocolTemplateObj):
            self.ixnObj.logInfo('%s: %s' % (str(index + 1), eachProtocol.DisplayName), timestamp=False)

    def showTrafficItemPacketStack(self, configElementObj):
        """
        Description
           Display a list of the current packet stack in a Traffic Item

           1: Ethernet II
           2: VLAN
           3: IPv4
           4: UDP
           5: Frame Check Sequence CRC-32

        Parameters
           configElementObj: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}
       """
        print()
        stackObj = configElementObj.Stack.find()
        self.ixnObj.logInfo('\n', timestamp=False)
        for (index, eachStackObj) in enumerate(stackObj):
            self.ixnObj.logInfo('%s: %s' % (str(index + 1), eachStackObj.DisplayName), timestamp=False)

    def addTrafficItemPacketStack(self, configElementObj, protocolStackNameToAdd, stackNumber, action='append'):
        """
        Description
           To either append or insert a protocol stack to an existing packet.

           You must know the exact name of the protocolTemplate to add by calling
           showProtocolTemplates() API and get the exact name  as a value for the parameter protocolStackNameToAdd.

           You must also know where to add the new packet header stack.  Use showTrafficItemPacketStack() to see
           your current stack numbers.

           This API returns the protocol stack object handle so you could use it to config its settings.

         Parameters
           configElementObj: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}

           action:
               append: To add after the specified stackNumber
               insert: To add before the specified stackNumber

           protocolStackNameToAdd: The name of the protocol stack to add.  To get a list of options,
                                   use API showProtocolTemplates().
                                   Some common ones: MPLS, IPv4, TCP, UDP, VLAN, IGMPv1, IGMPv2, DHCP, VXLAN

           stackNumber: The stack number to append or insert into.
                        Use showTrafficItemPacketStack() to view the packet header stack in order to know
                        which stack number to insert your new stack before or after the stack number.

        Example:
            addTrafficItemPacketStack(configElement, protocolStackNameToAdd='UDP',
                                      stackNumber=3, action='append', apiKey=apiKey, verifySslCert=False

        Returns:
            /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}/stack/{id}
        """
        protocolTemplateObj = None
        newStackObj = None
        stackObj = configElementObj.Stack.find()[stackNumber - 1]
        self.showTrafficItemPacketStack(configElementObj)
        protocolTemplatesObj = self.ixNetwork.Traffic.ProtocolTemplate.find()
        protocolTemplateId = None
        for eachProtocol in protocolTemplatesObj:
            if bool(re.match('^%s$' % protocolStackNameToAdd, eachProtocol.DisplayName.strip(), re.I)):
                # /api/v1/sessions/1/traffic/protocolTemplate/30
                protocolTemplateId = eachProtocol.href
                protocolTemplateObj = eachProtocol

        if protocolTemplateId is None:
            raise IxNetRestApiException('No such protocolTemplate name found: {0}'.format(protocolStackNameToAdd))
        self.ixnObj.logInfo('protocolTemplateId: %s' % protocolTemplateId, timestamp=False)
        if action == 'append':
            newStackObj = stackObj.AppendProtocol(protocolTemplateObj)
        if action == 'insert':
            newStackObj = stackObj.InserProtocol(protocolTemplateObj)
        self.ixnObj.logInfo('addTrafficItemPacketStack: Returning: %s' % newStackObj, timestamp=False)
        allStackObj = configElementObj.Stack.find()
        for eachStack in allStackObj:
            if eachStack.href == newStackObj:
                newStackObj = eachStack
        return newStackObj

    def getTrafficItemPktHeaderStackObj(self, configElementObj=None, trafficItemName=None, packetHeaderName=None):
        """
        Description
           Get the Traffic Item packet header stack object based on the displayName.
           To get the displayName, you could call this function: self.showTrafficItemPacketStack(configElementObj)

           For this function, you could either pass in a configElement object or the Traffic Item name.
           
        Parameters
           configElementObj: <str>: Optional: The configElement object.
                             Example: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1

           trafficItemName: <str>: Optional: The Traffic Item name.

           packetHeaderName: <str>: Mandatory: The packet header name.
                             Example: ethernet II, mpls, ipv4, ...

        Return
           The stack object
        """
        if configElementObj is None:
            trafficItem = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)
            if trafficItem is None:
                raise IxNetRestApiException('\nNo such Traffic Item name found: %s' % trafficItemName)
            trafficItemObj = trafficItem.href
            configElementObj = trafficItemObj + '/configElement/1'
        stacks = configElementObj.Stack.find()

        for eachStack in stacks:
            currentStackDisplayName = eachStack.DisplayName.strip()
            self.ixnObj.logInfo('Packet header name: {0}'.format(currentStackDisplayName), timestamp=False)
            if bool(re.match('^{0}$'.format(packetHeaderName), currentStackDisplayName, re.I)):
                self.ixnObj.logInfo('\nstack: {0}: {1}'.format(eachStack, currentStackDisplayName), timestamp=False)
                stackObj = eachStack.href
                return stackObj

        raise IxNetRestApiException(
            '\nError: No such stack name found. Verify stack name existence and spelling: %s' % packetHeaderName)

    def showTrafficItemStackLink(self, configElementObj):
        # Return a list of configured Traffic Item packet header in sequential order.
        #   1: Ethernet II
        #   2: MPLS
        #   3: MPLS
        #   4: MPLS
        #   5: MPLS
        #   6: IPv4
        #   7: UDP
        #   8: Frame Check Sequence CRC-32

        stackList = []
        stackLinkObj = configElementObj.StackLink.find()
        self.ixnObj.logInfo('\n', timestamp=False)
        for eachStackLink in stackLinkObj:
            if eachStackLink.LinkedTo != 'null':
                self.ixnObj.logInfo(eachStackLink.LinkedTo, timestamp=False)
                stackList.append(eachStackLink.LinkedTo)
        return stackList

    def getPacketHeaderStackIdObj(self, configElementObj, stackId):
        """
        Desciption
           This API should be called after calling showTrafficItemPacketStack(configElementObj) in
           order to know the stack ID number to use.  Such as ...

            Stack1: Ethernet II
            Stack2: MPLS
            Stack3: MPLS
            Stack4: MPLS
            Stack5: MPLS
            Stack6: IPv4
            Stack7: UDP
            Stack8: Frame Check Sequence CRC-32

        Parameters
           configElementObj: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}
           stackId: In this example, IPv4 stack ID is 6.

         Return stack ID object: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}/stack/{id}
        """
        stackObj = configElementObj.Stack.find()
        self.ixnObj.logInfo('\n', timestamp=False)
        for (index, eachStackObj) in enumerate(stackObj):
            self.ixnObj.logInfo('{0}: {1}'.format(index + 1, eachStackObj.DisplayName), timestamp=False)
            if stackId == index + 1:
                self.ixnObj.logInfo('\tReturning: %s' % self.httpHeader + eachStackObj.href, timestamp=False)
                return eachStackObj

    def modifyTrafficItemPacketHeader(self, configElementObj, packetHeaderName, fieldName, values):
        """
        Description
           Modify any Traffic Item packet header.  You will need to use the IxNetwor API browser
           to understand the packetHeaderName, fieldName and data to modify.

           Since a Traffic Item could contain many endpointSet (Flow Groups), a Traffic Item could 
           have multiple configElement objects.  A configElementObj is the object handle for an 
           endpointSet.  You have to get the configElement object first.  To get the ConfigElement
           object, you call getConfigElementObj().  

           self.getConfigElementObj(self, trafficItemObj=None, trafficItemName=None, endpointSetName=None):
           Use case #1: trafficItemName + endpointSetName
           Use case #2: trafficItemObj + endpointSetName
           Use case #3: trafficItemName only (Will assume there is only one configElement object which will be returned)
           Use case #4: trafficItemObj only  (Will assume there is only one configElement object which will be returned)

        Parameters
           configElementObj: <str|obj>: The Traffic Item's Config Element object handle.
           packetHeaderName: <str>: The packet header name. You could get the list of names from the 
                                    IxNetwork API browser under trafficItem/{id}/configElement/{id}/stack.
           fieldName: <str>: The packet header field name. View API browser under:
                             trafficItem/{id}/configElement/{id}/stack/{id}/field
           values: <dict>: Any amount of attributes from the /stack/{id}/field/{id} to modify.

        Example:  For IP Precedence TOS 
           packetHeaderName='ipv4'
           fieldName='Precedence'
           values={'fieldValue': '011 Flash'}
        """
        stackIdObj = self.getTrafficItemPktHeaderStackObj(configElementObj=configElementObj,
                                                          packetHeaderName=packetHeaderName)
        self.configPacketHeaderField(stackIdObj, fieldName, values)

    def modifyTrafficItemIpPriorityTos(self, trafficItemObj=None, trafficItemName=None, endpointSetName=None,
                                       packetHeaderName='ipv4', fieldName='Precedence', values=None):
        """
        Description
           Modify a Traffic Item Flow group IP Priority TOS fields.

        Parameters
           value: <dict>: {'fieldValue': '000 Routine'|'001 Priority'|'010 Immediate'|'011 Flash'|'100 Flash Override'
                           '101 CRITIC/ECP'|'110 Internetwork Control'}
        
           trafficItemObj: <str|obj>: The Traffic Item object handle.
           trafficItemName: <str|obj>: The Traffic Item name.
           endpointSetName: <str|obj>: The endpointSet name (Flow-Group).

           Option #1: trafficItemName + endpointSetName
           Option #2: trafficItemObj + endpointSetName
           Option #3: trafficItemName only (Will assume there is only one configElement object)
           Option #4: trafficItemObj only  (Will assume there is only one configElement object)

        Requirement
           Call self.getConfigElementObj() to get the config element object first.

        Example
           trafficObj.modifyTrafficItemIpPriorityTos(trafficItemName='Raw MPLS/UDP',
           values={'fieldValue': '001 Priority'})
        """
        configElementObj = self.getConfigElementObj(trafficItemObj=trafficItemObj, trafficItemName=trafficItemName,
                                                    endpointSetName=endpointSetName)
        self.modifyTrafficItemPacketHeader(configElementObj, packetHeaderName=packetHeaderName,
                                           fieldName=fieldName, values=values)

    def modifyTrafficItemDestMacAddress(self, trafficItemObj=None, trafficItemName=None, endpointSetName=None,
                                        values=None):
        """
        Description
           Modify a Traffic Item Flow group IP Priority TOS fields.

        Parameters
           value: <'str'|dict>: 
                  If str: The mac address address
                  If dict: Any or all the properties and the values:

                          {'valueType': 'increment',
                           'startValue': destMacAddress,
                           'stepValue': '00:00:00:00:00:00',
                           'countValue': 1,
                           'auto': False}
           
           trafficItemObj: <str|obj>: The Traffic Item object handle.
           trafficItemName: <str|obj>: The Traffic Item name.
           endpointSetName: <str|obj>: The endpointSet name (Flow-Group).

           Option #1: trafficItemName + endpointSetName
           Option #2: trafficItemObj + endpointSetName
           Option #3: trafficItemName only (Will assume there is only one configElement object)
           Option #4: trafficItemObj only  (Will assume there is only one configElement object)

        Requirement
           Call self.getConfigElementObj() to get the config element object first.

        Example
           trafficObj.modifyTrafficItemDestMacAddress(trafficItemName='Raw MPLS/UDP', values='00:01:01:02:00:01')
        """

        if type(values) == str:
            values = {'valueType': 'increment',
                      'startValue': values,
                      'stepValue': '00:00:00:00:00:00',
                      'countValue': 1,
                      'auto': False}

        configElementObj = self.getConfigElementObj(trafficItemObj=trafficItemObj, trafficItemName=trafficItemName,
                                                    endpointSetName=endpointSetName)
        self.modifyTrafficItemPacketHeader(configElementObj, packetHeaderName='ethernet',
                                           fieldName='Destination MAC Address', values=values)

    def showPacketHeaderFieldNames(self, stackObj):
        """
        Description
           Get all the packet header field names.

        Parameters
           stackObj = /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}/stack/{id}

        Example for Ethernet stack field names
           1: Destination MAC Address
           2: Source MAC Address
           3: Ethernet-Type
           4: PFC Queue
        """
        self.ixnObj.logInfo('showPacketHeaderFieldNames: %s' % stackObj.href + '/field', timestamp=False)
        stackFieldObj = stackObj.Field.find()
        for (index, eachField) in enumerate(stackFieldObj):
            self.ixnObj.logInfo('\t{0}: {1}'.format(index + 1, eachField.DisplayName), timestamp=False)

    def convertTrafficItemToRaw(self, trafficItemName):
        """
        Description

        Parameter
        """
        trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        if trafficItemObj == 0:
            raise IxNetRestApiException('\nNo such Traffic Item name: %s' % trafficItemName)
        trafficItemObj.ConvertToRaw()

    def configPacketHeaderField(self, stackIdObj, fieldName, data):
        """
        Desciption
            Configure raw packets in a Traffic Item.
            In order to know the field names to modify, use showPacketHeaderFieldNames() to display the names:

        stackIdObj: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/{id}/configElement/{id}/stack/{id}

        fieldName: The field name in the packet header to modify.
                   Example. In a MPLS packet header, the fields would be "Label value", "MPLS Exp", etc.

                   Note: Use showPacketHeaderFieldNames(stackObj) API to dispaly your options.

        data: Example:
             data={'valueType': 'valueList', 'valueList': ['1001', '1002'], auto': False}
             data={'valueType': 'increment', 'startValue': '1.1.1.1', 'stepValue': '0.0.0.1', 'countValue': 2}
             data={'valueType': 'increment', 'startValue': '00:01:01:01:00:01', 'stepValue': '00:00:00:00:00:01'}
             data={'valueType': 'increment', 'startValue': 1001, 'stepValue': 1, 'countValue': 2, 'auto': False}
        
        Example: To modify MPLS field:
            packetHeaderObj = trafficObj.getTrafficItemPktHeaderStackObj(trafficItemName='Raw MPLS/UDP',
            packetHeaderName='mpls')
            trafficObj.configPacketHeaderField(packetHeaderObj,
                                               fieldName='MPLS Exp',
                                               data={'valueType': 'increment',
                                               'startValue': '4',
                                               'stepValue': '1',
                                               'countValue': 1,
                                               'auto': False})
        """
        fieldId = None
        fieldObj = None
        stackFieldObj = stackIdObj.Field.find()
        for (index, eachFieldId) in enumerate(stackFieldObj):
            if bool(re.match(fieldName, eachFieldId.DisplayName, re.I)):
                fieldId = index + 1
                fieldObj = eachFieldId
                break
        if fieldId is None:
            raise IxNetRestApiException('Failed to located your provided fieldName:', fieldName)
        self.ixnObj.logInfo('configPacketHeaderFieldId:  fieldIdObj: %s' % stackIdObj.href + '/field/' + str(fieldId),
                            timestamp=False)
        fieldObj.ValueType = data.get('valueType')
        if data.get('auto'):
            fieldObj.Auto = data['auto']
        if data.get('valueType') == 'singleValue':
            fieldObj.SingleValue = data['singleValue'] if data.get('singleValue') else 0
        elif data.get('valueType') in ['increment', 'decrement']:
            for item in data.keys():
                if item in ['startValue', 'stepValue', 'countValue']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
        elif data.get('valueType') == 'valueList':
            if data.get('valueList'):
                fieldObj.ValueList = data['valueList']
        elif data.get('valueType') == 'random':
            for item in data.keys():
                if item in ['countValue', 'seed', 'randomMask', 'fixedBits']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
        elif data.get('valueType') == 'repeatableRandomRange':
            for item in data.keys():
                if item in ['countValue', 'seed', 'stepValue', 'maxValue', 'minValue']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
        elif data.get('valueType') == 'nonRepeatableRandom':
            for item in data.keys():
                if item in ['randomMask', 'fixedBits']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")

    def getPacketHeaderAttributesAndValues(self, streamObj, packetHeaderName, fieldName):
        """
        Parameters
           streamObj: <str>: configElementObj|highLevelStreamObj
                      Ex: /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{1}/configElement/{id} 
                       or /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{1}/highLevelStream/{id}

           packetHeaderName: <str>: Display Name of the stack.  Example: Ethernet II, VLAN, IPv4, TCP, etc. 

           fieldName: <str>: Display Name of the field.  Example: If packetHeaderName is Ethernet II, field names
           could be Destination MAC Address, Source MAC Address, Ethernet-Type and PFC Queue.
                                    You will have to know these field names. To view them, make your configurations
                                    and then go on the API browser and go to:

                            /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{1}/configElement/{id}/stack/{id}/field

        Example:
            streamObj = '/api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}/configElement/{id}'
            data= trafficObj.getPacketHeaderAttributesAndValues(streamObj,
                                                                'Ethernet II', 'Source MAC Address')
            data['singleValue'] = For single value.
            data['startValue'] = If it is configured to increment.

        Returns
            All the attributes and values in JSON format.
        """
        stackObj = streamObj.Stack.find()
        for eachStack in stackObj:
            if packetHeaderName == eachStack.DisplayName.strip():
                fieldObj = eachStack.Field.find()
                for eachField in fieldObj:
                    if fieldName == eachField.DisplayName:
                        return eachField

    def configEgressCustomTracking(self, trafficItemObj, offsetBits, widthBits):
        """
        Description
           Configuring custom egress tracking. User must know the offset and the bits width to track.
           In most use cases, packets ingressing the DUT gets modified by the DUT and to track the
           correctness of the DUT's packet modification, use this API to verify the receiving port's packet
           offset and bit width.
        """
        self.applyTraffic()
        egressObj = trafficItemObj.Tracking.find().Egress
        egressObj.Encapsulation = 'Any: Use Custom Settings'
        egressObj.CustomOffsetBits = offsetBits
        egressObj.CustomWidthBits = widthBits
        trafficItemObj.EgressEnabled = True
        self.regenerateTrafficItems()
        self.applyTraffic()

    def createEgressStatView(self, trafficItemObj, egressTrackingPort, offsetBit, bitWidth,
                             egressStatViewName='EgressStatView', ingressTrackingFilterName=None):
        """
        Description
           Create egress statistic view for egress stats.

        """
        egressTrackingOffsetFilter = 'Custom: ({0}bits at offset {1})'.format(int(bitWidth), int(offsetBit))
        trafficItemName = self.getTrafficItemName(trafficItemObj)
        self.ixnObj.logInfo('Creating new statview for egress stats...')
        egressStatViewObj = self.ixNetwork.Statistics.View.add(Caption=egressStatViewName,
                                                               TreeViewNodeName='Egress Custom Views',
                                                               Type='layer23TrafficFlow', Visible=True)
        self.ixnObj.logInfo('egressStatView Object: %s' % egressStatViewObj.href)

        self.ixnObj.logInfo('Creating layer23TrafficFlowFilter')
        # Dynamically get the PortFilterId
        availablePortFilterObj = egressStatViewObj.AvailablePortFilter.find()
        portFilterId = []
        for eachPortFilterId in availablePortFilterObj:
            # 192.168.70.10/Card2/Port1
            self.ixnObj.logInfo('\tAvailable PortFilterId: %s' % eachPortFilterId.Name, timestamp=False)
            if eachPortFilterId.Name == egressTrackingPort:
                self.ixnObj.logInfo('\tLocated egressTrackingPort: %s' % egressTrackingPort, timestamp=False)
                portFilterId.append(eachPortFilterId.href)
                break
        if not portFilterId:
            raise IxNetRestApiException('No port filter ID found')
        self.ixnObj.logInfo('PortFilterId: %s' % portFilterId)
        # Dynamically get the Traffic Item Filter ID
        availableTrafficItemFilterObj = egressStatViewObj.AvailableTrafficItemFilter.find()
        availableTrafficItemFilterId = []
        for eachTrafficItemFilterId in availableTrafficItemFilterObj:
            if eachTrafficItemFilterId.Name == trafficItemName:
                availableTrafficItemFilterId.append(eachTrafficItemFilterId.href)
                break
        if not availableTrafficItemFilterId:
            raise IxNetRestApiException('No traffic item filter ID found.')
        self.ixnObj.logInfo('availableTrafficItemFilterId: %s' % availableTrafficItemFilterId, timestamp=False)
        # /api/v1/sessions/1/ixnetwork/statistics/view/12
        self.ixnObj.logInfo('egressStatView: %s' % egressStatViewObj.href, timestamp=False)
        layer23TrafficFlowFilterObj = egressStatViewObj.Layer23TrafficFlowFilter.find()
        self.ixnObj.logInfo('layer23TrafficFlowFilter: %s' % layer23TrafficFlowFilterObj, timestamp=False)
        layer23TrafficFlowFilterObj.EgressLatencyBinDisplayOption = 'showEgressRows'
        layer23TrafficFlowFilterObj.TrafficItemFilterId = availableTrafficItemFilterId[0]
        layer23TrafficFlowFilterObj.PortFilterIds = portFilterId
        layer23TrafficFlowFilterObj.TrafficItemFilterIds = availableTrafficItemFilterId
        # Get the egress tracking filter
        egressTrackingFilter = None
        ingressTrackingFilter = None
        availableTrackingFilterObj = egressStatViewObj.AvailableTrackingFilter.find()
        self.ixnObj.logInfo('Available tracking filters for both ingress and egress...', timestamp=False)
        for (index, eachTrackingFilter) in enumerate(availableTrackingFilterObj):
            self.ixnObj.logInfo('\tFilter Name: {0}: {1}'.format(str(index + 1), eachTrackingFilter.Name),
                                timestamp=False)
            if bool(re.match('Custom: *\([0-9]+ bits at offset [0-9]+\)', eachTrackingFilter.Name)):
                egressTrackingFilter = eachTrackingFilter.href

            if ingressTrackingFilterName is not None:
                if eachTrackingFilter.Name == ingressTrackingFilterName:
                    ingressTrackingFilter = eachTrackingFilter.href
        if egressTrackingFilter is None:
            raise IxNetRestApiException('Failed to locate your defined custom offsets: {0}'.
                                        format(egressTrackingOffsetFilter))
        # /api/v1/sessions/1/ixnetwork/statistics/view/23/availableTrackingFilter/3
        self.ixnObj.logInfo('Located egressTrackingFilter: %s' % egressTrackingFilter, timestamp=False)
        enumerationFilterObj = layer23TrafficFlowFilterObj.EnumerationFilter.add(SortDirection='ascending',
                                                                                 TrackingFilterId=egressTrackingFilter)
        if ingressTrackingFilterName is not None:
            self.ixnObj.logInfo('Located ingressTrackingFilter: %s' % ingressTrackingFilter, timestamp=False)
            enumerationFilterObj = layer23TrafficFlowFilterObj.EnumerationFilter.add(SortDirection='ascending',
                                                                                     TrackingFilterId=ingressTrackingFilter)
        statisticObj = egressStatViewObj.Statistic.find()
        for eachEgressStatCounter in statisticObj:
            eachStatCounterObject = eachEgressStatCounter
            eachStatCounterName = eachEgressStatCounter.Caption
            self.ixnObj.logInfo('\tEnabling egress stat counter: %s' % eachStatCounterName, timestamp=False)
            eachStatCounterObject.Enabled = True
        egressStatViewObj.Enabled = True
        self.ixnObj.logInfo('createEgressCustomStatView: Done')

        return egressStatViewObj

    def enableTrafficItem(self, trafficItemNumber):
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()[trafficItemNumber - 1]
        trafficItemObj.Enabled = True

    def disableTrafficItem(self, trafficItemNumber):
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()[trafficItemNumber - 1]
        trafficItemObj.Enabled = False

    def enableAllTrafficItems(self, mode=True):
        """
        Description
           Enable or Disable all Traffic Items.
         
        Parameter
           mode: True|False
                 True: Enable all Traffic Items
                 False: Disable all Traffic Items
        """
        trafficItemsObj = self.ixNetwork.Traffic.TrafficItem.find()
        for trafficItem in trafficItemsObj:
            trafficItem.Enabled = mode

    def isTrafficItemNameExists(self, trafficItemName):
        """
        Description
           Verify if the Traffic Item name exists in the configuration.

        Parameter
           trafficItemName: The Traffic Item name to verify
        """
        trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        if trafficItemObj != 0:
            return True
        return False

    def enablePacketLossDuration(self):
        self.ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = True

    def disablePacketLossDuration(self):
        self.ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = False

    def getTrafficItemStatus(self, trafficItemObj):
        return trafficItemObj.State

    def checkTrafficItemState(self, trafficItemList=None, expectedState=['stopped'], timeout=60, ignoreException=False):
        """
        Description
            Check the traffic item expected state.
            This is best used to verify that traffic has started before calling getting stats.

        Traffic states are:
            startedWaitingForStats, startedWaitingForStreams, started, stopped,
            stoppedWaitingForStats, txStopWatchExpected, locked, unapplied

        Parameters
            trafficItemList: <list|objects>: A list of traffic item objects: 
                             Ex: ['/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1']
            expectedState: <str>:  Input a list of expected traffic state.
                            Example: ['started', startedWaitingForStats'] <-- This will wait until stats has arrived.

            timeout: <int>: The amount of seconds you want to wait for the expected traffic state.
                      Defaults to 45 seconds.
                      In a situation where you have more than 10 pages of stats, you will
                      need to increase the timeout time.

            ignoreException: <bool>: If True, return 1 as failed, and don't raise an Exception.

        Return
            1: If failed.
        """
        if type(expectedState) != list:
            expectedState.split(' ')

        self.ixnObj.logInfo('checkTrafficState: Expecting state: {0}\n'.format(expectedState))
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()
        if trafficItemList is None:
            trafficItemList = trafficItemObj

        for eachTrafficItem in trafficItemList:
            for counter in range(1, timeout + 1):
                currentTrafficState = eachTrafficItem.State

                if currentTrafficState == 'unapplied':
                    self.ixnObj.logWarning('\nCheckTrafficState: Traffic is UNAPPLIED')
                    self.applyTraffic()

                self.ixnObj.logInfo('\ncheckTrafficState: {}'.format(eachTrafficItem))
                self.ixnObj.logInfo(
                    '\t{trafficState}: Expecting: {expectedStates}.'.format(trafficState=currentTrafficState,
                                                                            expectedStates=expectedState),
                    timestamp=False)

                self.ixnObj.logInfo('\tWaited {counter}/{timeout} seconds'.format(counter=counter, timeout=timeout),
                                    timestamp=False)

                if counter <= timeout and currentTrafficState not in expectedState:
                    time.sleep(1)
                    continue

                if counter <= timeout and currentTrafficState in expectedState:
                    self.ixnObj.logInfo('checkTrafficState: {}: Done\n'.format(eachTrafficItem))
                    break

                if counter == timeout and currentTrafficState not in expectedState:
                    if not ignoreException:
                        raise IxNetRestApiException('checkTrafficState: Traffic item state did not reach the expected '
                                                    'state(s): {0}: {1}. It is at: {2}'
                                                    .format(eachTrafficItem, expectedState, currentTrafficState))
                    else:
                        return 1

    def checkTrafficState(self, expectedState=['stopped'], timeout=60, ignoreException=False):
        """
        Description
            Check the traffic state for the expected state.
            This is best used to verify that traffic has started before calling getting stats.

        Traffic states are:
            startedWaitingForStats, startedWaitingForStreams, started, stopped,
            stoppedWaitingForStats, txStopWatchExpected, locked, unapplied

        Parameters
            expectedState: <str>:  Input a list of expected traffic state.
                            Example: ['started', startedWaitingForStats'] <-- This will wait until stats has arrived.

            timeout: <int>: The amount of seconds you want to wait for the expected traffic state.
                      Defaults to 45 seconds.
                      In a situation where you have more than 10 pages of stats, you will
                      need to increase the timeout time.

            ignoreException: <bool>: If True, return 1 as failed, and don't raise an Exception.

        Return
            1: If failed.
        """
        currentTrafficState = None
        if type(expectedState) != list:
            expectedState.split(' ')

        self.ixnObj.logInfo('checkTrafficState: Expecting state: {0}\n'.format(expectedState))
        for counter in range(1, timeout + 1):
            # response = self.ixnObj.get(self.ixnObj.sessionUrl+'/traffic', silentMode=True)
            currentTrafficState = self.ixNetwork.Traffic.State
            if currentTrafficState == 'unapplied':
                self.ixnObj.logWarning('\nCheckTrafficState: Traffic is UNAPPLIED')
                self.applyTraffic()

            self.ixnObj.logInfo('\ncheckTrafficState: {trafficState}: Expecting: {expectedStates}.'.
                                format(trafficState=currentTrafficState, expectedStates=expectedState), timestamp=False)
            self.ixnObj.logInfo('\tWaited {counter}/{timeout} seconds'.format(counter=counter, timeout=timeout),
                                timestamp=False)

            if counter <= timeout and currentTrafficState not in expectedState:
                time.sleep(1)
                continue

            if counter <= timeout and currentTrafficState in expectedState:
                time.sleep(8)
                self.ixnObj.logInfo('checkTrafficState: Done\n')
                return 0

        if not ignoreException:
            raise IxNetRestApiException('checkTrafficState: Traffic state did not reach the expected state(s): {0}. '
                                        'It is at: {1}'.format(expectedState, currentTrafficState))
        else:
            return 1

    def getRawTrafficItemSrcIp(self, trafficItemName):
        """
        Description
            Get the Raw Traffic Item source IP address. Mainly to look up each Device Group
            IPv4 that has the source IP address to get the gateway IP address.

        Parameter
            trafficItemName: The Raw Traffic Item name
        """
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)
        fieldObj = trafficItemObj.ConfigElement.find().Stack.find(StackTypeId="ipv4").Field.find(
            FieldTypeId="ipv4.header.srcIp")
        sourceIp = fieldObj.FieldValue
        return sourceIp

    def getTrafficItemType(self, trafficItemName):
        """
        Description
            Get the Traffic Item traffic type by the Traffic Item name.

        Parameter
            trafficItemName: The Traffic Item name

        Return
            The traffic type
        """
        trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        if trafficItemObj == 0:
            raise IxNetRestApiException('\nNo such Traffic Item name: %s' % trafficItemName)
        return trafficItemObj.TrafficItemType

    def enableTrafficItemByName(self, trafficItemName, enable=True):
        """
        Description
            Enable or Disable a Traffic Item by its name.

        Parameter
            trafficItemName: The exact spelling of the Traffic Item name.
            enable: True | False
                    True: Enable Traffic Item
                    False: Disable Traffic Item
        """
        trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        if trafficItemObj == 0:
            raise IxNetRestApiException('\nNo such Traffic Item name: %s' % trafficItemName)
        trafficItemObj.Enabled = enable

    def getTrafficItemName(self, trafficItemObj):
        """
        Description
            Get the Traffic Item name by its object.

        Parameter
            trafficItemObj: The Traffic Item object.
                            /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1
        """
        return trafficItemObj.Name

    def getAllTrafficItemObjects(self, getEnabledTrafficItemsOnly=False):
        """
        Description
            Get all the Traffic Item objects. 
            Due to the 100 items limit on REST call, using skip and take to break down the large list.
        
        Parameter
            getEnabledTrafficItemOnly: <bool>
        Return
            A list of Traffic Items
        """
        trafficItemObjList = []
        numOfTrafficItem = 0
        response = self.ixnObj.get(
            self.ixnObj.sessionUrl + '/traffic/trafficItem' + "?skip=" + str(numOfTrafficItem) + "&take=100")

        while numOfTrafficItem < response.json()['count']:
            for eachTrafficItem in response.json()['data']:
                if getEnabledTrafficItemsOnly:
                    if eachTrafficItem['enabled']:
                        trafficItemObjList.append(eachTrafficItem['links'][0]['href'])
                else:
                    trafficItemObjList.append(eachTrafficItem['links'][0]['href'])
            numOfTrafficItem += 100
            response = self.ixnObj.get(
                self.ixnObj.sessionUrl + '/traffic/trafficItem' + "?skip=" + str(numOfTrafficItem) + "&take=100")

        return trafficItemObjList

    def getAllTrafficItemNames(self):
        """
        Description
            Return all of the Traffic Item names.
        """
        trafficItemNameList = []
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()
        for eachTrafficItem in trafficItemObj:
            trafficItemNameList.append(eachTrafficItem.Name)
        return trafficItemNameList

    def getTrafficItemObjByName_backup(self, trafficItemName):
        """
        Description
            Get the Traffic Item object by the Traffic Item name.

        Parameter
            trafficItemName: Name of the Traffic Item.

        Return
            0: No Traffic Item name found. Return 0.
            traffic item object:  /api/v1/sessions/1/ixnetwork/traffic/trafficItem/2
        """
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)
        try:
            return trafficItemObj
        except:
            return 0

    def getTrafficItemObjByName(self, trafficItemName):
        """
        Description
            Get the Traffic Item object by the Traffic Item name.

        Parameter
            trafficItemName: Name of the Traffic Item.

        Return
            0: No Traffic Item name found. Return 0.
            traffic item object:  /api/v1/sessions/1/ixnetwork/traffic/trafficItem/2
        """
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)
        try:
            return trafficItemObj
        except:
            return 0

    def applyTraffic(self):
        """
        Description
            Apply the configured traffic.
        """
        self.ixNetwork.Traffic.Apply()

    def regenerateTrafficItems(self, trafficItemList='all'):
        """
        Description
            Performs regenerate on Traffic Items.

        Parameter
            trafficItemList: 'all' will automatically regenerate from all Traffic Items.
                             Or provide a list of Traffic Items.
                             ['/api/v1/sessions/1/ixnetwork/traffic/trafficItem/1', ...]
        """
        trafficItemObjList = []
        trafficItemHrefList = []
        if trafficItemList == 'all':
            trafficItemsObj = self.ixNetwork.Traffic.TrafficItem.find()
            for eachTrafficItem in trafficItemsObj:
                trafficItemHrefList.append(eachTrafficItem.href)
                trafficItemObjList.append(eachTrafficItem)
        elif type(trafficItemList) != list:
            trafficItemList = trafficItemList.split(' ')
            for eachTrafficItem in trafficItemList:
                trafficItemHrefList.append(eachTrafficItem.href)
                trafficItemObjList.append(eachTrafficItem)
        self.ixnObj.logInfo('Regenerating traffic items: %s' % trafficItemList)
        for eachTrafficItem in trafficItemObjList:
            eachTrafficItem.Generate()

    def startTraffic(self, regenerateTraffic=True, applyTraffic=True, blocking=False):
        """
        Description
            Start traffic and verify traffic is started.
            This function will also give you the option to regenerate and apply traffic.

        Parameter
            regenerateTraffic: <bool>
                          
            applyTraffic: <bool> 
                          In a situation like packet capturing, you cannot apply traffic after
                          starting packet capture because this will stop packet capturing. 
                          You need to set applyTraffic to False in this case.

            blocking: <bool> If True, API server doesn't return until it has
                             started traffic and ready for stats.  Unblocking is the opposite.

        Syntax
            For blocking state:
               POST:  /api/v1/sessions/{id}/ixnetwork/traffic/operations/startstatelesstrafficblocking'
               DATA:  {arg1: ['/api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}' ...]}

            For non blocking state:
               POST: /api/v1/sessions/1/ixnetwork/traffic/operations/start
               DATA: {arg1: '/api/v1/sessions/{id}/ixnetwork/traffic'}

        Requirements:
            For non blocking state only:

               # You need to check the traffic state before getting stats.
               # Note: Use the configElementObj returned by configTrafficItem()
               if trafficObj.getTransmissionType(configElementObj) == "fixedFrameCount":
                   trafficObj.checkTrafficState(expectedState=['stopped', 'stoppedWaitingForStats'], timeout=45)

               if trafficObj.getTransmissionType(configElementObj) == "continuous":
                   trafficObj.checkTrafficState(expectedState=['started', 'startedWaitingForStats'], timeout=45)
        """
        if regenerateTraffic:
            self.regenerateTrafficItems()

        if applyTraffic:
            self.applyTraffic()

        if not blocking:
            url = self.ixnObj.sessionUrl + '/traffic/operations/start'
            response = self.ixnObj.post(url, data={'arg1': self.ixnObj.sessionUrl + '/traffic'})
            self.ixnObj.waitForComplete(response, url + '/' + response.json()['id'], timeout=120)

        # Server will go into blocking state until it is ready to accept the next api command.
        if blocking:
            enabledTrafficItemList = self.getAllTrafficItemObjects(getEnabledTrafficItemsOnly=True)
            url = self.ixnObj.sessionUrl + '/traffic/trafficItem/operations/startstatelesstrafficblocking'
            response = self.ixnObj.post(url, data={'arg1': enabledTrafficItemList})
            self.ixnObj.waitForComplete(response, url + '/' + response.json()['id'], timeout=120)

    def stopTraffic(self, blocking=False):
        """
        Description
            Stop traffic and verify traffic has stopped.

        Parameters
           blocking: <bool>: True=Synchronous mode. Server will not accept APIs until the process is complete.

        Syntax
            For blocking state:
               POST: /api/v1/sessions/{id}/ixnetwork/traffic/operations/stopstatelesstrafficblocking
               DATA:  {arg1: ['/api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}' ...]}

            For non blocking state:
               POST: /api/v1/sessions/{id}/ixnetwork/traffic/operations/stop
               DATA: {'arg1': '/api/v1/sessions/{id}/ixnetwork/traffic'}
        """
        if blocking:
            enabledTrafficItemList = self.getAllTrafficItemObjects(getEnabledTrafficItemsOnly=True)
            url = self.ixnObj.sessionUrl + '/traffic/operations/stopstatelesstrafficblocking'
            response = self.ixnObj.post(url, data={'arg1': enabledTrafficItemList})
            self.ixnObj.waitForComplete(response, url + '/' + response.json()['id'], timeout=120)

        if not blocking:
            self.ixnObj.logInfo('stopTraffic: %s' % self.ixnObj.sessionUrl + '/traffic/operations/stop')
            url = self.ixnObj.sessionUrl + '/traffic/operations/stop'
            response = self.ixnObj.post(url,
                                        data={'arg1': '{0}/ixnetwork/traffic'.format(self.ixnObj.headlessSessionId)})
            self.ixnObj.waitForComplete(response, url + '/' + response.json()['id'], timeout=120)

        self.checkTrafficState(expectedState=['stopped'])
        time.sleep(3)

    def showTrafficItems(self):
        """
        Description
            Show All Traffic Item details.
        """
        trafficItemsObj = self.ixNetwork.Traffic.TrafficItem.find()
        self.ixnObj.logInfo('\n', end='', timestamp=False)
        for (index, trafficItem) in enumerate(trafficItemsObj):
            self.ixnObj.logInfo('TrafficItem: {0}\n\tName: {1}  Enabled: {2}  State: {3}'.format(
                index + 1, trafficItem.Name, trafficItem.Enabled, trafficItem.State), timestamp=False)
            self.ixnObj.logInfo('\tTrafficType: {0}  BiDirectional: {1}'.format(trafficItem.TrafficType,
                                                                                trafficItem.BiDirectional),
                                timestamp=False)

            for tracking in trafficItem.Tracking.find():
                self.ixnObj.logInfo('\tTrackings: {0}'.format(tracking.TrackBy), timestamp=False)

            for endpointSet, cElement in zip(trafficItem.EndpointSet.find(), trafficItem.ConfigElement.find()):
                self.ixnObj.logInfo('\tEndpointSetId: {0}  EndpointSetName: {1}'.format(endpointSet.index,
                                                                                        endpointSet.Name),
                                    timestamp=False)
                srcList = []
                for src in endpointSet.Sources:
                    srcList.append(src.split('/ixnetwork')[1])

                dstList = []
                for dest in endpointSet.Destinations:
                    dstList.append(dest.split('/ixnetwork')[1])

                self.ixnObj.logInfo('\t    Sources: {0}'.format(srcList), timestamp=False)
                self.ixnObj.logInfo('\t    Destinations: {0}'.format(dstList), timestamp=False)
                self.ixnObj.logInfo('\t    FrameType: {0}  FrameSize: {1}'.format(cElement.FrameSize.Type,
                                                                                  cElement.FrameSize.FixedSize),
                                    timestamp=False)
                self.ixnObj.logInfo('\t    TranmissionType: {0}  FrameCount: {1}  BurstPacketCount: {2}'.format(
                    cElement.TransmissionControl.Type, cElement.TransmissionControl.FrameCount,
                    cElement.TransmissionControl.BurstPacketCount), timestamp=False)

                self.ixnObj.logInfo('\t    FrameRateType: {0}  FrameRate: {1}'.format(
                    cElement.FrameRate.Type, cElement.FrameRate.Rate), timestamp=False)

            self.ixnObj.logInfo('\n', end='', timestamp=False)

    def setFrameSize(self, trafficItemName, **kwargs):
        """
        Description
            Modify the frame size.

        Parameters
            type: <str>:  fixed|increment|presetDistribution|quadGaussian|random|weightedPairs
        
            trafficItemName: <str>: The name of the Traffic Item..

        Example:
            trafficObj.setFrameSize('Topo1 to Topo2', type='fxied', fixedSize=128)
            trafficObj.setFrameSize('Topo1 to Topo2', type='increment', incrementFrom=68, incrementStep=2,
            incrementTo=1200)
        """
        frameSizeObj = self.ixNetwork.Traffic.TrafficItem(Name=trafficItemName).ConfigElement.find().FrameSize
        frameSizeObj.Type = kwargs.get('type')
        frameSizeType = kwargs.get('type')
        if frameSizeType == 'fixed':
            frameSizeObj.FixedSize = kwargs['fixedSize'] if kwargs.get('fixedSize') else 128
        elif frameSizeType == 'increment':
            frameSizeObj.IncrementFrom = kwargs['incrementFrom'] if kwargs.get('incrementFrom') else 64
            frameSizeObj.IncrementTo = kwargs['incrementTo'] if kwargs.get('incrementTo') else 1518
            frameSizeObj.IncrementStep = kwargs['incrementStep'] if kwargs.get('incrementStep') else 1
        elif frameSizeType == 'random':
            frameSizeObj.RandomMin = kwargs['randomMin'] if kwargs.get('randomMin') else 64
            frameSizeObj.RandomMax = kwargs['randomMax'] if kwargs.get('randomMax') else 1518
        elif frameSizeType == 'presetDistribution':
            frameSizeObj.PresetDistribution = kwargs['presetDistribution'] if kwargs.get('presetDistribution') \
                else 'cisco'
        elif frameSizeType == 'quadGaussian':
            if kwargs.get('quadGaussian'):
                frameSizeObj.QuadGaussian = kwargs['quadGaussian']
        elif frameSizeType == 'weightedPairs':
            frameSizeObj.WeightedPairs = kwargs['weightedPairs'] if kwargs.get('weightedPairs') else [64, 1]
            if kwargs.get('weightedRangePairs'):
                frameSizeObj.WeightedRangePairs = kwargs['weightedRangePairs']

    def configFramePayload(self, configElementObj, payloadType='custom', customRepeat=True, customPattern=None):
        """
        Description
            Configure the frame payload.

        Parameters
            payloadType: <str>: Options:
                           custom, decrementByte, decrementWord, incrementByte, incrementWord, random
            customRepeat: <bool>
            customPattern: <str>: Enter a custom payload pattern
        """
        framePayloadObj = configElementObj.FramePayload
        framePayloadObj.Type = payloadType
        framePayloadObj.CustomRepeat = customRepeat
        framePayloadObj.CustomPattern = customPattern

    def enableMinFrameSize(self, enable=True):
        """
        Description
           Enable the global traffic option to allow smaller frame size.

        Parameter
           enable: <bool>: True to enable it.
        """
        self.ixNetwork.Traffic.EnableMinFrameSize = enable

    def suspendTrafficItem(self, trafficItemObj, suspend=True):
        """
        Description
           Suspend the Traffic Item from sending traffic.
        
        Parameter
           trafficItemObj: <str>: The Traffic Item object.
           suspend: <bool>: True=suspend traffic.
        
        Syntax
           PATCH: /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{id}
           DATA:  {'suspend': True}
        """
        trafficItemObj.Suspend = suspend
