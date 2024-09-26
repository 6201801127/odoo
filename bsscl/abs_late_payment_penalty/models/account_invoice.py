# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api,fields,models,_
import odoo.addons.decimal_precision as dp
from datetime import date

#inherit AccountMove class. 
class AccountMove(models.Model):
    _inherit = "account.move"

    penalty_source_invoice = fields.Char('Penalty Source Invoice')
    penalty = fields.Selection([('fixed', 'Penalty Amount'), ('penalty_percentage', 'Penalty Percentage'),],string='Penalty', default='fixed')
    percentage_of_penalty = fields.Float("Penalty Percentage",digits='Account', default=10.0)
    fixed_amount = fields.Float("Penalty Amount",default=200.0)
    
    #create function for late payment penalty. 
    def late_payment_penalty(self):
        invoice_dict = {} 
        invoice_line_dict ={} 
        today_date = date.today()  
        current_date = str(today_date)
        product = self.env.ref('abs_late_payment_penalty.penalty_product')
        ir_property_obj = self.env['ir.property']
        account_invoice_object = self.env['account.move']
        account_invoice_line_object = self.env['account.move.line']
        inc_acc = ir_property_obj._get('property_account_income_categ_id', 'product.category')
        invoice_ids = self.env['account.move'].search([('payment_state', '=', 'not_paid')])
        if invoice_ids: 
            for invoice_id in invoice_ids:
                if invoice_id:  
                    if invoice_id.invoice_date_due == False:
                        continue 
                    elif str(invoice_id.invoice_date_due) < str(current_date):
                        if invoice_id.penalty == 'fixed':
                            invoice_dict = {
                                            'partner_id':invoice_id.partner_id.id,
                                            'invoice_date':today_date,
                                            'move_type':'out_invoice', 
                                            'penalty_source_invoice':invoice_id.name,
                                            'invoice_line_ids':[(0, 0, {
                                                                        'product_id': product.id,
                                                                        'price_unit': invoice_id.fixed_amount,
                                                                        'account_id':inc_acc.id, 
                                                                        'name':'Penalty',
                                                                        })],
                                           }
                            if invoice_dict:  
                                account_invoice_object.create(invoice_dict)
                        if invoice_id.penalty == 'penalty_percentage':  
                            penalty_cal_percentage = (invoice_id.amount_residual * invoice_id.percentage_of_penalty) / 100 
                            invoice_dict = {
                                            'partner_id':invoice_id.partner_id.id,
                                            'invoice_date':today_date,
                                            'move_type':'out_invoice', 
                                            'penalty_source_invoice':invoice_id.name,
                                            'invoice_line_ids':[(0, 0, {
                                                                        'product_id': product.id,
                                                                        'price_unit': penalty_cal_percentage,
                                                                        'account_id':inc_acc.id, 
                                                                        'name':'Penalty',
                                                                        })],
                                           }
                            if invoice_dict: 
                                account_invoice_object.create(invoice_dict)
