from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class OutgoingfileWizard(models.TransientModel):
    _name = 'file.outgoing'
    _description = 'Wizard of Outgoing Files'

    file_id = fields.Many2one('folder.master', string='file')

    def show_outgoing_file(self):
        if self:
            my_id = []
            files = self.env['folder.master'].search([])
            srch_id = self.env.user.id
            for file in files:
                if srch_id in file.previous_owner.ids:
                    my_id.append(file.id)
            return {
                'name': 'Outgoing Files',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot,form',
                'res_model': 'folder.master',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                # 'view_id': self.env.ref('hr_applicant.view_employee_relative_tree').id,
                'domain': [('id', 'in', my_id)],
                }


    def show_outgoing_sec_file(self):
        if self:
            my_file = []
            emp_l = []
            emp = self.env['hr.employee'].search(['|', ('parent_id', '=', self.env.user.id), ('parent_id.parent_id', '=', self.env.user.id)])
            for e in emp:
                emp_l.append(e.id)
            files = self.env['folder.master'].search([])
            for file in files:
                for po in file.previous_owner.ids:
                    if po.id in emp.ids:
                        my_file.append(file.id)
            return {
                'name': 'Incoming Files',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'folder.master',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                # 'view_id': self.env.ref('hr_applicant.view_employee_relative_tree').id,
                'domain': [('id', 'in', my_file)],
                }


