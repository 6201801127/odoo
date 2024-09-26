import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class kw_add_product_consolidation(models.Model):
    _name = 'kw_add_product_consolidation'
    _description = "A master model to add the Products for Indent Consolidation"

    item_code = fields.Many2one('product.product', string="Item Code")
    item_description = fields.Char(string="Item Description")
    quantity_required = fields.Integer(string="Quantity Required")
    quantity_onorder = fields.Integer(string="Quantity On Order")
    quantity_balance = fields.Integer(string="Quantity Balance")
    last_proc_date = fields.Date(string='Last Proc.Date', default=fields.Date.context_today)
    last_proc_value = fields.Integer(string="Last Proc.Value")
    status = fields.Char(string="Status")
    indent_rel = fields.Many2one('kw_consolidation', ondelete='cascade')
    add_product_id = fields.Many2many('kw_add_product', string='Add Product Id')

    @api.onchange("item_code")
    def _onchange_item_code(self):
        for record in self:
            if record.item_code:
                record.item_description = record.item_code.name

    @api.depends('partner_id')
    def validate_partner_id(self):
        for record in self:
            if len(record.partner_id) == 0:
                raise ValidationError('Please provide a valid Vendor')

    @api.model
    def create(self, vals):
        new_record = super(kw_add_product_consolidation, self).create(vals)
        for record in new_record:
            record.quantity_balance = record.quantity_required

        return new_record

    @api.constrains('quantity_required')
    def validate_qty_required(self):
        for record in self:
            if record.quantity_required == 0:
                raise ValidationError("Quantity cannot be 0")
