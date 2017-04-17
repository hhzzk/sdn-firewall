import ast
import json
import uuid
import copy
import logging

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

class GetACLRuleHandler(RequestHandler):
    def initialize(self):
        logger.info(
            'Receive request from %s',
            self.request.remote_ip
        )

    def get(self):
        with open('rules.json') as data_file:
            rules_list = json.load(data_file)

        for item in rules_list:
            rule = ''
            condition = item['condition']
            for one in condition:
                if(condition[one]):
                    rule += one + '=' + condition[one] + ', '
            item['condition'] = rule

        self.write(json.dumps(rules_list))


class SetACLRuleHandler(RequestHandler):
    def initialize(self):
        logger.info(
            'Receive request from %s',
            self.request.remote_ip
        )

    def post(self):
        request_body = json_decode(self.request.body)
        logger.info('Request body %s', request_body)
        
        if request_body:
            if request_body['post_type'] == 'aclrule':
                self.set_acl_rule(request_body)
            elif request_body['post_type'] == 'deleteacl':
                self.del_acl_rule(request_body)
            else:
                self.authentication(request_body)

        return

    def del_acl_rule(self, body):
        if not self.get_secure_cookie("base_auth"):
            self.write("Please Authentication")
            return

        acl_id = body['id']

        rules_list = []
        with open('rules.json') as data_file:
            try:
                rules_list = json.load(data_file)
            except:
                self.write(500) 

        body_tmp = {}
        is_exist = False
        for temp in rules_list:
            if(temp['id'] == acl_id):
                body_tmp = temp['condition']
                body_tmp['action'] = str(temp['action'])
                rules_list.remove(temp)
                is_exist = True
                break

        if not is_exist:
            return

        with open('rules.json', 'w') as outfile:
            json.dump(rules_list, outfile)

        controller_ip = self.get_secure_cookie("controller_ip")
        controller_port = self.get_secure_cookie("controller_port")
        base_auth = self.get_secure_cookie("base_auth")

        base_url = 'http://' + str(controller_ip) + ':' \
                + str(controller_port)
        remove_acl_api = '/restconf/operations/sal-flow:remove-flow'
        url = base_url + remove_acl_api

        payload = self.generate_xml(body_tmp)
        #import pdb;pdb.set_trace()
        headers = {
                'authorization': base_auth,
                'content-type': "application/xml" 
            }
        ret = requests.post(
                url,
                data=payload,
                headers=headers
            )

        if ret.status_code == 200:
            for item in rules_list:
                rule = ''
                condition = item['condition']
                for one in condition:
                    if(condition[one]):
                        rule += one + '=' + condition[one] + ', '
                item['condition'] = rule

            self.write( json.dumps(rules_list))
        else:
            self.write_error(500)
        return


    def generate_match_xml(self, body):
        # add source mac march
        ethernet_type = '<ethernet-type><type>2048</type></ethernet-type>'
        source_mac_xml = ''
        dest_mac_xml = ''
        source_ip_xml = ''
        dest_ip_xml = ''
        ip_match_xml = '' 

        if(body['source_mac']):
            source_mac_xml = \
                    '<ethernet-source><address>' + \
                    body['source_mac'] + \
                    '</address></ethernet-source>'

        # add destination mac march
        if(body['dest_mac']):
            dest_mac_xml = \
                    '<ethernet-destination><address>' + \
                    body['dest_mac'] + \
                    '</address></ethernet-destination>'

        ethernet_match = \
            '<ethernet-match>' + \
                ethernet_type + \
                source_mac_xml + \
                dest_mac_xml + \
            '</ethernet-match>'

        # add soure ip march
        if(body['source_ip']):
            source_ip_xml = '<ipv4-source>' + body['source_ip'] + '</ipv4-source>' 

        # add destination ip march
        if(body['dest_ip']):
            dest_ip_xml = '<ipv4-destination>' + body['dest_ip'] + '</ipv4-destination>' 

        if(body['protocol']):
            protocol = body['protocol']
            ip_match_xml = '<ip-match><ip-protocol>' + \
                            protocol + \
                            '</ip-protocol></ip-match>'    

        match_xml = '<match>' + \
                    ethernet_match + \
                    source_ip_xml + \
                    dest_ip_xml + \
                    ip_match_xml + \
                    '</match>'

        return match_xml

    def generate_xml(self, body):
        xml_header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><input xmlns="urn:opendaylight:flow:service">'
        common_element = \
            '<barrier>false</barrier>' + \
            '<cookie>136</cookie>' + \
            '<flags>SEND_FLOW_REM</flags>' + \
            '<hard-timeout>0</hard-timeout>' + \
            '<idle-timeout>0</idle-timeout>' + \
            '<installHw>false</installHw>' + \
            '<strict>false</strict>' + \
            '<table_id>0</table_id>'

        if(int(body['action']) == 0):
            action_element = '<action><order>0</order><drop-action/></action>'
        else:
            action_element = '<action><order>0</order><output-action><output-node-connector>ALL</output-node-connector><max-length>60</max-length></output-action></action>'

        instructions_element = \
                '<instructions>' + \
                    '<instruction>' + \
                        '<order>0</order>' + \
                        '<apply-actions>' + \
                            action_element + \
                        '</apply-actions>' + \
                    '</instruction>' + \
                '</instructions>' 

        match_element = self.generate_match_xml(body)
        priority_element = '<priority>3</priority>'

        node_id = body['nodeid']
        node_element = '<node xmlns:inv="urn:opendaylight:inventory">/inv:nodes/inv:node[inv:id="' + str(node_id) + '"]</node>'
        xml_tail = '</input>'

        xml = xml_header + common_element + match_element + instructions_element + priority_element + node_element + xml_tail

        return xml

    def set_acl_rule(self, body):

        if not self.get_secure_cookie("base_auth"):
            self.write("Please Authentication")
            return

        
        body_cp = copy.deepcopy(body)
        action = body_cp['action']
        body_cp.pop('action')
        body_cp.pop('post_type')
        rule = {
            "id"     : str(uuid.uuid1()),
            "condition"   : body_cp,
            "action" : action
        }

        rules_list = []
        with open('rules.json') as data_file:
            try:
                rules_list = json.load(data_file)
            except:
                pass 

        add_rule = True
        for temp in rules_list:
            if(temp['condition'] == rule['condition']):
                if(temp['action'] != rule['action']):
                    rules_list.append(rule)
                    rules_list.remove(temp)
                    add_rule = False
                else:
                    return

        if add_rule:
            rules_list.append(rule)
        with open('rules.json', 'w') as outfile:
            json.dump(rules_list, outfile)


        controller_ip = self.get_secure_cookie("controller_ip")
        controller_port = self.get_secure_cookie("controller_port")
        base_auth = self.get_secure_cookie("base_auth")

        base_url = 'http://' + str(controller_ip) + ':' \
                + str(controller_port)
        add_acl_api = '/restconf/operations/sal-flow:add-flow'
        url = base_url + add_acl_api

        payload = self.generate_xml(body)
        #import pdb;pdb.set_trace()
        headers = {
                'authorization': base_auth,
                'content-type': "application/xml" 
            }
        ret = requests.post(
                url,
                data=payload,
                headers=headers
            )

        if ret.status_code == 200:
            self.write(" success ")
        else:
            self.write_error(500)
        return

    def authentication(self, body):
        try:
            controller_ip = body['controller_ip'] 
            controller_port = body['controller_port'] 
            base_auth = body['authentication'] 
        except:
           self.write("Authentication failed!!") 

        topo_api = '/restconf/operational/network-topology:network-topology'
        topo_url = 'http://' + str(controller_ip) + ':' + \
                str(controller_port) + topo_api

        headers = {'authorization': base_auth}
        input_data = {}
        node_list = []
        ret = requests.get(topo_url, headers=headers)
        if ret:
            network_topology = ret.json()['network-topology']
            try:
                nodes = network_topology['topology'][0]['node']
                for node in nodes:
                    if 'host' not in node['node-id']:
                        node_list.append(node['node-id'])
            except:
               pass 

        if ret.status_code == 200:
            self.set_secure_cookie("controller_ip", controller_ip)
            self.set_secure_cookie("controller_port", controller_port)
            self.set_secure_cookie("base_auth", base_auth)
            self.write(json.dumps(node_list))
        else:
            self.write_error(500)

        return
