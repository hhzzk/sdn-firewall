import logging

import json
import requests
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.escape import json_encode
from requests.auth import HTTPBasicAuth

import odl_rest_url


logger = logging.getLogger('server')
FORMAT = '%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(module)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


class IndexHandler(RequestHandler):
    def initialize(self):
        logger.info(
            'Receive request from %s',
            self.request.remote_ip
        )

    def get(self):
        self.render("template/index.html")


class SetACLRuleHandler(RequestHandler):
    def initialize(self):
        logger.info(
            'Receive request from %s',
            self.request.remote_ip
        )
        self.controller_ip = None
        self.controller_port = None
        self.base_auth = None

    def post(self):
        request_body = json_decode(self.request.body)
        logger.info('Request body %s', request_body)
        
        if request_body:
            if request_body['post_type'] == 'aclrule':
                self.set_acl_rule(request_body)
            else:
                self.authentication(request_body)

        return

    def set_acl_rule(self, body):
        base_url = 'http://' + str(self.controller_ip) + ':' \
                + str(self.controller_port)
        url = base_url+ietf_al

        input_data = {}
        ret = requests.post(url, data=json.dumps(input_data), \
                auth=self.base_auth)

        if ret.status_code == 200:
            self.write(" success ")
        else:
            self.write_error(500)
        return

    def authentication(self, body):
        try:
            self.controller_ip = body['controller_ip'] 
            self.controller_port = body['controller_port'] 
            self.base_auth = body['authentication'] 
        except:
           self.write("Authentication failed!!") 

        topo_api = '/restconf/operational/network-topology:network-topology'
        topo_url = 'http://' + str(self.controller_ip) + ':' + \
                str(self.controller_port) + topo_api

        headers = {'authorization': self.base_auth}
        input_data = {}
        node_list = []
        ret = requests.get(topo_url, headers=headers)
        if ret:
            network_topology = ret.json()['network-topology']
            try:
                nodes = network_topology['topology'][0]['node']
                for node in nodes:
                    node_list.append(node['node-id'])
            except:
               pass 

        if ret.status_code == 200:
            self.write(json.dumps(node_list))
        else:
            self.write_error(500)

        return
