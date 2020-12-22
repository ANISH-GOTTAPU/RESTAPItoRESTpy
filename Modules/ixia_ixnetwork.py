#**************************************************
# Copyright (c) 2017 Cisco Systems, Inc.
# All rights reserved.
#**************************************************
'''
IXIA traffic lib
'''

#from tgn.ixia_resthttp import IxiaOperationException
#from utils.cafyexception import CafyException
#import tabulate

Route_property_type = ['BgpRoutePropertyObj',
                       'OSPFRoutePropertyObj',
                       'ldpFECPropertyObj',
                       'ISISRoutePropertyObj',
                       'IpPrefixPool'
                       ]

supported_search = ['BgpPeerNameToObj',
                    'igmpMcastIPv4GroupList',
                    'mldMcastIPv6GroupList',
                    'IPv4Obj',
                    'IPv6Obj',
                    'PimV4Obj',
                    'PimV6Obj',
                    'IpPrefixPool'
                    ]
supported_search.extend(Route_property_type)
v4_supported_type=[]
v6_supported_type=[]
common_supported_type=[]

for supported_type in supported_search:
    if 'v4' in supported_type.lower():
        v4_supported_type.append(supported_type)
    elif 'v6' in supported_type.lower():
        v6_supported_type.append(supported_type)
    else:
        common_supported_type.append(supported_type)

class IxNetwork():
    '''
    IXIA object: map to IxNetwork API hierarchy
                 provided by IxNetwork API Browser
    :child_class supported
        Traffic
            trafficitems: list of TrafficItem
                configelements: list of ConfigElement
                    framesize (CommonClass)
                    framerate (CommonClass)
                    transmission_control (CommonClass)
                    stacks: list of stack
                        fields: list of field
                tracking
                    egress
        topologies: list of Topology
            devicegroups: list of Devicegroup
                ethernets: list of Ethernet
                    ipv4s: list of Ipv4
                        bgpipv4peers: list of BgpIpv4Peer (CommonClass)
                        igmphosts: list of IgmpHost
                            igmp_mcast_ipv4_grouplist : IgmpMcastIPv4GroupList
                            port :
                                active : ['true' ...]
                        pimv4interfaces: list of PimInterface
                            pim_candidate_rp_list:
                            pim_source_list:
                            ports:
                            pim_join_prune_list
                        ports : list of port (CommonClass)
                networkgroups: list of networkGroup
                    ipv4prefixpools: list of ipv4PrefixPools
                        bgpiprouteproperties: list of bgpIPRouteProperty
                            ports: list of port bgpIPRouteProperty (CommonClass)
                        ospfRouteProperties: list of ospfRouteProperty
                            ports: list of port ospfRouteProperty (CommonClass)
                        ldpFECProperties: list of ldpFECProperty
                            ports: list of port ldpFECProperty (commonClass)
                    ipv6prefixpools: list of ipv4PrefixPools
                        bgpiprouteproperties: list of bgpIPRouteProperty
                            ports: list of port bgpIPRouteProperty (CommonClass)
                        ospfv3RouteProperties: list of ospfRouteProperty
                            ports: list of port ospfv3RouteProperty (CommonClass)
                        ldpv6FECProperties: list of ldpFECProperty
                            ports: list of port ldpFECProperty (commonClass)
            ports: list of port (CommonClass)
        vports: list of vport
    '''
    def __init__(self, rest):
        self._rest = rest ;# This is the RestPy object passed in from ixia.py
        self.links = []
        self.traffic = Traffic(self._rest)
        self.topologies = []
        self.vports = []

    def new_blank_config(self):
        '''
        new blank config
        '''
        self._rest.log.info('create blank config')
        url = self._rest.session_url + '/operations/newconfig'
        self._rest.post_request(url)

    def get_topologies(self):
        '''get topology list from chassis'''
        url = self._rest.session_url + '/topology'
        response = self._rest.get_request(url)
        self.topologies = []
        for topo_dict in response.json():
            topo_obj = Topology(self._rest, topo_dict)
            self.topologies.append(topo_obj)
        return self.topologies

    def get_vports(self):
        '''get vport list from chassis'''
        url = self._rest.session_url + '/vport'
        response = self._rest.get_request(url)
        self.vports = []
        for vport_dict in response.json():
            vport_obj = Vport(self._rest, vport_dict)
            self.vports.append(vport_obj)
        return self.vports

    def release_ports(self, port_list=None):
        """
        Release the ports held by current session or based on given
        port list.

        :param: Optional
            port_list =  List of ports to be released. If None, for all ports
        :return:
            True if successfull else raise Exception
        """
        port_obj_list = self.find_vport_obj(port_list)
        for port_obj in port_obj_list:
            port_url = port_obj.url + '/operations/releaseport'
            data = {'arg1': [port_obj.href]}
            self._rest.post_request(port_url, data)

    def get_obj(self, param_dict):
        '''
        IPv4Obj:
            :param type: IPv4Obj
                   ports: list of port name
                   IPs:   list of interface's IP
            :return IPv4 object list
        IPv6Obj:
            :param type: IPv6Obj
                   ports: list of port name
                   IPs:   list of interface's IP
            :return IPv6 object list
        BgpPeerNameToObj: BGP peer name
            :param  type: BgpPeerNameToObj
                    bgp_peer_name_list: list of BgpPeerName
            :return BGP peer object
        BGPRoutePropertyPortObj:
            :param  type: BGPRoutePropertyPortObj
                    ports: list of port name
                    last_address_list: list of last network address
            :return bgpIPPort object
        igmpMcastIPv4GroupList/mldMcastIPv6GroupList:
            :param ports:
                   hostip:
                   groups:
                   version:
        PimV4Obj:
            :param type: PimV4Obj
                   port_obj: list of selected port obj
                   mode: sourcetogroup, startogroup
                   groups: list of group address
                   neighborIP: list of
        PimV6Obj:
            :param type: PimV6Obj
                   port_obj: list of selected port obj
                   mode: sourcetogroup, startogroup
                   groups: list of group address
                   neighborIP: list of

        '''
        #Return object for topology tree

        if not self.topologies:
            self._rest.log.debug('Geting topology data from chassis')
            self.get_topologies()
        if not self.vports:
            self._rest.log.debug('Geting vport data from chassis')
            self.get_vports()
        selected_ports = param_dict.get('ports', None)
        if selected_ports:
            selected_port_objs = self.find_vport_obj(selected_ports)
            param_dict['vports_handle_selected'] = [i.href for i in selected_port_objs]
        param_dict['vports_handle_name'] = {}
        for i in self.vports:
            param_dict['vports_handle_name'][i.href] = i.name
        obj_list = []
        if param_dict['type'] in supported_search:
            self._rest.log.debug('Working on %s' % param_dict['type'])
            for topo_obj in self.topologies:
                obj_list += topo_obj.get_obj(param_dict)

        else:
            self._rest.log.debug('%s is not supported' % param_dict['type'])
        return obj_list

    def find_vport_obj(self, ports=None):
        '''
        get vport obj base on ports
        :ports list of port name defined in config file or
               list of port handle: <card number>/<port number>
               list of interface name defined in Json file:
                   <chassis IP>/<card number>/<port number>
               default is None for all avaiable vports
        :return vport object list
                raise Exception if not all ports are found
        '''
        if not self.vports:
            self._rest.log.debug('Geting vport data from chassis')
            self.get_vports()
        if not ports:
            return self.vports
        if not isinstance(ports, list):
            ports = [ports]
        obj_list = []
        for one_obj in self.vports:
            if one_obj.name in ports or \
               one_obj.assignedTo.replace(':', '/') in ports or \
               one_obj.port_handle in ports:
                obj_list.append(one_obj)
        if len(ports) != len(obj_list):
            port_handles = [i.port_handle for i in obj_list]
            msg = 'Not all ports are found. Ports:%s, found ports:%s' % \
            (ports, port_handles)
            self._rest.log.error(msg)
            raise CafyException.TgenConfigMissingError(msg)
        return obj_list


class Traffic():
    '''
    IXIA traffic object
    '''
    def __init__(self, rest):
        self._rest = rest
        self.trafficitems = []
        self.traffic_enabled_names = []
        self.traffic_enabled_urls = []
        self.traffic_disabled_urls = []

    def get_trafficitems(self):
        '''
        get traffic Item from chassis
        :return all trafficItems object
        '''
        url = self._rest.session_url + '/traffic/trafficItem' + '?skip=0&take=end'
        response = self._rest.get_request(url)
        self.trafficitems = []
        self.traffic_enabled_names = []
        self.traffic_enabled_urls = []
        self.traffic_disabled_urls = []
        traffic_streams = response.json()
        if isinstance(traffic_streams, dict):
            traffic_streams = response.json()['data']
        for ti_dict in traffic_streams:
            ti_obj = TrafficItem(self._rest, ti_dict)
            self.trafficitems.append(ti_obj)
            if ti_obj.enabled:
                self.traffic_enabled_names.append(ti_obj.name)
                self.traffic_enabled_urls.append(ti_obj.url)
            else:
                self.traffic_disabled_urls.append(ti_obj.url)

        return self.trafficitems

    def get_enabled_trafficitems(self):
        '''
        :return enabled trafficitems name
        '''
        ena_ti_name = []
        #for ti_obj in self.trafficitems:
        #    if ti_obj.enabled:
        #        ena_ti_name.append(ti_obj.name)

        for ti in self._rest.Traffic.TrafficItem.find():
            print(ti)
            if ti.Enabled == True:
                ena_ti_name.append(ti)

        return ena_ti_name
        

    def modify_traffic(self, ti_name_list, config_type, data, msg):
        '''
        Modify traffic items
        :param ti_name_list: list of traffic items to be disabled
                if None, disable all
        :param config_type: trafficitem, configelement, framesize, framerate,
                flowtracking, transmission_control
        :param data: dict for data to be modified
        :return: raise IxiaOperationException if error or failed
        '''
        if len(self.trafficitems) is 0:
            self.trafficitems = self.get_trafficitems()
        if ti_name_list is None:
            ti_name_list = [i.name for i in self.trafficitems]
        self._rest.log.info(msg % ti_name_list)
        for ti_obj in self.trafficitems:
            if ti_obj.name in ti_name_list:
                ti_obj.modify_trafficitem(config_type, data)

        return ti_name_list


