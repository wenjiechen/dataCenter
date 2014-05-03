import abc, re

class Switch(object):
    """abstract base class of Switch"""
    __metaclass__ = abc.ABCMeta

    def __init__(self,ID):
        self._ID = int(ID)
        self.connections = {}

    # ID is read only attribute
    @property
    def ID(self):
        return self._ID

    def add_connection(self, port, machine):
        self.connections[int(port)] = machine

    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def __eq__(self, other):
        """Override, in order to be used by networks"""
        return

    @abc.abstractmethod
    def __hash__(self):
        """override, in order to be used by networks"""
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
        self.connections = {}
        self.MACs = MACs
        self.IPs = IPs

    @property
    def rack_id(self):
        return self._rack_id

    @property
    def ID(self):
        return self._ID

    def _decompose_complex_ID(self,complex_ID):
        id_pattern = re.compile(r'^r\d+_\d+')
        if id_pattern.match(complex_ID) == None:
            raise ValueError("It's not valid complex ID for Host:" + complex_ID)
        rack_id, host_id = complex_ID.split('_')
        self._rack_id = int(rack_id[1:])
        self._ID = int(host_id)

    def add_connection(self,port,machine):
        self.connections[int(port)] = machine

    def __str__(self):
        # return 'Host_' + str(self.ID) + ', Rack_' + str(self.rack_num) + ', MACs: '+str(self.MACs) + ', IPs: ' + str(self.IPs)
        return 'Host_' + str(self.ID) + '@Rack_' + str(self.rack_id)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Host) and self.ID == other.ID and self.rack_id == other.rack_id

    def __hash__(self):
        return hash('host') + hash(17 + self.ID*31 + self.rack_id)

class Rack(object):

    def __init__(self,ID):
        self.ID = int(ID)
        self.hosts = []

    def add_host(self,host):
        self.hosts.append(host)

    def __str__(self):
        return 'Rack_' + str(self.ID)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Rack) and self.ID == other.ID

    def __hash__(self):
        return hash('rack') + hash(17 + self.ID)

def factory(type, ID):
    if type == "Spine":
        return Spine(ID)
    elif type == "Leaf":
        return Leaf(ID)
    elif type == "Host":
        return Host(ID)
    elif type == "Rack":
        return Rack(ID)
    else:
        raise TypeError("Don't have the type: "+ type)

def test3():
    s1 = Spine(1)
    s2 = Spine(2)
    d = {s1:100, s2:200}
    print d[Spine(1)]
    print d[factory('Spine',2)]
    # s1.ID = 200
    print s1

if __name__=='__main__':
    test3()