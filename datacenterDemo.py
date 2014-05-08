'''
Demonstration of how to use datacenter module
'''
from devicemodels import Host, Spine, Leaf, Rack
from datacenter import DataCenter

__author__ = 'Wenjie Chen'


def demo_load_model_remove_devices_and_links():
    print '-----demo_load_model_remove_devices_and_links-----'

    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    file_path3 = 'dcModel3.csv'

    # load from multi files
    dc.load_model_from_files(file_path2,file_path3)
    dc.clean_datacenter()

    # change delimiter of csv file
    dc.load_model_from_files('testModelPipeline.csv',delimiter='|')
    dc.clean_datacenter()

    #remove devices
    dc.load_model_from_files(file_path2)
    print 'is spine1 in data center: ',
    print Spine(1) in dc.all_devices
    print 'is host10 in data center: ',
    print Host(10) in dc.all_devices
    print 'after remove spine1, host10'

    dc.remove_devices(Spine(1),Host(10))

    print 'is spine1 in data center: ',
    print Spine(1) in dc.all_devices
    print 'is host10 in data center: ',
    print Host(10) in dc.all_devices

    #remove not exist device, get WARNING
    dc.remove_devices('spine1')
    dc.clean_datacenter()

    #remove link
    dc.load_model_from_files(file_path2)
    dc.remove_link(Spine(2),Leaf(4))
    dc.remove_link('spine3','leaf4')
    print 'is spine2-leaf4 in data center:',
    print (Spine(2),Leaf(4)) in dc.all_links
    print 'is spine3-leaf4 in data center:',
    print (Spine(3),Leaf(4)) in dc.all_links

    #remove not exist link, get WARNING
    dc.remove_link(Spine(2),Host(1))


def demo_query_device():
    print '\n--------demo_query_device--------'
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    # port20 of leaf1 not exist, get WARNING
    print 'device connected to port20 of leaf1:',
    print dc.query_device('leaf1',20)

    # leaf10 not exist, get WARNING
    print 'device connected to port20 of leaf10:',
    print dc.query_device('leaf10',20)

    # correct query
    print 'device connected to port2 of host1:',
    print dc.query_device(Host(1),2)

    # rack3 is not exist, get WARNING
    print 'device connected to port5 of leaf1 in rack3:',
    print dc.query_device(Leaf(1),5,Rack(3))

    # leaf1 is not in rakc2, get WARNING
    print 'device connected to port5 of leaf1 in rack2:',
    print dc.query_device(Leaf(1),5,Rack(2))

    # correct query
    print 'device connected to port5 of leaf1 in rack1:',
    print dc.query_device(Leaf(1),5,Rack(1))

    # port5 of leaf3 doesn't connect other device, get WARNING
    print 'device connected to port5 of leaf3 in rack2:',
    dc.remove_link(Leaf(3),Host(13))
    print dc.query_device(Leaf(3),5,Rack(2))


def demo_query_ports():
    print '\n--------demo_query_ports--------'
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    # query with specify racks
    print 'which ports of leaf1 connected to host2:',
    ports_iter =  dc.query_ports(Leaf(1),Host(2),Rack(1),Rack(1))
    print ports_iter.next()

    # query without specify racks
    print 'which ports of host12 connected to leaf4:',
    ports_iter =  dc.query_ports('host12','leaf4')
    print ports_iter.next()

    # query multi links between two devices
    dc.load_model_from_files('testModelMultiLink.csv')
    print 'which ports of leaf1 connected to spine1:',
    ports_iter = dc.query_ports(Leaf(1),Spine(1))
    print ', '.join(str(port) for port in ports_iter)


def demo_find_all_paths():
    print '\n--------demo_find_all_paths--------'
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    print 'all paths bewteen leaf1 and host12: '
    path_iter = dc.query_all_paths(Leaf(1),Host(12))
    print '\n'.join(str(p) for p in path_iter)


def demo_check_break_links():
    print '\n--------demo_check_break_links--------'
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    dc.break_link(Leaf(1),Host(1))
    dc.break_link(Spine(2),Leaf(3))
    dc.break_link(Spine(2),Leaf(1))

    print 'broken links: ', dc.check_link()


def demo_access_device_trhough_API():
    print '\n--------demo_access_device_trhough_API--------'
    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    # use object of device to represent device in data center
    dc.remove_link(Leaf(1),Spine(1))
    dc.remove_devices(Host(10),Leaf(2))
    print dc.query_device(Host(12),2,Rack(2))
    print dc.query_ports(Leaf(3),Host(15))
    print dc.query_all_paths(Host(2),Host(12))

    dc.clean_datacenter()
    dc.load_model_from_files(file_path2)

    # use string to represent device in data center
    dc.remove_link('leaf1','spine1')
    dc.remove_devices('host-10','leaf-2')
    print dc.query_device('host_12',2,'rack_2')
    print dc.query_ports('Leaf3','Host15')
    print dc.query_all_paths('host----2','host--12')

def demo_devices_in_rack_and_device_connection_info():
    print '\n----demo_devices_in_rack_and_device_connection_info----'

    dc = DataCenter()
    file_path2 = 'dcModel2.csv'
    dc.load_model_from_files(file_path2)

    print 'devices in rack1 :',
    print dc.get_devices_in_rack('rack1')

    print 'connections on Spine2 :',
    print dc.get_connections_of_device('spine2')

    # spine3 is not exist, get WARNING
    print 'connections on Spine3 :',
    print dc.get_connections_of_device('spine3')

if __name__ == '__main__':
    demo_load_model_remove_devices_and_links()
    demo_query_device()
    demo_query_ports()
    demo_find_all_paths()
    demo_check_break_links()
    demo_access_device_trhough_API()
    demo_devices_in_rack_and_device_connection_info()