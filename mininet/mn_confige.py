'''
This file includes the configuration of th topology and controller of
the mininet which used to create the test environment.
'''

from mininet.topo import Topo 
from mininet.node import RemoteController, OVSSwitch
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI

class TestTopo(Topo):

    def __init__(self):

        Topo.__init__(self)

        # Add hosts and switches
        h00 = self.addHost('h00', ip='10.0.0.2', mac='00:00:00:00:00:01')
        h01 = self.addHost('h01', ip='10.0.0.3', mac='00:00:00:00:00:02')
        s0  = self.addSwitch('s0', ip='10.0.0.1', mac='00:00:00:00:00:03')

        h10 = self.addHost('h10', ip='10.0.1.2', mac='00:00:00:00:00:04')
        h11 = self.addHost('h11', ip='10.0.1.3', mac='00:00:00:00:00:05')
        s1  = self.addSwitch('s1', ip='10.0.1.1',mac='00:00:00:00:00:06')

        # Add links
        self.addLink(h00, s0)
        self.addLink(h01, s0)
        self.addLink(h10, s1)
        self.addLink(h11, s1)
        self.addLink(s0, s1)

def basicTest():
    c0 = RemoteController('c0', ip='127.0.0.1', port=6633)
    net = Mininet(topo=TestTopo(),controller=None, switch=OVSSwitch)
    net.addController(c0)
    net.start()
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    basicTest()
#topos = {'testtopo' : (lambda: TestTopo())}
