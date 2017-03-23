'''
This file includes the configuration of th topology and controller of
the mininet which used to create the test environment.
'''

from mininet.topo import Topo

class TestTopo(Topo):

    def __init__(self):

        Topo.__init__(self):

        # Add hosts and switches
        h00 = self.addHost('h00')
        h01 = self.addHost('h01')
        s0  = self.addSwitch('s0')

        h10 = self.addHost('h10')
        h11 = self.addHost('h11')
        s1  = self.addSwitch('s1')

        # Add links
        self.addLink(h00, s0)
        self.addLink(h01, s0)
        self.addLink(h10, s1)
        self.addLink(h11, s1)
        self.addLink(s0, s1)


topos = {'testtopo' : (lambda: TestTopo())}
