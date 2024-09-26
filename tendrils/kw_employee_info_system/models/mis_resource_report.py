from odoo import fields, models, api, tools
import datetime
from datetime import date


class ContractEndReport(models.Model):
    _name = 'mis_resources_report'
    _description = 'Resource  Report'

    def get_fiscal_year(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.datetime.today().date()),
             ('date_stop', '>=', datetime.datetime.today().date())])
        return current_fiscal

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    fiscalyear_id = fields.Many2one('account.fiscalyear', string='FY', default=get_fiscal_year, required=True)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)
    resource_type = fields.Char(string="Resource Type", required=True)
    head_count = fields.Integer(string="Headcount", required=True)