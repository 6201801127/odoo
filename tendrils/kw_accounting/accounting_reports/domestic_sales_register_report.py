from odoo import models, fields, api
from odoo import tools


class DomesticSalesRegisterReport(models.Model):
    _name = "domestic.sales.register.report"
    _description = "Domestic Sales Register Report"
    _auto = False

    transaction_date = fields.Date("Transaction Date")
    invoice_date = fields.Date("Invoice Date")
    voucher_no = fields.Char(string="Voucher No")
    invoice_number = fields.Char(string="Invoice Number")
    recepiant_name = fields.Char(string="Recepiant Name")
    recepiant_gstin = fields.Char(string="Recepiant GSTIN")
    recepiant_state = fields.Char(string="Recepiant State")
    item_id = fields.Many2one('product.product',string="Item / Service Description")
    narration= fields.Text(string="Narration")
    product_category = fields.Selection([('product','Goods'),('service','Service')],"GOODS / SERVICES")
    hsn_sac_code = fields.Char(string="HSN/SAC")
    taxable_value = fields.Monetary(string="TAXABLE VALUE")
    quantity = fields.Float(string='Quantity')
    currency_id = fields.Many2one('res.currency',related_sudo=False, readonly=False)
    igst_rate = fields.Float(string="IGST Rate")
    igst_amount = fields.Monetary(string="IGST Amount")
    cgst_rate = fields.Float(string="CGST Rate")
    cgst_amount = fields.Monetary(string="CGST Amount")
    sgst_rate = fields.Float(string="SGST Rate")
    sgst_amount = fields.Monetary(string="SGST Amount")
    invoice_total = fields.Monetary(string="Invoice Total")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select 
            row_number() over() as id,
            ai.date as transaction_date,
            ai.date_invoice as invoice_date,
            ai.number as voucher_no,
            ai.currency_id as currency_id,
            ai.reference_number as invoice_number,
            rp.name as recepiant_name,
            rp.vat as recepiant_gstin,
            rs.name as recepiant_state,
            pp.id as item_id,
            ai.comment as narration,
            apl.product_category as product_category,
            apl.hsn_code as hsn_sac_code,
            apl.quantity as quantity,
            apl.price_unit as taxable_value,
            CAST (apl.igst_per AS DOUBLE PRECISION)  as igst_rate,
            apl.igst_amount as igst_amount,
            CAST (apl.cgst_per AS DOUBLE PRECISION) as cgst_rate,
            apl.cgst_amount as cgst_amount,
            CAST (apl.sgst_per AS DOUBLE PRECISION) as sgst_rate,
            apl.sgst_amount as sgst_amount,
            apl.amount as invoice_total


            from account_product_line apl
            left join account_invoice ai on ai.id = apl.invoice_id
            left join res_partner rp on rp.id = ai.partner_id
            left join res_country_state rs on rs.id = rp.state_id
            left join product_product pp on pp.id = apl.product_id

            where rp.business_operation = '1' and ai.type= 'out_invoice' and ai.state != 'draft'

        )"""
        self.env.cr.execute(query)






