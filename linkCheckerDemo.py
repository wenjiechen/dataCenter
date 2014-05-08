"""
Demonstrate how to check broken link by multi-threading
"""

import time
from datacenter import DataCenter, LinkChecker

__author__ = 'wenjie'

if __name__=='__main__':

    #print datacenter inner state
    dc = DataCenter(is_print=True)
    file = 'dcModel2.csv'
    links_to_be_broken=[('leaf1','host1'),('leaf3','spine1'),
                        ('host3','leaf2'),('leaf2','spine2'),
                        ('leaf4','host12'),('spine2','leaf4'),
                        ('leaf3','host20'),('host18','leaf4'),
                        ('leaf2','host8'),('leaf4','host16')]

    # linkChecker run every 0.5 second
    link_checker = LinkChecker(dc,0.5)
    link_checker.start()

    # load a new model, then break two links
    for i in range(0,5):
        dc.load_model_from_files(file)
        dc.break_link(*links_to_be_broken[2*i-1])
        dc.break_link(*links_to_be_broken[2*i])
        time.sleep(1)
        dc.clean_datacenter()

    #stop linkChecker
    link_checker.stop()
