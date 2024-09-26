# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.kw_utility_tools import kw_whatsapp_integration

class kw_whatsapp_message_log(models.Model):
    _name           = 'kw_whatsapp_message_log'
    _description    = 'whatsApp message log'

    _rec_name       = 'mobile_no'
   

    mobile_no       = fields.Char(
        string='Mobile No',required=True,
    )

    message         = fields.Text(
        string='Message',required=True,
    )
  
    process_status  = fields.Boolean(
        string='Process Status',
    )

    response        = fields.Text(
        string='Message Response',
    )
    

    ##main function called by scheduler
    def call_whatsapp_send_api(self):

        message_log       = self.env['kw_whatsapp_message_log'].search([('process_status','=',False)])

        if message_log:
            for log_rec in message_log:
                if log_rec.mobile_no and log_rec.message:
                    resp = kw_whatsapp_integration.send_whatsapp_message(log_rec.mobile_no,log_rec.message)
                    
                    log_rec.write({'response':resp['result']}) 
            
            message_log.write({'process_status':True}) 





    
