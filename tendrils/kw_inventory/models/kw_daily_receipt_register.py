# import datetime
# import calendar
from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class kw_daily_receipt_register(models.Model):
    _name = "kw_daily_receipt_register"
    _description = "Daily receipt register"

    name = fields.Char(string='DRR Number', default="DRR-001")
    partner_id = fields.Char(string='Vendor')
    po_number = fields.Char(string='PO Number')
    receipt_number = fields.Char(string='Receipt/Invoice Number')
    received_by = fields.Char(string='Received By')
    received_date = fields.Date(string='Received Date')
    products = fields.Html(string="Products/Items")
    remark = fields.Char(string='Remarks')
