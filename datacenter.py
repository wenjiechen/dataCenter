__author__ = 'wenjie'
from Models import Host, Spine, Leaf, Rack
import Models
import networkx as nx
import csv

class DataCenter(object):

    def __init__(self, name='test'):
        self.name = name
        self._datacenter_model = nx.Graph()

    def _add_edge(self, args):
        type1, id1, port1, type2, id2, port2, link_speed = args
        node1 = Models.factory(type1,id1)
        node2 = Models.factory(type2,id2)
        self._datacenter_model.add_edge(node1,node2)
        if isinstance(node1,Host):
            rack = Models.factory('Rack',node1.rack_id)
            self._datacenter_model.add_node(rack)

    def load_model_by_edges(self, file_path, delimiter=','):
        with open(file_path,'rb') as csv_model:
            reader = csv.reader(csv_model,delimiter=delimiter)
            # skip the headers
            next(reader, None)
            for line in reader:
                # eliminate whitespace in words
                self._add_edge([e.strip() for e in line])

    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

if __name__=='__main__':
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path2)
    print sorted(dc._datacenter_model.nodes())
    print dc._datacenter_model.neighbors(Spine(1))
    print dc._datacenter_model.neighbors(Leaf(1))
    print dc._datacenter_model.neighbors(Host(1,1))






