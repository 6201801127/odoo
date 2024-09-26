from datetime import date , datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request

class ProductGatePass(models.Model):
    _name = "kw_product_gatepass"
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    
    sequence = fields.Char('Serial No')
    vendor_ref = fields.Char('Vendor Reference')
    # partner_id = fields.Many2one('res.partner', string='Vendor')
    po_id = fields.Char(string='Purchase Order Reference')
    state = fields.Selection(selection=[('draft', 'Draft'),('checkin', 'Check-In'), ('checkout', 'CHeck-Out'),('rejected', 'Rejected')],default='draft',string='State')
    # operation_type = fields.Selection(selection=[('po', 'PO'),('return', 'Return'),('backorder', 'Backorder')],string='Operation Type') # show from which operation the gate pass is created. 
    # branch_id = fields.Char(string='Location/Ship To')
    company_id = fields.Char(string='Company')
    remark = fields.Text(string='Remark',track_visibility='always')
    date = fields.Datetime(string='Check-in/Check-out Date')
    # raised_by_id = fields.Many2one('hr.employee', string='Raised by')
    received_by_id = fields.Char(string='Recieved By')
    challan_no = fields.Char('Challan No')
    lorry_driver_phn_no = fields.Char('Delivery Person Phn No.')
    lorry_driver_name = fields.Char('Delivery Person Name.')
    address=fields.Text(string='Address')
    company_address=fields.Text(string='Address')
    gatepass_line_ids = fields.One2many("kw_product_gatepass_line", 'gatepass_line', string="Gate Pass lines")
    
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('product_gatepass_sequence') or '/'
        res = super(ProductGatePass, self).create(vals)
        return res
    
    @api.multi
    def action_checkin_gatepass(self):
        self.state = 'checkin'
    
    @api.multi
    def action_checkout_gatepass(self):
        self.state = 'checkout'
    
    @api.multi
    def action_reject_gatepass(self):
        self.state = 'rejected'
   

class ProductGatePassLine(models.Model):
    _name = "kw_product_gatepass_line"
    
    product_id = fields.Char(string="Product")
    gatepass_line = fields.Many2one('kw_product_gatepass', string="Product")
    description = fields.Char(stringatepassg="Product Description")
    uom = fields.Char(string="Unit Of Measurement")
    quantity = fields.Float(string="Quantity")
