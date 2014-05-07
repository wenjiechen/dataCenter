from devicemodels import Host, Spine, Leaf, Rack
import devicemodels
import networkx as nx
import csv,sys
from datacenter import DataCenter
__author__ = 'wenjie'


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
    print 'links\n', dc.all_links()
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
    dc.clean_model()
    dc.load_model_from_files(file_path,'testModel.csv',file_path2,delimiter=',')
    print dc.model.nodes()
    dc.clean_model()
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
    # print "host1's links", dc.model.node[Host(1)]['links']
    # print "host1's neighbors", dc.model.neighbors(Host(1))
    # print "leaf1's links ", dc.model.node[Leaf(1)]['links']
    print dc.link_check()
    # print dc.model.node[Host(1)]['links']
    # print dc.model.node[Leaf(1)]['links']

def test10():
    dc = DataCenter()
    file_path1 = 'testBadModel.csv'
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path1)
    print dc.all_devices()

if __name__ == '__main__':
    # test4()
    # test5()
    # test6()
    # test7()
    # test8()
    test9()
    # test10()