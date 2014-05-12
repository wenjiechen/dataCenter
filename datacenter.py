"""
The graph model of data center. Each device is a node in the graph model
"""

import csv
import sys
import re
import threading
import time
import networkx as nx
from devicemodels import Host, Spine, Leaf, Rack, devices_factory

__author__ = 'Wenjie Chen'


def synchronized_with(lock_name):
    """A decorator to place an instance based lock around a method
    """

    def _synched(method):

        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
        return synced_method

    return _synched


class DataCenter(object):
    """ Data center model represented by graph.
    """

    def __init__(self,is_print=False):
        """

        :param is_print: print the trace of the data center state.
                         used for LinkChecker in multi-threading environment,
                         to indicate inner state of data center
        """
        self._graph_model = nx.Graph()
        self.rlock=threading.RLock()
        self._is_print = is_print


    @property
    def all_devices(self):
        """ All device in data center

        rtype: list
        :return: list of nodes, change the list won't affect model
        """
        return self._graph_model.nodes()


    @property
    def all_links(self):
        """ All links in data center

        rtype: list
        :return: list of links, which are pairs of two nodes
        """
        return self._graph_model.edges()


    def _add_or_get_device_in_model(self,device):
        #get exist node or add not exist node in graph model.
        #Don't use the method out side this class

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


    def _add_link(self, fields):
        # add link and corresponding devices in Data Center model, used by load_model_from_files
        device1, id1, port1, device2, id2, port2, link_speed = fields

        # get exist node or add not exist node in graph model.
        device1 = self._add_or_get_device_in_model(devices_factory(device1,id1))
        device2 = self._add_or_get_device_in_model(devices_factory(device2,id2))

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
            rack = self._add_or_get_device_in_model(devices_factory('Rack',host.rack_id))
            self._graph_model.node[rack]['hosts_leafs'].add(host)

            # add Leaf to Rack
            leaf = device2 if host == device1 else device1
            self._graph_model.node[rack]['hosts_leafs'].add(leaf)


    @synchronized_with("rlock")
    def load_model_from_files(self, file_path1, *file_paths,**kwargs):
        """ Load data center model from csv files, model is defined by links.

        usage: load_model_from_files(file1,...,file_n, delimiter='|')
        :param file_path1: first file, required
        :param file_paths: rest files, various length and not required
        :param kwargs: can change 'delimiter' of csv, default delimiter=','
        :raise:
        """
        if self._is_print is True:
            print '---------------load model---------------'

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
                        print >> sys.stderr,"ERROR: Check model file: '%s', at line: %d" %(file_path,line_num+2)
                        raise


    @synchronized_with("rlock")
    def clean_datacenter(self):
        """Remove all devices and links in data center.
        """
        self._graph_model.clear()


    def _is_device_exist(self,device):
        if device not in self._graph_model.nodes():
            print >> sys.stderr, "WARNING: '%s' is not exist" %device
            return False
        else:
            return True


    def _convert_device_input(self,device_input):
        #convert a input string to device object
        if type(device_input) is not str:
            return device_input
        valid_ptn = re.compile(r'^[a-zA-Z]+[-_]*\d+$')

        if valid_ptn.match(device_input) is None:
            raise ValueError("%s is not valid input pattern."
                             "\nPlease input like 'spine1', 'host-1' or 'leaf_1', no matter lower "
                             "or upper case" %device_input)

        type_ptn = re.compile(r'[a-zA-Z]+')
        device_type = type_ptn.match(device_input).group()
        id_ptn = re.compile(r'\d+')
        id = id_ptn.findall(device_input)[0]
        return devices_factory(device_type,id)


    @synchronized_with("rlock")
    def remove_link(self,device1,device2):
        """Remove link between two devices.

        If link is not exist, print a WARNING to standard error
        :param device1: first device of the link
        :param device2: second device of the link
        """
        device1 = self._convert_device_input(device1)
        device2 = self._convert_device_input(device2)
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


    @synchronized_with("rlock")
    def remove_devices(self,device,*devices):
        """Remove devices and corresponding all links in data center.

        If device is host or leaf, also remove it from its rack
        If a device is not exist, print a WARNING to standard error
        usage: remove_devices(device1,....,device_n)
        :param device: first device, required
        :param devices: rest devices, various length and not required
        """
        device_list = [self._convert_device_input(dev) for dev in devices]
        device_list.append(self._convert_device_input(device))
        for dev in device_list:
            self._remove_device(dev)


    def _remove_device(self,device):
        # remove a signal device and its links in data center
        # check if node is valid
        device = self._convert_device_input(device)
        if not self._is_device_exist(device):
            return

        # remove all edge between node and its neighbors
        for neighbor in self._graph_model.neighbors(device):
            self.remove_link(device,neighbor)

        # remove device from graph model
        self._graph_model.remove_node(device)

        # remove Leaf or Host from rack
        if type(device) in (Leaf,Host):
            for node in self._graph_model.nodes_iter():
                if isinstance(node,Rack) and device in self._graph_model.node[node]['hosts_leafs']:
                    self._graph_model.node[node]['hosts_leafs'].remove(device)
                    break


    def _is_device_in_rack(self,device,rack):
        # check if rack is exist in data center model
        if rack not in self._graph_model.nodes():
            print >> sys.stderr, "WARNING: '%s' is not exist" %(rack)
            return False
        elif device not in self._graph_model.node[rack]['hosts_leafs']:
            print >> sys.stderr, 'WARNING: device "%s" is not in %s' %(device,rack)
            return False
        else:
            return True


    @synchronized_with("rlock")
    def query_device(self,device_queried,port,rack=None):
        """Find the device that connected to a specific port of another device.

        Rack is not required, because each device has a unique identify.
        :param device_queried: device is being queried
        :param port: port number of the device.
                     If not exist on the device, print a WARNING to standard error
        :param rack: the rack holds the device, not required.
                     If specify a wrong Rack, which device is not in, return None
        :return: device connected to the specific port, or None
        """
        device = self._convert_device_input(device_queried)
        rack = self._convert_device_input(rack)
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


    @synchronized_with("rlock")
    def query_ports(self,device_queried,device2,rack1=None,rack2=None):
        """Find the port of device_queried is connected to device2.

        Rack is not required, because each device has a unique identifier.
        :param device_queried: queried device, which has the connected ports
        :param device2: device_queried connected to
        :param rack1: device_queried's rack
                      If specify a wrong Rack, in which device is not, return None
        :param rack2: device2's rack
        :return: list of ports on device_queried, return empty list if no ports exist
        """
        device_queried = self._convert_device_input(device_queried)
        device2 = self._convert_device_input(device2)
        rack1 = self._convert_device_input(rack1)
        rack2 = self._convert_device_input(rack2)

        # check if devices are exist and placed on racks
        if not self._is_device_exist(device_queried) or not self._is_device_exist(device2):
            return []
        if rack1 is not None and not self._is_device_in_rack(device_queried,rack1):
            return []
        if rack2 is not None and not self._is_device_in_rack(device2,rack2):
            return []

        # find the ports of device_queried connected to device2
        links1 = self._graph_model.node[device_queried]['links']
        return [port for port, device in links1.items() if device == device2]


    @synchronized_with("rlock")
    def get_device(self,device):
        """Get device object in data center

        Used for test.
        device can be a device object, or a string representing the device.
        string patterns are: 'spine1','spine-1',or 'spine_1' for device Spine with id=1
        :param device:
        :return: device object in data center
        """
        device = self._convert_device_input(device)
        for node in self._graph_model.nodes_iter():
            if node == device:
                return node
        return None


    @synchronized_with("rlock")
    def query_all_paths(self,source,target):
        """all paths from source to target device

        :param source: source device
        :param target: target device
        :return: list of all paths, return empty list if no paths exist
        """
        source = self._convert_device_input(source)
        target = self._convert_device_input(target)
        try:
             return [path for path in nx.all_shortest_paths(self._graph_model, source, target)]
        except Exception:
            #no path
            return []


    @synchronized_with("rlock")
    def break_link(self,device1,device2):
        """Break a link between two devices. only used for testing check_link()

        Don't use for other purpose, which will cause a inconsistent state of data center
        :param device1: first device of a link
        :param device2: second device of a link
        """
        device1 = self._convert_device_input(device1)
        device2 = self._convert_device_input(device2)

        try:
            self._graph_model.remove_edge(device1,device2)
        except Exception as ex:
            if self._is_device_exist(device1) and self._is_device_exist(device2):
                print >> sys.stderr,"WARNING: %s" %(ex.args[0])

        if self._is_print:
            print '***break link***'


    @synchronized_with("rlock")
    def check_link(self):
        """ Check broken links in data center

        :return: broken links, which are nodes pair
        """
        #check each Spine, Leaf, Host
        broken_pairs=[]
        for device in ( node for node in self._graph_model.nodes_iter() if type(node) is not Rack):
            links = self._graph_model.node[device]['links']
            for port, device2 in links.items():
                if device2 not in self._graph_model.neighbors(device):
                    broken_pairs.append((device,device2))
                    del links[port]
                    # delete link in device2's links dict
                    links2 = self._graph_model.node[device2]['links']
                    for port2,device_tmp in links2.items():
                        if device_tmp == device:
                            del links2[port2]
        # print result
        if self._is_print is True:
            print 'broken links: ', broken_pairs
        return broken_pairs


    @synchronized_with("rlock")
    def get_devices_in_rack(self,rack):
        """ All devices in the rack

        :param rack:
        :rtype : set
        :return: the copy of set of devices
        """
        rack = self._convert_device_input(rack)
        if self._is_device_exist(rack):
            return set(self._graph_model.node[rack]['hosts_leafs'])


    @synchronized_with("rlock")
    def get_connections_of_device(self,src_device):
        """ Get devices connected to source device

        :param src_device: source device
        :return: the copy of dictionary <port, device> of connected devices,
        """
        device = self._convert_device_input(src_device)
        if self._is_device_exist(device) and type(device) is not Rack:
            return dict(self._graph_model.node[device]['links'])


class LinkChecker(threading.Thread):
    """A Thread to check if there are broken links in a data center
    """

    def __init__(self,datacenter,check_interval=30):
        """

        :param datacenter: to be checked
        :param check_interval: how often to check, default is per 30 seconds
        """
        threading.Thread.__init__(self)
        self.dc = datacenter
        self.check_interval = check_interval
        self._stop = False


    def run(self):
        while self._stop is False:
            self.dc.check_link()
            time.sleep(self.check_interval)


    def stop(self):
        """stop the link checker
        """
        self._stop = True