from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date



class IndentLedger(models.Model):
    _name = 'stock.log.book'
    _description = "Issue Request"
    

    employee_id = fields.Many2one('hr.employee', string='Requested/Received By')
    branch_id = fields.Many2one('res.branch', string='Center', store=True)
    Indent_id = fields.Many2one('indent.request', string='Indent/GRN')
    Indent_item_id = fields.Many2one('indent.request.items', string='Indent Item')
    item_category_id = fields.Many2one('product.category', string='Item Category')
    item_id = fields.Many2one('indent.stock', string='Item')
    specification = fields.Text('Specifications')
    serial_bool = fields.Boolean(string='Serial Number')
    serial_number = fields.Char(string='Serial Number')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    requested_date = fields.Date('Requested Date')
    approved_date = fields.Date('Approved Date', default=fields.Date.today())
    opening = fields.Integer('Opening')
    quantity = fields.Integer('Quantity')
    balance = fields.Integer('Balance')


    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                               ],track_visibility='always', string='Type')
