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
                self._datacenter_graph_model.add_node(node,connections={})
            return node
        # get exist node in model
        else:
            for n in self._datacenter_graph_model.nodes_iter():
                if n == node:
                    return n

    def _add_edge(self, args):
        device1, id1, port1, device2, id2, port2, link_speed = args

        # get exist node or add not exist node in graph model.
        node1 = self._add_or_get_node_in_model(Models.factory(device1,id1))
        node2 = self._add_or_get_node_in_model(Models.factory(device2,id2))

        # add connection in node
        node1.add_connection(port1,node2)
        node2.add_connection(port2,node1)

        # add edge between two nodes and set nodes' connections attributes
        self._datacenter_graph_model.add_edge(node1,node2,{'link_speed':link_speed})
        self._datacenter_graph_model.node[node1]['connections'][int(port1)]=node2
        self._datacenter_graph_model.node[node2]['connections'][int(port2)]=node1

        # if a node is Host, add the corresponding Rack node
        host = None
        if isinstance(node1,Host):
            host = node1
        elif isinstance(node2,Host):
            host = node2

        if not host == None:
            # add Host to Rack
            rack = self._add_or_get_node_in_model(Models.factory('Rack',host.rack_id))
            rack.add_host(host)
            # self._datacenter_graph_model.add_edge(rack,host)
            self._datacenter_graph_model.node[rack]['hosts_leafs'].add(host)

            # add Leaf to Rack
            leaf = node2 if host==node1 else node1
            rack.add_leaf(leaf)
            # self._datacenter_graph_model.add_edge(rack,leaf)
            self._datacenter_graph_model.node[rack]['hosts_leafs'].add(leaf)

    def load_model_by_edges(self, file_path, delimiter=','):
        self._datacenter_graph_model = nx.Graph()

        with open(file_path,'rb') as csv_model:
            reader = csv.reader(csv_model,delimiter=delimiter)
            # skip the headers of csv file
            next(reader, None)
            for line_num, line in enumerate(reader):
                try:
                    # eliminate whitespace in words
                    self._add_edge([e.strip() for e in line])
                except Exception:
                    print "!!!ERROR: check model file: '%s', at line: %d" %(file_path,line_num+2)
                    raise

    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

    def clear_model(self):
        self._datacenter_graph_model.clear()

    def delete_edge(self,node1,node2):
        #delete edge from model
        try:
            self._datacenter_graph_model.remove_edge(node1,node2)
        except Exception as ex:
            print "!!!ERROR: " + str(ex.args)
            return

        #delete connection attribute in nodes
        try:
            connections1 = self._datacenter_graph_model.node[node1]['connections']
            connections2 = self._datacenter_graph_model.node[node2]['connections']
        except Exception:
            raise
        else:
            # delete connection in node1 and node2
            for port, node in connections1.items():
                if node == node2:
                    del connections1[port]
            for port, node in connections2.items():
                if node == node1:
                    del connections2[port]

    def delete_node(self,node):
        # check if node is valid
        if node not in self._datacenter_graph_model.nodes():
            print "!!!ERROR: %s is not in the graph model"
            return

        # delete all edge between node and its neighbors
        for neighbor in self._datacenter_graph_model.neighbors(node):
            self.delete_edge(node,neighbor)

        self._datacenter_graph_model.remove_node(node)

    # def query_device_on_port_by_keywords(self,**kwargs):
    #     for k,v in kwargs.items():

    def query_device_on_port(self,device_type,device_id,port,rack_id=None):

        device = Models.factory(device_type,device_id)
        try:
            ret_device = self._datacenter_graph_model.node[device]['connections'][int(port)]
        except KeyError as ex:
            if ex.args[0] == port:
                print "!!!ERROR: the 'port: %s' of '%s' is not exist or not connected to any device" %(ex,device)
            else:
                print "!!!ERROR: '%s' is not exist in model" %ex
            return None
        except Exception:
            raise
        # found the device and check if it's valid
        else:
            if rack_id == None:
                return ret_device
            else:
                if Rack(rack_id) not in self._datacenter_graph_model.nodes():
                    print "!!!ERROR: 'rack_%d' is not exist" %(rack_id)
                    return None
                elif device not in self._datacenter_graph_model.node[Rack(rack_id)]['hosts_leafs']:
                    print '!!!ERROR: device "%s" is not in rack %d' %(device,rack_id)
                    return None
                else:
                    return ret_device

    def find_ports(self):
        pass

def test4():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    #delete node
    print dc.model.neighbors(Spine(1))
    print dc.model.neighbors(Leaf(1))
    print dc.model.neighbors(Leaf(2))
    print dc.model.neighbors(Leaf(3))
    print dc.model.neighbors(Leaf(4))
    print '==-----'
    dc.delete_node(Spine(1))
    print dc.model.neighbors(Leaf(1))
    print dc.model.neighbors(Leaf(2))
    print dc.model.neighbors(Leaf(3))
    print dc.model.neighbors(Leaf(4))
    dc.delete_edge(Spine(2),Leaf(4))
    print dc.model.neighbors(Spine(2))

def test5():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    print dc.query_device_on_port('leaf',1,20)
    print dc.query_device_on_port('leaf',10,20)
    print dc.query_device_on_port('host',1,2)
    print dc.query_device_on_port('leaf',1,5,3)
    print dc.query_device_on_port('leaf',1,5,2)
    print dc.query_device_on_port('leaf',1,5,1)
    # print dc.model.node[Rack(1)]['hosts_leafs']
    # print dc.model.neighbors(Leaf(1))

    # print dc.model.node[Rack(2)]
    # print dc.model.node[Host(1)]

    # print dc.query_device_on_port('leaf',12,2)
    # print dc.query_device_on_port('leaf',1,20)
    # print dc.query_device_on_port('leaf',1,10,rack_id=3)
    # print dc.query_device_on_port('leaf',1,10,rack_id=2)
    # print dc.model.neighbors(Host('r1_2'))

if __name__=='__main__':
    # test1()
    # test2()
    # test4()
    test5()