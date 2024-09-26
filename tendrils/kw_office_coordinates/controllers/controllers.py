# -*- coding: utf-8 -*-
# from odoo import http, api
# import requests
# import json

# class servicecall(http.Controller):
#     @http.route('/message/',type="http", auth='public',website=True, methods=['GET'], csrf=False)
#     def returnapi(self, **kw):
#         url = 'http://172.27.37.145/prd.service.portalV6.csmpl.com/OdooSynSVC.svc/getDMLQuery'
#         myobj = {'strQuery': 'UPDATE designationMaster SET nvch_designame = "Hatt Paglu" WHERE int_DesignationId = 10'}
#         headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#         data = json.dumps(myobj)
#         response = requests.post(url, data = data, headers = headers)
#         print(response)
#         json_data = response.text
#         #load the json to a string
#         resp = json.loads(json_data)
#         print(resp)
#         print (type(resp))  
#         #extract an element in the response
#         for x in resp['getDMLQueryResult']:
#             y=x['OutMessage']
#         return y
