from odoo import models, fields, api

class CSGSalesCollection(models.Model):
    _name = 'csg_sales_collection'
    _description = 'CSG Sales Collection'
    _rec_name = 'sl_no'

    sl_no = fields.Char(string="SL. No.",default="New")
    currency_type = fields.Selection([('inr','INR'),('usd','USD')],string="Currency Type")
    csg_name = fields.Char(string="CSG Name")
    csg_head_id = fields.Many2one('hr.employee',string="CSG Head")
    account_holder_id = fields.Many2one('hr.employee',string="Account Holder")
    amount_received = fields.Float(string="Amount Received")
    date_of_receipt = fields.Date(string="Date of Receipt")
    mode_of_receipt = fields.Selection([('cheque','Cheque'),('bank_transfer','Bank Transfer')],string="Mode of Payment")
    client_name = fields.Many2one('res.partner',string="Client")
    invoice_amount_taxed =fields.Float(string="Invoice Amount (Incl. Tax)")
    collection_lines_ids = fields.One2many('csg_sales_collection_lines','parent_id',string="Collections")
    state = fields.Selection([('draft','Draft'),('mail_sent','Mail Sent'),('sync','Synched to V5'),('close','Closed')],default="draft",string="State")
    
    def sent_mail_to_account_holder(self):
        for record in self:
            record.state = 'mail_sent'

    def synched_to_v5(self):
        for record in self:
            record.state = 'sync'

    @api.model
    def create(self, vals):
        if vals.get('sl_no', 'New') == 'New':
            vals['sl_no'] = self.env['ir.sequence'].next_by_code('csg_sales_collection') or 'New'
        return super(CSGSalesCollection, self).create(vals)
        


class CSGSalesCollectionLines(models.Model):
    _name = 'csg_sales_collection_lines'
    _description = 'CSG Sales Collection Lines'

    parent_id = fields.Many2one('csg_sales_collection',string="Collection")
    invoice_no = fields.Char(string="Invoice Number")
    workorder_id = fields.Many2one('kw_project_budget_master_data',string="Workorder")
    bank_charges = fields.Float(string="Bank Charges")
    currency_type = fields.Selection([('inr','INR'),('usd','USD')],string="Currency Type",related="parent_id.currency_type")
    cgst_tds = fields.Float(string="CGST-TDS")
    igst_tds = fields.Float(string="IGST-TDS")
    it_tds = fields.Float(string="IT-TDS")
    penalty = fields.Float(string="Penalty")
    sgst_tds = fields.Float(string="SGST-TDS")
    withholding_tax = fields.Float(string="WithHolding Tax")


