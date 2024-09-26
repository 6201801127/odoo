from odoo import models, fields, api, _
from datetime import date
import requests, json

class AccountingDataSync(models.Model):
    
    _name = "kw_accounting_sync_data"
    _description = "Kw Accounting Data Sync Schedulers"


    def create_other_voucher_details(self):
        others_voucher_url = self.env.ref('kw_accounting.v5_accounting_other_vouchers_details').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        data = json.dumps({})
        resp_result = requests.post(others_voucher_url, headers=header, data=data)
        resp = json.loads(resp_result.text)
        if resp:
            try:
                for acc_data in resp:
                    voucherDetails,voucherLineItemDetails = [],[]
                    voucherType = acc_data['Vch_VoucherNo'].split('-')[0] if acc_data['Vch_VoucherNo'] else None
                    move_type = 'receipt' if voucherType == 'RV' else 'payment' if voucherType == 'PV' else 'general' if voucherType == 'JV' else 'contra'
                    date = acc_data['DtmTransDate'] if 'DtmTransDate' in acc_data else None
                    
                    branch_name = acc_data['Branch']
                    branch_name = 'c1' if branch_name == "C1-CSMPL" else 'csmpl'
                    branch = self.env['accounting.branch.unit'].sudo().search([('code', '=', branch_name)], limit=1)
                    branch_id = branch.id if branch else None
                    payment_method = acc_data['Vchpaymode'] if 'Vchpaymode' in acc_data else None
                    # cheque_date = datetime.strptime(acc_data['DtmCheckDate'], '%Y-%m-%d').date() if acc_data['DtmCheckDate'] else None,
                    cheque_date = None if acc_data['DtmCheckDate'] == '' else acc_data['DtmCheckDate']
                    cheque_reference = acc_data['Vch_CheckNo'] if 'Vch_CheckNo' in acc_data else ''
                    if move_type == 'receipt' and acc_data['Transmode'] == 'Cash':
                        code = 'RVCSH'
                    elif move_type == 'receipt' and acc_data['Transmode'] == 'Bank':
                        code = 'RVBNK'
                    elif move_type == 'payment' and acc_data['Transmode'] == 'Cash':
                        code = 'PVCSH'
                    elif move_type == 'payment' and acc_data['Transmode'] == 'Bank':
                        code = 'PVBNK'
                    elif move_type == 'general':
                        code = 'MISC'
                    elif move_type == 'contra':
                        code = 'CV'
                        
                    journal_id = self.env['account.journal'].search([('code', 'in',[code])], limit=1)
                    narration = acc_data['VchNotes'] if 'VchNotes' in acc_data else ''
                    
                    if acc_data['VoucherDetails']:
                        for line in acc_data['VoucherDetails']:
                            budget_type = line['BudgetType'] or None
                            department_id = self.env['hr.department'].search([('kw_id','=',int(line['Dept']))],limit=1)
                            employee_id = self.env['hr.employee'].search([('kw_id','=',int(line['EmpKwID']))],limit=1)
                            account_id = self.env['account.account'].search([('kw_ledger_code','=',line['VchLedgerCode'])],limit=1)
                            project_id = self.env['kw_sales_workorder_master'].search([('kw_wo_id','=',int(line['kw_wo_id']))],limit=1)
                            voucherLineItemDetails.append({
                                'budget_type': budget_type,
                                'department_id': department_id.id if department_id else None,
                                'employee_id': employee_id.id if employee_id else None,
                                'debit': float(line['Amt']) if line['TransMode'] == 'debit' else 0.0,
                                'credit': float(line['Amt']) if line['TransMode'] == 'credit' else 0.0,
                                'account_id': account_id.id,
                                'project_id': project_id.id if project_id else None,
                            })
                            
                    
                    voucherDetails.append({
                        'move_type' : move_type, 'date' : date, 'journal_id': journal_id.id, 'branch_id' : branch_id, 'payment_method_type': payment_method, 
                        'cheque_date': cheque_date, 'cheque_reference': cheque_reference, 'narration' : narration,
                        'kw_voucher_no' : acc_data['Vch_VoucherNo'],
                        'line_ids' : [[0,0,line_item] for line_item in voucherLineItemDetails]
                    })
                    
                    
                    account_move = self.env['account.move']
                    exist_move = account_move.search([('kw_voucher_no','=',acc_data['Vch_VoucherNo'])],limit=1)
                    if exist_move:
                        account_move.sudo().write(voucherDetails)
                    else:
                        account_move.sudo().create(voucherDetails)
                return {
                    'status': 200,
                    'error': 0,
                    'sync_status': 1
                }
            except Exception as e:
                self.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'Accounting Voucher Integration',
                    'error_log': e,
                    'response_result': resp,
                    'request_params': others_voucher_url,
                })
                return {'error': str(e), 'status': 500,'Reference ID': acc_data['Vch_VoucherNo'], 'sync_status': 0}
            
    def create_purchase_voucher_details(self):
        purchase_sale_voucher_url = self.env.ref('kw_accounting.v5_accounting_purchase_vouchers_details').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        data = json.dumps({})
        resp_result = requests.post(purchase_sale_voucher_url, headers=header, data=data)
        resp = json.loads(resp_result.text)
        if resp:
            try:
                for acc_data in resp:
                    voucherDetails,voucherLineItemDetails,VoucherProductDetls = [],[],[]
                    voucherType = acc_data['Vch_VoucherNo'].split('-')[0] if acc_data['Vch_VoucherNo'] else None
                    type = 'out_invoice' if voucherType == 'SV' else 'in_invoice'
                    date = acc_data['DtmTransDate'] if 'DtmTransDate' in acc_data else None
                    reference_number = acc_data['VchInvNo']

                    branch_name = acc_data['Branch']
                    branch_name = 'c1' if branch_name == "C1-CSMPL" else 'csmpl'
                    branch = self.env['accounting.branch.unit'].sudo().search([('code', '=', branch_name)], limit=1)
                    branch_id = branch.id if branch else None
                    date_invoice = acc_data['DtmInvDate'] if 'DtmInvDate' in acc_data else None
                    date_due = None if acc_data['duedate'] == '' else acc_data['duedate']
                    
                    partner_id = self.env['res.partner'].search(['|',('property_account_payable_id.kw_ledger_code','=',acc_data['VchPartnrlegCoe']),('property_account_receivable_id.kw_ledger_code','=',acc_data['VchPartnrlegCoe'])],limit=1) 
                    narration = acc_data['VchNotes'] if 'VchNotes' in acc_data else ''
                    
                    if acc_data['VoucherDetails']:
                        for line in acc_data['VoucherDetails']:
                            if line['VchLedgerCode'] != acc_data['VchPartnrlegCoe']:
                                budget_type = line['BudgetType'] or None
                                department_id = self.env['hr.department'].search([('kw_id','=',int(line['Dept']))],limit=1)
                                employee_id = self.env['hr.employee'].search([('kw_id','=',int(line['EmpKwID']))],limit=1)
                                account_id = self.env['account.account'].search([('kw_ledger_code','=',line['VchLedgerCode'])],limit=1)
                                project_id = self.env['kw_sales_workorder_master'].search([('kw_wo_id','=',int(line['kw_wo_id']))],limit=1)
                                voucherLineItemDetails.append({
                                    'budget_type': budget_type,
                                    'department_id': department_id.id if department_id else '',
                                    'employee_id': employee_id.id if employee_id else '',
                                    'mode': line['TransMode'] if line['TransMode']  else ' ',
                                    'transaction_amount': float(line['Amt']) if line['Amt'] else 0.0,
                                    'account_id': account_id.id if account_id else None,
                                    'project_id': project_id.id if project_id else None,
                                    'price_unit': 1.00,
                                    'quantity': 1
                                })
                    if acc_data['ProductLnItem']:
                        for product_line in acc_data['ProductLnItem']:
                            product_id = self.env['product.product'].search([('default_code','=',product_line['ProductName'])],limit=1)
                            VoucherProductDetls.append({
                                'product_category': product_line['Category'] or None ,
                                'product_id': product_id.id or None,
                                'hsn_code':  product_line['HSNSAC'] if product_line['HSNSAC']  else ' ',
                                'quantity':  product_line['Quantity'] if product_line['Quantity']  else 0,
                                'rate':  product_line['Rate'] if product_line['Rate']  else 0,
                                'price_unit':  product_line['BaseAmount'] if product_line['BaseAmount']  else 0 ,
                                'cgst_per':  product_line['CGSTPer'] if product_line['CGSTPer']  else ' ' ,
                                'cgst_amount': float( product_line['CGSTAmount']) if product_line['CGSTAmount']  else  0.0,
                                'sgst_per':  product_line['SGSTPer'] if product_line['SGSTPer']  else ' ',
                                'sgst_amount': float( product_line['SGSTAmount']) if product_line['SGSTAmount']  else  0.0 ,
                                'igst_per':  product_line['IGSTPer'] if product_line['IGSTPer']  else ' ' ,
                                'igst_amount': float( product_line['IGSTAmount']) if product_line['IGSTAmount']  else  0.0,
                                'amount':  float(product_line['TotalAmount']) if product_line['TotalAmount']  else 0.0,
                                'rcm_applicable': True if product_line['RcmApp'] == '1' else False,
                                'itc_applicable': True if product_line['ItcApp'] == '1' else False,
                            })
                            
                    voucherDetails.append({
                        'type' : type, 'reference_number': reference_number, 'partner_id' : partner_id.id,
                        'date' : date,'date_invoice':date_invoice, 'date_due': date_due,
                        'unit_id' : branch_id, 
                        'comment' : narration,
                        'kw_voucher_no' : acc_data['Vch_VoucherNo'],
                        
                        'invoice_line_ids' : [[0,0,line_item] for line_item in voucherLineItemDetails],
                        'product_line_ids' : [[0,0,product_line_item] for product_line_item in VoucherProductDetls]
                        
                    })
                    
                    
                    account_invoice = self.env['account.invoice']
                    exist_invoice = account_invoice.search([('kw_voucher_no','=',acc_data['Vch_VoucherNo'])],limit=1)
                    if exist_invoice:
                        account_invoice.sudo().write(voucherDetails)
                    else:
                        account_invoice.sudo().create(voucherDetails)
                return {
                    'status': 200,
                    'error': 0,
                    'sync_status': 1
                }
            except Exception as e:
                self.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'Sales/Purchase Voucher Integration',
                    'error_log': e,
                    'response_result': resp,
                    'request_params': purchase_sale_voucher_url,
                })
                return {'error': str(e), 'status': 500,'Reference ID': acc_data['Vch_VoucherNo'], 'sync_status': 0}
            
    def create_client_details(self):
        v5_client_data_url = self.env.ref('kw_accounting.v5_accounting_customer_details').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        data = json.dumps({})
        resp_result = requests.post(v5_client_data_url, headers=header, data=data)
        resp = json.loads(resp_result.text)
        if resp:
            try:
                for client_data in resp:
                    # kw_id = client_data['Kw_customr_id']
                    name = client_data['vch_CustomerName']
                    intRefLedgerId = client_data['intRefLedgerId']
                    street = client_data['nvch_ClientAddress']
                    city = client_data['vch_City']
                    vendor_code = client_data['vch_ClientCode']
                    vch_ClientType1 = client_data['vch_ClientType1']
                    country_name = client_data['vch_Country']
                    country = self.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
                    state_name = client_data['vch_State']
                    state = self.env['res.country.state'].sudo().search([('name', '=', state_name)], limit=1)
                    vch_FaxNo = client_data['vch_FaxNo']
                    vat = client_data['vch_GstNo']
                    mobile = client_data['vch_MobNo']
                    pan = client_data['vch_Panno']
                    vch_RefLedCode = client_data['vch_RefLedCode']
                    phone_code = client_data['vch_TelCode']
                    phone_no = client_data['vch_TelNo']
                    website = client_data['vch_WebAddress']
                    email = client_data['vch_email']
                    vchclienttype = client_data['vchclienttype']
                    phone = '(' + str(phone_code) + ')-' + str(phone_no)
                    ClientDetails = {
                        'kw_id' : client_data['Kw_customr_id'], 
                        'name' : name ,
                        'website' : website if website else None,
                        'street' : street if street else None,
                        'city' : city if city else None,
                        'state_id' : state.id if state else None,
                        'country_id' : country.id if country else None, 
                        'phone' : phone if phone else None,
                        'mobile' : mobile if mobile else None,
                        'email':email if email else None,
                        'pan':pan if pan else None, 
                        'vat' : vat if vat else None,
                        'customer':True,
                    }
                    
                    res_partner = self.env['res.partner']
                    old_partner = res_partner.sudo().search([('kw_id','=',client_data['Kw_customr_id']),('customer','=',True)])
                    if old_partner:
                        res_partner.sudo().write(ClientDetails)
                    else:
                        res_partner.sudo().create(ClientDetails)
                        
                return {
                    'status': 200,
                    'error': 0,
                    'sync_status': 1
                }
            except Exception as e:
                self.env['kw_kwantify_integration_log'].sudo().create({
                    'name': 'Sales/Purchase Voucher Integration',
                    'error_log': e,
                    'response_result': resp,
                    'request_params': v5_client_data_url,
                })
                return {'error': str(e), 'status': 500,'Reference ID': client_data['Kw_customr_id'], 'sync_status': 0}