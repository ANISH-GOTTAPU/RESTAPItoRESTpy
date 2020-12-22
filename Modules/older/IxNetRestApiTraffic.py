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

            endpoints: [list]: A list: [{name: sources:[], destionations:[], highLevelStreams: None, (add more endpoints)... ]
                               Scroll down to see example.

            configElements: [list]: Config Element kwargs.
                                    Each item in this list is aligned to the sequential order of your endpoint list.

        If mode is create:
            The required parameters are: mode, trafficItem, endpoints and configElements

        If mode is modify:
            The required parameters are: mode, obj, and one of the objects to modify (trafficIemObj, endpointObj or configElementObj).

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

            trackBy: [list]: trackingenabled0, ethernetIiSourceaddress0, ethernetIiDestinationaddress0, ethernetIiPfcQueue0,
                             vlanVlanId0, vlanVlanUserPriority0, ipv4SourceIp0, sourceDestValuePair0, sourceDestEndpointPair0,
                             ipv4Precedence0, ipv4SourceIp0, flowGroup0, frameSize0

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
            trackBy: <list>: Some options: flowGroup0, vlanVlanId0, ethernetIiDestinationaddress0, ethernetIiSourceaddress0,
                             sourcePort0, sourceDestPortPair0, ipv4DestIp0, ipv4SourceIp0, ipv4Precedence0,
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
                             highLevelStream obj Ex: /api/v1/sessions/{1}/ixnetwork/traffic/trafficItem/{1}/highLevelStream/{1}
        
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
        transmissionControlData = {}
        frameRateData = {}
        frameRateDistribution = {}
        for item in configElements.keys():
            # These attributes are int type
            # capitalize the item
            # if item == 'burstPacketCount':
            #     configElementObj.TransmissionControl.BurstPacketCount = int(configElements[item])
            # if item == 'duration':
            #     configElementObj.TransmissionControl.Duration = int(configElements[item])
            # if item == 'frameCount':
            #     configElementObj.TransmissionControl.FrameCount = int(configElements[item])
            # if item == 'interBurstGap':
            #     configElementObj.TransmissionControl.InterBurstGap = int(configElements[item])
            # if item == 'interStreamGap':
            #     configElementObj.TransmissionControl.InterStreamGap = int(configElements[item])
            # if item == 'iterationCount':
            #     configElementObj.TransmissionControl.IterationCount = int(configElements[item])
            # if item == 'minGapBytes':
            #     configElementObj.TransmissionControl.MinGapBytes = int(configElements[item])
            # if item == 'repeatBurst':
            #     configElementObj.TransmissionControl.RepeatBurst = int(configElements[item])
            # if item == 'startDelay':
            #     configElementObj.TransmissionControl.StartDelay = int(configElements[item])
            # if item == 'enableInterBurstGap':
            #     configElementObj.TransmissionControl.EnableInterBurstGap = str(configElements[item])
            # if item == 'enableInterStreamGap':
            #     configElementObj.TransmissionControl.EnableInterStreamGap = str(configElements[item])
            # if item == 'interBurstGapUnits':
            #     configElementObj.TransmissionControl.InterBurstGapUnits = str(configElements[item])
            # if item == 'startDelayUnits':
            #     configElementObj.TransmissionControl.StartDelayUnits = str(configElements[item])
            # if item == 'type':
            #     configElementObj.TransmissionControl.Type = str(configElements[item])
            if item in ['burstPacketCount', 'duration', 'frameCount', 'interBurstGap', 'interStreamGap',
                        'iterationCount', 'minGapBytes', 'repeatBurst', 'startDelay']:
                itemObj = item[0:1].capitalize() + item[1:]
                eval("trafficitem.TransmissionControl." + "update(" + itemObj + " =  int(configElements[item]))")
                # configElementObj.TransmissionControl.itemObj = int(configElements[item])
                # transmissionControlData.update({itemObj: int(configElements[item])})

            if item in ['enableInterBurstGap', 'enableInterStreamGap', 'interBurstGapUnits',
                        'startDelayUnits', 'type']:
                itemObj = item[0:1].capitalize() + item[1:]
                eval("trafficitem.TransmissionControl." + "update(" + itemObj + " =  str(configElements[item]))")
                # configElementObj.TransmissionControl.itemObj = str(configElements[item])
                # transmissionControlData.update({itemObj: str(configElements[item])})

            if item == 'frameRateType':
                configElementObj.FrameRate.Type = str(configElements[item])
                # frameRateData.update({'type': str(configElements[item])})

            if item == 'frameRate':
                configElementObj.FrameRate.Rate = float(configElements[item])
                # frameRateData.update({'rate': float(configElements[item])})

            if item == 'frameRateBitRateUnitsType':
                configElementObj.FrameRate.BitRateUnitsType = str(configElements[item])
                # frameRateData.update({'bitRateUnitsType': str(configElements[item])})

            if item == 'portDistribution':
                configElementObj.FrameRateDistribution.PortDistribution = configElements[item]
                # frameRateDistribution.update({'portDistribution': configElements[item]})

            if item == 'streamDistribution':
                configElementObj.FrameRateDistribution.StreamDistribution = configElements[item]
                # frameRateDistribution.update({'streamDistribution': configElements[item]

        # Note: transmissionType is not an attribute in configElement. It is created to be more descriptive than 'type'.
        if 'transmissionType' in configElements:
            # self.ixnObj.patch(configElementObj+'/transmissionControl',
            # data={'type': configElements['transmissionType']})
            configElementObj.TransmissionControl.Type = configElements['transmissionType']

        # if transmissionControlData != {}:
        #    self.ixnObj.patch(configElementObj+'/transmissionControl', data=transmissionControlData)

        # if frameRateData != {}:
        #    self.ixnObj.patch(configElementObj+'/frameRate', data=frameRateData)

        if 'frameSize' in configElements:
            # self.ixnObj.patch(configElementObj+'/frameSize', data={'fixedSize': int(configElements['frameSize'])})
            configElementObj.FrameSize.FixedSize = int(configElements['frameSize'])

        if 'frameSizeType' in configElements:
            # self.ixnObj.patch(configElementObj+'/frameSize', data={'type': configElements['frameSizeType']})
            configElementObj.FrameSize.Type = configElements['frameSizeType']
            if configElements['frameSizeType'] == 'random':
                # self.ixnObj.patch(configElementObj+'/frameSize', data={'incrementFrom':
                # configElements['incrementFrom'],'incrementTo': configElements['incrementTo']})
                configElementObj.FrameSize.IncrementFrom = configElements['incrementFrom']
                configElementObj.FrameSize.IncrementTo = configElements['incrementTo']
        # if frameRateDistribution != {}:
        #    self.ixnObj.patch(configElementObj+'/frameRateDistribution', data=frameRateDistribution)

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
        # if trafficItemObj:
        #     trafficItemName = self.getTrafficItemName(trafficItemObj)
        #
        # if trafficItemName:
        #     if endpointSetName:
        #         queryData = {'from': '/traffic',
        #                      'nodes': [{'node': 'trafficItem', 'properties': ['name'],
        #                                 'where': [{'property': 'name', 'regex': trafficItemName}]},
        #                                {'node': 'endpointSet', 'properties': ['name'],
        #                                 'where': [{'property': 'name', 'regex': endpointSetName}]},
        #                                ]}
        #
        #     if endpointSetName == None:
        #         queryData = {'from': '/traffic',
        #                      'nodes': [{'node': 'trafficItem', 'properties': ['name'],
        #                                 'where': [{'property': 'name', 'regex': trafficItemName}]},
        #                                {'node': 'endpointSet', 'properties': [],
        #                                 'where': []},
        #                                ]}
        #
        #     queryResponse = self.ixnObj.query(data=queryData)
        #
        #     trafficItemList = queryResponse.json()['result'][0]['trafficItem']
        #     if trafficItemList == []:
        #         raise IxNetRestApiException('\nError: No traffic item name found: {0}'.format(trafficItemName))
        #
        #     endpointSetList = queryResponse.json()['result'][0]['trafficItem'][0]['endpointSet']
        #     if endpointSetList == []:
        #         raise IxNetRestApiException('\nError: No endpointSet name: {0} found in Traffic Item name: {1}'.
        #         format(endpointSetName, trafficItemName))
        #
        #     endpointSetObj = queryResponse.json()['result'][0]['trafficItem'][0]['endpointSet'][0]['href']
        #     endpointSetId = endpointSetObj.split('/')[-1]
        #
        #     # With the traffic item name and endpointSetId, get the Traffic Item's config element object handle.
        #     queryData = {'from': '/traffic',
        #                  'nodes': [{'node': 'trafficItem', 'properties': ['name'],
        #                             'where': [{'property': 'name', 'regex': trafficItemName}]},
        #                            {'node': 'configElement', 'properties': ['endpointSetId'],
        #                             'where': [{'property': 'endpointSetId', 'regex': endpointSetId}]}
        #                            ]}
        #
        #     queryResponse = self.ixnObj.query(data=queryData)
        #     configElementObj = queryResponse.json()['result'][0]['trafficItem'][0]['configElement'][0]['href']
        #     print(configElementObj)
        #     return configElementObj
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
        # trafficItemUrl = self.ixnObj.httpHeader + trafficItemObj
        # response = self.ixnObj.get(trafficItemUrl + '/configElement')
        configElementsObj = trafficItemObj.ConfigElement.find()
        configElementObjList = []
        for eachConfigElementObj in configElementsObj:
            configElementObjList.append(eachConfigElementObj.href)
        return configElementObjList

    def getTransmissionType(self, configElement):
        # configElement: /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1
        # Returns: fixedFrameCount, continuous

        # response = self.ixnObj.get(self.ixnObj.httpHeader+configElement+'/transmissionControl')
        transmissionControlObj = configElement.TransmissionControl
        return transmissionControlObj.Type

    def configTrafficLatency(self, enabled=True, mode='storeForward'):
        # enabled = True|False
        # mode    = storeForward|cutThrough|forwardDelay|mef
        # self.ixnObj.patch(self.ixnObj.sessionUrl+'/traffic/statistics/latency', data={'enabled':enabled, 'mode':mode})
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
        # Get a list of all the protocol templates:
        # response = self.ixnObj.get(self.ixnObj.sessionUrl+'/traffic/protocolTemplate?skip=0&take=end')
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
        # response = self.ixnObj.get(self.ixnObj.httpHeader+configElementObj+'/stack')
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
        # if action == 'append':
        #     action = 'appendprotocol'
        # if action == 'insert':
        #     action = 'insertprotocol'
        #
        #     # /api/v1/sessions/1
        # match = re.match('http.*(/api.*sessions/[0-9]).*', self.ixnObj.sessionUrl)
        # if match:
        #     apiHeader = match.group(1)
        #
        # # /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1
        # arg1 = configElementObj + '/stack/' + str(stackNumber)
        #
        # # Display a list of the current packet stack
        # response = self.ixnObj.get(self.ixnObj.httpHeader + configElementObj + '/stack')
        # for (index, eachHeader) in enumerate(response.json()):
        #     self.ixnObj.logInfo('{0}: {1}'.format(index + 1, eachHeader['displayName']), timestamp=False)
        #
        # # Get a list of all the protocol templates:
        # response = self.ixnObj.get(self.ixnObj.sessionUrl + '/traffic/protocolTemplate?skip=0&take=end')
        #
        # protocolTemplateId = None
        # for eachProtocol in response.json()['data']:
        #     if bool(re.match('^%s$' % protocolStackNameToAdd, eachProtocol['displayName'].strip(), re.I)):
        #         # /api/v1/sessions/1/traffic/protocolTemplate/30
        #         protocolTemplateId = eachProtocol['links'][0]['href']
        #
        # if protocolTemplateId == None:
        #     raise IxNetRestApiException('No such protocolTemplate name found: {0}'.format(protocolStackNameToAdd))
        # self.ixnObj.logInfo('protocolTemplateId: %s' % protocolTemplateId, timestamp=False)
        # data = {'arg1': arg1, 'arg2': protocolTemplateId}
        # response = self.ixnObj.post(self.ixnObj.httpHeader + configElementObj + '/stack/operations/%s' % action,
        #                             data=data)
        #
        # self.ixnObj.waitForComplete(response,
        #                             self.ixnObj.httpHeader + configElementObj + '/stack/operations/appendprotocol/' +
        #                             response.json()['id'])
        #
        # # /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1/stack/4
        # self.ixnObj.logInfo('addTrafficItemPacketStack: Returning: %s' % response.json()['result'], timestamp=False)
        # return response.json()['result']
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
            # Expect user to pass in the Traffic Item name if user did not pass in a configElement object.
            # queryData = {'from': '/traffic',
            #              'nodes': [{'node': 'trafficItem', 'properties': ['name'],
            #                         'where': [{'property': 'name', 'regex': trafficItemName}]}]}
            #
            # queryResponse = self.ixnObj.query(data=queryData)
            trafficItem = self.ixNetwork.Traffic.TrafficItem.find(Name=trafficItemName)

            # if queryResponse.json()['result'][0]['trafficItem'] == []:
            #    raise IxNetRestApiException('\nNo such Traffic Item name found: %s' % trafficItemName)

            if trafficItem is None:
                raise IxNetRestApiException('\nNo such Traffic Item name found: %s' % trafficItemName)
            trafficItemObj = trafficItem.href
            configElementObj = trafficItemObj + '/configElement/1'

        # response = self.ixnObj.get(self.ixnObj.httpHeader+configElementObj+'/stack')
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
        # response = self.ixnObj.get(self.ixnObj.httpHeader+configElementObj+'/stackLink')
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
        # response = self.ixnObj.get(self.ixnObj.httpHeader+configElementObj+'/stack')
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
        # /api/v1/sessions/1/ixnetwork/traffic/trafficItem/1/configElement/1/stack/6
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
        self.ixnObj.logInfo('showPacketHeaderFieldNames: %s' % stackObj + '/field', timestamp=False)
        # response = self.ixnObj.get(self.ixnObj.httpHeader + stackObj + '/field?skip=0&take=end')
        stackFieldObj = stackObj.Field.find()
        for (index, eachField) in enumerate(stackFieldObj):
            self.ixnObj.logInfo('\t{0}: {1}'.format(index + 1, eachField.DisplayName), timestamp=False)

        # for eachField in stackFieldObj:
        #     if 'id' in eachField:
        #         id = eachField.Id__
        #         fieldName = eachField.DisplayName
        #         self.ixnObj.logInfo('\t{0}: {1}'.format(id, fieldName), timestamp=False)
        #
        #     if 'data' in stackFieldObj:
        #         for eachDataField in response.json()['data']:
        #             if 'id' in eachDataField:
        #                 id = eachDataField['id']
        #                 fieldName = eachDataField['displayName']
        #                 self.ixnObj.logInfo('\t{0}: {1}'.format(id, fieldName), timestamp=False)

    def convertTrafficItemToRaw(self, trafficItemName):
        """
        Description

        Parameter
        """
        # self.ixnObj.post(self.ixnObj.sessionUrl+'/traffic/trafficItem/operations/converttoraw',
        # data={'arg1': trafficItemObj})
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()
        for eachTrafficItem in trafficItemObj:
            if eachTrafficItem.Name == trafficItemName:
                trafficItemObj = eachTrafficItem
                break
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
        # fieldId = None
        # # Get the field ID object by the user defined fieldName
        # # response = self.ixnObj.get(self.ixnObj.httpHeader+stackIdObj+'/field')
        # response = self.ixnObj.get(self.ixnObj.httpHeader + stackIdObj + '/field?skip=0&take=end')
        #
        # for eachFieldId in response.json():
        #     if 'displayName' in eachFieldId:
        #         if bool(re.match(fieldName, eachFieldId['displayName'], re.I)):
        #             fieldId = eachFieldId['id']
        #
        #     if 'data' in eachFieldId:
        #         for dataFieldId in response.json()['data']:
        #             if bool(re.match(fieldName, dataFieldId['displayName'], re.I)):
        #                 fieldId = dataFieldId['id']
        #
        # if fieldId == None:
        #     raise IxNetRestApiException('Failed to located your provided fieldName:', fieldName)
        #
        # self.ixnObj.logInfo('configPacketHeaderFieldId:  fieldIdObj: %s' % stackIdObj + '/field/' + str(fieldId),
        #                     timestamp=False)
        # response = self.ixnObj.patch(self.ixnObj.httpHeader + stackIdObj + '/field/' + str(fieldId), data=data)
        fieldId = None
        stackFieldObj = stackIdObj.Field.find()
        for (index, eachFieldId) in enumerate(stackFieldObj):
            if bool(re.match(fieldName, eachFieldId.DisplayName, re.I)):
                fieldId = index + 1
                fieldObj = eachFieldId
        if fieldId is None:
            raise IxNetRestApiException('Failed to located your provided fieldName:', fieldName)
        self.ixnObj.logInfo('configPacketHeaderFieldId:  fieldIdObj: %s' % stackIdObj.href + '/field/' + str(fieldId),
                            timestamp=False)
        fieldObj.ValueType = data.get('valueType')
        if data.get('valueType') == 'singleValue':
            fieldObj.SingleValue = data['singleValue'] if data.get('singleValue') else 0
        elif data.get('valueType') in ['increment', 'decrement']:
            for item in data.keys():
                if item in ['startValue', 'stepValue', 'countValue']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
            # if data.get('startValue'):
            #     fieldObj.StartValue = data['startValue']
            # if data.get('stepValue'):
            #     fieldObj.StepValue = data['stepValue']
            # if data.get('countValue'):
            #     fieldObj.CountValue = data['countValue']
            if data.get('auto'):
                fieldObj.Auto = data['auto']
        elif data.get('valueType') == 'valueList':
            if data.get('valueList'):
                fieldObj.ValueList = data['valueList']
            if data.get('auto'):
                fieldObj.Auto = data['auto']
        elif data.get('valueType') == 'random':
            # fixed,mask,seed,count
            for item in data.keys():
                if item in ['countValue', 'seed', 'randomMask', 'fixedBits']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
            # if data.get('countValue'):
            #     fieldObj.CountValue = data['countValue']
            # if data.get('seed'):
            #     fieldObj.Seed = data['seed']
            # if data.get('randomMask'):
            #     fieldObj.RandomMask = data['randomMask']
            # if data.get('fixedBits'):
            #     fieldObj.FixedBits = data['fixedBits']
            if data.get('auto'):
                fieldObj.Auto = data['auto']
        elif data.get('valueType') == 'repeatableRandomRange':
            for item in data.keys():
                if item in ['countValue', 'seed', 'stepValue', 'maxValue', 'minValue']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
            # if data.get('countValue'):
            #     fieldObj.CountValue = data['countValue']
            # if data.get('seed'):
            #     fieldObj.Seed = data['seed']
            # if data.get('stepValue'):
            #     fieldObj.StepValue = data['stepValue']
            # if data.get('maxValue'):
            #     fieldObj.MaxValue = data['maxValue']
            # if data.get('minValue'):
            #     fieldObj.MinValue = data['minValue']
            if data.get('auto'):
                fieldObj.Auto = data['auto']
        elif data.get('valueType') == 'nonRepeatableRandom':
            for item in data.keys():
                if item in ['randomMask', 'fixedBits']:
                    itemObj = item[0:1].capitalize() + item[1:]
                    eval("fieldObj." + "update(" + itemObj + " =  int(data[item]))")
            if data.get('auto'):
                fieldObj.Auto = data['auto']
            # if data.get('randomMask'):
            #     fieldObj.RandomMask = data['randomMask']
            # if data.get('fixedBits'):
            #     fieldObj.FixedBits = data['fixedBits']

    def getPacketHeaderAttributesAndValues(self, streamObj, packetHeaderName, fieldName):
        """
        Parameters
           streamObj: <str>: configElementObj|highLevelStreamObj
                      Ex: /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{1}/configElement/{id} 
                       or /api/v1/sessions/{id}/ixnetwork/traffic/trafficItem/{1}/highLevelStream/{id}

           packetHeaderName: <str>: Display Name of the stack.  Example: Ethernet II, VLAN, IPv4, TCP, etc. 

           fieldName: <str>: Display Name of the field.  Example: If packetHeaderName is Ethernet II, field names could be
                                    Destination MAC Address, Source MAC Address, Ethernet-Type and PFC Queue.
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
        # response = self.ixnObj.get(self.ixnObj.httpHeader+streamObj+'/stack')
        stackObj = streamObj.Stack.find()
        for eachStack in stackObj:
            # stackHref = eachStack.href
            # response = self.ixnObj.get(self.ixnObj.httpHeader+stackHref)
            #  need to do strip() to response.json()['displayName'] because some displayName has trailing spaces. 
            #  for example:  "IPv4 " 
            if packetHeaderName == eachStack.DisplayName.strip():
                # response = self.ixnObj.get(self.ixnObj.httpHeader+stackHref+'/field')
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
        # Safety check: Apply traffic or else configuring egress tracking won't work.
        # self.applyTraffic()
        # self.ixnObj.patch(self.ixnObj.httpHeader+trafficItemObj+'/tracking/egress',
        #            data={'encapsulation': 'Any: Use Custom Settings',
        #                  'customOffsetBits': offsetBits,
        #                  'customWidthBits': widthBits
        #              })
        # self.ixnObj.patch(self.ixnObj.httpHeader + trafficItemObj, data={'egressEnabled': True})
        # self.regenerateTrafficItems()
        # self.applyTraffic()
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
        # egressTrackingOffsetFilter = 'Custom: ({0}bits at offset {1})'.format(int(bitWidth), int(offsetBit))
        # trafficItemName = self.getTrafficItemName(trafficItemObj)
        #
        # # Get EgressStats
        # # Create Egress Stats
        # self.ixnObj.logInfo('Creating new statview for egress stats...')
        # response = self.ixnObj.post(self.ixnObj.sessionUrl + '/statistics/view',
        #                             data={'caption': egressStatViewName,
        #                                   'treeViewNodeName': 'Egress Custom Views',
        #                                   'type': 'layer23TrafficFlow',
        #                                   'visible': True})
        #
        # egressStatView = response.json()['links'][0]['href']
        # self.ixnObj.logInfo('egressStatView Object: %s' % egressStatView)
        # # /api/v1/sessions/1/ixnetwork/statistics/view/12
        #
        # self.ixnObj.logInfo('Creating layer23TrafficFlowFilter')
        # # Dynamically get the PortFilterId
        # response = self.ixnObj.get(self.ixnObj.httpHeader + egressStatView + '/availablePortFilter')
        # portFilterId = []
        # for eachPortFilterId in response.json():
        #     # 192.168.70.10/Card2/Port1
        #     self.ixnObj.logInfo('\tAvailable PortFilterId: %s' % eachPortFilterId['name'], timestamp=False)
        #     if eachPortFilterId['name'] == egressTrackingPort:
        #         self.ixnObj.logInfo('\tLocated egressTrackingPort: %s' % egressTrackingPort, timestamp=False)
        #         portFilterId.append(eachPortFilterId['links'][0]['href'])
        #         break
        # if portFilterId == []:
        #     raise IxNetRestApiException('No port filter ID found')
        # self.ixnObj.logInfo('PortFilterId: %s' % portFilterId)
        #
        # # Dynamically get the Traffic Item Filter ID
        # response = self.ixnObj.get(self.ixnObj.httpHeader + egressStatView + '/availableTrafficItemFilter')
        # availableTrafficItemFilterId = []
        # for eachTrafficItemFilterId in response.json():
        #     if eachTrafficItemFilterId['name'] == trafficItemName:
        #         availableTrafficItemFilterId.append(eachTrafficItemFilterId['links'][0]['href'])
        #         break
        # if availableTrafficItemFilterId == []:
        #     raise IxNetRestApiException('No traffic item filter ID found.')
        #
        # self.ixnObj.logInfo('availableTrafficItemFilterId: %s' % availableTrafficItemFilterId, timestamp=False)
        # # /api/v1/sessions/1/ixnetwork/statistics/view/12
        # self.ixnObj.logInfo('egressStatView: %s' % egressStatView, timestamp=False)
        # layer23TrafficFlowFilter = self.ixnObj.httpHeader + egressStatView + '/layer23TrafficFlowFilter'
        # self.ixnObj.logInfo('layer23TrafficFlowFilter: %s' % layer23TrafficFlowFilter, timestamp=False)
        # response = self.ixnObj.patch(layer23TrafficFlowFilter,
        #                              data={'egressLatencyBinDisplayOption': 'showEgressRows',
        #                                    'trafficItemFilterId': availableTrafficItemFilterId[0],
        #                                    'portFilterIds': portFilterId,
        #                                    'trafficItemFilterIds': availableTrafficItemFilterId})
        #
        # # Get the egress tracking filter
        # egressTrackingFilter = None
        # ingressTrackingFilter = None
        # response = self.ixnObj.get(self.ixnObj.httpHeader + egressStatView + '/availableTrackingFilter')
        # self.ixnObj.logInfo('Available tracking filters for both ingress and egress...', timestamp=False)
        # for eachTrackingFilter in response.json():
        #     self.ixnObj.logInfo('\tFilter Name: {0}: {1}'.format(eachTrackingFilter['id'],
        #     eachTrackingFilter['name']), timestamp=False)
        #     if bool(re.match('Custom: *\([0-9]+ bits at offset [0-9]+\)', eachTrackingFilter['name'])):
        #         egressTrackingFilter = eachTrackingFilter['links'][0]['href']
        #
        #     if ingressTrackingFilterName is not None:
        #         if eachTrackingFilter['name'] == ingressTrackingFilterName:
        #             ingressTrackingFilter = eachTrackingFilter['links'][0]['href']
        #
        # if egressTrackingFilter is None:
        #     raise IxNetRestApiException(
        #         'Failed to locate your defined custom offsets: {0}'.format(egressTrackingOffsetFilter))
        #
        # # /api/v1/sessions/1/ixnetwork/statistics/view/23/availableTrackingFilter/3
        # self.ixnObj.logInfo('Located egressTrackingFilter: %s' % egressTrackingFilter, timestamp=False)
        # enumerationFilter = layer23TrafficFlowFilter + '/enumerationFilter'
        # response = self.ixnObj.post(enumerationFilter,
        #                             data={'sortDirection': 'ascending',
        #                                   'trackingFilterId': egressTrackingFilter})
        #
        # if ingressTrackingFilterName is not None:
        #     self.ixnObj.logInfo('Located ingressTrackingFilter: %s' % egressTrackingFilter, timestamp=False)
        #     response = self.ixnObj.post(enumerationFilter,
        #                                 data={'sortDirection': 'ascending',
        #                                       'trackingFilterId': ingressTrackingFilter})
        #
        # # Must enable one or more egress statistic counters in order to enable the
        # # egress tracking stat view object next.
        # #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Tx Frames"
        # #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Rx Frames"
        # #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Frames Delta"
        # #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Loss %"
        # response = self.ixnObj.get(self.ixnObj.httpHeader + egressStatView + '/statistic')
        # for eachEgressStatCounter in response.json():
        #     eachStatCounterObject = eachEgressStatCounter['links'][0]['href']
        #     eachStatCounterName = eachEgressStatCounter['caption']
        #     self.ixnObj.logInfo('\tEnabling egress stat counter: %s' % eachStatCounterName, timestamp=False)
        #     self.ixnObj.patch(self.ixnObj.httpHeader + eachStatCounterObject, data={'enabled': True})
        #
        # self.ixnObj.patch(self.ixnObj.httpHeader + egressStatView, data={'enabled': True})
        # self.ixnObj.logInfo('createEgressCustomStatView: Done')
        #
        # return egressStatView

        egressTrackingOffsetFilter = 'Custom: ({0}bits at offset {1})'.format(int(bitWidth), int(offsetBit))
        trafficItemName = self.getTrafficItemName(trafficItemObj)
        self.ixnObj.logInfo('Creating new statview for egress stats...')
        egressStatViewObj = self.ixNetwork.Statistics.View.add(Caption=egressStatViewName,
                                                               TreeViewNodeName='Egress Custom Views',
                                                               Type='layer23TrafficFlow', Visible=True)
        self.ixnObj.logInfo('egressStatView Object: %s' % egressStatViewObj.href)
        # /api/v1/sessions/1/ixnetwork/statistics/view/12

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
        # Must enable one or more egress statistic counters in order to enable the
        # egress tracking stat view object next.
        #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Tx Frames"
        #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Rx Frames"
        #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Frames Delta"
        #   Enabling: ::ixNet::OBJ-/statistics/view:"EgressStats"/statistic:"Loss %"
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
        # url = self.ixnObj.sessionUrl + '/traffic/trafficItem/%s' % str(trafficItemNumber)
        # response = self.ixnObj.patch(url, data={"enabled": "true"})
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()[trafficItemNumber - 1]
        trafficItemObj.Enabled = True

    def disableTrafficItem(self, trafficItemNumber):
        # url = self.ixnObj.sessionUrl + '/traffic/trafficItem/%s' % str(trafficItemNumber)
        # response = self.ixnObj.patch(url, data={"enabled": "false"})
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
        # queryData = {'from': '/traffic',
        #              'nodes': [{'node': 'trafficItem', 'properties': [], 'where': []}]}
        # queryResponse = self.ixnObj.query(data=queryData)
        # for trafficItem in queryResponse.json()['result'][0]['trafficItem']:
        #     self.ixnObj.patch(self.ixnObj.httpHeader + trafficItem['href'], data={'enabled': mode})
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
        # trafficItemNameExists = False
        # response = self.ixnObj.get(self.ixnObj.sessionUrl+'/traffic/trafficItem')
        trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        if trafficItemObj != 0:
            return True
        return False

    def enablePacketLossDuration(self):
        # self.ixnObj.patch(self.ixnObj.sessionUrl+'/traffic/statistics/packetLossDuration', data={'enabled': 'true'})
        self.ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = True

    def disablePacketLossDuration(self):
        # self.ixnObj.patch(self.ixnObj.sessionUrl+'/traffic/statistics/packetLossDuration', data={'enabled': 'false'})
        self.ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = False

    def getTrafficItemStatus(self, trafficItemObj):
        # response = self.ixnObj.get(self.ixnObj.httpHeader + trafficItemObj, silentMode=True)
        # currentTrafficState = response.json()['state']
        # return currentTrafficState
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

        for trafficItemObj in trafficItemList:
            for counter in range(1, timeout + 1):
                # response = self.ixnObj.get(self.ixnObj.httpHeader + trafficItemObj, silentMode=True)
                currentTrafficState = trafficItemObj.State

                if currentTrafficState == 'unapplied':
                    self.ixnObj.logWarning('\nCheckTrafficState: Traffic is UNAPPLIED')
                    self.applyTraffic()

                self.ixnObj.logInfo('\ncheckTrafficState: {}'.format(trafficItemObj))
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
                    # time.sleep(8)
                    self.ixnObj.logInfo('checkTrafficState: {}: Done\n'.format(trafficItemObj))
                    break

                if counter == timeout and currentTrafficState not in expectedState:
                    if not ignoreException:
                        raise IxNetRestApiException('checkTrafficState: Traffic item state did not reach the expected '
                                                    'state(s): {0}: {1}. It is at: {2}'.format(
                            trafficItemObj, expectedState, currentTrafficState))
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

        # queryData = {
        #     "from": trafficItemObj + "/configElement/1",
        #     "nodes": [{"node": "stack", "properties": ["*"], "where": [{"property": "stackTypeId", "regex": "ipv4"}]},
        #               {"node": "field", "properties": ["*"],
        #                "where": [{"property": "fieldTypeId", "regex": "ipv4.header.srcIp"}]}]
        # }
        # queryResponse = self.ixnObj.query(data=queryData)
        # sourceIp = queryResponse.json()['result'][0]['stack'][1]['field'][26]['fieldValue']
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()

        for eachTrafficItem in trafficItemObj:
            if eachTrafficItem.Name == trafficItemName:
                trafficItemObj = eachTrafficItem
                break
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
        # queryData = {'from': '/traffic',
        #             'nodes': [{'node': 'trafficItem', 'properties': ['name', 'trafficType'], 'where': [{'property':
        #             'name', 'regex': trafficItemName}]},
        #            ]}
        # queryResponse = self.ixnObj.query(data=queryData)
        # if queryResponse.json()['result'][0]['trafficItem'] == []:
        #    raise IxNetRestApiException('getTrafficItemType: No such Traffic Item Name found: %s' % trafficItemName)
        # return (queryResponse.json()['result'][0]['trafficItem'][0]['trafficType'])

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
        # trafficItemObj = self.getTrafficItemObjByName(trafficItemName)
        # if trafficItemObj == 0:
        #    raise IxNetRestApiException('No such Traffic Item name: %s' % trafficItemName)
        # self.ixnObj.patch(self.ixnObj.httpHeader+trafficItemObj, data={"enabled": enable})
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
        # response = self.ixnObj.get(self.ixnObj.httpHeader+trafficItemObj)
        # return response.json()['name']
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
        # numOfTrafficItem = 0
        # trafficItemNameList = []
        # trafficItemUrl = self.ixnObj.sessionUrl + '/traffic/trafficItem'
        # response = self.ixnObj.get(trafficItemUrl + "?skip=" + str(numOfTrafficItem) + "&take=100")
        # while numOfTrafficItem < response.json()['count']:
        #     for eachTrafficItemId in response.json()['data']:
        #         trafficItemNameList.append(eachTrafficItemId['name'])
        #     numOfTrafficItem += 100
        #     response = self.ixnObj.get(trafficItemUrl + "?skip=" + str(numOfTrafficItem) + "&take=100")
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
        # queryData = {'from': '/traffic',
        #              'nodes': [{'node': 'trafficItem', 'properties': ['name'],
        #                         'where': [{"property": "name", "regex": trafficItemName}]}
        #                        ]}
        #
        # queryResponse = self.ixnObj.query(data=queryData, silentMode=False)
        #
        # try:
        #     return queryResponse.json()['result'][0]['trafficItem'][0]['href']
        # except:
        #     return 0
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()

        for eachTrafficItem in trafficItemObj:
            if eachTrafficItem.Name == trafficItemName:
                return eachTrafficItem.href
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
        # /api/v1/sessions/<id>/ixnetwork/traffic
        # fromObj = self.ixnObj.apiSessionId + '/traffic'
        # queryData = {"selects": [{"from": fromObj, "properties": [],
        #                          "children": [{"child": "trafficItem", "properties": ["*"],
        #                                      "filters": [{"property": "name", "regex": trafficItemName}]}],
        #                                      "inlines": []}]}

        # queryResponse = self.ixnObj.select(queryData)
        # try:
        #  return queryResponse.json()['result'][0]['trafficItem'][0]['href']
        # except:
        #  return 0
        trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()

        for eachTrafficItem in trafficItemObj:
            if eachTrafficItem.Name == trafficItemName:
                return eachTrafficItem.href
        return 0

    def applyTraffic(self):
        """
        Description
            Apply the configured traffic.
        """
        # restApiHeader = '/api'+self.ixnObj.sessionUrl.split('/api')[1]
        # response = self.ixnObj.post(self.ixnObj.sessionUrl+'/traffic/operations/apply', data={'arg1': restApiHeader+
        # '/traffic'})
        # self.ixnObj.waitForComplete(response, self.ixnObj.sessionUrl+'/traffic/operations/apply/'+
        # response.json()['id'])
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

        # if trafficItemList == 'all':
        #     trafficItemList = []
        #     numOfTrafficItem = 0
        #     response = self.ixnObj.get(
        #         self.ixnObj.sessionUrl + '/traffic/trafficItem' + "?skip=" + str(numOfTrafficItem) + "&take=100")
        #     trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()
        #     while numOfTrafficItem < len(trafficItemObj):
        #         for eachTrafficItem in trafficItemObj:
        #             trafficItemList.append(eachTrafficItem.href)
        #         numOfTrafficItem += 100
        #         response = self.ixnObj.get(
        #             self.ixnObj.sessionUrl + '/traffic/trafficItem' + "?skip=" + str(numOfTrafficItem) + "&take=100")
        # else:
        #     if type(trafficItemList) != list:
        #         trafficItemList = trafficItemList.split(' ')
        # url = self.ixnObj.sessionUrl + "/traffic/trafficItem/operations/generate"
        # data = {"arg1": trafficItemList}
        # self.ixnObj.logInfo('Regenerating traffic items: %s' % trafficItemList)
        # response = self.ixnObj.post(url, data=data)
        # self.ixnObj.waitForComplete(response, url + '/' + response.json()['id'])
        if trafficItemList == 'all':
            trafficItemList = []
            trafficItemObjList = []
            trafficItemObj = self.ixNetwork.Traffic.TrafficItem.find()
            for eachTrafficItem in trafficItemObj:
                trafficItemList.append(eachTrafficItem.href)
                trafficItemObjList.append(eachTrafficItem)
        else:
            if type(trafficItemList) != list:
                trafficItemList = trafficItemList.split(' ')
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
            # queryData = {"from": "/traffic",
            #     "nodes": [{"node": "trafficItem", "properties": ["enabled"], "where": [{"property": "enabled",
            #     "regex": "True"}]}]}

            # queryResponse = self.ixnObj.query(data=queryData, silentMode=False)
            # enabledTrafficItemHrefList = [trafficItem['href'] for trafficItem in
            # queryResponse.json()['result'][0]['trafficItem']]

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
        # queryData = {'from': '/traffic',
        #              'nodes': [{'node': 'trafficItem',
        #                         'properties': ['name', 'enabled', 'state', 'biDirectional', 'trafficType', 'warning',
        #                                        'errors'], 'where': []},
        #                        {'node': 'endpointSet', 'properties': ['name', 'sources', 'destinations'],
        #                        'where': []},
        #                        {'node': 'configElement', 'properties': ['name', 'endpointSetId', ], 'where': []},
        #                        {'node': 'frameSize', 'properties': ['type', 'fixedSize'], 'where': []},
        #                        {'node': 'framePayload', 'properties': ['type', 'customRepeat'], 'where': []},
        #                        {'node': 'frameRate', 'properties': ['type', 'rate'], 'where': []},
        #                        {'node': 'frameRateDistribution',
        #                         'properties': ['streamDistribution', 'portDistribution'], 'where': []},
        #                        {'node': 'transmissionControl', 'properties': ['type', 'frameCount',
        #                        'burstPacketCount'],
        #                         'where': []},
        #                        {'node': 'tracking', 'properties': ['trackBy'], 'where': []},
        #                        ]
        #              }
        #
        # queryResponse = self.ixnObj.query(data=queryData, silentMode=True)
        trafficItemsObj = self.ixNetwork.Traffic.TrafficItem.find()
        self.ixnObj.logInfo('\n', end='', timestamp=False)
        for (index, ti) in enumerate(trafficItemsObj):
            self.ixnObj.logInfo('TrafficItem: {0}\n\tName: {1}  Enabled: {2}  State: {3}'.format(
                index + 1, ti.Name, ti.Enabled, ti.State), timestamp=False)
            self.ixnObj.logInfo('\tTrafficType: {0}  BiDirectional: {1}'.format(ti.TrafficType, ti.BiDirectional),
                                timestamp=False)

            for tracking in ti.Tracking.find():
                self.ixnObj.logInfo('\tTrackings: {0}'.format(tracking.TrackBy), timestamp=False)

            for endpointSet, cElement in zip(ti.EndpointSet.find(), ti.ConfigElement.find()):
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
        # queryData = {'from': '/traffic',
        #              'nodes': [{'node': 'trafficItem', 'properties': ['name'],
        #                         'where': [{'property': 'name', 'regex': trafficItemName}]},
        #                        {'node': 'configElement', 'properties': [], 'where': []}]}
        # queryResponse = self.ixnObj.query(data=queryData)
        # if queryResponse.json()['result'][0]['trafficItem'] == []:
        #     raise IxNetRestApiException('\nNo such Traffic Item name found: %s' % trafficItemName)
        #
        # configElementObj = queryResponse.json()['result'][0]['trafficItem'][0]['configElement'][0]['href']
        # self.ixnObj.patch(self.ixnObj.httpHeader + configElementObj + '/frameSize', data=kwargs)
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
        # data = {'type': payloadType, 'customRepeat': customRepeat, 'customPattern': customPattern}
        # self.ixnObj.patch(self.ixnObj.httpHeader+configElementObj+'/framePayload', data=data)
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
        # self.ixnObj.patch(self.ixnObj.sessionUrl+'/traffic', data={'enableMinFrameSize': enable})
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
        # self.ixnObj.patch(self.ixnObj.httpHeader+trafficItemObj, data={'suspend': suspend})
        trafficItemObj.Suspend = suspend
