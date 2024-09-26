from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.http import json


class sms_log(models.Model):
    _name = "sms_log"
    _description = "SMS Log"
    _rec_name = 'mobile_no'

    mobile_no       = fields.Char('Mobile No.', readonly=False)
    message_id      = fields.Text('Messages', readonly=False)
    status          = fields.Boolean('Status', readonly=False)
    category        = fields.Char('Category', readonly=False)
    response_status = fields.Char('Response Status',)
    # gatewayurl_id = fields.Many2one('gateway_setup',required=True,string='SMS Gateway')

    #@api.model
    def send_sms(self):
        log_report          = self.env['sms_log'].search([('status', '=', False)])
        gatewayurl_record   = self.env['gateway_setup'].sudo().search([('is_default', '=', True)], limit=1)

        if gatewayurl_record:
            for record in log_report:            
                sms_sent        = self.env['send_sms'].send_sms_link(record.message_id,record.mobile_no, record, 'gateway_setup', gatewayurl_record)
                # data = json.loads(sms_sent)
                # print(data," Response data")
                # print("sms sent -------",sms_sent)
                record.write({'status': True, 'response_status': sms_sent})
