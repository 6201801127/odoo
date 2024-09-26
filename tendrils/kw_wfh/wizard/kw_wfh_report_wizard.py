# -*- coding: utf-8 -*-

import calendar
from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import date


class kw_wfh_report_wizard(models.TransientModel):
    _name = 'kw_wfh_report_wizard'
    _description = 'WFH Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    applied_by = fields.Selection([
        ('dt', 'Date Wise'),
        ('employee', 'Employee'),
    ], string="Applied By", default='dt')
    employee_ids = fields.Many2many('hr.employee', 'employee_wfh_report_rel', 'wfh_report_id', 'employee_id',
                                    string="Employee")

    def search_wfh_report(self):
        tree_view_id = self.env.ref('kw_wfh.kw_wfh_employee_report_tree').id
        form_view_id = self.env.ref('kw_wfh.kw_wfh_employee_report_form').id
        if self.applied_by == 'dt':
            from_date = self.date_from
            to_date = self.date_to
            record_data = self.env['kw_wfh'].sudo().search([])
            for rec in record_data:
                domain = ['|', '|', '&', '&', ('request_from_date', '<=', from_date), ('request_to_date', '>=', from_date), ('state','!=','draft'),
                          '&', '&',('request_from_date', '<=', to_date), ('request_to_date', '>=', to_date), ('state','!=','draft'),
                          '&', '&',('request_from_date', '>=', from_date), ('request_to_date', '<=', to_date), ('state','!=','draft'),]
                return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                        'view_mode': 'tree,form',
                        'name': ('WFH - All'),
                        'res_model': 'kw_wfh',
                        'domain': domain,
                        'target': 'main',
                        'context': {"search_default_filter_applied_state":1,"search_default_filter_grant_state":1}
                    }

        if self.applied_by == 'employee':
            record_data = self.env['kw_wfh'].sudo().search([])
            for rec in record_data:
                return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                        'view_mode': 'tree,form',
                        'name': ('WFH - All'),
                        'res_model': 'kw_wfh',
                        'domain':[('employee_id', 'in', self.employee_ids.ids), ('state','!=','draft')],
                        'target': 'main',
                        'context': {"search_default_filter_applied_state":1,"search_default_filter_grant_state":1}
                    }
