from odoo import models, fields, api
from datetime import date,datetime


class kw_employee_grievance(models.TransientModel):
    _name        = 'kw.remark'
    _description = 'A model to give remark'
    

    remark = fields.Text(string="Remark")
    # forward_section = fields.Many2one('kw.grievance.type')
                   
    def update_so_progress(self):
        if self.env.context.get('record_id'):
            griev_id = self.env.context.get('record_id')
            griev_rec = self.env['kw.grievance'].sudo().search([('id','=',griev_id)])
            
            griev_rec.write({
                    'so_update_progress':self.remark,
                    'so_update_boolean':True
                })
            # print(griev_rec.so_update_boolean,griev_rec.so_update_progress)
            