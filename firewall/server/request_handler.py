import json
import requests
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.escape import json_encode
from requests.auth import HTTPBasicAuth

import odl_rest_url


class IndexHandler(RequestHandler):
    def get(self):
        self.render("templete/index.html")


class SetACLRuleHandler(RequestHandler):
    def initialize(self):
        self.controller_ip = None
        self.controller_port = None
        self.base_auth = None

    def post(self):
        request_body = json_decode(self.request.body)
        
        if request_body:
            if request_body['post_type'] == 'aclrule':
                self.set_acl_rule(request_body)
            else:
                self.authentication(request_body)

        self.write("Set ACL Rule fail")
        return

    def set_acl_rule(self, body):
        base_url = 'http://' + self.controller_ip + ':' \
                + self.controller_port
        url = base_url+ietf_al

        input_data = {}
        ret = requests.post(url, data=json.dumps(input_data), \
                auth=self.base_auth)

        if ret.status_code == 200:
            rewrite(" success ")

        return

    def authentication(self, body):
        try:
            self.controller_ip = body['controller_ip'] 
            self.controller_port = body['controller_port'] 
            self.base_auth = self.body['authorization'] 
        except:
           self.write("Authentication") 
        return
        


