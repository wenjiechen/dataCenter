import abc

class Switch(object):
    """abstract base class of Switch"""
    __metaclass__ = abc.ABCMeta

    def __init__(self,ID):
        self.ID = int(ID)
        self.switch_table = []

    @abc.abstractmethod
    def update_switch_table(self):
        """update switch table"""
        pass

    def __repr__(self):
        return self.__str__()

class Spine(Switch):

    def update_switch_table(self):
        print 'spine'

    def __str__(self):
        return 'Spine_'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Spine) and self.ID == other.ID

    def __hash__(self):
        return hash('spine') + hash(17 + self.ID)

class Leaf(Switch):
    def update_switch_table(self):
        print'Leaf'

    def __str__(self):
        return 'Leaf_'+str(self.ID)

    def __eq__(self, other):
        return isinstance(other, Leaf) and self.ID == other.ID

    def __hash__(self):
        return hash('leaf') + hash(17 + self.ID)

class Host(object):

    def __init__(self,rack_id,ID,MACs=None,IPs=None):
        self.rack_id = int(rack_id)
        self.ID = int(ID)
        self.MACs = MACs
        self.IPs = IPs

    def __str__(self):
        # return 'Host_' + str(self.ID) + ', Rack_' + str(self.rack_num) + ', MACs: '+str(self.MACs) + ', IPs: ' + str(self.IPs)
        return 'Host_' + str(self.ID) + '@Rack_' + str(self.rack_id)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Host) and self.ID == other.ID and self.rack_id == other.rack_id

    def __hash__(self):
        return hash(17 + self.ID*31 + self.rack_id)

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
        return hash(17 + self.ID)

def factory(type, ID):
    if type == "Spine":
        return Spine(ID)
    elif type == "Leaf":
        return Leaf(ID)
    elif type == "Host":
        rack_id, host_id = ID.split('_')
        host = Host(rack_id[1:],host_id)
        return host
    elif type == "Rack":
        return Rack(ID)
    else:
        raise TypeError("Don't have this type")

def test3():
    s1 = Spine(1)
    s2 = Spine(2)
    d = {s1:100, s2:200}
    print d[Spine(1)]
    print d[factory('Spine',2)]

if __name__=='__main__':
    test3()