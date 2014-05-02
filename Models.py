import abc

class Switch(object):
    """abstract base class of Switch"""
    __metaclass__ = abc.ABCMeta

    def __init__(self,ID):
        self.ID = ID
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

class Leaf(Switch):
    def update_switch_table(self):
        print'Leaf'

    def __str__(self):
        return 'Leaf_'+str(self.ID)

class Host(object):

    def __init__(self,rack_num,ID,MAC=None,IP=None):
        self.rack_num = rack_num
        self.ID = ID
        self.MAC = MAC
        self.IP = IP

    def __str__(self):
        return 'Host_' + str(self.ID) + ', Rack_' + str(self.rack_num) + ', MAC: '+str(self.MAC) + ', IP: ' + str(self.IP)

    def __repr__(self):
        return self.__str__()

if __name__=='__main__':
    s1 = Spine(1)
    print str(s1)
    l1 = Leaf(1)
    print l1
    h1 = Host(1,1)
    print h1