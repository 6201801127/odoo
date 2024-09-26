# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import date, datetime


class kw_emp_archieve(models.TransientModel):
    _name = 'kw_emp_archieve'
    _description = 'model to store the employee eos details'

    last_working_day = fields.Date('Last working Day')
    reason = fields.Many2one('kw_resignation_master', string="Reason")

    def button_confirm(self):
        # self.write({'active': False})
        employee = self.env.context.get('archieve_id')
        emp_rec = self.env['hr.employee'].sudo().search([('id', '=', employee)])
        emp_rec.write({'last_working_date': self.last_working_day,
                       'resignation_reason': self.reason.id,
                       'active': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
