# -*- coding: utf-8 -*-
from odoo import http
from io import StringIO
import xlsxwriter
from odoo.http import request

class AccountingRevenueBudget(http.Controller):
    @http.route('/download-xls-format/', type='http', auth='user')
    def generate_xls(self):
        workbook = xlsxwriter.Workbook('/tmp/data.xlsx')
        worksheet = workbook.add_worksheet('Data')
        row_num = 0
        columns = ['name_of_expenses', 'expense_type', 'apr_budget','may_budget','jun_budget','jul_budget','aug_budget','sep_budget','oct_budget','nov_budget','dec_budget','jan_budget','feb_budget','mar_budget','remark']
        for col_num, column in enumerate(columns):
            worksheet.write(row_num, col_num, column)
        workbook.close()
        with open('/tmp/data.xlsx', 'rb') as f:
            xlsx_data = f.read()
        return request.make_response(
            xlsx_data,
            headers=[
                ('Content-Disposition', 'attachment; filename="Budget Line.xlsx"'),
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            ]
        )
        

    # @http.route('/budget/revenue_expenses_panel', auth='user', type='json')
    # def get_panel_data(self):
    #     # january_income = request.env['revenue_budget_expense_report'].search([('account_id.group_type.code', '=', '3')])
    #     # january_expenses = request.env['revenue_budget_expense_report'].search([('account_id.group_type.code', '=', '4')])
    #     # net_profit_january = sum(january_income.mapped('january_actual')) - sum(january_expenses.mapped('january_actual'))
    #     total_income = request.env['revenue_budget_expense_report'].search([('account_id.group_type.code','=','3')])
    #     total_expenses = request.env['revenue_budget_expense_report'].search([('account_id.group_type.code','=','4')])
    #     net_profit =  sum(total_income.mapped('actual_amount'))-sum(total_expenses.mapped('actual_amount'))
    #     vals = {'total_income': sum(total_income.mapped('actual_amount')),
    #     'total_expenses': sum(total_expenses.mapped('actual_amount')),
    #     'net_profit':net_profit
    #     }
    #     return {
    #             'html':request.env.ref('kw_budget.budget_expenses_template').render({
    #             'object': request.env['revenue_budget_expense_report'],
    #             'values': vals
    #         })
    #     }
        


        