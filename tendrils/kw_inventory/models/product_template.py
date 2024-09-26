from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
import re


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = 'default_code asc'

    type = fields.Selection(selection_add=[('it', 'IT'),('nonit', 'Non-IT')])
    varient_description = fields.Text(string='Description')
    code = fields.Char('Code')
    critical_item = fields.Boolean(string="Critical Item")
    temporary_item = fields.Boolean(string="Temporary Item")
    old_item_code = fields.Char(string="Old Item Code", size=250)
    equipment_code = fields.Char(string="Equipment Code", size=250)
    ledger_number = fields.Char(string="Ledger Number", size=250)
    folio_number = fields.Char(string="Folio Number", size=250)
    current_price = fields.Float(string="Current Price")
    average_price = fields.Float(string="Average Price")
    purchase_price = fields.Float(string="Purchase Price")
    opening_balance_qty = fields.Float(string="Opening Balance Qty", digits=dp.get_precision('Product Unit of Measure'))
    closing_balance_qty = fields.Float(string="Closing Balance Qty", digits=dp.get_precision('Product Unit of Measure'))
    opening_balance_price = fields.Float(string="Opening Balance Price")
    closing_balance_price = fields.Float(string="Closing Balance Price")
    is_asset = fields.Boolean(string="Is Asset?")

    product_qutetion_ids = fields.One2many(string='Product Quotation', comodel_name='kw_quotation_items',
                                           inverse_name='product_id', )
    salvage_value = fields.Float(string="Salvage Value")
    alias_name = fields.Char('Alias')
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", help="Ensure the traceability of a storable product in your warehouse.", default='serial', required=True)

    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes " 
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    
    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        res['type'] = ''
        return res

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            pattern = r'^[0-9A-Z]{2}$'
            if not re.match(pattern, record.code):
                raise ValidationError("Code must be two characters: one integer and one alphabet or two alphabet or two integer characters.")


    def _compute_quantities(self):
        for rec in self:
            product_record =self.env['stock.quant'].search_count([('product_id','in',rec.product_variant_ids.ids),('is_issued','=',False),('process_location','=','store')])
            # print("product record========",product_record)
            if product_record:
                rec.qty_available = product_record
                # print("product record========",rec.qty_available)
                
            else:
                rec.qty_available = 0
                
    def action_open_quants(self):
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['domain'] = [('product_id', '=', self.product_variant_ids.ids),('is_issued','=',False),('process_location','=','store')]
        action['context'] = {'search_default_internal_loc': 1}
        return action
                
    @api.constrains('type')
    def check_product_type(self):
        if self.type == 'consu' or self.type == 'product':
                raise ValidationError('Consumable and storable product type is not in use,please choose another.')
            
    @api.constrains('attribute_line_ids')
    def _check_attribute_line_lin(self):
        if len(self.attribute_line_ids) > 3:
            raise ValidationError('You can add upto 3 specifications for a product.')
        
            
    @api.onchange('name')
    def convert_uppercase(self):
        for record in self:
            if record.name:
                record.name = record.name.upper()
                
    @api.onchange('name')
    def convert_uppercase(self):
        for record in self:
            if record.name:
                record.varient_description = record.name.upper()

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        res = super(ProductTemplate, self).write(vals)
        return res

    # categ_id = fields.Many2one(
    #     'product.category', 'Product Category',
    #     change_default=True, default=_get_default_category_id,
    #     required=False, help="Select category for the current product")
    # , search='_search_qty_available'
    qty_ordered = fields.Float(
        'Quantity Ordered', compute='_compute_quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Ordered quantity of products.")
    # , search='_search_qty_available'
    qty_indented = fields.Float(
        'Quantity Indented', compute='_compute_quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Ordered quantity of products.")

    @api.model
    def create(self, vals):
        last_code = self.env['product.template'].search([], order='id desc', limit=1).mapped('code')
        # print("last_code==============",last_code)
        last_code = last_code[0] if last_code else 'false'
        generated_code = self.generate_next_product_code(last_code)
        vals['code'] = generated_code
        res = super(ProductTemplate, self).create(vals)
        res.name =res.name.upper()
        return res

    def generate_next_product_code(self, last_code):
        code_options = []

        for i in range(100):
            code_options.append(f'{i:02d}')

        for i in range(10):
            for j in range(26):
                code_options.append(f'{i}{chr(ord("A") + j)}')

        for i in range(26):
            for j in range(26):
                code_options.append(f'{chr(ord("A") + i)}{chr(ord("A") + j)}')

        for i in range(26):
            for j in range(10):
                code_options.append(f'{chr(ord("A") + i)}{j}')

        if last_code not in code_options:
            return '00' 
        last_code_index = code_options.index(last_code)
        next_code_index = (last_code_index + 1) % len(code_options)

        next_code = code_options[next_code_index]
        # print("next code============",next_code)

        return next_code