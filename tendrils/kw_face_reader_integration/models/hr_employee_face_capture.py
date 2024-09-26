# -*- coding: utf-8 -*-

from urllib import request
from odoo import models, fields, api
import requests, json
import base64
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    # employee_id = fields.Many2one('hr.employee',string='Employee')
    capture_status = fields.Boolean(string='Captured', default=False)

    @api.multi
    def get_face_capture_url(self):
        empl_bio_id = int(self.biometric_id)
        # print('bio_id', empl_bio_id)
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = self.env['ir.config_parameter'].sudo().get_param('kw_face_reader_url')
        # url="http://192.168.103.105:3000/widget/_get_authtoken"
        response=requests.post(url, headers=header, data=json.dumps({"Id": empl_bio_id}), verify=False)
        json_data = dict(response.json())
        # print('json_data',json_data)
        if json_data.get('auth_token') and empl_bio_id:
            final_url = f"https://fr.csm.tech/visitor_train.html?Id={empl_bio_id}&name={self.name}&authtoken={json_data.get('auth_token')}" 
        else:
            # final_url = ''
            raise ValidationError('Bio id or Auth Token does not available!')
        return{
            'type': 'ir.actions.act_url',
            'name': "Face capture url",
            'target': 'self',
            'url': final_url
        }
