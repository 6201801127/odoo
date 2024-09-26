from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BudgetReportGroupMapping(models.Model):
    _name = "budget_report_group_mapping"
    _description = "Budget Report Account code Mapping"
    _rec_name = 'code'

    
    code =  fields.Selection(string="Code",selection=[('cp', 'CP'),('rv', 'RV')])
    group_type_id = fields.Many2one('kw.group.type', string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name', string='Group Name')
   

   