from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError,ValidationError
import re

class PaymentDetails(models.Model):
	_name = 'payment.details'
	_inherit=['mail.thread','mail.activity.mixin']

	pid = fields.Char("PID")
	fin_year = fields.Char("Financial Year")
	tax_amount = fields.Float("Tax Amount")
	arrear = fields.Float("Arrear")
	payment_mode = fields.Char("Payment Mode")
	paid_on = fields.Char("Paid On")
	transaction_ref_no = fields.Char("Transaction reference number")
	challan_no = fields.Char("Challan No")
	receipt_no = fields.Char("Receipt No")
	received_by = fields.Char("Received By")
	ptax_ref_no = fields.Char("Ptax Reference Number")
	remark = fields.Char("Remarks")
	payment_detail_ids = fields.One2many('payment.details.line', 'payment_id', "Payment Details")
	status = fields.Char("Status")
	data_type = fields.Selection([('property', 'Property Tax'), ('other', 'Other')], string="Data Type")
	payment_type = fields.Selection([('direct', 'Direct'), ('revised', 'Revised')], default='direct', string="Payment")


class PaymentDetailsLine(models.Model):
	_name= 'payment.details.line'

	payment_id = fields.Many2one('payment.details', "Payment")
	transaction_date = fields.Char("Transaction Date")
	transaction_id = fields.Char("Transaction ID")
	transaction_amount = fields.Char("Transaction Amount")
	transaction_mode = fields.Char("Transaction Mode")