class TrafficItem():
    '''
    IXIA traffic itme obj
    '''
    def __init__(self, rest, tiItemDict):
        self._rest = rest
        self.links = []
        self.name = ''
        self.enabled = ''
        self.endpointname_id = {}
        self.trafficType = None
        self.__dict__.update(tiItemDict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.configelements = self.get_configelements()
        self.endpointsets = self.get_endpointsets()
        self.tracking = FlowTracking(rest, self.url + '/tracking')
    def __str__(self):
        return self.url
    def get_endpointsets(self):
        '''
        get data from chassis, create field object list
        '''
        url = self.url + '/endpointSet' + '?skip=0&take=end'
        eps_response = self._rest.get_request(url)
        eps_obj_list = []
        endpoint_sets = eps_response.json()
        if isinstance(endpoint_sets, dict):
            endpoint_sets = eps_response.json()['data']
        for eps_dict in endpoint_sets:
            eps_obj = CommonClass(self._rest, eps_dict)
            eps_obj_list.append(eps_obj)
            self.endpointname_id[eps_obj.name] = eps_obj.id
        return eps_obj_list
    def get_configelements(self):
        '''
        get data from chassis, create configElements object list
        '''
        url = self.url + '/configElement' + '?skip=0&take=end'
        ce_response = self._rest.get_request(url)
        ce_obj_list = []
        config_elements = ce_response.json()
        if isinstance(config_elements, dict):
            config_elements = ce_response.json()['data']
        for ce_dict in config_elements:
            ce_obj = ConfigElement(self._rest, ce_dict)
            ce_obj_list.append(ce_obj)
        return ce_obj_list
    def get_frame_l4_information(self):
        '''
        get l4 information
        '''
        l4_info = []
        without_l4 = []
        for endpoint in self.configelements:
            ep_l4 = endpoint.get_frame_l4_information()
            stream_endpoint = 'stream:%s, endpoint ID:%s %s' %\
                              (self.name,
                               endpoint.id,
                               ep_l4)
            if ep_l4 == '':
                without_l4.append(stream_endpoint)
            else:
                l4_info.append(stream_endpoint)
        return l4_info, without_l4
    def get_ipv4_tos_information(self):
        '''
        Get the IPv4 Type of Service (ToS) information
        '''
        tos_info = []
        without_tos = []
        for endpoint in self.configelements:
            ep_tos = endpoint.get_ipv4_tos_information()
            stream_endpoint = 'stream:%s, endpoint ID:%s %s' %\
                              (self.name,
                               endpoint.id,
                               ep_tos)
            if ep_tos == '':
                without_tos.append(stream_endpoint)
            else:
                tos_info.append(stream_endpoint)
        return tos_info, without_tos
    def get_ipv6_traffic_class_information(self):
        '''
        Get the IPv6 traffic class (ToS) information
        '''
        tc_info = []
        without_tc = []
        for endpoint in self.configelements:
            ep_tc = endpoint.get_ipv6_traffic_class_information()
            stream_endpoint = 'stream:%s, endpoint ID:%s %s' %\
                              (self.name,
                               endpoint.id,
                               ep_tc)
            if ep_tc == '':
                without_tc.append(stream_endpoint)
            else:
                tc_info.append(stream_endpoint)
        return tc_info, without_tc
    def modify_trafficitem(self, config_type, data):
        '''Modify traffic item'''
        if config_type is 'trafficitem':
            self._rest.patch_request(self.url, data)
        elif config_type in ['flow_tracking', 'egress_tracking']:
            self.tracking.modify_tracking(config_type, data)
        elif config_type in ['configelement', 'framesize', 'framerate',
                             'transmission_control', 'stack_field', 'stack_field_mac']:
            if config_type == 'stack_field_mac' and self.trafficType != 'raw':
                # This should be changed to apply to any field item
                # that has a field.auto value of True
                tmp_msg = 'Traffic Item %s is %s. Only raw support stack modification' \
                % (self.name, self.trafficType)
                raise IxiaOperationException(tmp_msg)
            for ce_obj in self.configelements:
                if 'endpoint_name' in data.keys():
                    if data['endpoint_name'] not in self.endpointname_id.keys():
                        tmp_msg = 'EndpointSet %s, is not found' % data['endpoint_name']
                        raise IxiaOperationException(tmp_msg)
                    if self.endpointname_id[data['endpoint_name']] != ce_obj.endpointSetId:
                        continue
                    data.pop('endpoint_name')
                ce_obj.modify_configelement(config_type, data)
        else:
            msg = '%s is not supported!' % config_type
            raise IxiaOperationException(msg)

class ConfigElement():
    '''
    IXIA configelement obj
    '''
    def __init__(self, rest, ce_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(ce_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.framesize = CommonClass(rest, self.url + '/frameSize')
        self.framerate = CommonClass(rest, self.url + '/frameRate')
        self.transmission_control = CommonClass(rest, self.url + '/transmissionControl')
        self.stacks = self.get_stacks()
    def __str__(self):
        return self.url
    def get_data(self):
        '''Get data from chassis'''
        resp = self._rest.get_request(self.url)
        self.__dict__.update(resp.json())
        self.url = self._rest.server_url + self.links[0]['href']
    def get_frame_l4_information(self):
        '''
        get l4 inforamtion
        '''
        l4_info = ''
        for ti_stack in self.stacks:
            l4_name = ti_stack.displayName.lower()
            if l4_name in ['tcp', 'udp']:
                l4_info += '<%s %s> ' % (l4_name,
                                         ti_stack.get_frame_l4_information(l4_name))
        if l4_info != '':
            l4_info = 'with L4 header ' + l4_info
        return l4_info
    def get_ipv4_tos_information(self):
        '''
        Get the IPv4 Type of Service (ToS) information
        '''
        tos_info = ''
        for ti_stack in self.stacks:
            if ti_stack.displayName == 'IPv4 ':
                tos_info += ti_stack.get_ipv4_tos_information()
        return tos_info
    def get_ipv6_traffic_class_information(self):
        '''
        Get the IPv6 traffic class information
        '''
        tc_info = ''
        for ti_stack in self.stacks:
            if ti_stack.displayName == 'IPv6 ':
                tc_info += ti_stack.get_ipv6_traffic_class_information()
        return tc_info
    def get_stacks(self):
        '''
        get data from chassis, create stacks object list
        '''
        url = self.url + '/stack' + '?skip=0&take=end'
        stack_response = self._rest.get_request(url)
        stack_obj_list = []
        stacks = stack_response.json()
        if isinstance(stacks, dict):
            stacks = stack_response.json()['data']
        for stack_dict in stacks:
            stack_obj = Stack(self._rest, stack_dict)
            stack_obj_list.append(stack_obj)
        return stack_obj_list
    def modify_configelement(self, config_type, data):
        '''Modify configElement'''
        if config_type is 'configelement':
            self._rest.patch_request(self.url, data)
        elif config_type is 'framesize':
            self.framesize.modify(data)
        elif config_type is 'framerate':
            self.framerate.modify(data)
        elif config_type is 'transmission_control':
            self.transmission_control.modify(data)
        elif config_type is 'stack_field' or config_type is 'stack_field_mac':
            for stack_obj in self.stacks:
                tmp = stack_obj.modify_stack(data)
                if tmp is True:
                    return tmp
            msg = '%s is not found in the stacks' % data['displayName']
            raise IxiaOperationException(msg)
        else:
            msg = '%s is not supported!' % config_type
            raise IxiaOperationException(msg)

class Stack():
    '''
    IXIA Stack obj
    '''
    def __init__(self, rest, stack_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(stack_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.fields = self.get_fields()
    def __str__(self):
        return self.url
    def get_data(self):
        '''refresh data from chassis'''
        resp = self._rest.get_request(self.url)
        self.__dict__.update(resp.json())
        self.url = self._rest.server_url + self.links[0]['href']
    def get_frame_l4_information(self, l4_name):
        '''
        get l4 information
        '''
        l4_info = ''
        for stack_field in self.fields:
            for i in ['src', 'dst']:
                if stack_field.name == '%s_%s_prt' % (l4_name, i):
                    l4_info += '%s port:%s ' % (i, stack_field.get_value())
        return l4_info
    def get_ipv4_tos_information(self):
        '''
        Get the IPv4 Type of Service (ToS) information
        '''
        tos_info = ''
        for stack_field in self.fields:
            if stack_field.name == 'precedence':
                tos_info = stack_field.get_value()
        return tos_info
    def get_ipv6_traffic_class_information(self):
        '''
        Get the IPv6 traffic class information
        '''
        tc_info = ''
        for stack_field in self.fields:
            if stack_field.name == 'trafficClass':
                tc_info = stack_field.get_value()
        return tc_info
    def get_fields(self):
        '''
        get data from chassis, create field object list
        '''
        url = self.url + '/field' + '?skip=0&take=end'
        field_response = self._rest.get_request(url)
        field_obj_list = []
        fields = field_response.json()
        if isinstance(fields, dict):
            fields = field_response.json()['data']
        for field_dict in fields:
            field_obj = Field(self._rest, field_dict)
            field_obj_list.append(field_obj)
        return field_obj_list
    def modify_stack(self, data):
        '''Modify stack field'''
        '''1) check data['displayName'] match any of field'''
        for field_obj in self.fields:
            if data['displayName'] == field_obj.displayName:
                field_obj.modify(data)
                return True

class Field():
    '''
    IXIA stack field Class
    '''
    def __init__(self, rest, field_dict):
        self._rest = rest
        self.links, self.startUcastAddr = [], None
        self.name = None
        self.id = None
        self.valueType = ''
        self.singleValue = None
        self.startValue = None
        self.stepValue = None
        self.countValue = None
        self.valueList = None
        self.__dict__.update(field_dict)
        self.url = self._rest.server_url + self.links[0]['href']
    def __str__(self):
        return self.url
    def get_value(self):
        '''
        get value
        '''
        if self.valueType == 'singleValue':
            f_value = self.singleValue
        elif self.valueType == 'increment' or \
             self.valueType == 'decrement':
            f_value = "%s, start: %s, step: %s, count: %s" % \
                      (self.valueType,
                       self.startValue,
                       self.stepValue,
                       self.countValue)
        elif 'NullReferenceException' in self.valueType:
            f_value = 'auto'
        elif self.valueType == 'valueList':
            f_value = "list: %s" % self.valueList
        else:
            f_value = self.valueType
        return f_value
    def modify(self, data):
        '''modify parameters'''
        self._rest.patch_request(self.url, data)


class FlowTracking():
    '''
    IXIA tracking object
    '''
    def __init__(self, rest, url):
        self._rest = rest
        self.links = []
        self.url = url
        self.get_data()
        self.egress = CommonClass(rest, self.url + '/egress')
    def __str__(self):
        return self.url
    def get_data(self):
        '''Get data from chassis'''
        resp = self._rest.get_request(self.url)
        self.__dict__.update(resp.json())
        self.url = self._rest.server_url + self.links[0]['href']
    def modify_tracking(self, config_type, data):
        '''modify tracking'''
        if config_type is 'flow_tracking':
            self._rest.patch_request(self.url, data)
        elif config_type is 'egress_tracking':
            self.egress.modify(data)
        else:
            msg = '%s is not supported!' % config_type
            raise IxiaOperationException(msg)

class Vport():
    '''
    IXIA vPort Object
    '''
    def __init__(self, rest, vport_dict):
        self._rest = rest
        self.links, self.startUcastAddr = [], None
        self.name = None
        self.id = None
        self.connectedTo = None
        self.href = None
        self.__dict__.update(vport_dict)
        self.href = self.links[0]['href']
        self.url = self._rest.server_url + self.href
        self.port_handle = '%s/%s' % (self.connectedTo.split('/')[-3],
                                      self.connectedTo.split('/')[-1])
    def __str__(self):
        return self.url
    def modify(self, data):
        '''modify parameters'''
        self._rest.patch_request(self.url, data)

class CommonClass():
    '''
    IXIA CommonClass
    '''
    def __init__(self, rest, url):
        self._rest = rest
        self.url = url
        self.links, self.startUcastAddr = [], None
        self.name = None
        self.id = None
        self.get_data()
    def __str__(self):
        if self.name:
            return self.name
        return self.url
    def get_data(self):
        '''Get data from chassis'''
        if isinstance(self.url, dict):
            resp_json = self.url
        else:
            resp = self._rest.get_request(self.url)
            resp_json = resp.json()
        self.__dict__.update(resp_json)
        self.url = self._rest.server_url + self.links[0]['href']
    def modify(self, data):
        '''modify parameters'''
        self._rest.patch_request(self.url, data)

class Topology():
    '''IXIA topology object'''
    def __init__(self, rest, topo_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(topo_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.devicegroups = self.get_devicegroups()
        self.ports = self.get_port()
    def __str__(self):
        return self.url
    def get_devicegroups(self):
        '''get devicegroup list from chassis'''
        url = self.url + '/deviceGroup'
        response = self._rest.get_request(url)
        self.devicegroups = []
        for device_dict in response.json():
            device_obj = DeviceGroup(self._rest, device_dict)
            self.devicegroups.append(device_obj)
        return self.devicegroups
    def get_port(self):
        '''get port list from chassis'''
        url = self.url + '/port'
        response = self._rest.get_request(url)
        self.ports = []
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports
    def topo_port_id(self, selected_handles):
        '''return topo port ids matched with ports name'''
        topo_port_ids_selected = []
        for port_obj in self.ports:
            if port_obj.vport in selected_handles:
                topo_port_ids_selected.append(port_obj.id)
        return topo_port_ids_selected
    def topo_ports_name(self, vports_hadle_name):
        '''return dict topo port id:topo port name'''
        topo_port_id_name_dict = {}
        for port_obj in self.ports:
            topo_port_id_name_dict[port_obj.id] = vports_hadle_name[port_obj.vport]
        return topo_port_id_name_dict

    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        selected_ports = param_dict.get('ports', None)
        if selected_ports:
            param_dict['topo_port_ids_selected'] = \
            self.topo_port_id(param_dict['vports_handle_selected'])
            #print('selected topo port id %s' % param_dict['topo_port_ids_selected'])
        param_dict['topo_port_id_name'] = self.topo_ports_name(param_dict['vports_handle_name'])
        #print('topo port name dict %s' % param_dict['topo_port_id_name'])
        for device_obj in self.devicegroups:
            if selected_ports and not param_dict['topo_port_ids_selected']:
                return obj_list
            obj_list += device_obj.get_obj(param_dict)
        return obj_list

class DeviceGroup():
    '''
    IXIA DeviceGroup object
    '''
    def __init__(self, rest, device_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(device_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ethernets = self.get_ethernets()
        self.networkgroups = self.get_networkgroups()
    def __str__(self):
        return self.url
    def get_ethernets(self):
        '''get ethernet list from chassis'''
        url = self.url + '/ethernet'
        response = self._rest.get_request(url)
        self.ethernets = []
        for ethernet_dict in response.json():
            ethernet_obj = Ethernet(self._rest, ethernet_dict)
            self.ethernets.append(ethernet_obj)
        return self.ethernets
    def get_networkgroups(self):
        '''get networkGroup from chassis'''
        url = self.url + '/networkGroup'
        response = self._rest.get_request(url)
        self.networkgroups = []
        for networkgroup_dict in response.json():
            networkgroup_obj = NetworkGroup(self._rest, networkgroup_dict)
            self.networkgroups.append(networkgroup_obj)
        return self.networkgroups

    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        if (param_dict['type'] in Route_property_type) or (param_dict['type'] == "IpPrefixPool"):
            for ng_obj in self.networkgroups:
                if 'network_group' in param_dict:
                    if param_dict['network_group'] == ng_obj.name:
                        obj_list += ng_obj.get_obj(param_dict)
                else:
                    obj_list += ng_obj.get_obj(param_dict)
        elif param_dict['type'] in supported_search:
            for ethernet_obj in self.ethernets:
                obj_list += ethernet_obj.get_obj(param_dict)
        return obj_list

class Ethernet():
    '''
    IXIA Ethernet object
    '''
    def __init__(self, rest, ethernet_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(ethernet_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ipv4s = self.get_ipv('v4')
        self.ipv6s = self.get_ipv('v6')
    def __str__(self):
        return self.url
    def get_ipv(self, af):
        '''
        get ipv4/ipv6 info from chassis
        :Param af: CHOICES 'v4' and 'v6'
        :Return obj list
        '''
        url = self.url + '/ip' + af
        response = self._rest.get_request(url)
        ip_objs = []
        for ip_dict in response.json():
            ip_obj = Ipv46(self._rest, ip_dict, af)
            ip_objs.append(ip_obj)
        return ip_objs
    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        ipv_list = []
        if param_dict['type'] in v6_supported_type:
            ipv_list = self.ipv6s.copy()
        elif param_dict['type'] in v4_supported_type:
            ipv_list = self.ipv4s.copy()
        else:
            ipv_list = self.ipv4s.copy()
            ipv_list.extend(self.ipv6s)
        for ipv_obj in ipv_list:
            obj_list += ipv_obj.get_obj(param_dict)
        return obj_list

class Ipv46():
    '''
    IXIA IPv4/IPv6 object
    '''
    def __init__(self, rest, ipv_dict, af):
        self._rest = rest
        self.af = af
        self.links = []
        self.ports = []
        self.port_id_list = []
        self.port_ip_list = []
        self.address = None
        self.__dict__.update(ipv_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.bgpPeers = self.get_bgpPeers()
        if af == 'v4':
            self.igmphosts = self.get_igmp_mld_hosts()
            self.pimv4interfaces = self.get_piminterface()
        else:
            self.mldhosts = self.get_igmp_mld_hosts()
            self.pimv6interfaces = self.get_piminterface()
    def __str__(self):
        return self.url
    def get_bgpPeers(self):
        '''get bgp peer list from chassis'''
        if self.af == 'v4':
            url = self.url + '/bgpIpv4Peer'
        else:
            url = self.url + '/bgpIpv6Peer'
        response = self._rest.get_request(url)
        self.bgpPeers = []
        for bgp_peer_dict in response.json():
            bgp_peer_obj = CommonClass(self._rest, bgp_peer_dict)
            self.bgpPeers.append(bgp_peer_obj )
        return self.bgpPeers
    def get_address(self):
        '''get host ip addresses from chassis'''
        #url = self._rest.server_url + self.address
        #response = self._rest.get_request(url)
        address_values = self._rest.get_multivalue(self.address)
        return address_values
    def get_igmp_mld_hosts(self):
        '''get igmpHost/mldHost list'''
        if self.af == 'v4':
            host_type = '/igmpHost'
        else:
            host_type = '/mldHost'
        url = self.url + host_type
        response = self._rest.get_request(url)
        igmp_mld_hosts = []
        for igmpmldhost_dict in response.json():
            igmpmldhost_obj = IgmpMldHost(self._rest, igmpmldhost_dict, self.af)
            igmp_mld_hosts.append(igmpmldhost_obj)
        return igmp_mld_hosts
    def get_piminterface(self):
        '''
        get pimV4Interface list for IPv4
        get pimV6Interface list for IPv6
        '''
        pim_type = {'v4':'/pimV4Interface',
                    'v6':'/pimV6Interface'}
        url = self.url + pim_type[self.af]
        response = self._rest.get_request(url)
        piminterface_objs = []
        for piminterface_dict in response.json():
            piminterface_obj = PimInterface(self._rest, piminterface_dict, self.af)
            piminterface_objs.append(piminterface_obj)
        return piminterface_objs
    def get_ports(self):
        '''get ipv4 ports'''
        url = self.url + '/port'
        self.ports = []
        response = self._rest.get_request(url)
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports
    def get_port_id_ip_list(self):
        '''get port id and port ip address'''
        self.port_id_list = []
        self.port_ip_list = []
        if not self.ports:
            self.get_ports()
        for port_obj in self.ports:
            port_ips = self._rest.get_multivalue(port_obj.address)
            self.port_ip_list.extend(port_ips)
            self.port_id_list.extend(port_obj.id for i in range(len(port_ips)))
    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        if param_dict['type'] in ['BgpPeerNameToObj']:
            param_dict.setdefault('bgp_peer_name_list',['ALL',])
            for bgp_peer_obj in self.bgpPeers:
                if 'ALL' in param_dict['bgp_peer_name_list']:
                    if (bgp_peer_obj.name not in param_dict['bgp_peer_name_list']) and (self.af in param_dict['ip_type']) :
                        param_dict['bgp_peer_name_list'].append(bgp_peer_obj.name)
                if bgp_peer_obj.name in param_dict['bgp_peer_name_list']:
                    obj_list.append(bgp_peer_obj)

        elif param_dict['type'] in ['IPv4Obj', 'IPv6Obj']:
            obj_list.append(self)
            if not self.port_id_list:
                self.get_port_id_ip_list()

        elif param_dict['type'] in ['igmpMcastIPv4GroupList',
                                    'mldMcastIPv6GroupList']:
            #ip_add_multivalue = self.get_address()
            if not self.port_id_list:
                self.get_port_id_ip_list()
            param_dict['port_id_list'] = self.port_id_list
            param_dict['port_ip_list'] = self.port_ip_list
            mcast_hosts = []
            if param_dict['type'] == 'igmpMcastIPv4GroupList' and \
               self.af == 'v4':
                mcast_hosts = self.igmphosts
            elif param_dict['type'] == 'mldMcastIPv6GroupList' and \
                 self.af == 'v6':
                mcast_hosts = self.mldhosts
            for host_obj in mcast_hosts:
                #get list for port Name, host IP, grp address and source address
                obj_list.extend(host_obj.get_obj(param_dict))

        elif param_dict['type'] in ['PimV4Obj']:
            for pim_interface_obj in self.pimv4interfaces:
                obj_list += (pim_interface_obj.get_obj(param_dict))

        elif param_dict['type'] in ['PimV6Obj']:
            for pim_interface_obj in self.pimv6interfaces:
                obj_list += (pim_interface_obj.get_obj(param_dict))

        return obj_list

class IgmpMldHost():
    '''IXIA igmpHost object'''
    def __init__(self, rest, igmpmldhost_dict, af):
        self._rest = rest
        self.af = af
        self.links = []
        self._version_type = []
        self._grp_addr = []
        self._src_mode = []
        self._src_addr = []
        self.active, self.versionType = None, None
        self.__dict__.update(igmpmldhost_dict)
        self.href = self._rest.get_href(self.links)
        self.url = self._rest.server_url + self.href
        self.mcast_grouplist = self.get_mcast_grouplist()
    def __str__(self):
        return self.url
    def get_active_value(self):
        '''get active value from chassis'''
        #url = self._rest.server_url + self.active
        #response = self._rest.get_request(url)
        active_values = self._rest.get_multivalue(self.active)
        return active_values
    def get_version(self):
        '''get version type from chassis'''
        #url = self._rest.server_url + self.versionType
        #response = self._rest.get_request(url)
        version_type = self._rest.get_multivalue(self.versionType)
        return version_type
    def get_mcast_addr(self):
        '''get multicast group address'''
        #url = self._rest.server_url + self.igmp_mcast_ipv4_grouplist.startMcastAddr
        #response = self._rest.get_request(url)
        grp_add = self._rest.get_multivalue(self.mcast_grouplist.startMcastAddr)
        return grp_add
    def get_source_mode(self):
        '''get multicast source mode'''
        #url = self._rest.server_url + self.igmp_mcast_ipv4_grouplist.sourceMode
        #response = self._rest.get_request(url)
        src_mode = self._rest.get_multivalue(self.mcast_grouplist.sourceMode)
        return src_mode
    def get_mcast_grouplist(self):
        '''get mcast ipv4/ipv6 grouplist'''
        if self.af == 'v4':
            url = self.url + '/igmpMcastIPv4GroupList'
        else:
            url = self.url + '/mldMcastIPv6GroupList'
        #response = self._rest.get_request(url)
        mcast_grouplist = McastGroupList(self._rest, url, self.af)
        return mcast_grouplist
    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        action_list = []
        selected_index = []
        selected_info = []
        #old_active_state = self.get_active_value()
        new_active_state = self.get_active_value()
        if param_dict['groups']:
            #Get version, source mode, group address and source address from chassis
            #Skip getting data from chassis to saving time if exists
            #version2 create *,g routes
            #version3 create *,g routes if source mode is exclude
            #version3 create s,g routes if source mode is include
            if not self._version_type:
                #need a while getting data from chassis for multivalues
                self._version_type = self.get_version()
            if not self._grp_addr:
                self._grp_addr = self.get_mcast_addr()
            if not self._src_addr:
                self._src_addr = self.mcast_grouplist.get_source_addr()
            if not self._src_mode:
                self._src_mode = self.get_source_mode()
        if param_dict['version']:
            if not self._version_type:
                #need a while getting data from chassis
                self._version_type = self.get_version()
        for (i, one_state) in enumerate(new_active_state):
            grp_flag = True
            port_flag = True
            ip_flag = True
            version_flag = True
            if param_dict['ports']:
                if param_dict['port_id_list'][i] not in param_dict['topo_port_ids_selected']:
                    port_flag = False
            _tmp_info = 'port:%s' % param_dict['topo_port_id_name'][param_dict['port_id_list'][i]]
            if param_dict['hostip']:
                if param_dict['port_ip_list'][i] not in param_dict['hostip']:
                    ip_flag = False
            _tmp_info += ' host ip:%s' % param_dict['port_ip_list'][i]
            if param_dict['version']:
                ver_dict = {'v1':'version1',
                            'v2':'version2',
                            'v3':'version3'}
                if ver_dict[param_dict['version']] == self._version_type[i]:
                    _tmp_info += ' version:%s' % param_dict['version']
                else:
                    version_flag = False
            if param_dict['groups']:
                if param_dict['type'] == 'igmpMcastIPv4GroupList':
                    #for igmp *,g group address
                    tmp_version = ['version1', 'version2']
                else:
                    #for mld *,g group address
                    tmp_version = ['version1']
                if self._version_type[i] in tmp_version or self._src_mode[i] == 'exclude':
                    grp_range = ('*', self._grp_addr[i])
                else:
                    grp_range = (self._src_addr[i], self._grp_addr[i])
                if grp_range not in param_dict['groups']:
                    grp_flag = False
                else:
                    _tmp_info = _tmp_info + ' grp address:%s' % str(grp_range)
            action_flag = grp_flag and port_flag and ip_flag and version_flag
            action_list.append(action_flag)
            if action_flag:
                selected_index.append(i+1)
                selected_info.append(_tmp_info)
                if param_dict['action'] == 'join':
                    new_active_state[i] = 'true'
                else:
                    new_active_state[i] = 'false'
        if selected_index:
            obj_list = [{'igmp_mld_host_obj': self,
                         'action_list' : action_list,
                         'new_active_state' : new_active_state,
                         'port_ips' : param_dict['port_ip_list'],
                         'selected_index': selected_index,
                         'selected_info': selected_info
                        }]
        return obj_list

class McastGroupList():
    '''class IgmpMcastIPv4GroupList'''
    def __init__(self, rest, url, af):
        self._rest = rest
        self.links = []
        resp = self._rest.get_request(url)
        self.startMcastAddr, self.sourceMode = None, None
        self.__dict__.update(resp.json())
        self.href = self._rest.get_href(self.links)
        self.url = self._rest.server_url + self.href
        if af == 'v4':
            url = self.url + '/igmpUcastIPv4SourceList'
        else:
            url = self.url + '/mldUcastIPv6SourceList'
        self.ucast_ip_sourcelist = CommonClass(self._rest, url)
    def __str__(self):
        return self.url
    def get_source_addr(self):
        '''get source address'''
        #url = self._rest.server_url + self.igmp_ucast_ip_sourcelist.startUcastAddr
        #resp = self._rest.get_request(url)
        source_addr = self._rest.get_multivalue(self.ucast_ip_sourcelist.startUcastAddr)
        return source_addr

class PimInterface():
    '''class PimInterface for both V4 and V6'''
    def __init__(self, rest, piminterface_dict, ip_type):
        self._rest = rest
        self.links = None
        self.v4Neighbor = None
        self.neighborV6Address = None
        self.joinPrunes = None
        self.localRouterId = None
        self.links = None
        self.__dict__.update(piminterface_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.selected_index = []
        if self.localRouterId is None:
            #version above 8.40 need ?includes='localRouteId to get the value
            url = self.url + '?includes=localRouterId'
            response = self._rest.get_request(url)
            self.localRouterId = response.json()['localRouterId']
        if ip_type == 'v4':
            _rp = '/pimV4CandidateRPsList'
            _src = '/pimV4SourcesList'
            _join_prune = '/pimV4JoinPruneList'
            nei_url = self.v4Neighbor
        else:
            _rp = '/pimV6CandidateRPsList'
            _src = '/pimV6SourcesList'
            _join_prune = '/pimV6JoinPruneList'
            nei_url = self.neighborV6Address
        url = self.url + _join_prune
        self.pim_join_prune_list = PimJoinPruneList(self._rest, url, ip_type)
        url = self.url + _rp
        self.pim_candidate_rp_list = CommonClass(self._rest, url)
        url = self.url + _src
        self.pim_source_list = CommonClass(self._rest, url)
        self.learned_info_list = self.get_learned_info()
        self.ports = self.get_port()
        self.neighbor_list = self._rest.get_multivalue(nei_url)
        self.pim_join_prune_list.router_id =\
            self._rest.dup_list(self.localRouterId, self.joinPrunes)
        self.pim_join_prune_list.neighbor_list =\
            self._rest.dup_list(self.neighbor_list, self.joinPrunes)
    def __str__(self):
        return self.url
    def get_port(self):
        '''get port obj list'''
        self.ports = []
        url = self.url + '/port'
        response = self._rest.get_request(url)
        for _dict in response.json():
            _obj = CommonClass(self._rest, _dict)
            self.ports.append(_obj)
        return self.ports
    def get_learned_info(self):
        '''get learnedInfo'''
        self.learned_info_list = []
        url = self.url + '/learnedInfo'
        response = self._rest.get_request(url)
        for learned_info_dict in response.json():
            learned_info_obj = CommonClass(self._rest, learned_info_dict)
            self.learned_info_list.append(learned_info_obj)
        return self.learned_info_list
    def get_obj(self, param_dict):
        '''get object'''
        self.selected_index = [i+1 for i in range(len(self.pim_join_prune_list.router_id))]
        if param_dict['neighborIP']:
            if not isinstance(param_dict['neighborIP'], list):
                param_dict['neighborIP'] = [param_dict['neighborIP']]
            tmp_index = []
            for tmp_i in param_dict['neighborIP']:
                nei_index = [i+1 for i, val in enumerate(self.pim_join_prune_list.neighbor_list)
                             if val == tmp_i]
                tmp_index += nei_index
            self.selected_index = list(set(self.selected_index) & set(tmp_index))
        if param_dict['mode']:
            mode = self.pim_join_prune_list.range_type_list
            tmp_index = [i+1 for i, val in enumerate(mode) if val == param_dict['mode']]
            self.selected_index = list(set(self.selected_index) & set(tmp_index))
        if param_dict['groups']:
            tmp_index = []
            for src_add, grp_add in param_dict['groups']:
                grp_list = self.pim_join_prune_list.grp_add_list
                grp_index = [i+1 for i, val in enumerate(grp_list)
                             if val == grp_add]
                src_list = self.pim_join_prune_list.src_add_list
                if src_add == '*':
                    src_index = [i+1 for i in range(len(src_list))]
                else:
                    src_index = [i+1 for i, val in enumerate(src_list)
                                 if val == src_add]
                src_grp_index = list(set(src_index) & set(grp_index))
                tmp_index += src_grp_index
            self.selected_index = list(set(self.selected_index) & set(tmp_index))
        if self.selected_index:
            return [self]
        return []

class PimJoinPruneList():
    '''class PimJoinPruneList for both V4 and V6'''
    def __init__(self, rest, url, ip_type):
        self._rest = rest
        self.links = []
        self.groupV4Address = None
        self.sourceV4Address = None
        self.groupV6Address = None
        self.sourceV6Address = None
        self.rangeType = None
        resp = self._rest.get_request(url)
        self.__dict__.update(resp.json())
        self.url = self._rest.server_url + self.links[0]['href']
        self.ports = self.get_port()
        if ip_type == 'v4':
            grp_add_url = self.groupV4Address
            src_add_url = self.sourceV4Address
        else:
            grp_add_url = self.groupV6Address
            src_add_url = self.sourceV6Address
        self.grp_add_list = self._rest.get_multivalue(grp_add_url)
        self.src_add_list = self._rest.get_multivalue(src_add_url)
        self.range_type_list = self._rest.get_multivalue(self.rangeType)
    def __str__(self):
        return self.url
    def get_port(self):
        '''get port obj list'''
        self.ports = []
        url = self.url + '/port'
        response = self._rest.get_request(url)
        for _dict in response.json():
            _obj = CommonClass(self._rest, _dict)
            self.ports.append(_obj)
        return self.ports

class NetworkGroup():
    '''
    IXIA networkGroup object
    '''
    def  __init__(self, rest, networkgoup_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(networkgoup_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ipv4prefixpools = self.get_prefix_pools('ipv4')
        self.ipv6prefixpools = self.get_prefix_pools('ipv6')
    def __str__(self):
        return self.url
    def get_prefix_pools(self, ip_type):
        '''get ipv4PrefixPools list from chassis'''
        url = self.url + '/%sPrefixPools' % ip_type
        response = self._rest.get_request(url)
        ipprefixpools = []
        for prefix_pool_dict in response.json():
            ippp_obj = IpPrefixPool(self._rest, prefix_pool_dict, ip_type)
            ipprefixpools.append(ippp_obj)
        return ipprefixpools
    def get_obj(self, param_dict):
        '''get obj'''
        obj_list = []
        if  param_dict['IP_type'].lower() == 'ipv4':
            prefixpools = self.ipv4prefixpools
        else:
            prefixpools = self.ipv6prefixpools
        for ipvpp_obj in prefixpools:
            obj_list += ipvpp_obj.get_obj(param_dict)
        return obj_list

class IpPrefixPool():
    '''
    IXIA ipv4PrefixPools object
    '''
    def  __init__(self, rest, ipv4pp_dict, ip_type):
        self._rest = rest
        self.links = []
        self.lastNetworkAddress = []
        self.__dict__.update(ipv4pp_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.bgpiprouteproperties = self.get_bgp_ip_route_properties(ip_type)
        self.ospf_route_properties = self.get_ospf_route_properties(ip_type)
        self.ldp_fec_properties = self.get_ldp_fec_properties(ip_type)
        self.isis_route_properties = self.get_isis_route_properties(ip_type)

        if not self.lastNetworkAddress:
            #version above 8.40 need ?includes='lastNetworkAddress to get the value
            url = self.url + '?includes=lastNetworkAddress'
            response = self._rest.get_request(url)
            self.lastNetworkAddress = response.json().get('lastNetworkAddress')

    def __str__(self):
        return self.url

    def get_ospf_route_properties(self, ip_type):
        '''get ospfIPRouteProperty list from chassis'''
        self.ospf_route_properties=[]
        if ip_type == 'ipv4':
            url = self.url + '/ospfRouteProperty'
        else:
            url = self.url + '/ospfv3RouteProperty'
        response = self._rest.get_request(url)
        for ospf_ip_route_property_dict in response.json():
            ospf_ip_route_property_obj = OspfRouteProperty(self._rest, ospf_ip_route_property_dict)
            self.ospf_route_properties.append(ospf_ip_route_property_obj)
        return self.ospf_route_properties

    def get_ldp_fec_properties(self, ip_type):
        '''get ldpProperty list from chassis'''
        self.ldp_fec_properties=[]
        if ip_type == 'ipv4':
            url = self.url + '/ldpFECProperty'
        else:
            # support upon request
            # url = self.url + '/ldpv6FECProperty'
            return None
        response = self._rest.get_request(url)
        for ldp_fec_property_dict in response.json():
            ldp_fec_property_obj = ldpFECProperty(self._rest, ldp_fec_property_dict)
            self.ldp_fec_properties.append(ldp_fec_property_obj)
        return self.ldp_fec_properties

    def get_isis_route_properties(self, ip_type):
        '''get isisIPRouteProperty list from chassis'''
        self.isis_route_properties = []
        url = self.url + '/isisL3RouteProperty'
        response = self._rest.get_request(url)
        for isis_ip_route_property_dict in response.json():
            isis_ip_route_property_obj = IsIsRouteProperty(self._rest, isis_ip_route_property_dict)
            self.isis_route_properties.append(isis_ip_route_property_obj)
        return self.isis_route_properties

    def get_bgp_ip_route_properties(self, ip_type):
        '''get bgpIPRouteProperty list from chassis'''
        if ip_type == 'ipv4':
            url = self.url + '/bgpIPRouteProperty'
        else:
            url = self.url + '/bgpV6IPRouteProperty'
        response = self._rest.get_request(url)
        self.bgpiprouteproperties = []
        for bgpiprp_dict in response.json():
            bgpiprp_obj = BgpIPRouteProperty(self._rest, bgpiprp_dict)
            self.bgpiprouteproperties.append(bgpiprp_obj)
        return self.bgpiprouteproperties

    def get_obj(self, param_dict):
        '''get bgpIPRouteProperty object and index list based on prefix list'''
        obj_list = []

        if param_dict['type'] == 'BGPRoutePropertyObj':
            param_dict['lastNetworkAddress'] = self.lastNetworkAddress
            for bgpiprp_obj in self.bgpiprouteproperties:
                obj_list += bgpiprp_obj.get_obj(param_dict)
        elif param_dict['type'] == 'OSPFRoutePropertyObj':
            param_dict['lastNetworkAddress'] = self.lastNetworkAddress
            for ospf_ip_route_property_obj in self.ospf_route_properties:
                obj_list += ospf_ip_route_property_obj.get_obj(param_dict)
        elif param_dict['type'] == 'ldpFECPropertyObj':
            param_dict['lastNetworkAddress'] = self.lastNetworkAddress
            for ldp_property_obj in self.ldp_fec_properties:
                obj_list += ldp_property_obj.get_obj(param_dict)
        elif param_dict['type'] == 'ISISRoutePropertyObj':
            param_dict['lastNetworkAddress'] = self.lastNetworkAddress
            for isis_ip_route_property_obj in self.isis_route_properties:
                obj_list += isis_ip_route_property_obj.get_obj(param_dict)
        elif param_dict['type'] == 'IpPrefixPool':
            obj_list.append({'ip_prefix_pool_obj': self})

        return obj_list

class OspfRouteProperty():
    '''
    IXIA ospfRouteProperty object
    '''
    def __init__(self, rest, ospf_ip_route_property_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(ospf_ip_route_property_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ports = self.get_ports()
        self.port_id_list = []
        self.active = None

    def get_ports(self):
        """
        Get port object from chassis
        :param param_dict: Dictionary of the required parameters
        :return: List of port objects
        """
        url = self.url + '/port'
        response = self._rest.get_request(url)
        self.ports = []
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports

    def _get_port_id_list(self):
        """
        Get device counter for port from the chassis
        :return List of port id for each device
        """
        self.port_id_list = []
        for ospf_port_obj in self.ports:
            url = self._rest.server_url + ospf_port_obj.active
            self.active = url
            response = self._rest.get_request(url)
            device_count = response.json()['count']
            self.port_id_list.extend(ospf_port_obj.id for i in range(device_count))
        return self.port_id_list

    def get_obj(self, param_dict):
        """
        Get port object and index list based on prefix list and port name
        :param param_dict: Dictionary of the required parameters
        :return: List of OspfRouteProperty objects
        """
        obj_list = []
        selected_ospf_range_list = []

        if not param_dict['last_address_list']:
            selected_ospf_range_list = [True]
        else:
            if not self.port_id_list:
                self._get_port_id_list()
            if param_dict['ports']:
                port_id_selected = param_dict['topo_port_ids_selected']
            else:
                port_id_selected = set(self.port_id_list)
            if param_dict['last_address_list']:
                last_address_selected = param_dict['last_address_list']
            else:
                last_address_selected = param_dict['lastNetworkAddress']
            for i in range(len(self.port_id_list)):
                if param_dict['lastNetworkAddress'][i] in last_address_selected and \
                                self.port_id_list[i] in port_id_selected:
                        selected_ospf_range_list.append(True)
                else:
                    selected_ospf_range_list.append(False)
        if True in selected_ospf_range_list:
            obj_list.append({'ospf_route_property_object': self,
                             'selected_ospf_range_list': selected_ospf_range_list})
        return obj_list

class IsIsRouteProperty():
    '''
    IXIA isisRouteProperty object
    '''
    def __init__(self, rest, isis_ip_route_property_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(isis_ip_route_property_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ports = self.get_ports()
        self.port_id_list = []
        self.active = None

    def get_ports(self):
        """
        Get port object from chassis
        :param param_dict: Dictionary of the required parameters
        :return: List of port objects
        """
        url = self.url + '/port'
        response = self._rest.get_request(url)
        self.ports = []
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports

    def _get_port_id_list(self):
        """
        Get device counter for port from the chassis
        :return List of port id for each device
        """
        self.port_id_list = []
        for isis_port_obj in self.ports:
            url = self._rest.server_url + isis_port_obj.active
            self.active = url
            response = self._rest.get_request(url)
            device_count = response.json()['count']
            self.port_id_list.extend(isis_port_obj.id for i in range(device_count))
        return self.port_id_list

    def get_obj(self, param_dict):
        """
        Get port object and index list based on prefix list and port name
        :param param_dict: Dictionary of the required parameters
        :return: List of IsIsRouteProperty objects
        """
        obj_list = []
        selected_isis_range_list = []

        if not param_dict['last_address_list']:
            selected_isis_range_list = [True]
        else:
            if not self.port_id_list:
                self._get_port_id_list()
            if param_dict['ports']:
                port_id_selected = param_dict['topo_port_ids_selected']
            else:
                port_id_selected = set(self.port_id_list)
            if param_dict['last_address_list']:
                last_address_selected = param_dict['last_address_list']
            else:
                last_address_selected = param_dict['lastNetworkAddress']
            for i in range(len(self.port_id_list)):
                if param_dict['lastNetworkAddress'][i] in last_address_selected and \
                                self.port_id_list[i] in port_id_selected:
                        selected_isis_range_list.append(True)
                else:
                    selected_isis_range_list.append(False)
        if True in selected_isis_range_list:
            obj_list.append({'isis_route_property_object': self,
                             'selected_isis_range_list': selected_isis_range_list})
        return obj_list

class BgpIPRouteProperty():
    '''
    IXIA bgpIPRouteProperty object
    '''
    def __init__(self, rest, bgpiprp_dict):
        self._rest = rest
        self.links = []
        self.enableFlapping = None
        self.uptime = None
        self.downtime = None
        self.__dict__.update(bgpiprp_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ports = self.get_ports()
        self.port_id_list = []
    def __str__(self):
        return self.url
    def get_ports(self):
        '''get port object from chassis'''
        url = self.url + '/port'
        response = self._rest.get_request(url)
        self.ports = []
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports
    def get_flapping_value(self, param_dict):
        '''return enableflapping, uptime, downtime value in dict'''
        flapping_value = {}
        #when flapping for all address and ports
        #avoiding to get data from chassis for saving running time
        if not param_dict['ports'] and not param_dict['last_address_list']:
            return flapping_value
        for (key, href) in [('enableFlapping', self.enableFlapping),
                            ('uptime', self.uptime),
                            ('downtime', self.downtime)]:
            flapping_value[key] = self._rest.get_multivalue(href)
        return flapping_value
    def get_port_id_list(self):
        '''
        get device counter for port from chassis
        :return list of port id for each device
        '''
        self.port_id_list = []
        for bgpport_obj in self.ports:
            href = bgpport_obj.enableFlapping
            url = self._rest.server_url + href
            response = self._rest.get_request(url)
            device_count = response.json()['count']
            self.port_id_list.extend(bgpport_obj.id for i in range(device_count))
        return self.port_id_list
    def get_obj(self, param_dict):
        '''get port object and index list based on prefix list, port name'''
        obj_list = []
        flap_overlay_list = []
        #when flapping for all address and ports
        #avoiding to get data from chassis for saving running time
        if not param_dict['ports'] and not param_dict['last_address_list']:
            flap_overlay_list = [True]
        else:
            if not self.port_id_list:
                self.get_port_id_list()
            if param_dict['ports']:
                port_id_selected = param_dict['topo_port_ids_selected']
            else:
                port_id_selected = set(self.port_id_list)
            if param_dict['last_address_list']:
                last_address_selected = param_dict['last_address_list']
            else:
                last_address_selected = param_dict['lastNetworkAddress']
            for i in range(len(self.port_id_list)):
                if param_dict['lastNetworkAddress'][i] in last_address_selected and \
                    self.port_id_list[i] in port_id_selected:
                    flap_overlay_list.append(True)
                else:
                    flap_overlay_list.append(False)
        if True in flap_overlay_list:
            current_flap_value = self.get_flapping_value(param_dict)
            obj_list.append({'bgprp_obj' : self,
                             'flap_overlay_list' : flap_overlay_list,
                             'current_value' : current_flap_value,
                             'port_name' : [param_dict['topo_port_id_name'][i]
                                            for i in set(self.port_id_list)],
                             'last_address_list' : param_dict['lastNetworkAddress']})
        return obj_list

class ldpFECProperty():
    '''
    IXIA ldpFECProperty object
    '''

    def __init__(self, rest, ldp_ip_route_property_dict):
        self._rest = rest
        self.links = []
        self.__dict__.update(ldp_ip_route_property_dict)
        self.url = self._rest.server_url + self.links[0]['href']
        self.ports = self.get_ports()
        self.port_id_list = []
        self.active = None

    def get_ports(self):
        """
        Get port object from chassis
        :param param_dict: Dictionary of the required parameters
        :return: List of port objects
        """
        url = self.url + '/port'
        response = self._rest.get_request(url)
        self.ports = []
        for port_dict in response.json():
            port_obj = CommonClass(self._rest, port_dict)
            self.ports.append(port_obj)
        return self.ports

    def _get_port_id_list(self):
        """
        Get device counter for port from the chassis
        :return List of port id for each device
        """
        self.port_id_list = []
        for ldp_port_obj in self.ports:
            url = self._rest.server_url + ldp_port_obj.active
            self.active = url
            response = self._rest.get_request(url)
            device_count = response.json()['count']
            self.port_id_list.extend(ldp_port_obj.id for i in range(device_count))
        return self.port_id_list

    def get_obj(self, param_dict):
        """
        Get port object and index list based on prefix list and port name
        :param param_dict: Dictionary of the required parameters
        :return: List of ldpFECProperty objects
        """
        obj_list = []
        selected_ldp_range_list = []

        if not param_dict['last_address_list']:
            selected_ldp_range_list = [True]
        else:
            if not self.port_id_list:
                self._get_port_id_list()
            if param_dict['ports']:
                port_id_selected = param_dict['topo_port_ids_selected']
            else:
                port_id_selected = set(self.port_id_list)
            if param_dict['last_address_list']:
                last_address_selected = param_dict['last_address_list']
            else:
                last_address_selected = param_dict['lastNetworkAddress']
            for i in range(len(self.port_id_list)):
                if param_dict['lastNetworkAddress'][i] in last_address_selected and \
                                self.port_id_list[i] in port_id_selected:
                    selected_ldp_range_list.append(True)
                else:
                    selected_ldp_range_list.append(False)
        if True in selected_ldp_range_list:
            obj_list.append({'ldp_fec_property_object': self,
                             'selected_ldp_range_list': selected_ldp_range_list})
        return obj_list


class TrafficStats():
    '''
    IXIA Traffic verify
    '''
    def __init__(self,
                 item_stats,
                 flow_stats,
                 debug,
                 **kwargs):
        self.flow_stats = flow_stats
        self.item_stats = item_stats
        self.debug = debug
        self.kwargs = kwargs
        self.item_objs = []
        self.flow_objs = []
        self.flow_sorted_objs = []
        self.verify_results = True
    def drilldown(self, traffic_items):
        '''
        Report traffic stats per traffic item. traffic per flow will be
        repored when debug is True
        '''
        for one_item in self.item_stats.values():
            item_obj = self.Stats(traffic_stats=one_item,
                                  traffic_opt=traffic_items,
                                  traffic_opt_all=traffic_items.get('all_traffic_items', True),
                                  traffic_name=one_item['Traffic Item'],
                                  **self.kwargs)
            if item_obj.selected:
                if not item_obj.traffic_verify():
                    self.verify_results = False
                self.item_objs.append(item_obj)
        if self.debug:
            for one_item in self.flow_stats.values():
                item_obj = self.Stats(traffic_stats=one_item,
                                      traffic_opt=traffic_items,
                                      traffic_opt_all=traffic_items.get('all_traffic_items', True),
                                      traffic_name=one_item['Traffic Item'],
                                      **self.kwargs)
                if item_obj.selected:
                    self.flow_objs.append(item_obj)
            block_dict = self.item_block_dict(sort_key='Traffic Item')
            self.flow_sorted_objs = self.frame_loss_sort(block_dict=block_dict,
                                                         **self.kwargs)
    def port_drilldown(self,
                       ports,
                       mode,
                       traffic_items):
        '''
        Report traffic stats per tx_port or rx_port. Stats per flow will be
        reported if debug is True
        '''
        sorted_dict = {}
        #Filter Ports and traffic items. By default all traffic items are included
        #Create flow objects
        mode_key = {'rx_port':'Rx Port',
                    'tx_port':'Tx Port'}
        for one_item in self.flow_stats.values():
            item_obj = self.Stats(traffic_stats=one_item,
                                  traffic_opt=ports,
                                  traffic_opt_all=ports.get('all_ports', True),
                                  traffic_name=one_item[mode_key[mode]],
                                  traffic_opt2=traffic_items,
                                  traffic_opt2_all=traffic_items.get('all_traffic_items', True),
                                  traffic_name2=one_item['Traffic Item'],
                                  **self.kwargs)
            if item_obj.selected:
                self.flow_objs.append(item_obj)
        #Create traffic item objects
        block_dict = self.item_block_dict(sort_key=mode_key[mode])
        i = 0
        self.item_stats = {}
        for item_name, values in block_dict.items():
            i += 1
            self.item_stats[i] = {}
            self.item_stats[i][mode_key[mode]] = item_name
            tx_frame = 0
            rx_frame = 0
            frame_delta = 0
            for obj_list in values.values():
                for one_obj in obj_list:
                    tx_frame += one_obj.tx_frames()
                    rx_frame += one_obj.rx_frames()
                    frame_delta += one_obj.frame_delta()
            loss_percent = 100.0 * frame_delta / tx_frame
            self.item_stats[i]['Loss %'] = float('%.3f' % loss_percent)
            self.item_stats[i]['Tx Frames'] = str(tx_frame)
            self.item_stats[i]['Rx Frames'] = str(rx_frame)
            self.item_stats[i]['Frames Delta'] = str(frame_delta)
            item_obj = self.Stats(traffic_stats=self.item_stats[i],
                                  traffic_opt=ports,
                                  traffic_opt_all=ports.get('all_ports', True),
                                  traffic_name=item_name,
                                  **self.kwargs)
            if not item_obj.traffic_verify():
                self.verify_results = False
            self.item_objs.append(item_obj)
        if self.debug:
            self.flow_sorted_objs = self.frame_loss_sort(block_dict=block_dict,
                                                         **self.kwargs)

    def item_block_dict(self,
                        sort_key):
        '''
        create block dict base on 'Traffic Item', 'Rx Port' or 'Tx Port' for frame loss sort
        per traffic stream or port
        if sort_key = 'Traffic Item':
            block_dict =  {'trafficItem1':{frameLoss:[obj1,obj2..], frameLoss2:[obj3,..]},
                            'trafficItem2':....}
        '''
        block_dict = {}
        for one_obj in self.flow_objs:
            item_name = one_obj.traffic_stats[sort_key]
            if item_name not in block_dict:
                block_dict[item_name] = {}
            frame_loss = int(one_obj.traffic_stats['Frames Delta'])
            if frame_loss in block_dict[item_name].keys():
                block_dict[item_name][frame_loss].append(one_obj)
            else:
                block_dict[item_name][frame_loss] = [one_obj]
        return block_dict

    def frame_loss_sort(self,
                        block_dict,
                        flow_per_stream=20,
                        **kwargs):
        '''
        sort flow_objs base on mode and frame lose, each item with
        up to 20 flows which has max frame delta
        '''
        sorted_objs = []
        for item in block_dict.keys():
            tmp_list = []
            for frame_loss in sorted(block_dict[item].keys(), reverse=True):
                tmp_list = tmp_list + block_dict[item][frame_loss]
            sorted_objs = sorted_objs + tmp_list[0:flow_per_stream]
        return sorted_objs

    def report(self, objs, **kwargs):
        '''
        Traffic stats report
        '''
        headers = ['Traffic Item', 'Tx Port', 'Rx Port', 'IP :Source Address',
                   'IP :Destination Address', 'MPLS:Label Value', 'MPLS:MPLS Exp',
                   'VLAN:VLAN-ID', 'Tx Frames', 'Rx Frames', 'UDP:UDP-Source-Port',
                   'UDP:UDP-Dest-Port', 'TCP:TCP-Source-Port', 'TCP:TCP-Dest-Port',
                   'Store-Forward Avg Latency (ns)', 'Frames Delta', 'Loss %',
                   'Expected', 'Tolerance', 'Status']
        headers = kwargs.get('headers', headers)
        data = []
        item_headers = headers.copy()
        stats_headers = set()
        for one_obj in objs:
            for head in one_obj.traffic_stats.keys():
                stats_headers.add(head)
        for _head in headers:
            if _head not in stats_headers:
                item_headers.remove(_head)
        for one_obj in objs:
            one_data = []
            for _head in item_headers:
                if _head in one_obj.traffic_stats.keys():
                    one_data.append(one_obj.traffic_stats[_head])
                else:
                    one_data.append('N/A')
            data.append(one_data)
        stats_tb = tabulate.tabulate(data,
                                     headers=item_headers,
                                     tablefmt='rst')
        return stats_tb

    class Stats():
        '''
        Traffic stats
        '''
        def __init__(self,
                     traffic_stats,
                     traffic_opt,
                     traffic_opt_all,
                     traffic_name,
                     tolerance_mode,
                     tolerance,
                     expected_mode,
                     expected,
                     traffic_opt2=None,
                     traffic_opt2_all=None,
                     traffic_name2=None,
                     **kwargs):
            self.traffic_stats = traffic_stats
            self.tolerance_mode = tolerance_mode
            self.tolerance = tolerance
            self.expected_mode = expected_mode
            self.expected = expected
            self.selected = False
            self.verify_results = True
            self.verify_mode = 'Loss frame'
            self.verify_value = '0'
            traffic_opt2_flag = True
            #match traffic record base on name of traffic item and port
            if traffic_opt2 is not None:
                if traffic_opt2_all is not True:
                    if traffic_name2 not in traffic_opt2.keys():
                        traffic_opt2_flag = False
            if traffic_name in traffic_opt and traffic_opt2_flag is True:
                self.tolerance_mode = traffic_opt[traffic_name].get('tolerance_mode',
                                                                    tolerance_mode)
                self.tolerance = traffic_opt[traffic_name].get('tolerance', tolerance)
                self.expected_mode = traffic_opt[traffic_name].get('expected_mode', expected_mode)
                self.expected = traffic_opt[traffic_name].get('expected', expected)
                self.selected = True
            elif traffic_opt_all and traffic_opt2_flag is True:
                self.selected = True

        def traffic_verify(self):
            '''
            Verify traffic loss, verify expected traffic rate
            '''
            if self.expected != None and self.expected_mode == 'percent':
                self.verify_mode = 'Expected Pecent'
                actual_rate = 100.0 * self.rx_frames() / self.tx_frames()
                expect_max = float(self.expected) + float(self.tolerance)
                expect_min = float(self.expected) - float(self.tolerance)
                if expect_min < 0:
                    expect_min = 0
                if self.tolerance == 0:
                    self.verify_value = '%.2f%%' % expect_max
                else:
                    self.verify_value = '(%.2f%%, %.2f%%)' % (expect_min, expect_max)
                    self.traffic_stats['Tolerance'] = '%.2f%%' % self.tolerance
                self.traffic_stats['Expected'] = self.verify_value
                if actual_rate > expect_max or \
                   actual_rate < expect_min:
                    self.verify_results = False
            elif self.expected and self.expected_mode == 'frame':
                self.verify_mode = 'Expected Frame'
                expect_max = self.tx_frames() + int(self.tolerance)
                expect_min = self.tx_frames() - int(self.tolerance)
                if self.tolerance == 0:
                    self.verify_value = self.tx_frames()
                else:
                    self.verify_value = '(%d, %d)' % (expect_min, expect_max)
                    self.traffic_stats['Tolerance'] = '%d' % self.tolerance
                self.traffic_stats['Expected'] = self.verify_value
                if int(self.rx_frames()) > expect_max or \
                   int(self.rx_frames()) < expect_min:
                    self.verify_results = False
            elif self.tolerance_mode == 'percent':
                self.verify_mode = 'Loss Percent'
                expect_max = float(self.tolerance)
                if self.traffic_stats['Loss %'].isdigit():
                    actual_rate = float(self.traffic_stats['Loss %'])
                else:
                    actual_rate = float(0)
                if self.tolerance == 0:
                    self.verify_value = '0'
                else:
                    self.verify_value = '(0, %.2f%%)' % expect_max
                    self.traffic_stats['Tolerance'] = self.verify_value
                if actual_rate > expect_max:
                    self.verify_results = False
            else:
                self.verify_mode = 'Loss Frame'
                expect_max = int(self.tolerance)
                actual_rate = self.frame_delta()
                if self.tolerance == 0:
                    self.verify_value = '0'
                else:
                    self.verify_value = '(0, %d)' % expect_max
                    self.traffic_stats['Tolerance'] = self.verify_value
                if actual_rate > expect_max:
                    self.verify_results = False
            if self.verify_results:
                self.traffic_stats['Status'] = 'pass'
            else:
                self.traffic_stats['Status'] = 'fail'
            return self.verify_results

        def rx_frames(self):
            '''
            rx_frame
            '''
            return int(self.traffic_stats['Rx Frames'])

        def tx_frames(self):
            '''
            tx_frame
            '''
            return int(self.traffic_stats['Tx Frames'])

        def frame_delta(self):
            '''
            frame delta
            '''
            return int(self.traffic_stats['Frames Delta'])

class TgenDevice():
    '''
    add new device
    '''
    class vPort():
        '''
        create new vport
        '''
        def __init__(self,
                     rest,
                     **kwargs):
            self._rest = rest
            self.port_list = []
            self.href_list = []
            self.raw_traffic_vport = False
            self.port_name_list = kwargs.get('port_name_list', None)
            self.assign_to_physical_port = kwargs.get('assign_to_physical_port', True)
            self.assign_port_timeout = kwargs.get('assign_port_timeout', 60)

        def create(self,
                   port_list,
                   chassis_ip):
            '''
            create_vports
            :param
                port_list: list of physical name. Exp. ['card/port', 'chassisIP/card/port']
                chassis_ip: IXIA chassis IP address
            :return: vport href list. Example: ['/api/v1/sessions/1/ixnetwork/vport/1']
            '''
            if self.port_name_list:
                if len(port_list) != len(self.port_name_list):
                    msg = 'port name:%s do not match ports:%s' % (self.port_name_list, port_list)
                    self._rest.log.error(msg)
                    raise CafyException.TgenConfigMissingError(msg)
            for (i, port) in enumerate(port_list):
                _tmp = port.split('/')
                if len(_tmp) == 2:
                    card, port = _tmp
                    self.port_list.append('%s/%s/%s' % (chassis_ip, card, port))
                else:
                    chassis = _tmp[0]
                    card = _tmp[1]
                    port = _tmp[2]
                    if chassis != chassis_ip:
                        self.port_list.append('%s/%s/%s' %(chassis, card, port))
                    else:
                        self.port_list.append('%s/%s/%s' % (chassis_ip, card, port))

                url = self._rest.session_url + '/vport'
                #create vport
                response = self._rest.post_request(url, wait_url_arg=None)
                vport_obj = self._rest.get_href(response.json()['links'])
                self._rest.log.info('create vport %s' % vport_obj)
                if self.raw_traffic_vport:
                    self.href_list.append(vport_obj + '/protocols')
                else:
                    self.href_list.append(vport_obj)
                #set vport name, default is card/port
                if self.port_name_list:
                    port_name = self.port_name_list[i]
                else:
                    port_name = '%s/%s' % (card, port)
                url = self._rest.server_url + vport_obj
                data = {'name':port_name}
                response = self._rest.patch_request(url, data)
                msg = 'Vport %s created with name:%s' % (self.href_list, port_name)
                self._rest.log.info(msg)
            if len(self.href_list) != len(port_list):
                msg = 'Not all vports are created\nports:%s\nvports:%s' % \
                      (port_list, self.href_list)
                self._rest.log.info(msg)
            if self.assign_to_physical_port:
                self.assign_ports()
            return self.href_list

        def assign_ports(self):
            '''
            assign physical port to vports
            '''
            vport_list = [self._rest.server_url+i for i in self.href_list]
            data = {'arg1': [], 'arg2': [], 'arg3': vport_list, 'arg4': 'false'}
            [data['arg1'].append({'arg1':port.split('/')[0],
                                  'arg2':port.split('/')[1],
                                  'arg3':port.split('/')[2]}) for port in self.port_list]
            url = self._rest.session_url+'/operations/assignports'
            response = self._rest.post_request(url, data, wait_timeout=self.assign_port_timeout)
            msg = 'vports %s are created and physical ports %s assigned' % \
                  (vport_list, self.port_list)
            self._rest.log.info(msg)
            return True

    class Topology():
        '''
        create topology
        '''
        def __init__(self, rest, vport_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.name = kwargs.get('topology_name', None)
            self.vport = vport_obj
        def create(self):
            '''
            create topology
            '''
            url = self._rest.session_url + '/topology'
            vport_url_list = [self._rest.server_url + i for i in self.vport.href_list]
            topology_data = {'vports':vport_url_list}
            if self.name:
                topology_data['name'] = self.name
            response = self._rest.post_request(url,
                                               topology_data,
                                               wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])
            msg = 'topology %s created with vports:%s' % (self.href, self.vport.href_list)
            self._rest.log.info(msg)
            return self.href

    class deviceGroup():
        '''
        create deviceGroup
        '''
        def __init__(self, rest,
                     topology_obj,
                     **kwargs):
            self._rest = rest
            self.topo = topology_obj
            interface_no_vlan_count = kwargs.get('interface_no_vlan_count', 1)
            vlan_id_count = kwargs.get('vlan_id_count', 0)
            self.multiplier = vlan_id_count +  interface_no_vlan_count
            self.name = None
            self.href = None
        def create(self):
            '''
            Create device group
            :param
                topology_obj:
                multiplier: default 1
                name: name of device
            :param_optional
                self.device_group_multiplier
            :return
                device href. Example: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/3'
            '''
            if not self.topo.href:
                msg = 'Topology href missed'
                self._rest.log.error(msg)
                raise self._rest.exception.TgenConfigMissingError(msg)
            url = self._rest.server_url + self.topo.href + '/deviceGroup'
            data = {'multiplier':int(self.multiplier)}
            if self.name != None:
                data['name'] = self.name
            response = self._rest.post_request(url,
                                               data,
                                               wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])
            msg = 'deviceGroup %s created in topology %s' % (self.href, self.topo.href)
            self._rest.log.info(msg)
            return self.href

    class ethernet():
        '''
        create ethernet
        '''
        def __init__(self, rest,
                     device_group_obj,
                     **kwargs):
            self._rest = rest
            self.dg_obj = device_group_obj
            self.default_value = {'ethernet_name': None,
                                  'interface_no_vlan_count': 1,
                                  'vlan_count': 1,
                                  'vlan_id_count': 0,
                                  'vlan_id_start': None,
                                  'vlan_id_step': 0,
                                  'vlan_id_port_step': 0,
                                  'vlan_priority_start': None,
                                  'vlan_priority_step': 0,
                                  'vlan_priority_port_step': 0,
                                  'vlan_tpid': None
                                 }
            self.tpid_list = {'0x8100': 'ethertype8100',
                              '0x88a8': 'ethertype88a8',
                              '0x9100': 'ethertype9100',
                              '0x9200': 'ethertype9200',
                              '0x9300': 'ethertype9300',}
            self.default_value.update(kwargs)
            #self.n
            self.href = None
            self.vlan_count = self.default_value['vlan_count']
            self.interface_no_vlan_count = self.default_value['interface_no_vlan_count']
            self.vlan_id_count = self.default_value['vlan_id_count']
            self.vlan_id_start = self.default_value['vlan_id_start']
            item = ['vlan_id_start', 'vlan_priority_start', 'vlan_tpid']
            for i in item:
                if self.default_value[i] is not None:
                    if not isinstance(self.default_value[i], list):
                        self.default_value[i] = [self.default_value[i]]
                    if len(self.default_value[i]) != self.vlan_count:
                        msg = 'Number of %s:%s is not same as vlan count:%d' % \
                        (i, self.default_value[i], self.vlan_count)
                        raise self._rest.exception.TgenConfigMissingError(msg)
            if self.vlan_id_count > 0:
                self.default_value['enable_vlans'] = ['false'] * self.interface_no_vlan_count + \
                                                     ['true'] * self.vlan_id_count

        def create(self):
            '''
            Create Ethernet in device group
            :param:
                device_href: Example: '/api/v1/sessions/1/ixnetwork/topology/1/deviceGroup/3'
                name
            :return
                href:
            '''

            url = self._rest.server_url + self.dg_obj.href + '/ethernet'
            data = {}
            if self.default_value['ethernet_name']:
                data['name'] = self.default_value['ethernet_name']
            response = self._rest.post_request(url,
                                               data,
                                               wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])
            msg = 'Ethernet %s created in deviceGroup %s' % (self.href, self.dg_obj.href)
            self._rest.log.info(msg)
            self.modify_vlan()
            return self.href
        def modify_vlan(self):
            '''
            Modify vlan count, vlan id
            '''
            new_value = None
            if self.default_value['vlan_tpid'] is not None:
                new_value = []
                for (i, tpid) in enumerate(self.default_value['vlan_tpid']):
                    if tpid.lower() in self.tpid_list.keys():
                        #self.default_value['vlan_tpid'][i] = self.tpid_list[tpid.lower()]
                        new_value.append(self.tpid_list[tpid.lower()])
                    else:
                        msg = 'tpid:%s is not supported. Suport list is:%s' % (tpid, self.tpid_list)
                        self._rest.log.error(msg)
                        raise self._rest.exception.TgenConfigMissingError(msg)

            items = [['vlan_count', 'vlanCount', self.href],
                     ['enable_vlans', 'enableVlans', self.href]]
            for i in items:
                if i[0] in self.default_value:
                    data = self.default_value[i[0]]
                    msg = self._rest.config_attribute(i[2], i[1], data)
                    self._rest.log.info('%s %s' % (i[0], msg))

            url = self._rest.server_url + self.href + '/vlan'
            response = self._rest.get_request(url)
            for inner_i, vlan_dict in enumerate(response.json()):
                items = []
                #modify vlan id . Default is None for no change
                href = self._rest.get_href(vlan_dict['links'])
                convert_list = [['vlanId', self.default_value['vlan_id_start'],
                                 'vlan_id_step', 'vlan_id_port_step', 1, 4095],
                                ['priority', self.default_value['vlan_priority_start'],
                                 'vlan_priority_step', 'vlan_priority_port_step', 0, 7],
                                ['tpid', new_value, None, None, None, None]]
                for conver_i in convert_list:
                    if conver_i[1] is None:
                        continue
                    vlan_id_org = self._rest.get_multivalue(vlan_dict[conver_i[0]])
                    new_id_list = []
                    vlan_start = conver_i[1][inner_i]
                    for port_i in range(len(self.dg_obj.topo.vport.href_list)):
                        i_b = port_i*self.dg_obj.multiplier
                        i_e = i_b + self.interface_no_vlan_count
                        if conver_i[2] is not None:
                            new_id_list = new_id_list + vlan_id_org[i_b:i_e]
                            new_tmp_list = self._rest.count_to_list(vlan_start,
                                                                    self.default_value[conver_i[2]],
                                                                    self.vlan_id_count,
                                                                    conver_i[4], conver_i[5])
                            vlan_start = new_tmp_list[-1] + self.default_value[conver_i[3]]
                            new_id_list += new_tmp_list
                        else:
                            new_id_list = vlan_start
                    inner_id = inner_i + 1
                    items.append(['VLAN-%d' % inner_id, conver_i[0], href, new_id_list])
                for i in items:
                    msg = self._rest.config_attribute(i[2], i[1], i[3])
                    self._rest.log.info('%s %s' % (i[0], msg))

    class Ip():
        '''
        create ethernet
        '''
        def __init__(self, rest,
                     ethernet_obj,
                     **kwargs):
            self._rest = rest
            self.href = None
            self.ethernet = ethernet_obj
            if 'ipv4_address_start' in kwargs.keys():
                self.ip_type = 'v4'
            else:
                self.ip_type = 'v6'
            self.default_value = {'ipv4_address_step':'0.0.1.0',
                                  'ipv4_address_prefix':24,
                                  'ipv4_address_direction':'increment',
                                  'ipv4_gateway_start':None,
                                  'ipv4_gateway_step':'0.0.1.0',
                                  'ipv4_gateway_direction':'increment',
                                  'ipv6_address_step':'::1:0:0:0',
                                  'ipv6_address_prefix':64,
                                  'ipv6_address_direction':'increment',
                                  'ipv6_gateway_start':None,
                                  'ipv6_gateway_step':'::1.0.0.0',
                                  'ipv6_gateway_direction':'increment'}
            self.default_value.update(kwargs)
            #convert to IXIA dict format
            for i in ['address', 'gateway']:
                start_k = 'ip%s_%s_start' % (self.ip_type, i)
                step_k = 'ip%s_%s_step' % (self.ip_type, i)
                dir_k = 'ip%s_%s_direction' % (self.ip_type, i)
                if self.default_value[start_k] is not None:
                    self.default_value[start_k] = {'start': self.default_value[start_k],
                                                   'direction': self.default_value[dir_k],
                                                   'step': self.default_value[step_k]}
                else:
                    self.default_value.pop(start_k)

        def create(self):
            '''
            create IPv4/v6 under Ethernet
            :param
                self.ethernet_href
                self.list
            :return
                self.href
            '''
            if not self.ethernet.href:
                msg = 'ethernet href missed'
                self._rest.log.error(msg)
                raise self._rest.exception.TgenConfigMissingError(msg)
            url = self._rest.server_url + self.ethernet.href + '/ip%s' % self.ip_type
            response = self._rest.post_request(url,
                                               wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])
            msg = 'ip%s %s created in Ethernet %s' % (self.ip_type, self.href, self.ethernet.href)
            self._rest.log.info(msg)
            self.modify()
            return self.href
        def modify(self):
            '''
            Modify IP address
            '''
            items = [['address_start', 'address', self.href],
                     ['address_prefix', 'prefix', self.href],
                     ['gateway_start', 'gatewayIp', self.href]
                    ]
            for i in items:
                key = 'ip%s_%s' %(self.ip_type, i[0])
                if key in self.default_value:
                    data = self.default_value[key]
                    msg = self._rest.config_attribute(i[2], i[1], data)
                    self._rest.log.info('%s %s' % (key, msg))

    class Ospf_v2():
        '''
        Create device OSPF config
        '''
        def __init__(self, rest, ipv_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.ipv = ipv_obj
            self.default_value = {}

            # Primary config
            self.ospf_active = None
            self.ospf_adjacency_status = None
            self.ospf_area_id = None
            self.ospf_network_type = None
            self.ospf_int_cost = None
            self.ospf_te_metric = None
            self.ospf_options = None
            self.ospf_authentication = None
            self.ospf_password = None
            self.ospf_hello_interval = None
            self.ospf_router_dead_interval = None
            self.ospf_retransmit_interval = None
            self.ospf_lsa_refresh_time = None
            self.ospf_flood_delay = None
            self.ospf_router_lsa_count = None
            self.ospf_network_lsa_count = None
            self.ospf_summary_lsa_count = None
            self.ospf_advertise = None

            # Route config
            # Router LSAs
            self.ospf_router_lsa_active = None
            self.ospf_router_lsa_advertising_id = None
            self.ospf_router_lsa_advertising_step = None
            self.ospf_router_lsa_router_type = None
            self.ospf_router_lsa_age = None
            self.ospf_router_lsa_seq_num = None

            # Summary LSAs
            self.ospf_summary_lsa_route_count = None
            self.ospf_summary_lsa_route_num = None #(this is probably redundant in IXIA)
            self.ospf_summary_lsa_prefix_start = None
            self.ospf_summary_lsa_incr = None
            self.ospf_summary_lsa_metric = None
            self.ospf_summary_lsa_sid_step = None
            self.ospf_summary_lsa_age = None
            self.ospf_summary_lsa_seq_num = None

            # Inter-area LSAs
            self.ospf_inter_area_lsa_type = None
            self.ospf_inter_area_lsa_advertising_id = None
            self.ospf_inter_area_lsa_link_state_id = None
            self.ospf_inter_area_lsa_prefix_num = None
            self.ospf_inter_area_lsa_incr = None
            self.ospf_inter_area_lsa_prefix_len = None
            self.ospf_inter_area_lsa_prefix_start = None
            self.ospf_inter_area_lsa_age = None
            self.ospf_inter_area_lsa_seq_num = None

        def create(self):
            '''
            Creates a new BGP device object
            '''
            pass

        def modify(self):
            '''
            Modifies an existing BGP device object
            '''

    class Ospfv3():
        '''
        Create device OSPF config
        '''
        def __init__(self, rest, ipv_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.ipv = ipv_obj
            self.default_value = {}

            # Primary config
            self.ospf_active = None
            self.ospf_adjacency_status = None
            self.ospf_area_id = None
            self.ospf_network_type = None
            self.ospf_int_cost = None
            self.ospf_te_metric = None
            self.ospf_options = None
            self.ospf_authentication = None
            self.ospf_password = None
            self.ospf_hello_interval = None
            self.ospf_router_dead_interval = None
            self.ospf_retransmit_interval = None
            self.ospf_lsa_refresh_time = None
            self.ospf_flood_delay = None
            self.ospf_router_lsa_count = None
            self.ospf_network_lsa_count = None
            self.ospf_summary_lsa_count = None
            self.ospf_advertise = None

            # Route config
            # Router LSAs
            self.ospf_router_lsa_active = None
            self.ospf_router_lsa_advertising_id = None
            self.ospf_router_lsa_advertising_step = None
            self.ospf_router_lsa_router_type = None
            self.ospf_router_lsa_age = None
            self.ospf_router_lsa_seq_num = None

            # Summary LSAs
            self.ospf_summary_lsa_route_count = None
            self.ospf_summary_lsa_route_num = None #(this is probably redundant in IXIA)
            self.ospf_summary_lsa_prefix_start = None
            self.ospf_summary_lsa_incr = None
            self.ospf_summary_lsa_metric = None
            self.ospf_summary_lsa_sid_step = None
            self.ospf_summary_lsa_age = None
            self.ospf_summary_lsa_seq_num = None

            # Inter-area LSAs
            self.ospf_inter_area_lsa_type = None
            self.ospf_inter_area_lsa_advertising_id = None
            self.ospf_inter_area_lsa_link_state_id = None
            self.ospf_inter_area_lsa_prefix_num = None
            self.ospf_inter_area_lsa_incr = None
            self.ospf_inter_area_lsa_prefix_len = None
            self.ospf_inter_area_lsa_prefix_start = None
            self.ospf_inter_area_lsa_age = None
            self.ospf_inter_area_lsa_seq_num = None

    class IgmpMld():
        '''
        create IGMP
        '''
        def __init__(self, rest,
                     ipv_obj,
                     **kwargs):
            self._rest = rest
            self.href = None
            self.ipv = ipv_obj
            self.default_value = {'igmp_group_step': '0.0.0.1',
                                  'igmp_group_direction': 'increment',
                                  'igmp_source_start' : None,
                                  'igmp_source_step': '0.0.0.1',
                                  'igmp_source_direction': 'increment',
                                  'mld_source_start' : None,
                                  'mld_group_step': '::1',
                                  'mld_group_direction': 'increment',
                                  'mld_source_step': '::1',
                                  'mld_source_direction': 'increment',
                                 }
            self.default_value.update(kwargs)
            #mld
            if self.ipv.ip_type == 'v6':
                self.host_name = 'mld'
            else:
                self.host_name = 'igmp'
            for i in ['group', 'source']:
                start_k = '%s_%s_start' % (self.host_name, i)
                step_k = '%s_%s_step' % (self.host_name, i)
                dir_k = '%s_%s_direction' % (self.host_name, i)
                if self.default_value[start_k] is not None:
                    self.default_value[start_k] = {'start': self.default_value[start_k],
                                                   'direction': self.default_value[dir_k],
                                                   'step': self.default_value[step_k]}
                else:
                    self.default_value.pop(start_k)

        def create(self):
            '''
            create igmpHost or mldHost
            '''
            url = self._rest.server_url + self.ipv.href + '/%sHost' % self.host_name
            response = self._rest.post_request(url,
                                               wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])
            msg = '%s host is created' % self.host_name
            self._rest.log.info(msg)
            self.modify()
            return self.href
        def modify(self):
            '''
            Modify
            '''
            #supported attribute
            href = self.href
            grp_list_href = '%s/%sMcastIP%sGroupList' %\
                             (href, self.host_name, self.ipv.ip_type)
            src_list_href = '%s/%sUcastIP%sSourceList' \
                              % (grp_list_href, self.host_name, self.ipv.ip_type)
            items = [['version', 'versionType', href],
                     ['num_of_group_range', 'noOfGrpRanges', href],
                     ['source_mode', 'sourceMode', grp_list_href],
                     ['group_start', 'startMcastAddr', grp_list_href],
                     ['group_port_step', ['startMcastAddr', '/nest/1'], grp_list_href],
                     ['group_address_count', 'mcastAddrCnt', grp_list_href],
                     ['group_address_increment', 'mcastAddrIncr', grp_list_href],
                     ['num_source_range', 'noOfSrcRanges', grp_list_href],
                     ['source_start', 'startUcastAddr', src_list_href],
                     ['source_port_step', ['startUcastAddr', '/nest/1'], src_list_href],
                     ['source_addree_increment', 'ucastAddrIncr', src_list_href],
                     ['source_address_count', 'ucastSrcAddrCnt', src_list_href]
                    ]
            for i in items:
                key = '%s_%s' %(self.host_name, i[0])
                if key in self.default_value:
                    data = self.default_value[key]
                    msg = self._rest.config_attribute(i[2], i[1], data)
                    self._rest.log.info('%s %s' % (key, msg))

class NewTrafficItem():
    class Traffic():
        '''
        Initializes a new traffic object. Not currently used for anything but
        implemented for the purpose of maintaining the rest API hierarchy

        Rest API Tree Path:
        IxNetwork
            Traffic
        '''
        def __init__(self, rest, **kwargs):
            self._rest = rest
            self.href = self._rest.session_url + '/traffic'
            self.state = None

    class TrafficItem():
        '''
        Initializes a new traffic item object.

        Rest API Tree Path:
        IxNetwork
            Traffic
                TrafficItem
        '''
        def __init__(self, rest, traffic_obj, traffic_type='ipv4', **kwargs):
            self._rest = rest
            self.href = None
            self.traffic = traffic_obj
            self.traffic_item_name = None
            self.traffic_type = traffic_type
            self.bidirectional = False
            self.allow_self_destined = False
            self.transmit_mode = 'interleaved'
            self.src_dst_mesh_type = 'none'
            self.route_mesh_type = 'oneToOne'
            self.enabled = None
            self.endpoint_sets = []

            items = ['traffic_item_name', 'traffic_type', 'src_dst_mesh_type',
                     'route_mesh_type', 'bidirectional', 'transmit_mode', 'enabled']

            for item in items:
                if item in kwargs.keys():
                    setattr(self, item, kwargs[item])

        def create(self):
            '''
            Creates a new traffic item object
            '''
            url = self.traffic.href + '/trafficItem'

            data = {'name': self.traffic_item_name,
                    'trafficType': self.traffic_type,
                    'biDirectional': self.bidirectional,
                    'allowSelfDestined': self.allow_self_destined,
                    'transmitMode': self.transmit_mode,
                    'srcDestMesh': self.src_dst_mesh_type,
                    'routeMesh': self.route_mesh_type,
            }

            response = self._rest.post_request(url, data, wait_url_arg=None)
            self.href = self._rest.get_href(response.json()['links'])

            msg = 'Traffic item %s was created at href %s' % (self.traffic_item_name, self.href)
            self._rest.log.info(msg)

            return self.href

        def enable_traffic_item(self):
            '''
            Enables the specified traffic item
            '''
            url = self._rest.server_url + self.href
            data = {
                'enabled': 'true'
            }
            response = self._rest.patch_request(url, data)

        def disable_traffic_item(self):
            '''
            Disables the specified traffic item
            '''
            url = self._rest.server_url + self.href
            data = {
                'enabled': 'false'
            }
            response = self._rest.patch_request(url, data)

        def set_traffic_type(self, traffic_type='ipv4'):
            '''
            Sets the traffic type ['ipv4|'ipv6']
            '''
            url = self._rest.server_url + self.href
            data = {
                'trafficType': traffic_type
            }
            response = self._rest.patch_request(url, data)

        def set_bidirectional(self, bidirectional=False):
            '''
            Sets a traffic item as bidirectional [True|False]
            '''
            url = self._rest.server_url + self.href
            data = {
                'biDirectional': bidirectional
            }
            response = self._rest.patch_request(url, data)

        def set_self_destined(self, self_destined=False):
            '''

            '''
            url = self._rest.server_url + self.href
            data = {
                'allowSelfDestined': self_destined
            }
            response = self._rest.patch_request(url, data)

        def set_mesh_type(self, mesh_type='oneToOne'):
            '''
            Sets a traffic item mesh type
            Options include fullMesh, manyToMany, none, oneToOne
            '''
            url = self._rest.server_url + self.href
            data = {
                'srcDestMesh': mesh_type
            }
            response = self._rest.patch_request(url, data)

        def set_mesh_route(self, mesh_type='oneToOne'):
            '''
            Sets a traffic item route mesh type
            Options include fullMesh, oneToOne
            '''
            url = self._rest.server_url + self.href
            data = {
                'routeMesh': mesh_type
            }
            response = self._rest.patch_request(url, data)

        def add_endpoint_set(self, sources, destinations, mcast_destinations):
            '''
            Adds a new endpoint set object to the traffic item
            '''
            new_endpoint_set = NewTrafficItem.EndpointSet(self._rest, self, sources, destinations, mcast_destinations)
            new_endpoint_set.create()
            self.endpoint_sets.append(new_endpoint_set)

            return new_endpoint_set.hrefs

    class EndpointSet():
        '''
        Initializes a new endpoint set object for a given traffic item.
        Supports IP -> IP and IP -> Multicast

        Rest API Tree Path:
        IxNetwork
            Traffic
                TrafficItem
                    EndpointSet
        '''
        def __init__(self, rest, traffic_item_obj, sources, destinations,
                     mcast_destinations=None, **kwargs):
            self._rest = rest
            self.hrefs = []
            self.traffic_item = traffic_item_obj
            self.name = None
            self.traffic_type = self.traffic_item.traffic_type
            self.sources = sources
            self.destinations = destinations
            self.mcast_destinations = mcast_destinations
            self.mcast_dest_start = destinations
            self.mcast_dest_count = 10

        def create(self):
            '''
            Creates a new endpoint set for a given traffic item

            :returns: The newly created endpoint sets href
                e.g. '/api/v1/sessions/1/ixnetwork/traffic/trafficItem/31/endpointSet/1'
            '''
            url = self._rest.server_url + self.traffic_item.href + '/endpointSet'

            sources_url = []
            destinations_url = []
            data = {}
            data['multicastDestinations'] = []
            temp_dict = {}

            # Searh all device groups and igmp/mld ranges for matching sources/destinations
            topo_url = self._rest.session_url + '/topology'
            topo_response = self._rest.get_request(topo_url)

            # Search topologies
            for topo_id in topo_response.json():
                device_group_url = topo_url + '/' + str(topo_id['id']) + '/deviceGroup'
                device_group_response = self._rest.get_request(device_group_url)

                # Search device groups
                for device_group in device_group_response.json():
                    ethernet_url = device_group_url + '/' + str(device_group['id']) + '/ethernet'
                    ethernet_response = self._rest.get_request(ethernet_url)

                    # search ethernets
                    for ethernet in ethernet_response.json():
                        if self.traffic_type == 'ipv4':
                            ip_url = ethernet_url + '/' + str(ethernet['id']) + '/ipv4'
                            ip_response = self._rest.get_request(ip_url)
                        if self.traffic_type == 'ipv6':
                            ip_url = ethernet_url + '/' + str(ethernet['id']) + '/ipv6'
                            ip_response = self._rest.get_request(ip_url)

                        # search ipv4s/ipv6s
                        for ip in ip_response.json():
                            address_url = ip_url + '/' + str(ip['id'])
                            address_response = self._rest.get_request(address_url)
                            address_href = address_response.json()['address']
                            addresses = self._rest.get_multivalue(address_href)

                            for source in self.sources:
                                if source in addresses:
                                    sources_url.append(address_url.split(self._rest.server_url)[1])
                            for destination in self.destinations:
                                if destination in addresses:
                                    destinations_url.append(address_url.split(self._rest.server_url)[1])

                            # search igmp/mld
                            if self.mcast_destinations:
                                for mcast in address_response.json():
                                    if self.traffic_type == 'ipv4':
                                        igmp_url = address_url + '/igmpHost'
                                        igmp_response = self._rest.get_request(igmp_url)
                                        for igmp_range in igmp_response.json():
                                            igmp_range_url = igmp_url + '/' + str(igmp_range['id']) + '/igmpMcastIPv4GroupList'
                                            igmp_range_response = self._rest.get_request(igmp_range_url)

                                            igmp_range_href = igmp_range_response.json()['startMcastAddr']
                                            igmp_range_incr_href = igmp_range_response.json()['mcastAddrIncr']
                                            igmp_range_count_href = igmp_range_response.json()['mcastAddrCnt']
                                            igmp_ranges = self._rest.get_multivalue(igmp_range_href)

                                            for mcast_dest in self.mcast_destinations:
                                                if mcast_dest in igmp_ranges:
                                                    mcast_dest_increment = self._rest.get_multivalue(igmp_range_incr_href)[0]
                                                    mcast_dest_count = self._rest.get_multivalue(igmp_range_count_href)[0]

                                                    if mcast_dest not in temp_dict.values():
                                                        temp_dict = {
                                                            'arg1': 'false',
                                                            'arg2': 'none',
                                                            'arg3': mcast_dest,
                                                            'arg4': mcast_dest_increment,
                                                            'arg5': mcast_dest_count
                                                        }
                                                        data['multicastDestinations'].append(temp_dict)

                                    if self.traffic_type == 'ipv6':
                                        mld_url = address_url + '/mldHost'
                                        mld_response = self._rest.get_request(mld_url)
                                        for mld_range in mld_response.json():
                                            mld_range_url = mld_url + '/' + str(mld_range['id']) + '/mldMcastIPv6GroupList'
                                            mld_range_response = self._rest.get_request(mld_range_url)

                                            mld_range_href = mld_range_response.json()['startMcastAddr']
                                            mld_range_incr_href = mld_range_response.json()['mcastAddrIncr']
                                            mld_range_count_href = mld_range_response.json()['mcastAddrCnt']
                                            mld_ranges = self._rest.get_multivalue(mld_range_href)

                                            for mcast_dest in self.mcast_destinations:
                                                if mcast_dest in mld_ranges:
                                                    mcast_dest_increment = self._rest.get_multivalue(mld_range_incr_href)[0]
                                                    mcast_dest_count = self._rest.get_multivalue(mld_range_count_href)[0]

                                                    if mcast_dest not in temp_dict.values():
                                                        temp_dict = {
                                                            'arg1': 'false',
                                                            'arg2': 'none',
                                                            'arg3': mcast_dest,
                                                            'arg4': mcast_dest_increment,
                                                            'arg5': mcast_dest_count
                                                        }
                                                        data['multicastDestinations'].append(temp_dict)

            if sources_url:
                data['sources'] = sources_url
            if destinations_url:
                data['destinations'] = destinations_url

            response = self._rest.post_request(url, post_data=data, wait_url_arg=None)
            href = self._rest.get_href(response.json()['links'])
            self.hrefs.append(self._rest.get_href(response.json()['links']))
            #self.endpoint_sets.append()

            msg = 'Endpoint set %s was created at href %s' % (self.name, href)
            self._rest.log.info(msg)


            return href

    class ConfigElement():
        '''
        Initializes the config element object. This mostly acts as a common href
        point for the various frame modifier objects

        Rest API Tree Path:
        IxNetwork
            Traffic
                TrafficItem
                    ConfigElement
        '''
        def __init__(self, rest, traffic_item_obj, **kwargs):
            self._rest = rest
            self.traffic_item = traffic_item_obj
            self.href = self.traffic_item.href + '/configElement'
            self.endpoint_set_id = None
            self.id_hrefs = []

            endpoint_set_url = self._rest.server_url + self.href
            endpoint_set_response = self._rest.get_request(endpoint_set_url)

            for endpoint_id in endpoint_set_response.json():
                self.id_hrefs.append(endpoint_set_url + '/' + str(endpoint_id['id']))

    class FramePayload():
        '''
        Initializes the frame payload object.

        Rest API Tree Path:
        Ixnetwork
            Traffic
                TrafficItem
                    ConfigElement
                        FramePayload
        '''
        def __init__(self, rest, config_element_obj, **kwargs):
            self._rest = rest
            self.hrefs = None
            self.config_element = config_element_obj
            self.payload_type = None
            self.payload_custom_pattern = None
            self.payload_custom_repeat = False

            if 'payload_type' in kwargs.keys():
                self.payload_type = kwargs['payload_type']
            if 'payload_custom_pattern' in kwargs.keys():
                self.payload_custom_pattern = kwargs['payload_custom_pattern']
            if 'payload_custom_repeat' in kwargs.keys():
                self.payload_custom_repeat = kwargs['payload_custom_repeat']

        def create(self):
            data = {}
            if self.payload_type:
                data['type'] = self.payload_type
            if self.payload_custom_pattern:
                data['customPattern'] = self.payload_custom_pattern
            if self.payload_custom_repeat:
                data['customRepeat'] = self.payload_custom_repeat

            if not data:
                self._rest.log.info("No frame payload values provided - using defaults")
            else:
                for config_element in self.config_element.id_hrefs:
                    url = config_element + '/framePayload'
                    self._rest.patch_request(url, data)

        def modify(self,
                   payload_type='incrementByte',
                   payload_custom_pattern='',
                   payload_custom_repeat=False):

            endpoint_set_url = self._rest.server_url + self.config_element.href
            endpoint_set_response = self._rest.get_request(endpoint_set_url)

            data = {
                'type': payload_type,
                'customPattern' : payload_custom_pattern,
                'customRepeat' : payload_custom_repeat,
            }

            for endpoint_id in endpoint_set_response.json():
                url = endpoint_set_url + '/' + str(endpoint_id['id']) + '/framePayload'
                self._rest.patch_request(url, data)

    class FrameRate():
        '''
        Initializes the frame rate object.

        Rest API Tree Path:
        Ixnetwork
            Traffic
                TrafficItem
                    ConfigElement
                        FrameRate
        '''
        def __init__(self, rest, config_element_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.config_element = config_element_obj
            self.rate_type = None
            self.bit_rate_units = None
            self.frame_rate = None
            self.enforce_min_inter_packet_gap = None
            self.inter_packet_gap_units_type = None

            if 'rate_type' in kwargs.keys():
                self.rate_type = kwargs['rate_type']
            if 'bit_rate_units' in kwargs.keys():
                self.bit_rate_units = kwargs['bit_rate_units']
            if 'frame_rate' in kwargs.keys():
                self.frame_rate = kwargs['frame_rate']
            if 'enforce_min_inter_packet_gap' in kwargs.keys():
                self.enforce_min_inter_packet_gap = kwargs['enforce_min_inter_packet_gap']
            if 'inter_packet_gap_units_type' in kwargs.keys():
                self.inter_packet_gap_units_type = kwargs['inter_packet_gap_units_type']

        def create(self):
            data = {}
            if self.rate_type:
                data['type'] = self.rate_type
            if self.bit_rate_units:
                data['bigRateUnitsType'] = self.bit_rate_units
            if self.frame_rate:
                data['rate'] = self.frame_rate
            if self.enforce_min_inter_packet_gap:
                data['enforceMinimumInterPacketGap'] = self.enforce_min_inter_packet_gap
            if self.inter_packet_gap_units_type:
                data['interPacketGapUnitsType'] = self.inter_packet_gap_units_type

            if not data:
                self._rest.log.info("No frame rate values provided - using defaults")
            else:
                for config_element in self.config_element.id_hrefs:
                    url = config_element + '/frameRate'
                    self._rest.patch_request(url, data)

        def modify(self,
                   rate_type='percentLineRate',
                   frame_rate=10,
                   bit_rate_units='bitsPerSec',
                   enforce_min_inter_packet_gap=8,
                   inter_packet_gap_units_type='bytes'):

            endpoint_set_url = self._rest.server_url + self.config_element.href
            endpoint_set_response = self._rest.get_request(endpoint_set_url)

            data = {
                'type': rate_type,
                'rate': frame_rate,
                'bitRateUnitsType': bit_rate_units,
                'enforceMinimumInterPacketGap': enforce_min_inter_packet_gap,
                'interPacketGapUnitsType': inter_packet_gap_units_type
            }

            for endpoint_id in endpoint_set_response.json():
                url = endpoint_set_url + '/' + str(endpoint_id['id']) + '/frameRate'
                self._rest.patch_request(url, data)

    class FrameRateDistribution():
        '''
        Initializes the frame rate distribution object.

        Rest API Tree Path:
        Ixnetwork
            Traffic
                TrafficItem
                    ConfigElement
                        FrameRateDistribution
        '''
        def __init__(self, rest, config_element_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.config_element = config_element_obj
            self.port_distribution = None
            self.stream_distribution = None

            if 'port_distribution' in kwargs.keys():
                self.port_distribution = kwargs['port_distribution']
            if 'stream_distribution' in kwargs.keys():
                self.stream_distribution = kwargs['stream_distribution']

        def create(self):
            data = {}
            if self.port_distribution:
                data['portDistribution'] = self.port_distribution
            if self.stream_distribution:
                data['streamDistribution'] = self.stream_distribution

            if not data:
                self._rest.log.info("No frame rate distribution values provided - using defaults")
            else:
                for config_element in self.config_element.id_hrefs:
                    url = config_element + '/frameRateDistribution'
                    self._rest.patch_request(url, data)

        def modify(self, port_distribution='applyRateToAll', stream_distribution='splitRateEvenly'):
            endpoint_set_url = self._rest.server_url + self.config_element.href
            endpoint_set_response = self._rest.get_request(endpoint_set_url)

            data = {
                'portDistribution': port_distribution,
                'streamDistribution': stream_distribution,
            }

            for endpoint_id in endpoint_set_response.json():
                url = endpoint_set_url + '/' + str(endpoint_id['id']) + '/frameRateDistribution'
                self._rest.patch_request(url, data)

    class FrameSize():
        '''
        Initializes the frame size object.

        Rest API Tree Path
        Ixnetwork
            Traffic
                TrafficItem
                    ConfigElement
                        FrameSize
        '''
        def __init__(self, rest, config_element_obj, **kwargs):
            self._rest = rest
            self.href = None
            self.config_element = config_element_obj
            self.frame_size_type = None
            self.frame_size_fixed_size = None
            self.frame_size_increment_start = None
            self.frame_size_increment_stop = None
            self.frame_size_increment_step = None
            self.frame_size_preset_distribution = None
            self.frame_size_quad_gaussian = None
            self.frame_size_random_min = None
            self.frame_size_random_max = None
            self.frame_size_weighted_pairs = None
            self.frame_size_weighted_pairs_range = None

            items = ['frame_size_type', 'frame_size_fixed_size', 'frame_size_increment_start', 'frame_size_increment_stop', 'frame_size_increment_step',
            'frame_size_preset_distribution', 'frame_size_quad_gaussian', 'frame_size_random_min', 'frame_size_random_max', 'frame_size_weighted_pairs',
            'frame_size_weighted_pairs_range']

            for item in items:
                if item in kwargs.keys():
                    setattr(self, item, kwargs[item])

        def create(self):
            data = {}

            if self.frame_size_type:
                data['frameType'] = self.frame_size_type
            if self.frame_size_fixed_size:
                data['fixedSize'] = self.frame_size_fixed_size
            if self.frame_size_increment_start:
                data['incrementFrom'] = self.frame_size_increment_start
            if self.frame_size_increment_stop:
                data['incrementTo'] = self.frame_size_increment_stop
            if self.frame_size_increment_step:
                data['incrementStep'] = self.frame_size_increment_step
            if self.frame_size_preset_distribution:
                data['presetDistribution'] = self.frame_size_preset_distribution
            if self.frame_size_quad_gaussian:
                data['quadGaussian'] = self.frame_size_quad_gaussian
            if self.frame_size_random_min:
                data['randomMin'] = self.frame_size_random_min
            if self.frame_size_random_max:
                data['randomMax'] = self.frame_size_random_max
            if self.frame_size_weighted_pairs:
                data['weightedPairs'] = self.frame_size_weighted_pairs
            if self.frame_size_weighted_pairs_range:
                data['weightedRangePairs'] = self.frame_size_weighted_pairs_range

            if not data:
                self._rest.log.info("No frame size values provided - using defaults")
            else:
                for config_element in self.config_element.id_hrefs:
                    url = config_element + '/frameSize'
                    self._rest.patch_request(url, data)

        def modify(self,
                   frame_size_type=None,
                   frame_size_fixed_size=None,
                   frame_size_increment_start=None,
                   frame_size_increment_stop=None,
                   frame_size_increment_step=None,
                   frame_size_preset_distribution=None,
                   frame_size_quad_gaussian=None,
                   frame_size_random_min=None,
                   frame_size_random_max=None,
                   frame_size_weighted_pairs=None,
                   frame_size_weighted_pairs_range=None):

            endpoint_set_url = self._rest.server_url + self.config_element.href
            endpoint_set_response = self._rest.get_request(endpoint_set_url)

            data = {}

            if frame_size_type:
                data['type'] = frame_size_type
            if frame_size_fixed_size:
                data['fixedSize'] = frame_size_fixed_size
            if frame_size_increment_start:
                data['incrementFrom'] = frame_size_increment_start
            if frame_size_increment_stop:
                data['incrementTo'] = frame_size_increment_stop
            if frame_size_increment_step:
                data['incrementStep'] = frame_size_increment_step
            if frame_size_preset_distribution:
                data['presetDistribution'] = frame_size_preset_distribution
            if frame_size_quad_gaussian:
                data['quadGaussian'] = frame_size_quad_gaussian
            if frame_size_random_min:
                data['randomMin'] = frame_size_random_min
            if frame_size_random_max:
                data['randomMax'] = frame_size_random_max
            if frame_size_weighted_pairs:
                data['weightedPairs'] = frame_size_weighted_pairs
            if frame_size_weighted_pairs_range:
                data['weightedRangePairs'] = frame_size_weighted_pairs_range

            for endpoint_id in endpoint_set_response.json():
                url = endpoint_set_url + '/' + str(endpoint_id['id']) + '/frameSize'
                self._rest.patch_request(url, data)
