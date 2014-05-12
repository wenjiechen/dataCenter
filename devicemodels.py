# -*- coding: utf-8 -*-
"""
All devices used in data center
"""

import abc
import re

__author__ = 'Wenjie Chen'


class Switch(object):
    """Abstract base class of Switch.

    Must override __eq__ and __hash__ methods in subclass
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,ID):
        self._ID = int(ID)

    @property
    def ID(self):
        """ ID of switch, read-only
        """
        return self._ID


    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def __eq__(self, other):
        """Override in subclass, in order to be used by networks lib"""
        return

    @abc.abstractmethod
    def __hash__(self):
        """override in subclass, in order to be used by networks lib"""
        return

class Spine(Switch):

    def __str__(self):
        return 'Spine-'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Spine) and self.ID == other.ID

    def __hash__(self):
        return hash('spine') + hash(17 + self.ID)

class Leaf(Switch):

    def __str__(self):
        return 'Leaf-'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Leaf) and self.ID == other.ID

    def __hash__(self):
        return hash('leaf') + hash(17 + self.ID)

class Host(object):

    def __init__(self,complex_ID,MACs=None,IPs=None):
        self._rack_id = None
        self._ID = None
        self._decompose_complex_ID(complex_ID)
        # self.links = {}
        self.MACs = MACs
        self.IPs = IPs

    @property
    def rack_id(self):
        """ The id of the rack containing the host, read-only property
        """
        return self._rack_id

    @property
    def ID(self):
        """ The id of the Host,read-only
        """
        return self._ID

    def _decompose_complex_ID(self,complex_ID):
        # complex id is like 'r1_1',which means host1 in rack1
        # simple id is like '1'
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

    def __str__(self):
        return 'Host-' + str(self.ID)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Host) and self.ID == other.ID

    def __hash__(self):
        return hash('host') + hash(17 + self.ID)

class Rack(object):

    def __init__(self,ID):
        self._ID = int(ID)

    @property
    def ID(self):
        """ ID of rack, read-only
        """
        return self._ID

    def __str__(self):
        return 'Rack-' + str(self._ID)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Rack) and self._ID == other._ID

    def __hash__(self):
        return hash('rack') + hash(17 + self._ID)

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
        raise ValueError("Don't have the device type: %s " %device_type)

if __name__ == '__main__':
    l1 = Leaf(1)
    print l1
    # l1.ID = 100
    print l1.ID