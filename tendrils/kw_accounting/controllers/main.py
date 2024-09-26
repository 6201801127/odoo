# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from datetime import date,datetime
import xlsxwriter

import json

class HrLoan(http.Controller):
    @http.route('/download-xls-format-loan/', type='http', auth='user')
    def generate_xls(self):
        workbook = xlsxwriter.Workbook('/tmp/data.xlsx')
        worksheet = workbook.add_worksheet('Data')
        row_num = 0
        columns = ['SL No', 'Date', 'Principal Recd.', 'Principal Paid', 'Interest Paid']
        for col_num, column in enumerate(columns):
            worksheet.write(row_num, col_num, column)
        workbook.close()
        with open('/tmp/data.xlsx', 'rb') as f:
            xlsx_data = f.read()
        return request.make_response(
            xlsx_data,
            headers=[
                ('Content-Disposition', 'attachment; filename="Loan Line.xlsx"'),
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            ]
        )

class FinancialReportController(http.Controller):

    @http.route('/account_reports', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report(self, model, options, output_format, token, financial_id=None, **kw):
        uid = request.session.uid
        report_obj = request.env[model].sudo(uid)
        options = json.loads(options)
        if financial_id and financial_id != 'null':
            report_obj = report_obj.browse(int(financial_id))
        report_name = report_obj.get_report_filename(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition(report_name + '.xlsx'))
                    ]
                )
                report_obj.get_xlsx(options, response)
            if output_format == 'pdf':
                response = request.make_response(
                    report_obj.get_pdf(options),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition(report_name + '.pdf'))
                    ]
                )
            if output_format == 'xml':
                content = report_obj.get_xml(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', content_disposition(report_name + '.xml')),
                        ('Content-Length', len(content))
                    ]
                )
            if output_format == 'xaf':
                content = report_obj.get_xaf(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', content_disposition(report_name + '.xaf')),
                        ('Content-Length', len(content))
                    ]
                )
            if output_format == 'txt':
                content = report_obj.get_txt(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'text/plain'),
                        ('Content-Disposition', content_disposition(report_name + '.txt')),
                        ('Content-Length', len(content))
                    ]
                )
            if output_format == 'csv':
                content = report_obj.get_csv(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'text/csv'),
                        ('Content-Disposition', content_disposition(report_name + '.csv')),
                        ('Content-Length', len(content))
                    ]
                )
            if output_format == 'zip':
                content = report_obj._get_zip(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/zip'),
                        ('Content-Disposition', content_disposition(report_name + '.zip')),
                    ]
                )
                # Adding direct_passthrough to the response and giving it a file
                # as content means that we will stream the content of the file to the user
                # Which will prevent having the whole file in memory
                response.direct_passthrough = True
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))

