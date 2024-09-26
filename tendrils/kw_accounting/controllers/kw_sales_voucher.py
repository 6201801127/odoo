from datetime import datetime
import json

from odoo import http
from odoo.http import request


class SalesVoucherAPI(http.Controller):
    @http.route('/get_v5_kw_sales_voucher/', methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def get_v5_kw_sales_voucher(self, **args):
        try:
            if args and 'sales_voucher_api_data' in args:
                sales_voucher_data = args['sales_voucher_api_data']
                kw_invoice_id = sales_voucher_data.get('invoice_kw_id', '')

                # Check Existing Invoice Record Achi ki nahi
                existing_invoice = request.env['account.invoice'].sudo().search([('invoice_kw_id', '=', kw_invoice_id)], limit=1)

                if existing_invoice:
                    # If  invoice re kw_invoice_id  thiba thn  write operation haba
                    existing_invoice.write({
                        'date_invoice': sales_voucher_data.get('date_invoice', ''),
                        'date_due': sales_voucher_data.get('date_due', ''),
                        'comment': sales_voucher_data.get('comment', ''),
                        'sync_status': sales_voucher_data.get('sync_status', ''),
                    })

                    # Update kariba existing invoice lines ku
                    if 'InvLineItemList' in sales_voucher_data:
                        inv_line_items = sales_voucher_data['InvLineItemList']
                        for line_data in inv_line_items:

                            project_args_id = line_data.get('kw_wo_id',False)
                            project_id = request.env['kw_project_budget_master_data'].search([('kw_wo_id','=',int(project_args_id))])
                            # To get account_id from Account Name
                            account_name = line_data.get('ledcode', '')
                            ledger_account = request.env['account.account'].sudo().search([('kw_ledger_code', '=', account_name)], limit=1)
                            account_id = ledger_account.id if ledger_account else None
                            department_name = line_data.get('department_id', '')
                            department = request.env['hr.department'].sudo().search([('name', '=', department_name)], limit=1)
                            department_id = department.id if department else None
                            # To get employee_id from Employee kw_id
                            employee_kw_id = line_data.get('employee_id', '')
                            emp_kw_id = request.env['hr.employee'].sudo().search([('kw_id', '=', employee_kw_id)], limit=1)
                            employee_id = emp_kw_id.id if emp_kw_id else None
                            invoice_line_data = {
                                'budget_type': line_data.get('budget_type', ''),
                                'account_id': account_id ,
                                'employee_id': employee_id,
                                'mode': line_data.get('mode', 'credit'),
                                'price_unit': 1,
                                'quantity': line_data.get('quantity', 1),
                                'transaction_amount': line_data.get('transaction_amount', 0.00),
                                'project_wo_id': project_id.id if project_id else None,
                                'department_id': project_id.sbu_id.representative_id.department_id.id,
                                'division_id': project_id.sbu_id.representative_id.division.id,
                                'section_id': project_id.sbu_id.representative_id.section.id,
                            }

                            existing_invoice_line = request.env['account.invoice.line'].sudo().search([
                                ('invoice_id', '=', existing_invoice.id),
                            ], limit=1)

                            existing_invoice_line.write(invoice_line_data)

                    # Update kariba existing product lines ku
                    if 'ProductDetls' in sales_voucher_data:
                        product_details = sales_voucher_data['ProductDetls']
                        for product_data in product_details:
                            # To get product_id from Product name
                            product_name = product_data.get('product_id', '')
                            product = request.env['product.product'].sudo().search([('default_code', '=', product_name)], limit=1)
                            product_id = product.id if product else None
                            product_line_data = {
                                'product_category': product_data.get('product_category', ''),
                                'product_id': product_id,
                                'hsn_code': product_data.get('hsn_code', ''),
                                'quantity': product_data.get('quantity', 0),
                                'rate': product_data.get('rate', 0.00),
                                'price_unit': product_data.get('price_unit', 0.00),
                                'cgst_per': product_data.get('cgst_per', '0'),
                                'cgst_amount': product_data.get('cgst_amount', 0.00),
                                'sgst_per': product_data.get('sgst_per', '0'),
                                'sgst_amount': product_data.get('sgst_amount', 0.00),
                                'igst_per': product_data.get('igst_per', '0'),
                                'igst_amount': product_data.get('igst_amount', 0.00),
                                'amount': product_data.get('amount', 0.00),
                            }

                            existing_product_line = request.env['account.product.line'].sudo().search([
                                ('invoice_id', '=', existing_invoice.id),
                            ], limit=1)

                            existing_product_line.write(product_line_data)

                    return {
                        'status': 200,
                        'sales_voucher_id': existing_invoice.id,
                        'invoice_kw_id': kw_invoice_id,
                        'reference_number': existing_invoice.reference_number,
                        'error': 0,
                        'sync_status': 1
                    }
                else:
                    # If  invoice re kw_invoice_id na thiba thn  create operation haba
                    state_gst = sales_voucher_data.get('State_GstIn', '') 
                    state_gstin_id = request.env['state_gstin'].sudo().search([('gstin_no', '=', state_gst)], limit=1)
                    partner_name = sales_voucher_data.get('ptnrledcode', '')
                    partner = request.env['res.partner'].sudo().search(['|',('property_account_payable_id.kw_ledger_code','=',partner_name),('property_account_receivable_id.kw_ledger_code','=',partner_name)],limit=1) 
                    kw_unit_name = sales_voucher_data.get('unit_id', '')
                    unit_name = 'C1' if kw_unit_name=="C1-CSMPL" else 'CSMPL'
                    unit = request.env['accounting.branch.unit'].sudo().search([('name', '=', unit_name)], limit=1)
                    unit_id = unit.id if unit else None
                    invoice_line_data,product_line_data = [],[]
                    
                    if 'InvLineItemList' in sales_voucher_data:
                        inv_line_items = sales_voucher_data['InvLineItemList']
                        for line_data in inv_line_items:
                            if line_data['ledgcode'] != sales_voucher_data['ptnrledcode']:
                                account_name = line_data.get('ledgcode', '')
                                ledger_account = request.env['account.account'].sudo().search([('kw_ledger_code', '=', account_name)], limit=1)
                                account_id = ledger_account
                                department_name = line_data.get('department_id', False)
                                department = request.env['hr.department'].sudo().search([('name', '=', department_name)], limit=1)
                                department_id = department.id if department else None
                                employee_kw_id = line_data.get('employee_id', False)
                                emp_kw_id = request.env['hr.employee'].sudo().search([('kw_id', '=', employee_kw_id)], limit=1)
                                employee_id = emp_kw_id.id if emp_kw_id else None
                                project_id = request.env['kw_project_budget_master_data'].search([('kw_wo_id','=',int(line_data['kw_wo_id']))],limit=1)
                                
                                invoice_line_data.append({
                                    'budget_type': 'project' if account_id.tds == False else 'other',
                                    'account_id': account_id.id,
                                    'employee_id': employee_id,
                                    'mode': line_data.get('mode', 'credit'),
                                    'price_unit': 1,
                                    'quantity': line_data.get('quantity', 1),
                                    'transaction_amount': line_data.get('transaction_amount', 0.00),
                                    'project_wo_id': project_id.id if project_id else None,
                                    'department_id': project_id.sbu_id.representative_id.department_id.id,
                                    'division_id': project_id.sbu_id.representative_id.division.id,
                                    'section_id': project_id.sbu_id.representative_id.section.id,

                                })

                            # request.env['account.invoice.line'].sudo().create({
                            #     'invoice_id': sales_voucher.id,
                            #     **invoice_line_data
                            # })

                    if 'ProductDetls' in sales_voucher_data:
                        product_details = sales_voucher_data['ProductDetls']
                        for product_data in product_details:
                            product_name = product_data.get('product_id', '')
                            product = request.env['product.product'].sudo().search([('name', '=', product_name)], limit=1)
                            product_id = product.id if product else None
                            product_line_data.append({
                                'product_category': product_data.get('product_category', ''),
                                'product_id': product_id,
                                'hsn_code': product_data.get('hsn_code', ''),
                                'quantity': product_data.get('quantity', 0),
                                'rate': product_data.get('rate', 0.00),
                                'price_unit': product_data.get('price_unit', 0.00),
                                'cgst_per': product_data.get('cgst_per', '0'),
                                'cgst_amount': product_data.get('cgst_amount', 0.00),
                                'sgst_per': product_data.get('sgst_per', '0'),
                                'sgst_amount': product_data.get('sgst_amount', 0.00),
                                'igst_per': product_data.get('igst_per', '0'),
                                'igst_amount': product_data.get('igst_amount', 0.00),
                                'amount': product_data.get('amount', 0.00),
                            })

                            # request.env['account.product.line'].sudo().create({
                            #     'invoice_id': sales_voucher.id,
                            #     **product_line_data
                            # })

                    sales_voucher_data_args = {
                        'state_gstin_id' : state_gstin_id.id if state_gstin_id else None,
                        'reference_number': sales_voucher_data.get('reference_number', ''),
                        'partner_id': partner.id if partner else None,
                        'date': datetime.strptime(sales_voucher_data.get('DtmTransDate'),'%Y-%m-%d').date() if sales_voucher_data.get('DtmTransDate') else None,
                        'date_invoice':datetime.strptime(sales_voucher_data.get('date_invoice'),'%Y-%m-%d').date() if sales_voucher_data.get('date_invoice') else None,
                        'date_due': datetime.strptime(sales_voucher_data.get('date_due'),'%Y-%m-%d').date() if sales_voucher_data.get('date_due')  else None,
                        'unit_id': unit_id,
                        'comment': sales_voucher_data.get('comment', ''),
                        'sync_status': sales_voucher_data.get('sync_status', ),
                        'invoice_kw_id': kw_invoice_id,
                        'kw_voucher_no' : sales_voucher_data['vch_voucherno'],
                        
                        'invoice_line_ids' : [[0,0,line_item] for line_item in invoice_line_data],
                        'product_line_ids' : [[0,0,product_line_item] for product_line_item in product_line_data]
                    }
                    sales_voucher = request.env['account.invoice'].sudo().create(sales_voucher_data_args)
                    return {
                        'status': 200,
                        'sales_voucher_id': sales_voucher.id,
                        'invoice_kw_id': kw_invoice_id,
                        'reference_number': sales_voucher.reference_number,
                        'error': 0,
                        'sync_status': 1
                    }

            else:
                raise Exception("All required data need")
        except Exception as e:
            request.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'Sales Voucher Integration from .Net',
                    'error_log': e,
                    'response_result': args,
                    'request_params': 'sales_api',
                })
            return {'error': str(e), 'reference_number': 0, 'sync_status': 0}

    @http.route('/get_v5_payment_journal/', methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def get_v5_payment_journal(self, **args):
        
        try:
            if args and 'payment_journal_data' in args:
                payment_journal = args['payment_journal_data']
                kw_payment_journal_id = payment_journal.get('payment_journal_kw_id', '')

                # Check Existing Payment Journal Record Achi ki nahi
                existing_payment_journal = request.env['account.move'].sudo().search([('kw_voucher_no', '=', kw_payment_journal_id)], limit=1)

                if existing_payment_journal:
                    # If  Payment Journal re kw_payment_journal_id  thiba thn  write operation haba
                    # Update kariba existing Payment Journal lines ku
                    if 'JrnlLineItemList' in payment_journal:
                        journal_line_items = payment_journal['JrnlLineItemList']
                        for line_data in journal_line_items:
                            # To get account_id from Account Name
                            account_name = line_data.get('LedgName', '')
                            ledger_account = request.env['account.account'].sudo().search([('kw_ledger_code','=',account_name)],limit=1)
                            account_id = ledger_account.id if ledger_account else None
                            journal_line_items = {
                                'budget_type': line_data.get('budget_type', ''),
                                'account_id': account_id,
                            }

                            existing_journal_line_items = request.env['account.move.line'].sudo().search([
                                ('move_id', '=', existing_payment_journal.id),
                            ], limit=1)

                            existing_journal_line_items.write(journal_line_items)

                    
                    return {
                        'status': 200,
                        'Payment Journal ID': existing_payment_journal.id,
                        'kw_payment_journal_id': kw_payment_journal_id,
                        'error': 0,
                        'sync_status': 1
                    }
                else:
                    # If  Payment Journal re kw_payment_journal_id na thiba thn  create operation haba
                   
                    code = ''
                    kw_branch_name = payment_journal.get('branch_id')
                    branch_name = 'c1' if kw_branch_name=="C1-CSMPL" else 'csmpl'
                    branch = request.env['accounting.branch.unit'].sudo().search([('code', '=', branch_name)], limit=1)
                    branch_id = branch.id if branch else None
                    if payment_journal.get('Tranmode') == 'Cash':
                        code = 'RVCSH'
                    elif payment_journal.get('Tranmode') == 'Bank':
                        code = 'RVBNK'
                    journal_id = request.env['account.journal'].sudo().search([('code', 'in',[code])], limit=1)
                    
                    journal_line_items_data = []
                    if 'JrnlLineItemList' in payment_journal:
                        journal_line_items = payment_journal['JrnlLineItemList']
                        for line_data in journal_line_items:
                            # budget_type = line_data['budget_type'] or 'other'
                            account_id = request.env['account.account'].sudo().search([('kw_ledger_code','=',line_data['ledgcode'])],limit=1)
                            project_id = request.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',int(line_data.get('kw_wo_id',False)))],limit=1)
                            
                            journal_line_items_data.append({
                                'budget_type': 'project' if account_id.tds == False else 'other',
                                'department_id': project_id.sbu_id.representative_id.department_id.id,
                                'division_id': project_id.sbu_id.representative_id.division.id,
                                'section_id': project_id.sbu_id.representative_id.section.id,
                                'project_wo_id': project_id.id if project_id else None,
                                'account_id': account_id.id ,
                                'debit': abs(float(line_data.get('transaction_amount'))) if line_data.get('mode') == 'debit' else 0.0,
                                'credit': abs(float(line_data.get('transaction_amount'))) if line_data.get('mode') == 'credit' else 0.0,
                            })
                    
                    payment_journal_data_args = {
                        'move_type': 'receipt',
                        'date': datetime.strptime(payment_journal.get('TDate'), '%Y-%m-%d').date() if payment_journal.get('TDate') else None,
                        'payment_method_type': payment_journal.get('payment_method_type', ''),
                        'cheque_date': datetime.strptime(payment_journal.get('cheque_date'), '%Y-%m-%d').date() if payment_journal.get('cheque_date') else None,
                        'cheque_reference': payment_journal.get('vchChequeNo', ''),
                        'journal_id': journal_id.id,
                        'branch_id': branch_id,
                        'narration': payment_journal.get('comment', ''),
                        'kw_voucher_no':payment_journal.get('payment_journal_kw_id', ''),
                        # 'sync_status': payment_journal.get('sync_status', ''),
                        'line_ids' : [[0,0,line_item] for line_item in journal_line_items_data]
                    }
                    
                    account_move = request.env['account.move'].sudo().create(payment_journal_data_args)

                    return {
                        'status': 200,
                        'Payment Journal ID': account_move.id,
                        'kw_payment_journal_id': kw_payment_journal_id,
                        'error': 0,
                        'sync_status': 1
                    }

            else:
                raise Exception("Unbale to get API data")
        except Exception as e:
            request.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'Collection Voucher Integration',
                    'error_log': e,
                    'response_result': args,
                    'request_params': 'collection_api',
                })
            return {'error': str(e), 'Payment Journal ID': kw_payment_journal_id, 'sync_status': 0}
        
        
        
    @http.route('/get_v5_new_customer_details/', methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def get_v5_customers(self, **args):
        try:
            if args and 'v5_customer_details' in args:
                customer_data = args['v5_customer_details']
                country = customer_data.get('VchCountry', '') 
                country_id = request.env['res.country'].sudo().search([('name', '=',country)], limit=1)
                state = customer_data.get('VchState', '') 
                state_id = request.env['res.country.state'].sudo().search([('name', '=',state)], limit=1)
                
                customer_details_data = {
                    'name' : customer_data.get('ClientFullName', ''),
                    'vendor_code' : customer_data.get('ClientShortname', ''),
                    'vat' : customer_data.get('GSTIN', ''),
                    'phone' : customer_data.get('OfficeLandlineNo', ''),
                    'mobile' : customer_data.get('OfficeLandMobno', ''),
                    'website' : customer_data.get('WebAddress', ''),
                    'email' : customer_data.get('EmailID', ''),
                    'country_id' :country_id.id if country_id else None,
                    'state_id' :state_id.id if state_id else None,
                    'city' : customer_data.get('vchCity', ''),
                    'street' : customer_data.get('vchClientAddress', ''),
                    'customer':True,
                    
                    
                   
                }
                customer = request.env['res.partner'].sudo().create(customer_details_data)
                return {
                    'status': 200,
                    'V6 customer_id': customer.id,
                    'customer_name': customer.name,
                    'V5 IntKwClientID':customer_data.get('IntKwClientID'),
                    'error': 0,
                    'sync_status': 1
                }

            else:
                raise Exception("Invalid API Data.")
        except Exception as e:
            request.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'New Customer Details from Kwantify V5',
                    'error_log': e,
                    'response_result': args,
                    'request_params': 'Customer API',
                })
            return {'error': str(e), 'V5 IntKwClientID':customer_data.get('IntKwClientID'), 'sync_status': 0}
        
        
    @http.route('/get_bg_tracker_data',  csrf=False, type='json', cors='*', auth='public', methods=['POST'])
    def bg_tracker_data_details(self):
        records = request.env['bg_tracker'].sudo().search([])
        data = []
        for record in records:
            lines = []
            for line in record.fd_reference_ids:
                lines.append({
                    'fd_name': line.fd_id.display_name,
                    'fd_start_date': line.fd_start_date.strftime('%Y-%m-%d') if line.fd_start_date else None,
                    'fd_maturity_date': line.fd_maturity_date.strftime('%Y-%m-%d') if line.fd_maturity_date else None,
                    'fd_principal_amt': line.fd_principal_amt,
                    'bg_amount': line.bg_amount,
                })
            data.append({
                'id': record.id,
                'sl_no': record.sl_no,
                'bank_name': record.bank_id.name,
                'bg_number': record.bg_number,
                'bg_date': record.bg_date.strftime('%Y-%m-%d') if record.bg_date else None,
                'bg_amount': record.bg_amount,
                'bg_expenses': record.bg_expenses,
                'bg_expiry_date': record.bg_expiry_date.strftime('%Y-%m-%d') if record.bg_expiry_date else None,
                'claim_date': record.claim_date.strftime('%Y-%m-%d') if record.claim_date else None,
                'bg_purpose': record.bg_purpose,
                'fd_amount': record.fd_amount,
                'wo_number': record.wo_number,
                'wo_name': record.wo_name,
                'wo_code': record.wo_id.code,
                'client_name': record.client_name,
                'project_amount': record.project_amount,
                'csg_head_name': record.csg_head_id.display_name,
                'account_holder_name': record.account_holder_id.display_name,
                'bg_closure_date': record.bg_closure_date.strftime('%Y-%m-%d') if record.bg_closure_date else None,
                'transaction_expiry': record.transaction_expiry.strftime('%Y-%m-%d') if record.transaction_expiry else None,
                'fd_line_ids':lines
                
            })
        return data