__author__ = 'wenjie'
from devicemodels import Host, Spine, Leaf, Rack
import devicemodels
import networkx as nx
import csv,sys

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
        device1 = self._add_or_get_device_in_model(devicemodels.factory(device1,id1))
        device2 = self._add_or_get_device_in_model(devicemodels.factory(device2,id2))

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
            rack = self._add_or_get_device_in_model(devicemodels.factory('Rack',host.rack_id))
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
                    except Exception as ex:
                        raise Exception("%s\nCheck model file: '%s', at line: %d" %(ex.args[0],file_path,line_num+2))



    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

    def clear_model(self):
        self._graph_model.clear()

    def _is_device_exist(self,device):
        if device not in self._graph_model.nodes():
            if type(device) in (Spine, Leaf, Host):
                print "WARNING: '%s' is not in the graph model" %device
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
                print "WARNING: %s" %(ex.args[0])
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
                print "WARNING: '%s' is not exist" %(rack)
                return False
        elif device not in self._graph_model.node[rack]['hosts_leafs']:
            print 'WARNING: device "%s" is not in %s' %(device,rack)
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
                print "WARNING: the 'port: %s' of '%s' is not exist or not connected to any device" %(ex,device)
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
                print "WARNING: %s" %(ex.args[0])
        print "break link between '%s' and '%s'" %(device1,device2)

    def all_devices(self):
        yield self._graph_model.nodes()

    def all_links(self):
        yield self._graph_model.edges()

    def link_check(self):
        #check each Spine, Leaf, Host
        for device in ( node for node in self._graph_model.nodes_iter() if type(node) is not Rack):
            links = self._graph_model.node[device]['links']
            for port, device2 in links.items():
                if device2 not in self._graph_model.neighbors(device):
                    print "WARNING: link between '%s' and '%s' is broken" %(device,device2)
                    del links[port]
                    # delete link in device2's link table
                    links2 = self._graph_model.node[device2]['links']
                    for port2,device_tmp in links2.items():
                        if device_tmp == device:
                            del links2[port2]

def test4():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)
    #delete node
    print dc.model.neighbors(Spine(1))
    print dc.model.neighbors(Leaf(1))
    print '==-----'
    dc.remove_devices(Spine(1),Host(10))
    print dc.model.neighbors(Leaf(1))
    print '==-----'
    dc.remove_link(Spine(2),Leaf(4))
    print dc.model.neighbors(Spine(2))
    print '==-----'
    dc.remove_link(Spine(3),Leaf(4))
    print '==-----'
    # dc.remove_devices(Spine(3))
    # dc.remove_devices('spine1')
    # dc.remove_link('spine1','leaf1')
    dc.remove_link(Spine(2),Host(1))
    dc.remove_devices(Host(2))
    print 'remove host(2), device on rack1 is',
    print Host(2) in dc.model.node[Rack(1)]['hosts_leafs']
    print dc.model.nodes()

def test5():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)
    print dc.query_device_on_port(Leaf(1),20)
    print dc.query_device_on_port(Leaf(10),20)
    print dc.query_device_on_port(Host(1),2)
    print dc.query_device_on_port(Leaf(1),5,Rack(3))
    print dc.query_device_on_port(Leaf(1),5,Rack(2))
    print dc.query_device_on_port(Leaf(1),5,Rack(1))
    # print dc.query_device_on_port('leaf1',5,Rack(1))
    # print dc.query_device_on_port(Leaf(1),5,'rack1')
    print dc.query_device_on_port(Leaf(3),5,Rack(2))
    dc.remove_link(Leaf(3),Host(13))
    print dc.query_device_on_port(Leaf(3),5,Rack(2))


def test6():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)
    print dc.query_connected_ports(Leaf(1),Spine(3))
    # print dc.query_connected_ports(Leaf(1),'spine3')
    # print dc.query_connected_ports(Leaf(5),Spine(1))
    # print dc.query_connected_ports('leaf1',Spine(1))
    print dc.query_connected_ports(Leaf(1),Host(2),Rack(2),Rack(2))
    print dc.query_connected_ports(Leaf(1),Host(2),Rack(1),Rack(2))
    g1 =  dc.query_connected_ports(Leaf(1),Host(2),Rack(1),Rack(1))
    print g1.next()
    gg = dc.query_connected_ports(Leaf(1),Spine(1))
    print '\n'.join(str(port) for port in gg)
    # for e in nx.edges_iter(dc.model,(Leaf(1),Spine(1))):
    #     print e

def test7():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)
    # l1 = dc.get_device(Leaf(1))
    # print l1.links
    # gen = dc.query_all_paths(Host(1),Host(12))
    # gen = dc.query_all_paths(Spine(1),Host(12))
    gen = dc.query_all_paths(Leaf(1),Host(12))
    print '\n'.join(str(p) for p in gen)

def test8():
    dc = DataCenter()
    file_path = 'dcModel3.csv'
    file_path2 = 'dcModel2.csv'
    # dc.load_model_from_files(file_path)
    # dc.load_model_from_files(file_path2)
    # dc.load_model_from_files(file_path,file_path2,delimiter=',')
    dc.load_model_from_files(file_path,file_path2)
    print dc.model.nodes()
    dc.clear_model()
    dc.load_model_from_files(file_path,'testModel.csv',file_path2,delimiter=',')
    print dc.model.nodes()
    dc.clear_model()
    dc.load_model_from_files(file_path,delimiter=',')
    print dc.model.nodes()

def test9():
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    # dc.load_model_from_files(file_path)
    # dc.load_model_from_files(file_path2)
    # dc.load_model_from_files(file_path,file_path2,delimiter=',')
    dc.load_model_from_files(file_path2)
    dc.break_link(Leaf(1),Host(1))
    print "host1's links", dc.model.node[Host(1)]['links']
    print "host1's neighbors", dc.model.neighbors(Host(1))
    print "leaf1's links ", dc.model.node[Leaf(1)]['links']
    dc.link_check()
    print dc.model.node[Host(1)]['links']
    print dc.model.node[Leaf(1)]['links']


if __name__ == '__main__':
    test4()
    test5()
    test6()
    test7()
    test8()
    test9()