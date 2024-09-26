"""

Description: This module contains a model for storing domain bill details.

"""
from datetime import datetime, date, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class KwDomainBillsDetails(models.Model):
    """
    Model class for storing domain bill details.
    """
    _name = "kw_domain_bill_details"
    _description = "Bill Details"
    _rec_name = "domain_name"

    domain_name = fields.Many2one("kw_cr_domain_server_configuration", string="Domain Name", required=True)
    client_name = fields.Char(string="Client Name", related="domain_name.client_name")
    registration_with = fields.Char(string="Registration With", related="domain_name.registration_at.registration_name")
    bill_date = fields.Date(string="Bill Date")
    bill_no = fields.Integer(string="Bill No")
    order_details_ids = fields.One2many("kw_domain_bill", "domain_bill_id", string="Order Details")

    @api.constrains('order_details_ids', 'domain_name')
    def validation_defects(self):
        if not self.order_details_ids.ids:
            raise ValidationError("Warning! Enter at least one order details.")


class KwDomainBill(models.Model):
    """
    Model class for storing domain bills.
    """
    _name = "kw_domain_bill"
    _description = "Bills"
    _rec_name = "domain_server_bill_id"
    _order = "order_date"

    # def _default_financial_yr(self):
    #     today = datetime.today().date()
    #     current_fiscal = self.env['account.fiscalyear'].search(
    #         [('date_start', '<=', today), ('date_stop', '>=', today)])
    #     print("current_fiscal >> ", current_fiscal)
    #     return current_fiscal

    account_head_id = fields.Many2one("kw_account_head_master", string="Account Head")
    fy_year = fields.Many2one("account.fiscalyear", string="Fiscal Year", store=True)
    # , default=_default_financial_yr
    bill_no = fields.Char(string="Bill No")
    domain_bill_id = fields.Many2one("kw_domain_bill_details")
    domain_server_bill_id = fields.Many2one("kw_cr_domain_server_configuration", string="Domain")
    order_date = fields.Date(string="Order Date")
    billed_amount = fields.Float(string="Billed Amount")
    discount = fields.Float(string="Discount")
    approved_amount = fields.Float(string="Approved Amount", compute="calculate_approve_amount", store=True)

    @api.onchange('order_date')
    def _compute_financial_yr(self):
        for rec in self:
            if not rec.order_date:
                rec.fy_year = False
            elif rec.order_date:
                current_fiscal = self.env['account.fiscalyear'].search(
                    [('date_start', '<=', rec.order_date), ('date_stop', '>=', rec.order_date)], limit=1)
                rec.fy_year = current_fiscal if current_fiscal else False

    @api.depends('billed_amount', 'discount')
    def calculate_approve_amount(self):
        for rec in self:
            if rec.billed_amount:
                # if rec.billed_amount and rec.discount and rec.discount > rec.billed_amount:
                #     raise ValidationError("Discount cannot be greater than Bill Amount.")
                # discount_amount = (rec.billed_amount * rec.discount) / 100
                approved_amount = rec.billed_amount - (rec.discount if rec.discount else 0)
                rec.approved_amount = approved_amount

    @api.constrains('billed_amount', 'discount')
    def bill_amount_validate(self):
        for rec in self:
            if rec.billed_amount <= 0:
                raise ValidationError("Billed amount should be greater Zero")
            elif rec.discount < 0:
                raise ValidationError("Discount amount should be greater Zero")
            elif rec.billed_amount and rec.discount and rec.billed_amount <= rec.discount:
                raise ValidationError("Billed amount should be greater than Discount amount.")
