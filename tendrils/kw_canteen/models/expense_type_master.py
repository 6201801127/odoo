import string
from odoo import models, fields, api

class BeverageType(models.Model):
    _name="kw_canteen_expense_type_master"
    _description = "Canteen Expense Type"
    _rec_name = "expense_on"

    expense_on = fields.Char(string="Name")
    expense_head_code=fields.Char(string="Code")