class BankReconciliation(http.Controller):  
    @http.route('/accounting/bank_reconciliation', auth='user', type='json')
    def get_bank_balance_data(self, **kw):
        ctx_bank_account_ledger_id = request.session.get('bank_reconciliation_ledger_id', False)
        ctx_start_date = request.session.get('start_date', False)
        ctx_end_date = request.session.get('end_date', False)
        reconciled = request.session.get('reconciled',False)
        company_data,bank_data,reconciled_bank_data,bank_balance_data = [],[],[],[]
        lang = request.env['res.lang']._lang_get(request.env.context.get('lang') or 'en_US')
        currency_id = request.env.user.company_id.currency_id
        fmt = "%.{0}f".format(currency_id.decimal_places)
        
        if ctx_bank_account_ledger_id:
            company_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.date <= '{ctx_end_date}' and am.state = 'posted')"
            request.cr.execute(company_query)
            company_data = request.cr.fetchall()
            
            bank_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where (aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = False and aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and am.state = 'posted') or (aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = True and aml.clear_date > '{ctx_end_date}' and am.state = 'posted'))"
            request.cr.execute(bank_query)
            bank_data = request.cr.fetchall()

            bank_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = True and aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and aml.clear_date >= '{ctx_start_date}' and aml.clear_date <= '{ctx_end_date}' and am.state = 'posted')"
            request.cr.execute(bank_query)
            reconciled_bank_data = request.cr.fetchall()

            bank_balance =  f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.date < '{ctx_start_date}' and aml.reconciled = True and am.state = 'posted')"
            request.cr.execute(bank_balance)
            bank_balance_data = request.cr.fetchall()
        
        for data in company_data:
            company_debit_balance = float("%.2f" % data[0])
            company_credit_balance = float("%.2f" % data[1])
        for data in bank_data:
            bank_debit_balance = float("%.2f" % data[0])
            bank_credit_balance = float("%.2f" % data[1])
        for data in bank_balance_data:
            bank_balance_debit = float("%.2f" % data[0])
            bank_balance_credit = float("%.2f" % data[1])
        for data in reconciled_bank_data:
            reconcile_bank_balance_debit = float("%.2f" % data[0])
            reconcile_bank_balance_credit = float("%.2f" % data[1])
        
        sum_bank_balance = (bank_balance_debit - bank_balance_credit)
        ledger_id = request.env['account.account'].browse(int(ctx_bank_account_ledger_id))
        # if reconciled:
        sum_bank_balance = sum_bank_balance + (reconcile_bank_balance_debit - reconcile_bank_balance_credit)

        reconciled_ids = request.env['account.move.line'].search([('account_id','=',int(ctx_bank_account_ledger_id)),('reconciled','=',True)])

        company_balance = lang.format(fmt, float("%.2f" % (company_debit_balance - company_credit_balance)), grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_unreconciled_debit_balance = lang.format(fmt, bank_debit_balance, grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_unreconciled_credit_balance = lang.format(fmt, bank_credit_balance, grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_balance = lang.format(fmt, float("%.2f" % sum_bank_balance), grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

        vals = {
            'bank': ledger_id.name,
            'date_from': ctx_start_date.strftime("%d-%b-%Y"),
            'date_to': ctx_end_date.strftime("%d-%b-%Y"),
            'company_balance': company_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_debit_balance': bank_unreconciled_debit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_credit_balance': bank_unreconciled_credit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_balance' : bank_balance if reconciled_ids else 0.0,
            'reconciled': reconciled,
        }
        if 'reconcile' in request.session:
            request.session.pop('reconciled')
        return {
                'html':request.env.ref('kw_accounting.bank_reconcile_bank_balance').render({
                'object': request.env['account.move.line'],
                'vals': vals
            })
        }

class BRSReport(http.Controller):  
    @http.route('/accounting/bank_reconciliation/report', auth='user', type='json')
    def get_bank_balance_data(self, **kw):
        ctx_bank_account_ledger_id = request.session.get('report_bank_reconciliation_ledger_id', False)
        ctx_start_date = request.session.get('report_start_date', False)
        ctx_end_date = request.session.get('report_end_date', False)
        reconciled = request.session.get('reconciled',False)
        company_data,bank_data,reconciled_bank_data,bank_balance_data = [],[],[],[]
        lang = request.env['res.lang']._lang_get(request.env.context.get('lang') or 'en_US')
        currency_id = request.env.user.company_id.currency_id
        fmt = "%.{0}f".format(currency_id.decimal_places)
        
        if ctx_bank_account_ledger_id:
            company_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.date <= '{ctx_end_date}' and am.state = 'posted')"
            request.cr.execute(company_query)
            company_data = request.cr.fetchall()
            
            bank_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where (aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = False and aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and am.state = 'posted') or (aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = True and aml.clear_date > '{ctx_end_date}' and am.state = 'posted'))"
            request.cr.execute(bank_query)
            bank_data = request.cr.fetchall()

            bank_query = f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.reconciled = True and aml.date >= '{ctx_start_date}' and aml.date <= '{ctx_end_date}' and aml.clear_date >= '{ctx_start_date}' and aml.clear_date <= '{ctx_end_date}' and am.state = 'posted')"
            request.cr.execute(bank_query)
            reconciled_bank_data = request.cr.fetchall()

            bank_balance =  f"(select coalesce(sum(aml.debit),0.0) as debit, coalesce(sum(aml.credit),0.0) as credit from account_move_line aml left join account_move am on am.id = aml.move_id where aml.account_id = {int(ctx_bank_account_ledger_id)} and aml.date < '{ctx_start_date}' and aml.reconciled = True and am.state = 'posted')"
            request.cr.execute(bank_balance)
            bank_balance_data = request.cr.fetchall()
        
        for data in company_data:
            company_debit_balance = float("%.2f" % data[0])
            company_credit_balance = float("%.2f" % data[1])
        for data in bank_data:
            bank_debit_balance = float("%.2f" % data[0])
            bank_credit_balance = float("%.2f" % data[1])
        for data in bank_balance_data:
            bank_balance_debit = float("%.2f" % data[0])
            bank_balance_credit = float("%.2f" % data[1])
        for data in reconciled_bank_data:
            reconcile_bank_balance_debit = float("%.2f" % data[0])
            reconcile_bank_balance_credit = float("%.2f" % data[1])
        
        sum_bank_balance = (bank_balance_debit - bank_balance_credit)
        ledger_id = request.env['account.account'].browse(int(ctx_bank_account_ledger_id))
        # if reconciled:
        sum_bank_balance = sum_bank_balance + (reconcile_bank_balance_debit - reconcile_bank_balance_credit)

        reconciled_ids = request.env['account.move.line'].search([('account_id','=',int(ctx_bank_account_ledger_id)),('reconciled','=',True)])

        company_balance = lang.format(fmt, float("%.2f" % (company_debit_balance - company_credit_balance)), grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_unreconciled_debit_balance = lang.format(fmt, bank_debit_balance, grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_unreconciled_credit_balance = lang.format(fmt, bank_credit_balance, grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        bank_balance = lang.format(fmt, float("%.2f" % sum_bank_balance), grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

        vals = {
            'bank': ledger_id.name,
            'date_from': ctx_start_date.strftime("%d-%b-%Y"),
            'date_to': ctx_end_date.strftime("%d-%b-%Y"),
            'company_balance': company_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_debit_balance': bank_unreconciled_debit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_credit_balance': bank_unreconciled_credit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_balance' : bank_balance if reconciled_ids else company_balance,
        }
        
        return {
                'html':request.env.ref('kw_accounting.bank_reconcile_bank_balance_report').render({
                'object': request.env['account.move.line'],
                'vals': vals
            })
        }

class BankReconciliationReport(http.Controller):
    @http.route('/accounting/get_session_info', auth='user', type='json')
    def get_bank_balance_data(self, **kw):
        company_id = request.session.get('accounting_company_id', False)
        branch_id = request.session.get('accounting_branch_id', False)
        financial_year_id = request.session.get('accounting_financial_year',False)

        company = request.env['res.company'].browse(company_id).name
        branch = request.env['accounting.branch.unit'].browse(branch_id).name
        financial_year = request.env['account.fiscalyear'].browse(financial_year_id).name

        vals = {
            'company' : company,
            'branch' : branch,
            'financial_year' : financial_year,
        }

        return {
                'html':request.env.ref('kw_accounting.accounting_session_info').render({
                'object': request.env['account.invoice'],
                'vals': vals
            })
        }

class PreviewVouchers(http.Controller):
    @http.route('/accounting/preview_vouchers',auth='user', type="json")
    def preview_voucher(self,**kw):
        session_invoice_id = request.session.get('invoice_id', False)
        invoice_id = request.env['account.invoice'].browse(int(session_invoice_id))
        product_list,ledger_list,tds_list = [],[],[]
        count = 1
        for line in invoice_id.tds_line_ids:
            tds_list.append({
                'nature': line.account_id.nature_of_payment,
                'under_section': line.account_id.under_section,
                'base_amount': line.base_amount,
                'percentage':line.percentage,
                'ds_amount': line.ds_amount,
            })
        for line in invoice_id.invoice_line_ids:
            print(line.budget_line.name_of_expenses,line.budget_line.sequence_ref)
            ledger_list.append({
                'ledger_id' : line.account_id.group_type.name + ' - '+ line.account_id.user_type_id.name + ' - '+line.account_id.group_name.name + ' - '+ line.account_id.account_head_id.name + ' - '+ line.account_id.account_sub_head_id.name,
                'account': line.account_id.name,
                'account_code':  '(' + line.account_id.code+ ')',
                'mode': line.mode,
                'transaction_amount': abs(line.price_subtotal) if line.price_subtotal else 0.0,
                'project' : str(line.project_wo_id.wo_code +' - '+ line.project_wo_id.wo_name) if line.project_wo_id else '',
                'department': line.department_id.name,
                'division': line.division_id.name,
                'section': line.section_id.name,
                'employee': line.employee_id.name,
                'capital_budget': 'Yes' if line.budget_update == True else '',
                'budget_line': "%s (%s)" % (line.budget_line.name_of_expenses or '', line.budget_line.sequence_ref or '') if line.budget_type == 'treasury' else "%s (%s)" % (line.project_line.head_of_expense or '', line.project_line.sequence_ref or '') if line.budget_type == 'project' else "%s (%s)" % (line.capital_line.name_of_expenses or '', line.capital_line.sequence_ref or '') if line.budget_type == 'capital' else '',
                'budget_type': dict(request.env['account.invoice.line'].fields_get(allfields='budget_type')['budget_type']['selection'])[line.budget_type] if line.budget_type else '',
            })
        ledger_list.append({
            'ledger_id': invoice_id.account_id.group_type.name + ' - '+ invoice_id.account_id.user_type_id.name + ' - '+ invoice_id.account_id.group_name.name + ' - '+ invoice_id.account_id.account_head_id.name + ' - '+ invoice_id.account_id.account_sub_head_id.name,
            'account': invoice_id.account_id.name,
            'account_code':  '(' + invoice_id.account_id.code+ ')',
            'mode': 'debit' if (invoice_id.type == 'out_invoice' or invoice_id.type == 'in_refund') else 'credit',
            'transaction_amount': invoice_id.amount_untaxed if invoice_id.amount_untaxed else 0.0,
            'project' : '',
            'department': '',
            'division': '',
            'section': '',
            'employee': '',
            'capital_budget': '',
            'budget_line':'',
            'budget_type' : '',
        })
        for line in invoice_id.product_line_ids:
            product_list.append({
                'sl_no': count,
                'item_name' : line.product_id.name,
                'hsn_code': line.hsn_code,
                'quantity': line.quantity,
                'rate': line.rate,
                'product_category': dict(request.env['account.product.line'].fields_get(allfields='product_category')['product_category']['selection'])[line.product_category] if line.product_category else '',
                'base_amount': line.price_unit,
                'cgst_per': line.cgst_per,
                'cgst_amount': line.cgst_amount,
                'sgst_per': line.sgst_per,
                'sgst_amount': line.sgst_amount,
                'igst_per': line.igst_per,
                'igst_amount': line.igst_amount,
                'amount': line.amount,
                'rcm': 'Yes' if line.rcm_applicable else 'No',
                'itc': 'Yes' if line.itc_applicable else 'No',
            })
            count = count + 1
        vals = {
            'move_type': 'Sales Voucher' if invoice_id.type == 'out_invoice' else 'Credit Note Voucher' if invoice_id.type == 'out_refund' else 'Purchase Voucher' if invoice_id.type == 'in_invoice' else 'Debit Note Voucher',
            'voucher_no' : invoice_id.move_name,
            'customer': invoice_id.partner_id.name,
            'gstin': invoice_id.partner_id.vat,
            'state': invoice_id.partner_id.state_id.name,
            'date': invoice_id.date.strftime("%d-%b-%Y") if invoice_id.date else '',
            'invoice_date': invoice_id.date_invoice.strftime("%d-%b-%Y") if invoice_id.date_invoice else '',
            'product_line': product_list,
            'ledger_line': ledger_list,
            'currency': invoice_id.company_id.currency_id,
            'narration': invoice_id.comment,
            'type': invoice_id.type,
            'company': invoice_id.company_id.name,
            'branch': invoice_id.unit_id.name,
            'voucher_state': invoice_id.state_gstin_id.state_name,
            'gst_treatment': dict(request.env['account.invoice'].fields_get(allfields='l10n_in_gst_treatment')['l10n_in_gst_treatment']['selection'])[invoice_id.l10n_in_gst_treatment] if invoice_id.l10n_in_gst_treatment else '',
            'msme_reg_no': invoice_id.partner_id.msme_reg_no,
            'tan': invoice_id.partner_id.tan,
            'pan': invoice_id.partner_id.pan,
            'invoice_no': invoice_id.reference_number,
            'tds_line': tds_list,
            'purchase_state': invoice_id.state_bill_id,
        }
        return {
                'html':request.env.ref('kw_accounting.preview_vouchers').render({
                'object': request.env['account.invoice'],
                'vals': vals
            })
        }

class PreviewMove(http.Controller):
    @http.route('/accounting/preview_move', auth="user", type="json")
    def preview_voucher(self, **kw):
        session_move_id = request.session.get('move_id', False)
        move_id = request.env['account.move'].browse(int(session_move_id))
        ledger_data,tds_list = [],[]
        for line in move_id.line_ids:
            ledger_data.append({
                'account_id': line.account_id.group_type.name + ' - '+ line.account_id.user_type_id.name + ' - '+line.account_id.group_name.name + ' - '+ line.account_id.account_head_id.name + ' - '+ line.account_id.account_sub_head_id.name,
                'account': line.account_id.name,
                'account_code':  '(' + line.account_id.code+ ')',
                'debit_amount': line.debit,
                'credit_amount' : line.credit,
                'employee': line.employee_id.name,
                'project': str(line.project_wo_id.wo_code +' - '+ line.project_wo_id.wo_name) if line.project_wo_id else '',
                'department': line.department_id.name,
                'division': line.division_id.name,
                'section': line.section_id.name,
                'capital_budget': 'Yes' if line.budget_update == True else '',
                'budget_line': "%s (%s)" % (line.budget_line.name_of_expenses or '', line.budget_line.sequence_ref or '') if line.budget_type == 'treasury' else "%s (%s)" % (line.project_line.head_of_expense or '', line.project_line.sequence_ref or '') if line.budget_type == 'project' else "%s (%s)" % (line.capital_line.name_of_expenses or '', line.capital_line.sequence_ref or '') if line.budget_type == 'capital' else '',
                'budget_type': dict(request.env['account.move.line'].fields_get(allfields='budget_type')['budget_type']['selection'])[line.budget_type] if line.budget_type else '',
            })
        for line in move_id.tds_line_ids:
            tds_list.append({
                'partner': line.partner_id.name,
                'nature': line.account_id.nature_of_payment,
                'under_section': line.account_id.under_section,
                'base_amount': line.base_amount,
                'percentage':line.percentage,
                'ds_amount': line.ds_amount,
            })
        vals = {
            'customer': move_id.partner_id.name,
            'gstin': move_id.partner_id.vat,
            'state': move_id.partner_id.state_id.name,
            'gst_treatment': dict(request.env['res.partner'].fields_get(allfields='l10n_in_gst_treatment')['l10n_in_gst_treatment']['selection'])[move_id.partner_id.l10n_in_gst_treatment] if move_id.partner_id.l10n_in_gst_treatment else '',
            'pan': move_id.partner_id.pan,
            'payment_from': move_id.line_ids.mapped('account_id').filtered(lambda x: x.ledger_type == 'bank').name or '',
            'type' : move_id.move_type,
            'move_type': 'Payment Voucher' if move_id.move_type == 'payment' else 'Receipt Voucher' if move_id.move_type == 'receipt' else 'Contra Voucher' if move_id.move_type == 'contra' else 'General Voucher',
            'company' : move_id.company_id.name,
            'branch': move_id.branch_id.name,
            'voucher_no': move_id.name,
            'date': move_id.date.strftime("%d-%b-%Y") if move_id.date else '',
            'mode_of_payment': move_id.payment_method_type,
            'cheque_no': move_id.cheque_reference,
            'currency': move_id.company_id.currency_id,
            'cheque_date': move_id.cheque_date.strftime("%d-%b-%Y") if move_id.cheque_date else '', 
            'narration': move_id.narration,
            'ledger_data' : ledger_data,
            'tds_list': tds_list,
            'name_type': 'Customer/Vendor' if move_id.partner_id.supplier and move_id.partner_id.customer else 'Customer' if move_id.partner_id.customer else 'Vendor',
        }
        return {
                'html':request.env.ref('kw_accounting.preview_move_vouchers').render({
                'object': request.env['account.move'],
                'vals': vals
            })
        }