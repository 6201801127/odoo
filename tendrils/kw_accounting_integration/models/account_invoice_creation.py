# -*- coding: utf-8 -*-

import requests, json
from odoo import models
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AccountInvoiceSynch(models.Model):
	_inherit = 'account.invoice'

	def create_invoices(self):
		account_sync_url = self.env['ir.config_parameter'].sudo().get_param('account.account_sync')
		header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		to_date = date.today()
		day_diff = self.env['ir.config_parameter'].sudo().get_param('account.day_diff')
		from_date = to_date - relativedelta(days=int(day_diff) if day_diff else 1)
		# print("from to date ============",from_date,to_date)
		accountInvoiceDateDict = {
			'FromDt': from_date.strftime('%d-%b-%Y'), #'06-Jan-2021',
			'ToDt': to_date.strftime('%d-%b-%Y') # '06-Feb-2021'
		}
		response = requests.post(account_sync_url + '/RetInvoiceDetails', headers=header, 
									data=json.dumps(accountInvoiceDateDict),verify=False)
		response_data = json.dumps(response.json())
		# print('response_data>>>>>>>>>',response_data)
		data = json.loads(response_data)

		for rec in data:
			invoice_obj = self.env['account.invoice'].sudo().search([('kw_id', '=', rec.get('Invoice_ID'))])
			if not invoice_obj:
				client_obj = self.env['res.partner'].sudo()
				product_obj = self.env['product.product'].sudo()
				journal_obj = self.env['account.journal'].sudo()
				client_id = client_obj.search([('kw_id', '=', int(rec.get('Client_ID')))])
				currency_id = self.env['res.currency'].sudo().search([('name', '=', rec.get('Currency'))])
				employee_id = self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec.get('Sales_PersId')))])
				due_dt = rec.get('Invoice_DueDate').split('-')
				invoice_dt = rec.get('Invoice_Date').split('-')
				
				vals = {
					# '': rec.get('Branch'),
					'currency_id': currency_id.id,
					# '': rec.get('Department') if rec.get('Department') else False,
					'date_invoice': f'{invoice_dt[2]}-{invoice_dt[1]}-{invoice_dt[0]}',
					'date_due': f'{due_dt[2]}-{due_dt[1]}-{due_dt[0]}',
					'kw_id': rec.get('Invoice_ID'),
					'invoice_number': rec.get('Invoice_Number'),
					'reference': rec.get('PaymentRef'),
					'user_id': employee_id.user_id.id if employee_id else False,
					'journal_id': journal_obj.browse(1).id, # Static value
					'invoice_line_ids': [[0, 0, {
						'product_id': product_obj.search([('kw_id', '=', int(r.get('Product')))]).id,
						'name': product_obj.search([('kw_id', '=', int(r.get('Product')))]).default_code.strip(),
						'account_id': journal_obj.browse(1).default_credit_account_id.id, # Static value
						'quantity': r.get('Quantity'),
						'price_unit': r.get('Price'),
					}] for r in rec.get('ZInvDtls')]
				}

				if client_id:
					vals['partner_id'] = client_id.id
				else:
					new_client_id = client_obj.create({
									'name': rec.get('Client_Name'),
									'kw_id': rec.get('Client_ID')
									})
					vals['partner_id'] = new_client_id.id
				self.env['account.invoice'].sudo().create(vals)
		return True

