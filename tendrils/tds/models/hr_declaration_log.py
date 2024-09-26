from odoo import models, fields, api, _


class HrDeclaration(models.Model):
    _name = 'hr_declaration_log'
    _description = 'IT Declaration Log'

    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year')
    tax_regime=fields.Selection([('new_regime', 'New Regime'),('old_regime', 'Old Regime')],'Tax Regime')
