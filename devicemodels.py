# -*- coding: utf-8 -*-
"""
All devices used in data center model
"""
__author__ = 'Wenjie Chen'
import abc
import re

class Switch(object):
    """Abstract base class of Switch.


    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,ID):
        self._ID = int(ID)
        self.links = {}

    # ID is read only attribute
    @property
    def ID(self):
        return self._ID

    def add_link(self, port, device):
        self.links[int(port)] = device

    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def __eq__(self, other):
        """Override in subclass, in order to be used by networks"""
        return

    @abc.abstractmethod
    def __hash__(self):
        """override in subclass, in order to be used by networks"""
        return

class Spine(Switch):

    def __str__(self):
        return 'Spine_'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Spine) and self.ID == other.ID

    def __hash__(self):
        return hash('spine') + hash(17 + self.ID)

class Leaf(Switch):

    def __str__(self):
        return 'Leaf_'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Leaf) and self.ID == other.ID

    def __hash__(self):
        return hash('leaf') + hash(17 + self.ID)

class Host(object):

    def __init__(self,complex_ID,MACs=None,IPs=None):
        self._rack_id = None
        self._ID = None
        self._decompose_complex_ID(complex_ID)
        self.links = {}
        self.MACs = MACs
        self.IPs = IPs

    @property
    def rack_id(self):
        return self._rack_id

    @property
    def ID(self):
        return self._ID

    def _decompose_complex_ID(self,complex_ID):
        complex_pattern = re.compile(r'^r\d+_\d+')
        simple_pattern = re.compile(r'^\d+')
        if complex_pattern.match(str(complex_ID)) :
            rack_id, host_id = complex_ID.split('_')
            self._rack_id = int(rack_id[1:])
            self._ID = int(host_id)
        elif simple_pattern.match(str(complex_ID)):
            self._ID = int(complex_ID)
        else:
            raise ValueError("'%s' not valid ID for Host." %(complex_ID))

    def add_link(self,port,device):
        self.links[int(port)] = device

    def __str__(self):
        return 'Host_' + str(self.ID)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Host) and self.ID == other.ID

    def __hash__(self):
        return hash('host') + hash(17 + self.ID)

class Rack(object):

    def __init__(self,ID):
        self.ID = int(ID)
        self.hosts_leafs = set()

    def add_hosts_leafs(self,host):
        self.hosts_leafs.add(host)

    def __str__(self):
        return 'Rack_' + str(self.ID)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Rack) and self.ID == other.ID

    def __hash__(self):
        return hash('rack') + hash(17 + self.ID)

def devices_factory(device_type, ID):
    device_type_l = device_type.lower()
    if device_type_l == "spine":
        return Spine(ID)
    elif device_type_l == "leaf":
        return Leaf(ID)
    elif device_type_l == "host":
        return Host(ID)
    elif device_type_l == "rack":
        return Rack(ID)
    else:
        raise TypeError("Don't have the device type: " + str(device_type))

def test3():
    s1 = Spine(1)
    s2 = Spine(2)
    d = {s1:100, s2:200}
    print d[Spine(1)]
    print d[devices_factory('Spine',2)]
    # s1.ID = 200
    print s1

if __name__=='__main__':
    test3()