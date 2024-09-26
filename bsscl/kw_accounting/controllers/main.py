# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from datetime import date,datetime

import json


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
        
    @http.route('/accounting/bank_reconciliation', auth='user', type='json')
    def get_bank_balance_data(self, **kw):
        ctx_bank_account_ledger_id = request.session.get('bank_reconciliation_ledger_id', False)
        ctx_start_date = request.session.get('start_date', False)
        ctx_end_date = request.session.get('end_date', False)
        reconciled = request.session.get('reconciled',False)
        company_data,bank_data,reconciled_bank_data,bank_balance_data = [],[],[],[]
        if ctx_bank_account_ledger_id:
            company_query = f"(select coalesce(sum(debit),0.0) as debit, coalesce(sum(credit),0.0) as credit from account_move_line where account_id = {int(ctx_bank_account_ledger_id)} and date <= '{ctx_end_date}')"
            request.cr.execute(company_query)
            company_data = request.cr.fetchall()
            
            bank_query = f"(select coalesce(sum(debit),0.0) as debit, coalesce(sum(credit),0.0) as credit from account_move_line where account_id = {int(ctx_bank_account_ledger_id)} and reconciled = False and date >= '{ctx_start_date}' and date <= '{ctx_end_date}')"
            request.cr.execute(bank_query)
            bank_data = request.cr.fetchall()

            bank_query = f"(select coalesce(sum(debit),0.0) as debit, coalesce(sum(credit),0.0) as credit from account_move_line where account_id = {int(ctx_bank_account_ledger_id)} and reconciled = True and date >= '{ctx_start_date}' and date <= '{ctx_end_date}' and clear_date >= '{ctx_start_date}' and clear_date <= '{ctx_end_date}')"
            request.cr.execute(bank_query)
            reconciled_bank_data = request.cr.fetchall()

            bank_balance =  f"(select coalesce(sum(debit),0.0) as debit, coalesce(sum(credit),0.0) as credit from account_move_line where account_id = {int(ctx_bank_account_ledger_id)} and date < '{ctx_start_date}' and reconciled = True)"
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
        if reconciled:
            sum_bank_balance = sum_bank_balance + (reconcile_bank_balance_debit - reconcile_bank_balance_credit)
        vals = {
            'bank': request.env['account.account'].browse(int(ctx_bank_account_ledger_id)).name,
            'date_from': ctx_start_date.strftime("%d-%b-%Y"),
            'date_to': ctx_end_date.strftime("%d-%b-%Y"),
            'company_balance': float("%.2f" % (company_debit_balance - company_credit_balance))  if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_debit_balance': bank_debit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_unreconciled_credit_balance': bank_credit_balance if ctx_bank_account_ledger_id else 0.0,
            'bank_balance' : float("%.2f" % sum_bank_balance)  if ctx_bank_account_ledger_id else 0.0,
            'reconciled': reconciled,
        }
        if 'reconcile' in request.session:
            print('reconcile')
            request.session.pop('reconciled')
        return {
                'html':request.env.ref('kw_accounting.bank_reconcile_bank_balance').render({
                'object': request.env['account.move.line'],
                'vals': vals
            })
        }
            