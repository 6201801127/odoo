from odoo import models, fields, api
from odoo import tools

class CreditorAgeing(models.Model):
    _name = 'creditor_ageing'
    _description = 'Creditor Ageing'
    _auto = False

    partner_id = fields.Many2one('res.partner',string="Vendor")
    partner_account_code = fields.Char(related="partner_id.property_account_payable_code",string="Vendor")
    bill_no = fields.Char(string="Vendor Bil No.")
    date_due = fields.Date(string="Due Date")
    purchase_order_id = fields.Many2one('purchase.order',string="Purchase Order")
    project_code = fields.Char(string="Workorder")
    csm_invoice_id = fields.Char(string="CSM Invoice Ref.")
    csm_inv_collection_date = fields.Date(string="CSM Inv. Coll. Dt.")
    payable_amount = fields.Float(string="Payable Amount")
    budget_type = fields.Char(string="Expense Type")
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select row_number() over(order by ai.id asc) as id,
            ai.partner_id as partner_id,
            ai.reference_number as bill_no,
            ai.date_due as date_due,
            po.id as purchase_order_id, 
            string_agg(kpbmd.wo_code,',') as project_code,
            string_agg(initcap(ail.budget_type),',') as budget_type,
            '' as csm_invoice_id, '' as csm_inv_collection_date, 
            ai.residual as payable_amount
            from account_invoice ai
            left join account_invoice_line ail on ail.invoice_id = ai.id
			left join kw_project_budget_master_data kpbmd on kpbmd.id = ail.project_wo_id
            left join purchase_order po on po.id = ai.purchase_order_id
            where ai.residual > 0 and ai.state in ('open')		
			group by ai.partner_id,ai.reference_number,ai.date_due,po.id, ai.residual,ai.id
        )"""
        self.env.cr.execute(query)
