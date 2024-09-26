from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class IncomingLetterWizard(models.TransientModel):
    _name = 'letter.outgoing'
    _description = 'Wizard of Outgoing Files'

    letter_id = fields.Many2one('muk_dms.file', string='Letter')

    def show_outgoing_letter(self):
        if self:
            my_id = []
            files = self.env['muk_dms.file'].search([])
            srch_id = self.env.user.id
            transfer_to_emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            for file in files:
                if transfer_to_emp.id in file.previous_owner_emp.ids:
                    my_id.append(file.id)
            return {
                'name': 'Outgoing Correspondence',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'muk_dms.file',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                # 'view_id': self.env.ref('hr_applicant.view_employee_relative_tree').id,
                'domain': [('id', 'in', my_id)],
                }


    def show_outgoing_sec_letter(self):
        if self:
            my_file = []
            emp_l = []
            emp = self.env['hr.employee'].search(['|', ('parent_id', '=', self.env.user.id), ('parent_id.parent_id', '=', self.env.user.id)])
            for e in emp:
                emp_l.append(e.id)
            files = self.env['muk_dms.file'].search([])
            for file in files:
                for po in file.previous_owner.ids:
                    if po.id in emp.ids:
                        my_file.append(file.id)
            return {
                'name': 'Incoming Correspondence',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'muk_dms.file',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                # 'view_id': self.env.ref('hr_applicant.view_employee_relative_tree').id,
                'domain': [('id', 'in', my_file)],
                }


