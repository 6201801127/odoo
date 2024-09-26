from odoo import _, api, fields, models, tools
from odoo.exceptions import except_orm, UserError, Warning
import requests
import urllib
import re
import logging


class GateWaysetup(models.Model):
    _name = "gateway_setup"
    _description = "GateWay Setup"
    _rec_name = 'name'

    name = fields.Char(required=True, string='Gateway Name')
    gateway_url = fields.Char(required=True, string='GateWay Url')
    message = fields.Text('Message')
    mobile = fields.Char('Mobile')
    is_default = fields.Boolean('Is Deafult')

    @api.model
    def create(self, vals):
        new_record = super(GateWaysetup, self).create(vals)
        # self.env.user.notify_success(message='New configuration created')
        return new_record

    def send_sms_link(self, sms_rendered_content, rendered_sms_to, record_id, model, gateway_url_id):
        sms_rendered_content = sms_rendered_content.encode('ascii', 'ignore')
        sms_rendered_content_msg = urllib.parse.quote_plus(sms_rendered_content)
        if rendered_sms_to:
            rendered_sms_to = re.sub(r' ', '', rendered_sms_to)
            if '+' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('+', '')
            if '-' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('-', '')

        if rendered_sms_to:
            send_url = gateway_url_id.gateway_url
            send_link = send_url.replace('{mobile}', rendered_sms_to).replace('{message}', sms_rendered_content_msg)
            # The url should contain mobile={mobile} and message={message} to replace the contents ..
            # For ex:-https://login.bulksmsgateway.in/sendmessage.php?user=KwantifyCS&password=TifyKwa%239854&mobile={mobile}&message={message}&sender=CSMKWA&type=3
            # send_link=send_url+"user="+str(username)+"&password="+str(password)+"&mobile="+str(rendered_sms_to)+"&message="+str(sms_rendered_content_msg)+"&sender="+sender_id
            # print(send_link)
            try:
                response = requests.request("GET", url=send_link).text
                return response
            except Exception as e:
                return e

    @api.one
    def sms_test_action(self):
        # active_model = 'gateway_setup'
        # message = self.env['send_sms'].render_template(self.message, active_model, self.id)
        # print(message)
        # mobile_no = self.env['send_sms'].render_template(self.mobile, active_model, self.id)
        # response = self.send_sms_link(message, mobile_no,self.id,active_model,self)
        # raise Warning(response)
        # Test The Main SMS Functionality with Test Button,logs ,responses
        record = self.env['send_sms'].sudo().search([('name', '=', 'Onboarding_SMS')])
        send = self.env['send_sms'].send_sms(record, self.id)
        # print(send)
