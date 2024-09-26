from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class IncomingLetterWizard(models.TransientModel):
    _name = 'letter.incoming'
    _description = 'Wizard of Incoming Files'

    letter_id = fields.Many2one('muk_dms.file', string='Letter')

    def show_incoming_letter(self):
        if self:
            my_id = []
            files = self.env['muk_dms.file'].search([])
            srch_id = self.env.user.id
            for file in files:
                if srch_id in file.sec_owner.ids or srch_id == file.current_owner_id.id:
                    print('=====================first=======================', file.name)
                    if file.folder_id != True:
                        print('=====================second=======================', file.name)
                        my_id.append(file.id)

            return {
                'name': 'Incoming Correspondence',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'muk_dms.file',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                'domain': [('id', 'in', my_id)],
                }



    def show_incoming_sec_letter(self):
        if self:
            my_ids = []
            employee = self.env['hr.employee'].search([])
            for emp in employee:
                if emp.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id:
                    my_ids.append(emp.user_id.id)
            return {
                'name': 'Incoming Correspondence',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'muk_dms.file',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'create': False,
                'domain': [('current_owner_id.id', 'in', my_ids),('folder_id', '=', False)],
                }


