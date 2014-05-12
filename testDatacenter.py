'''
Test datacenter module and provide example of how to use datacenter module
'''
import unittest
import datacenter
from devicemodels import Spine, Leaf, Host,Rack

__author__ = 'Wenjie Chen'


class TestDataCenter(unittest.TestCase):

    def setUp(self):
        '''Create standard test model
        '''
        path = 'dcModel2.csv'
        self.dc = datacenter.DataCenter()
        self.dc.load_model_from_files(path)
        self.device_cmp = lambda x,y : cmp(str(x), str(y))

    def test_clean_model(self):
        ''' remove all devices in model
        '''
        self.dc.clean_datacenter()
        self.assertEqual([],self.dc.all_devices)

    def test_load_model_from_one_file(self):
        ''' ensure all edges and nodes are added
        '''
        self.dc.clean_datacenter()
        self.dc.load_model_from_files('testModel2.csv')
        devices = self.dc.all_devices
        devices.sort(cmp=self.device_cmp)
        expected = [Spine(1),Leaf(1),Leaf(2),Host(1),Host(2),Rack(1)]
        expected.sort(cmp=self.device_cmp)
        self.assertEqual(devices,expected)

    def test_load_model_from_two_files(self):
        ''' ensure all nodes and edges in two files are added
        '''
        self.dc.clean_datacenter()
        file1 = 'testModel2.csv'
        file2 = 'testModel3.csv'
        self.dc.load_model_from_files(file1,file2)
        devices = self.dc.all_devices
        devices.sort(cmp=self.device_cmp)
        expected = [Spine(1),Leaf(1),Leaf(2),Host(1),Host(2),Host(3),Rack(1)]
        expected.sort(cmp=self.device_cmp)
        self.assertEqual(devices,expected)

    def test_load_model_by_pipeline_delimiter(self):
        ''' change the model file's delimiter to pipeline '|'
        '''
        self.dc.clean_datacenter()
        self.dc.load_model_from_files('testModelPipeline.csv',delimiter='|')
        devices = self.dc.all_devices
        devices.sort(cmp=self.device_cmp)
        expected = [Spine(1),Leaf(1)]
        expected.sort(cmp=self.device_cmp)
        self.assertEqual(devices,expected)

    def test_load_model_raise_exception(self):
        ''' Wrong data in model file.

        e.g. bad ID 's1' for Spine. Spine ID should be integer
        '''
        with self.assertRaises(Exception):
            self.dc.load_model_from_files('testBadModel.csv')

    def test_access_device_with_string(self):
        '''access Spine(1) and with string.

        the string pattern can be 'spine1','spine-1' or 'spine_1', no matter lower or upper case
        '''
        self.assertEqual(Spine(1),self.dc.get_device('spine1'))
        self.assertEqual(Spine(1),self.dc.get_device('Spine-1'))
        self.assertEqual(Spine(1),self.dc.get_device('Spine_1'))

    def test_access_device_with_wrong_string_pattern(self):
        '''access device using string, raise TypeError
        '''
        with self.assertRaises(ValueError):
            self.dc.remove_devices('spines1')
        with self.assertRaises(ValueError):
            self.dc.remove_devices('host-s1')


    def test_remove_link(self):
        '''remove link Spine(1)-Leaf(1), check if it still exists in model.
        '''
        self.dc.remove_link(Spine(1),Leaf(1))
        is_exist = (Spine(1),Leaf(1)) in self.dc.all_links
        self.assertEqual(False,is_exist)


    def test_remove_device(self):
        ''' remove Host(1)

        links host1-leaf1,host1-leaf2 are removed, and remove from Rack1
        '''
        self.dc.remove_devices(Host(1))
        is_exist1 = (Host(1),Leaf(1)) in self.dc.all_links
        is_exist2 = (Host(1),Leaf(2)) in self.dc.all_links
        is_exist3 = Host(1) in self.dc.get_devices_in_rack(Rack(1))
        self.assertEqual(False,is_exist1)
        self.assertEqual(False,is_exist2)
        self.assertEqual(False,is_exist3)

    def test_remove_two_devices(self):
        ''' remove Host(1),Host(2)

        links host1-leaf1,host1-leaf2 are removed, and remove from Rack1
        links host2-leaf1,host2-leaf2 are removed, and remove from Rack1
        '''
        self.dc.remove_devices(Host(1),Host(2))
        is_exist1 = (Host(1),Leaf(1)) in self.dc.all_links
        is_exist2 = (Host(1),Leaf(2)) in self.dc.all_links
        is_exist3 = Host(1) in self.dc.get_devices_in_rack(Rack(1))
        is_exist4 = (Host(2),Leaf(1)) in self.dc.all_links
        is_exist5 = (Host(2),Leaf(2)) in self.dc.all_links
        is_exist6 = Host(2) in self.dc.get_devices_in_rack(Rack(1))

        self.assertEqual(False,is_exist1)
        self.assertEqual(False,is_exist2)
        self.assertEqual(False,is_exist3)
        self.assertEqual(False,is_exist4)
        self.assertEqual(False,is_exist5)
        self.assertEqual(False,is_exist6)

    def test_query_device_on_port_without_rackid(self):
        ''' Find device connected to port2 of host(1).

        Because each device is uniquely defined by its ID,
        host1 can be identified without rack num.
        '''
        device = self.dc.query_device(Host(1),2)
        self.assertEqual(Leaf(2),device)

    def test_query_device_on_port_with_right_rackid(self):
        ''' find device connected to port2 of host(1) in rack1
        '''
        device = self.dc.query_device(Host(1),2,Rack(1))
        self.assertEqual(Leaf(2),device)

    def test_query_device_on_port_with_wrong_rackid(self):
        ''' find device connected to port2 of host(1) in rack2

        because host1 is not in rack2, return None, print warning to stderr
        '''
        device = self.dc.query_device(Host(1),2,Rack(2))
        self.assertEqual(None,device)

    def test_query_device_on_port_with_not_exist_rackid(self):
        ''' find device connected to port2 of host(1) in rack3

        because rack3 is not exist, return None, print warning to stderr
        '''
        device = self.dc.query_device(Host(1),2,Rack(3))
        self.assertEqual(None,device)

    def test_query_connected_one_port_without_rackid(self):
        ''' port1 of leaf1 connects to spine1.

        leaf1 and spine1 can be identified by their id without rack id
        '''
        ports = self.dc.query_ports(Leaf(1),Spine(1))
        self.assertEqual([1],ports)


    def test_query_connected_two_ports_without_rackid(self):
        ''' port1 and port100 of leaf1 connects to spine1
        '''
        self.dc.load_model_from_files('testModelMultiLink.csv')
        ports = self.dc.query_ports(Leaf(1),Spine(1))
        self.assertEqual([1,100],sorted(ports))


    def path_cmp(self,x,y):
        '''path comparator

        Compare based on string of nodes in paths
        '''
        if len(x) != len(y):
            raise Exception("lengths of two paths are not equal.")

        for xi,yi in zip(x,y):
            ret = cmp(str(xi),str(yi))
            if ret > 0:
                return 1
            elif ret < 0:
                return -1
        return 0

    def test_query_all_paths(self):
        ''' find all paths from leaf-1 to host-12
        '''
        paths = self.dc.query_all_paths(Leaf(1),Host(12))
        paths = sorted(paths,cmp = lambda x,y: self.path_cmp(x,y))
        expected=[[Leaf(1), Spine(1), Leaf(3), Host(12)],
                    [Leaf(1), Spine(2), Leaf(3), Host(12)],
                    [Leaf(1), Spine(1), Leaf(4), Host(12)],
                    [Leaf(1), Spine(2), Leaf(4), Host(12)]]
        expected = sorted(expected,cmp = lambda x,y: self.path_cmp(x,y))
        self.assertEqual(expected,paths)

    def test_link_check(self):
        '''break link leaf1-host1 and leaf1-spine1, then find the broken links
        '''
        self.dc.break_link(Leaf(1),Host(1))
        self.dc.break_link(Leaf(1),Spine(1))
        self.dc.break_link(Leaf(3),Spine(2))
        self.dc.break_link(Leaf(3),Host(12))

        broken_links = self.dc.check_link()
        broken_links = sorted(broken_links,cmp = lambda x,y: self.path_cmp(x,y))

        expected = [(Leaf(1),Host(1)),(Leaf(1),Spine(1)),(Leaf(3),Spine(2)),(Leaf(3),Host(12))]
        expected = sorted(expected,cmp = lambda x,y: self.path_cmp(x,y))

        self.assertEqual(expected,broken_links)

if __name__ == '__main__':
    unittest.main()