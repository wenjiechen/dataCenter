__author__ = 'wenjie'
from devicemodels import Host, Spine, Leaf, Rack
import devicemodels
import networkx as nx
import csv
import sys
import re

class DataCenter(object):

    def __init__(self, name='test'):
        self.name = name
        self._graph_model = nx.Graph()

    @property
    def model(self):
        return self._graph_model

    def _add_or_get_device_in_model(self,device):
        """get exist node or add not exist node in graph model.

            Don't use the method out side this class
        """
        #add not exist node
        if device not in self._graph_model.nodes():
            # add attribute for node
            if isinstance(device, Rack):
                self._graph_model.add_node(device,hosts_leafs=set())
            else:
                self._graph_model.add_node(device,links={})
            return device
        # get exist node in model
        else:
            for n in self._graph_model.nodes_iter():
                if n == device:
                    return n

    def _add_link(self, args):
        device1, id1, port1, device2, id2, port2, link_speed = args

        # get exist node or add not exist node in graph model.
        device1 = self._add_or_get_device_in_model(devicemodels.devices_factory(device1,id1))
        device2 = self._add_or_get_device_in_model(devicemodels.devices_factory(device2,id2))

        # add link in node
        device1.add_link(port1,device2)
        device2.add_link(port2,device1)

        # add edge between two nodes and set nodes' links attributes
        self._graph_model.add_edge(device1,device2,{'link_speed':link_speed})
        self._graph_model.node[device1]['links'][int(port1)]=device2
        self._graph_model.node[device2]['links'][int(port2)]=device1

        # if a node is Host, add the corresponding Rack node
        host = None
        if isinstance(device1,Host):
            host = device1
        elif isinstance(device2,Host):
            host = device2

        if host is not None:
            # add Host to Rack
            rack = self._add_or_get_device_in_model(devicemodels.devices_factory('Rack',host.rack_id))
            rack.add_hosts_leafs(host)
            self._graph_model.node[rack]['hosts_leafs'].add(host)

            # add Leaf to Rack
            leaf = device2 if host == device1 else device1
            rack.add_hosts_leafs(leaf)
            self._graph_model.node[rack]['hosts_leafs'].add(leaf)

    def load_model_from_files(self, file_path1, *file_paths,**kwargs):

        customized_delimiter = kwargs['delimiter'] if 'delimiter' in kwargs.keys() else ','
        paths = [file for file in file_paths]
        paths.append(file_path1)

        for file_path in paths:
            with open(file_path,'rb') as csv_model:
                reader = csv.reader(csv_model,delimiter=customized_delimiter)
                # skip the headers of csv file
                next(reader, None)
                for line_num, line in enumerate(reader):
                    try:
                        # eliminate whitespace in words
                        self._add_link([field.strip() for field in line])
                    except Exception:
                        print >> sys.stderr,"Check model file: '%s', at line: %d" %(file_path,line_num+2)
                        raise



    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

    def clean_model(self):
        self._graph_model.clear()

    def _is_device_exist(self,device):
        if device not in self._graph_model.nodes():
            if type(device) in (Spine, Leaf, Host):
                print >> sys.stderr, "WARNING: '%s' is not in the graph model" %device
                return False
            else:
                raise TypeError("Don't support: '%s'" %type(device))
        else:
            return True

    def remove_link(self,device1,device2):
        #delete edge from model
        try:
            self._graph_model.remove_edge(device1,device2)
        except Exception as ex:
            if self._is_device_exist(device1) and self._is_device_exist(device2):
                # link doesn't exist
                print >> sys.stderr, "WARNING: %s" %(ex.args[0])
            return
        else:
            # delete link attribute in node1 and node2
            links1 = self._graph_model.node[device1]['links']
            links2 = self._graph_model.node[device2]['links']
            for port, node in links1.items():
                if node == device2:
                    del links1[port]
            for port, node in links2.items():
                if node == device1:
                    del links2[port]

    def remove_devices(self,device,*devices):
        device_list = [dev for dev in devices]
        device_list.append(device)
        for dev in device_list:
            self._remove_device(dev)

    def _remove_device(self,device):
        # check if node is valid
        if not self._is_device_exist(device):
            return

        # delete all edge between node and its neighbors
        for neighbor in self._graph_model.neighbors(device):
            self.remove_link(device,neighbor)

        # delete device from graph model
        self._graph_model.remove_node(device)

        # delete device from rack
        if type(device) in (Leaf,Host):
            for node in self._graph_model.nodes_iter():
                if isinstance(node,Rack) and device in self._graph_model.node[node]['hosts_leafs']:
                    self._graph_model.node[node]['hosts_leafs'].remove(device)
                    break

    def _is_device_in_rack(self,device,rack):
        """

        :param device:
        :param rack:
        :return: :raise TypeError:
        """
        if rack not in self._graph_model.nodes():
            if not isinstance(rack,Rack):
                raise TypeError("Don't support '%s', only support 'Rack' type" %(type(rack)))
            else:
                print >> sys.stderr, "WARNING: '%s' is not exist" %(rack)
                return False
        elif device not in self._graph_model.node[rack]['hosts_leafs']:
            print >> sys.stderr, 'WARNING: device "%s" is not in %s' %(device,rack)
            return False
        else:
            return True

    def query_device_on_port(self,device,port,rack=None):
        """

        :param device:
        :param port:
        :param rack:
        :return:
        :raise:
        """
        if rack is not None and not self._is_device_in_rack(device,rack):
            return None

        try:
            # find the device on port
            ret_device = self._graph_model.node[device]['links'][int(port)]
        except KeyError as ex:
            if self._is_device_exist(device) and ex.args[0] == port:
                print >> sys.stderr, "WARNING: the 'port: %s' of '%s' is not exist or not connected to any device" %(ex,device)
            return None
        except Exception:
            raise
        else:
            return ret_device

    def query_connected_ports(self,device_queried,device2,rack1=None,rack2=None):
        """

        :param device_queried:
        :param device2:
        :param rack1:
        :param rack2:
        :return:
        """
        # check if devices are exist and placed on racks
        if not self._is_device_exist(device_queried) or not self._is_device_exist(device2):
            return None
        if rack1 is not None and not self._is_device_in_rack(device_queried,rack1):
            return None
        if rack2 is not None and not self._is_device_in_rack(device2,rack2):
            return None

        # find the ports of device_queried connected to device2
        links1 = self._graph_model.node[device_queried]['links']
        return (port for port, device in links1.items() if device == device2)

    def get_device(self,device):
        for node in self._graph_model.nodes_iter():
            if node == device:
                return node
        return None

    def query_all_paths(self,source,target):
        return nx.all_shortest_paths(self._graph_model, source, target)

    def break_link(self,device1,device2):
        """break link between two devices. only used for testing link_check()

        don't use for other purpose, which will cause a non consistent model state
        """
        try:
            self._graph_model.remove_edge(device1,device2)
        except Exception as ex:
            if self._is_device_exist(device1) and self._is_device_exist(device2):
                # link doesn't exist
                print >> sys.stderr,"WARNING: %s" %(ex.args[0])
        # print "break link between '%s' and '%s'" %(device1,device2)

    def link_check(self):
        #check each Spine, Leaf, Host
        break_pairs=[]
        for device in ( node for node in self._graph_model.nodes_iter() if type(node) is not Rack):
            links = self._graph_model.node[device]['links']
            for port, device2 in links.items():
                if device2 not in self._graph_model.neighbors(device):
                    break_pairs.append((device,device2))
                    print >> sys.stderr, "WARNING: link between '%s' and '%s' is broken" %(device,device2)
                    del links[port]
                    # delete link in device2's link table
                    links2 = self._graph_model.node[device2]['links']
                    for port2,device_tmp in links2.items():
                        if device_tmp == device:
                            del links2[port2]
            return break_pairs

    def all_devices(self):
        return self._graph_model.nodes()

    def all_links(self):
        return self._graph_model.edges()

    def all_links_iter(self):
        yield self._graph_model.edges()

    def all_devices_iter(self):
        yield self._graph_model.nodes()

    def devices_in_rack(self,rack):
        if self._is_device_exist(rack):
            return self._graph_model.node[rack]['hosts_leafs']

    def _convert_device_input(self,device_input):
        #convert a input string to device object
        if type(device_input) is not str:
            return device_input
        valid_ptn = re.compile(r'[a-zA-z]+_\d+$')

        if valid_ptn.match(device_input) is None:
            raise ValueError("%s is not valid input pattern."
                             "\nPlease input like 'host_1', no matter lower "
                             "or upper case" %device_input)

        type_ptn = re.compile(r'[a-zA-Z]+')
        device_type = type_ptn.match(device_input).group()
        id_ptn = re.compile(r'\d+')
        id = id_ptn.findall(device_input)[0]
        return devicemodels.devices_factory(device_type,id)

def test11():
    dc = DataCenter()
    file_path1 = 'testBadModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)
    # print dc.all_devices()
    print dc._convert_device_input('spine_1')
    print dc._convert_device_input('host_1')
    print dc._convert_device_input('leaf_10')
    print dc._convert_device_input('rack_1')
    print dc._convert_device_input(Host(100))
    # print dc._convert_device_input('Host(100)')
    # print dc._convert_device_input('host1')
    # print dc._convert_device_input('host_qq_sd2')

if __name__ == '__main__':
    test11()

