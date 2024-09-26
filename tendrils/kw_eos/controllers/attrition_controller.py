from odoo import http
from odoo.http import request

class AttritionDashboard(http.Controller):

    @http.route('/get_available_fiscal_years', type='json', auth='user')
    def get_available_fiscal_years(self):
        print("get_available_fiscal_years called===============================================")
        fiscal_years = request.env['account.fiscalyear'].search([])
        return {'fiscal_years': [fy.name for fy in fiscal_years]}

    # @http.route('/web/dataset/call_kw/kw.attrition.dashboard/get_attrition_by_tenure_data', type='json', auth='user')
    # def get_attrition_by_tenure_data(self, model, method, args, kwargs):
    #     selected_year = args[0] if args else None
    #     selected_quarter = args[1] if len(args) > 1 else None
    #     print("===========================",selected_year,selected_quarter)

    #     domain = [('active', '=', False)]
    #     if selected_year:
    #         fiscal_year = request.env['account.fiscalyear'].search([('name', '=', selected_year)], limit=1)
    #         if fiscal_year:
    #             domain += [('last_working_day', '>=', fiscal_year.date_start), ('last_working_day', '<=', fiscal_year.date_stop)]

    #     if selected_quarter:
    #         quarter_months = {
    #             'Q1': [1, 2, 3],
    #             'Q2': [4, 5, 6],
    #             'Q3': [7, 8, 9],
    #             'Q4': [10, 11, 12],
    #         }
    #         if selected_quarter in quarter_months:
    #             domain += [('last_working_day', 'in', quarter_months[selected_quarter])]

    #     employees = request.env['hr.employee'].search(domain)

    #     tenure_buckets = {
    #         '1-2 months': 0,
    #         '2-3 months': 0,
    #         '3-6 months': 0,
    #         '6-12 months': 0,
    #         '12-24 months': 0,
    #         '24-36 months': 0,
    #         '36+ months': 0,
    #     }

    #     for employee in employees:
    #         tenure_months = employee.tenure_months
    #         if 1 <= tenure_months <= 2:
    #             tenure_buckets['1-2 months'] += 1
    #         elif 2 < tenure_months <= 3:
    #             tenure_buckets['2-3 months'] += 1
    #         elif 3 < tenure_months <= 6:
    #             tenure_buckets['3-6 months'] += 1
    #         elif 6 < tenure_months <= 12:
    #             tenure_buckets['6-12 months'] += 1
    #         elif 12 < tenure_months <= 24:
    #             tenure_buckets['12-24 months'] += 1
    #         elif 24 < tenure_months <= 36:
    #             tenure_buckets['24-36 months'] += 1
    #         elif tenure_months > 36:
    #             tenure_buckets['36+ months'] += 1

    #     total_attrition = sum(tenure_buckets.values())
    #     attrition_by_tenure = [(count / total_attrition) * 100 if total_attrition else 0 for count in tenure_buckets.values()]

    #     return {
    #         'attrition_by_tenure': attrition_by_tenure,
    #     }
