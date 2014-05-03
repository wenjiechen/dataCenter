__author__ = 'wenjie'
from Models import Host, Spine, Leaf, Rack
import Models
import networkx as nx
import csv,sys

class DataCenter(object):

    def __init__(self, name='test'):
        self.name = name
        self._datacenter_model = None

    def _add_edge(self, args):
        type1, id1, port1, type2, id2, port2, link_speed = args

        # add nodes to graph model,
        node1 = Models.factory(type1,id1)
        node2 = Models.factory(type2,id2)
        node1.add_connection(port1,node2)
        node2.add_connection(port2,node1)
        self._datacenter_model.add_edge(node1,node2)

        # if a node is Host, then add the corresponding Rack node
        host = None
        if isinstance(node1,Host):
            host = node1
        elif isinstance(node2,Host):
            host = node2
        if not host == None:
            rack = Models.factory('Rack',host.rack_id)
            rack.add_host(host)
            self._datacenter_model.add_edge(rack,host)

    def _generate_edge(self,args):
        pass

    def load_model_by_edges(self, file_path, delimiter=','):
        self._datacenter_model = nx.Graph()

        with open(file_path,'rb') as csv_model:
            reader = csv.reader(csv_model,delimiter=delimiter)
            # skip the headers of csv file
            next(reader, None)
            for line_num, line in enumerate(reader):
                try:
                    # eliminate whitespace in words
                    self._add_edge([e.strip() for e in line])
                except Exception as ex:
                    sys.stderr.write('!!!WARNING: check model file: "'+str(file_path)+ '", at line: ' + str(line_num + 2) +'\n')
                    raise ex

    def load_hosts_attributes(self,file_path):
        pass

    def load_model_by_nodes(self):
        pass

if __name__=='__main__':
    dc = DataCenter()
    file_path = 'testModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_by_edges(file_path)
    print sorted(dc._datacenter_model.nodes())
    print sorted(dc._datacenter_model.edges())
    print dc._datacenter_model.neighbors(Spine(1))
    print dc._datacenter_model.neighbors(Leaf(1))
    print dc._datacenter_model.neighbors(Host('r1_1'))
    print '========'
    l1 = dc._datacenter_model.neighbors(Host('r1_1'))[1]
    print l1.connections
    # l1.ID = 2


