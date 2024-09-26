import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import datetime
from datetime import date, datetime


class kw_employee_sync_wizard(models.TransientModel):
    _name = 'kw_employee_sync_wizard'
    _description = 'Kw Employee Sync Wizard'

    from_date = fields.Date(string="From Date", default=date.today())
    to_date = fields.Date(string="To Date", default=date.today())
    page_no = fields.Integer(string="Page No")
    page_size = fields.Integer(string="Page Size")

    @api.multi
    def get_employee_synchronozation_data(self):
        if not self.from_date and not self.to_date:
            raise ValidationError("Please select Date range")
        else:
            from_date, to_date, page_no, page_size = self.from_date, self.to_date, self.page_no, self.page_size
            self.env['kw_kwantify_integration_log'].syncKwantifyData(from_date, to_date, page_no, page_size)
            self.env.user.notify_success(message='Employee Synchronized')
        """ Redirected wizard view """
        wizard_form = self.env.ref('kw_kwantify_integration.kw_employee_sync_wizard_form', False)
        action = {
            'name': 'Employee Synchronization Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw_employee_sync_wizard',
            'target': 'new',
            'context': {'default_from_date': self.from_date,
                        'default_to_date': self.to_date,
                        'default_page_no': self.page_no,
                        'default_page_size': self.page_size, },
        }
        return action


class kw_Exemployee_sync_wizard(models.TransientModel):
    _name = 'kw_exemployee_sync_wizard'
    _description = 'Kw Ex-Employee Sync Wizard'

    exemployee_ids = fields.Many2many('hr.employee', 'kw_sync_exhr_employee_rel', 'offboarding_wiz_id',
                                      'employee_id', string="Ex-employee",
                                      domain=[('active', '=', False), ('kw_id', '!=', False), '|', ('job_id', '=', False),
                                              ('department_id', '=', False)])
    kw_ids = fields.Char(string="KW ID", compute="_get_employee_kw_ids")

    @api.depends('exemployee_ids')
    def _get_employee_kw_ids(self):
        kw_ids = []
        for rec in self.exemployee_ids:
            kw_ids.append(str(rec.kw_id))
        self.kw_ids = ', '.join(kw_ids)

    @api.multi
    def get_ex_employee_synchronozation_data(self):
        for rec in self.exemployee_ids:
            self.env['kw_kwantify_integration_log'].syncKwantifyData(rec.kw_id)
            time.sleep(1)

        view_id = self.env.ref('kw_kwantify_integration.kw_ex_employee_sync_wizard_form').id
        return {
            'name': 'Ex-Employee Sync Log',
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'kw_exemployee_sync_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
