Author:Wenjie Chen

Config
---
* install networkx 1.8
* platform: python 2.7


Run
---
* There are 3 files can run, command `python filename.py` : 
  
  - datacenterDemo.py demonstrates how to use datacenter.py module, and will print WARNING to stderr. You can redirect stderr by `python datacenterDemo.py 2> error.log`
  
  - testDatacenter.py is the unittest file, which gives more demonstration about `datacenter` including raise exception
  
  - linkCheckerDemo.py gives an example that use a thread to check broken links in a data center and terminates in 5 seconds


Files Description
---
* devicemodels.py : defines all device models used in `datacenter` module, and provides a factory function to create a device instance

* datacenter.py : defines DataCenter class, a decorator for synchronization, and LinkChecker class, which is a thread

* datacenterDemo.py : demonstration of how to use datacenter module, and prints WARNING to stderr 

* testDatacenter.py : unittest cases and further demonstration for raising Exception

* linkCheckerDemo.py : demonstrate of how to use a thread to check broken link in data center

* *.csv: test models of data center, don't delete any csv file


Design and Trade off
---
* To directly use device object in networkx, each device class in `devicemodels.py` must override __eq__ and __hash__
  method.

* Each device object is identified by its ID attribute, which can't be changed after initialization. Especially for `Host` class, which contains attribute `rack_id`, is still uniquely identified by its ID. For example, 2nd host in rack1 is `Host2`, 2nd host in rack2 is `Host12`.

* For all public API in `datacenter` module, there are two ways to refer to a device in data center.
  - Creat a device object. For example, Host(1) refers to Host with id = 1 in a data center, and Spine(2) refers to Spine with id = 2

  - Use a string like: 'spine1', 'leaf-2' or 'host_3', no matter lower or upper case. Only dash or underscore is allowed to be added bewteen device and its id

* data center model in csv file is defined by links between devices. To simplify the model file, and keep the consistency of csv file: 
  - the relationship between Host and Rack is explicitly defined in host's id, called complex id. Its pattern like 'r1_2' for host2 in rack1, 'r2_16' for host16 in rack2. Except in model file, don't use complex id in other place, which will cause ValueError. 
  - the relationship between Leaf and Rack is implication. For example in model file define a link between Leaf-1 and Host-2, because Host-2 is explicitly placed in Rack1, Leaf-1 is also in Rack-1

* When query a device or a link which is not in data center model, just print a WARNING to stderr and don't raise a Exception to terminate client program. Because query a not exist device or link won't change the structre of data center model. But other wrong operation like add a device with wrong ID will raise Exception.


Public API for requirements in DataCenter Module 
---
This is brief introduction. For details, please see the docstring of modules, classes and methods. 

* load topology from csv:
  - load_model_from_files(): can import multiple csv files at once

* delete topology:
  - clean_datacenter(): remove all devices and links
  - remove_link(): remove a link
  - remove_devices: remove multiple devices and their links at once, if device is leaf or host also remove them from their racks 

* query device is connnected on a particular port:
  - query_device(): rack of queried device is not required, and print WARNING to stderr if port or device does not exist, or specify a wrong rack

* query ports a particular device is connected on: 
  - query_ports(): racks of devices are not required, and print WARNING to stderr if port or device does not exist, or specify a wrong rack. Return a generator of ports.

* query paths to a remote device:
  - query_all_paths(): returns a generator of all paths that have been found

* check broken links:
  - check_link(): synchronized method, can be invoked by other threads

  - LinkChecker class: a thread to check broken links

  - break_link(): Break a link between two devices. Only used for testing check_link(), and don't use for other purpose, which will cause a inconsistent state of data center

* Some APIs and properties are provided to help test the state of data center:
  - synchronized_with(): a decorator for synchronizing methods in a DataCenter instance
  
  - all_devices: property, read only

  - all_links: property, read only

  - get_device(): get a reference of a device in data center

  - get_devices_in_rack()

  - get_connections_of_device(): get links info of a device


Except check_link(),load_model_from_files() and break_link(), other methods can't be guaranteed as thread-safe. Don't invoke them in other threads.