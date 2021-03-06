from tornado.ioloop import IOLoop
from tornado.web import Application

from request_handler import IndexHandler, GetACLRuleHandler, SetACLRuleHandler

class SDNFirewall(object):
    def __init__(self, paths, port):
        self.port = port
        self.ioloop = IOLoop.instance()
        self.application = None

    def make_app(self):
        return Application(
                paths,
                cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
        )
    
    def start(self):
        print('Start server @ %s....' % self.port)
        self.application = self.make_app()
        self.application.listen(self.port)
        self.ioloop.start()
    

if __name__ == '__main__':
    paths = [
                (r"/", IndexHandler),
                (r"/setaclrule/", SetACLRuleHandler),
                (r"/getaclrule/", GetACLRuleHandler),
            ]
    port = 8888

    sdn_firewall = SDNFirewall(paths, port)
    sdn_firewall.start()
