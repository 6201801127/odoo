# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime, date, timedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    tds_amount = fields.Integer(string='TDS', compute='_compute_tds')

    @api.depends('line_ids')
    def _compute_tds(self):
        for rec in self:
            for record in rec.line_ids:
                if record.code == 'TDS':
                    rec.tds_amount = record.total


class Payslip(models.TransientModel):
    _name = 'tds_report_wizard'

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    filtered_by = fields.Selection([
        ('all', 'All'),
        ('date', 'Date'),
        ('employee', 'Employee'),
        ('department', 'Department'),
        ('location', 'Location'),
    ], 'Filtered By', default='date')

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    employee_ids = fields.Many2many('hr.employee', 'employee_tds_report_rel', 'tds_report_id', 'employee_id',string="Employee")
    department_ids = fields.Many2many('hr.department', 'department_tds_rel', 'tds_dept_id', 'dept_id',string="Department")
    # branch_ids = fields.Many2many("kw_res_branch", 'branch_tds_rel', 'tds_branch_id', string="Location")

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    def search_tds_report(self):
        tree_view_id = self.env.ref('tds.monthly_tds_report_view_tree').id
        if self.filtered_by == 'date':
            domain = [('salary_confirm_year', '=', self.year), ('salary_confirmation_month', '=', self.month),
                      ('state', '=', 'done')]
        elif self.filtered_by == 'employee':
            domain = [('employee_id', 'in', self.employee_ids.ids), ('state', '=', 'done')]
        elif self.filtered_by == 'all':
            domain = [('state', '=', 'done')]
        elif self.filtered_by == 'department':
            domain = [('department_id', 'in', self.department_ids.ids), ('state', '=', 'done')]
        else:
            domain = [('state', '=', 'done')]
        action = {
            'name': ('TDS Report'),
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'domain': domain,
            'target': 'main',
            'context': {'create':False,'delete':False,'edit':False}
        }
        return action
