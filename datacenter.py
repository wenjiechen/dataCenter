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
                self._datacenter_graph_model.add_node(node,hosts=set())
            else:
                self._datacenter_graph_model.add_node(node,connections={})
            return node
        # get exist node in model
        else:
            for n in self._datacenter_graph_model.nodes_iter():
                if n == node:
                    return n

    def _add_edge(self, args):
        type1, id1, port1, type2, id2, port2, link_speed = args

        # get exist node or add not exist node in graph model.
        node1 = self._add_or_get_node_in_model(Models.factory(type1,id1))
        node2 = self._add_or_get_node_in_model(Models.factory(type2,id2))

        # add connection in node
        node1.add_connection(port1,node2)
        node2.add_connection(port2,node1)

        # add edge between two nodes and set nodes' connections attributes
        self._datacenter_graph_model.add_edge(node1,node2,{'link_speed':link_speed})
        self._datacenter_graph_model.node[node1]['connections'][int(port1)]=node2
        self._datacenter_graph_model.node[node2]['connections'][int(port2)]=node1

        # if a node is Host, then add the corresponding Rack node
        host = None
        if isinstance(node1,Host):
            host = node1
        elif isinstance(node2,Host):
            host = node2

        if not host == None:
            rack = self._add_or_get_node_in_model(Models.factory('Rack',host.rack_id))
            rack.add_host(host)
            self._datacenter_graph_model.add_edge(rack,host)
            self._datacenter_graph_model.node[rack]['hosts'].add(host)

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
                except Exception as ex:
                    sys.stderr.write("!!!ERROR: check model file: '%s', at line: %d\n" %(file_path,line_num+2))
                    raise ex

    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

    def clear_model(self):
        self._datacenter_graph_model.clear()

    def delete_edge(self,node1,node2):
        #delete connection attribute in nodes
        try:
            # delete connection in node1
            connections = self._datacenter_graph_model.node[node1]['connections']
            for port, node in connections.items():
                if node == node2:
                    del connections[port]
            # delete connection in node2
            connections = self._datacenter_graph_model.node[node2]['connections']
            for port, node in connections.items():
                if node == node1:
                    del connections[port]
        except KeyError as ex:
            sys.stderr.write("!!!ERROR: Don't exist node '%s' or '%s' in model\n" %(node1,node2))
            raise ex
        except Exception as ex:
            raise ex

        #delete edge from model
        self._datacenter_graph_model.remove_edge(node1,node2)

    def delete_node(self,node):
        # delete all edge between node and its neighbors
        for neighbor in self._datacenter_graph_model.neighbors(node):
            self.delete_edge(node,neighbor)
        # delete node
        self._datacenter_graph_model.remove_node(node)

def test1():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    print sorted(dc._datacenter_graph_model.nodes())
    print sorted(dc._datacenter_graph_model.edges())
    print dc._datacenter_graph_model.neighbors(Spine(1))
    print dc._datacenter_graph_model.neighbors(Leaf(1))
    print dc._datacenter_graph_model.neighbors(Host('r1_1'))
    print '========'
    l1 = dc._datacenter_graph_model.neighbors(Leaf(1))
    print l1
    print l1[6].connections

def test2():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    # print dc._datacenter_graph_model[Leaf(3)]
    s1 = dc._add_or_get_node_in_model(Spine(1))
    l1 = dc._add_or_get_node_in_model(Leaf(1))
    h1 = dc._add_or_get_node_in_model(Host('r1_1'))
    r1 = dc._add_or_get_node_in_model(Rack(1))
    # print s1.connections
    # print l1.connections
    # print h1.connections
    # print r1.hosts
    # print '======='
    # print dc._datacenter_graph_model[s1]
    # print dc._datacenter_graph_model[Spine(1)]['connections']
    print dc._datacenter_graph_model[Spine(1)]
    print dc._datacenter_graph_model[Leaf(1)]['connections']
    print l1.connections
    print '=========='
    print dc._datacenter_graph_model[Rack(1)]['hosts']
    print r1.hosts

def test3():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    #delete edge
    print dc._datacenter_graph_model.neighbors(Spine(1))
    print dc._datacenter_graph_model.node[Spine(1)]
    print dc._datacenter_graph_model.neighbors(Leaf(1))
    print dc._datacenter_graph_model.node[Leaf(1)]
    dc.delete_edge(Spine(1),Leaf(1))
    print '-----------'
    print dc._datacenter_graph_model.neighbors(Spine(1))
    print dc._datacenter_graph_model.node[Spine(1)]
    print dc._datacenter_graph_model.neighbors(Leaf(1))
    print dc._datacenter_graph_model.node[Leaf(1)]
    print dc._datacenter_graph_model.node[Rack(1)]

def test4():
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    #delete node
    print dc.model.nodes()
    dc.clear_model()
    print dc.model.nodes()
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
    # dc.delete_edge(Spine(2),Leaf(5))

if __name__=='__main__':
    # test1()
    # test2()
    test4()