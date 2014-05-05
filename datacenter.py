__author__ = 'wenjie'
from Models import Host, Spine, Leaf, Rack
import Models
import networkx as nx
import csv,sys

class DataCenter(object):

    def __init__(self, name='test'):
        self.name = name
        self._datacenter_graph_model = None

    @property
    def model(self):
        return self._datacenter_graph_model

    def _add_or_get_node_in_model(self,node):
        """get exist node or add not exist node in graph model.

            Don't use the method out side this class
        """
        #add not exist node
        if node not in self._datacenter_graph_model.nodes():
            # add attribute for node
            if isinstance(node, Rack):
                self._datacenter_graph_model.add_node(node,hosts_leafs=set())
            else:
                self._datacenter_graph_model.add_node(node,links={})
            return node
        # get exist node in model
        else:
            for n in self._datacenter_graph_model.nodes_iter():
                if n == node:
                    return n

    def _add_link(self, args):
        device1, id1, port1, device2, id2, port2, link_speed = args

        # get exist node or add not exist node in graph model.
        node1 = self._add_or_get_node_in_model(Models.factory(device1,id1))
        node2 = self._add_or_get_node_in_model(Models.factory(device2,id2))

        # add link in node
        node1.add_link(port1,node2)
        node2.add_link(port2,node1)

        # add edge between two nodes and set nodes' links attributes
        self._datacenter_graph_model.add_edge(node1,node2,{'link_speed':link_speed})
        self._datacenter_graph_model.node[node1]['links'][int(port1)]=node2
        self._datacenter_graph_model.node[node2]['links'][int(port2)]=node1

        # if a node is Host, add the corresponding Rack node
        host = None
        if isinstance(node1,Host):
            host = node1
        elif isinstance(node2,Host):
            host = node2

        if host is not None:
            # add Host to Rack
            rack = self._add_or_get_node_in_model(Models.factory('Rack',host.rack_id))
            rack.add_hosts_leafs(host)
            self._datacenter_graph_model.node[rack]['hosts_leafs'].add(host)

            # add Leaf to Rack
            leaf = node2 if host == node1 else node1
            rack.add_hosts_leafs(leaf)
            self._datacenter_graph_model.node[rack]['hosts_leafs'].add(leaf)

    def load_model_by_links(self, file_path, delimiter=','):
        self._datacenter_graph_model = nx.Graph()

        with open(file_path,'rb') as csv_model:
            reader = csv.reader(csv_model,delimiter=delimiter)
            # skip the headers of csv file
            next(reader, None)
            for line_num, line in enumerate(reader):
                try:
                    # eliminate whitespace in words
                    self._add_link([e.strip() for e in line])
                except Exception as ex:
                    raise Exception("%s\nCheck model file: '%s', at line: %d" %(ex.args[0],file_path,line_num+2))

    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

    def clear_model(self):
        self._datacenter_graph_model.clear()

    def _is_device_exist(self,device):
        if device not in self._datacenter_graph_model.nodes():
            if type(device) in (Spine, Leaf, Host):
                print "WARNING: '%s' is not in the graph model" %device
                return False
            else:
                raise TypeError("Don't support: '%s'" %type(device))
        else:
            return True

    def delete_link(self,device1,device2):
        #delete edge from model
        try:
            self._datacenter_graph_model.remove_edge(device1,device2)
        except Exception as ex:
            if self._is_device_exist(device1) and self._is_device_exist(device2):
                # link doesn't exist
                print "WARNING: %s" %(ex.args[0])
            return
        else:
            # delete link attribute in node1 and node2
            links1 = self._datacenter_graph_model.node[device1]['links']
            links2 = self._datacenter_graph_model.node[device2]['links']
            for port, node in links1.items():
                if node == device2:
                    del links1[port]
            for port, node in links2.items():
                if node == device1:
                    del links2[port]

    def delete_device(self,device):
        # check if node is valid
        if not self._is_device_exist(device):
            return

        # delete all edge between node and its neighbors
        for neighbor in self._datacenter_graph_model.neighbors(device):
            self.delete_link(device,neighbor)

        # delete device from graph model
        self._datacenter_graph_model.remove_node(device)

    def _is_device_on_rack(self,device,rack):
        """

        :param device:
        :param rack:
        :return: :raise TypeError:
        """
        if rack not in self._datacenter_graph_model.nodes():
            if not isinstance(rack,Rack):
                raise TypeError("Don't support '%s', only support 'Rack' type" %(type(rack)))
            else:
                print "WARNING: '%s' is not exist" %(rack)
                return False
        elif device not in self._datacenter_graph_model.node[rack]['hosts_leafs']:
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
        try:
            # find the device on port
            ret_device = self._datacenter_graph_model.node[device]['links'][int(port)]
        except KeyError as ex:
            if self._is_device_exist(device) and ex.args[0] == port:
                print "WARNING: the 'port: %s' of '%s' is not exist or not connected to any device" %(ex,device)
            return None
        except Exception:
            raise
        # found the device and check if it's valid
        else:
            if rack is None:
                return ret_device
            else:
                return ret_device if self._is_device_on_rack(device,rack) else None

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
        if rack1 and not self._is_device_on_rack(device_queried,rack1):
            return None
        if rack2 and not self._is_device_on_rack(device2,rack2):
            return None

        # find the ports of device1 connected to device2
        links1 = self._datacenter_graph_model.node[device_queried]['links']
        return (port for port, device in links1.items() if device == device2)

    def get_device(self,device):
        for node in self._datacenter_graph_model.nodes_iter():
            if node == device:
                return node
        return None

    def query_paths(self,source,target):
        return nx.all_shortest_paths(self._datacenter_graph_model, source, target)

def test4():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_links(file_path2)
    #delete node
    print dc.model.neighbors(Spine(1))
    print dc.model.neighbors(Leaf(1))
    print '==-----'
    dc.delete_device(Spine(1))
    print dc.model.neighbors(Leaf(1))
    print '==-----'
    dc.delete_link(Spine(2),Leaf(4))
    print dc.model.neighbors(Spine(2))
    print '==-----'
    dc.delete_link(Spine(3),Leaf(4))
    print '==-----'
    # dc.delete_device(Spine(3))
    # dc.delete_device('spine1')
    # dc.delete_link('spine1','leaf1')
    dc.delete_link(Spine(2),Host(1))

def test5():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_links(file_path2)
    print dc.query_device_on_port(Leaf(1),20)
    print dc.query_device_on_port(Leaf(10),20)
    print dc.query_device_on_port(Host(1),2)
    print dc.query_device_on_port(Leaf(1),5,Rack(3))
    print dc.query_device_on_port(Leaf(1),5,Rack(2))
    print dc.query_device_on_port(Leaf(1),5,Rack(1))
    # print dc.query_device_on_port('leaf1',5,Rack(1))
    # print dc.query_device_on_port(Leaf(1),5,'rack1')
    print dc.query_device_on_port(Leaf(3),5,Rack(2))
    dc.delete_link(Leaf(3),Host(13))
    print dc.query_device_on_port(Leaf(3),5,Rack(2))


def test6():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_links(file_path2)
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
    dc.load_model_by_links(file_path2)
    # l1 = dc.get_device(Leaf(1))
    # print l1.links
    gen = dc.query_paths(Host(1),Host(12))
    print '\n'.join(str(p) for p in gen)

if __name__=='__main__':
    # test4()
    # test5()
    # test6()
    test7()