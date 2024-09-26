import re
from odoo import models, fields, api,tools
from datetime import date
from odoo.exceptions import ValidationError


class kw_po_register_report(models.Model):
    _name                   = "kw_po_register_report"
    _description            = "PO Register Report"
    _auto                   = False

    
    po_number               = fields.Char(string='PO Number')
    vendor                  = fields.Char(string='Vendor')
    date                    = fields.Char("Date") 
    state                   = fields.Char(string="Status")
    description             = fields.Char(string='Description') 
    unit_price              = fields.Char(string="Unit Price")
    unit_of_measure         = fields.Char(string="UOM")
    amount_total            = fields.Integer(string='Total Amount (Including Tax)')
    department_name         = fields.Char(string='Indenting Department')
    in_house                = fields.Char(string='In House')
    amount_tax              = fields.Integer(string='Total tax(Amount)')
    taxes_id                = fields.Char(string="Tax")
    workorder_code          = fields.Char(string='Workorder Code')
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT 
                p.id as id,
                p.name as po_number,
                p.amount_total as amount_total,
                p.date_order as date,
                p.state as state,
                p.amount_tax as amount_tax,
                (select string_agg(default_code,', ')from product_product pp join purchase_order_line pl on pp.id = pl.product_id where order_id = p.id)  as description,
                (select po_type from purchase_order_type where id in (select type_of_po from kw_purchase_requisition where id in (select kw_purchase_requisition_id from kw_rfq_po_rel where purchase_order_id = p.id))) as in_house,
                (select string_agg(name,', ') from hr_department where id in (select indenting_department from kw_purchase_requisition where id in (select kw_purchase_requisition_id from kw_rfq_po_rel where purchase_order_id = p.id))) as department_name,
                (select string_agg(price_unit::character varying,', ') from purchase_order_line where order_id = p.id) as unit_price,
				(select string_agg(at.name,', ') from purchase_order p  join purchase_order_line pl on p.id = pl.order_id join 
				account_tax_purchase_order_line_rel ptr on ptr.purchase_order_line_id = pl.id join account_tax at on ptr.account_tax_id = at.id) taxes_id,
                (select name from res_partner where id = p.id) as vendor,
                (select string_agg(u.name,', ') from uom_uom u join purchase_order_line l on u.id = l.product_uom where l.order_id = p.id ) as unit_of_measure ,
                (select string_agg(project_code,', ') 
                 FROM kw_purchase_requisition 
                 WHERE id IN (SELECT kw_purchase_requisition_id 
                              FROM kw_rfq_po_rel 
                              WHERE purchase_order_id = p.id)) as workorder_code
		    from purchase_order p  group by p.id
        )""" % (self._table))


        