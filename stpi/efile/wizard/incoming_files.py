from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class IncomingfileWizard(models.TransientModel):
    _name = 'file.incoming'
    _description = 'Wizard of Incoming Files'

    file_id = fields.Many2one('folder.master', string='file')

    def show_incoming_file(self):
        if self:
            my_id = []
            files = self.env['folder.master'].search([])
            srch_id = self.env.user.id
            for file in files:
                if srch_id == file.current_owner_id.id:
                    my_id.append(file.id)
            print('==================my_id========================', my_id)
            return {
                'name': 'Incoming Files',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'folder.master',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', my_id)],
                }



    def show_incoming_sec_file(self):
        if self:
            my_ids = []
            employee = self.env['hr.employee'].sudo().search([])
            for emp in employee:
                if emp.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id:
                    my_ids.append(emp.user_id.id)
            return {
                'name': 'Incoming Files',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'folder.master',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('current_owner_id.id', 'in', my_ids)],
                }


