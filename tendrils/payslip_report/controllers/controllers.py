# -*- coding: utf-8 -*-
import json
from mimetypes import guess_extension
from odoo import http
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.web.controllers.main import content_disposition


class PayslipsController(http.Controller):

    @http.route('/ex-employee-download-payslip/<int:emp_id>/<int:year>/<int:month>', type="http", cors='*', auth="none",
                methods=["GET"], csrf=False)
    def download_payslip(self, emp_id=None, year=None, month=None, **kwargs):
        try:
            emp_rec = request.env['hr.employee'].sudo().search([('id', '=', emp_id), ('active', '=', False)])
            if not emp_rec.exists():
                return request.not_found()

            payslip_data = request.env['hr.payslip'].sudo().search(
                [('state', '=', 'done'), ('employee_id', '=', emp_id),
                 ('salary_confirmation_month', '=', int(month)), ('salary_confirm_year', '=', int(year))], limit=1,
                order="id desc")
            if not payslip_data.exists():
                return request.not_found()

            payslip = request.env["hr.payslip"].sudo().search(
                [('state', '=', 'done'), ('employee_id', '=', emp_id)], limit=3, order="id desc")
            if payslip.exists():
                if payslip_data.id not in payslip.mapped('id'):
                    return request.not_found()

            report_template_id = request.env.ref(
                'payslip_report.action_payslip_report_payslips').sudo().render_qweb_pdf(payslip_data.id)
            extension = guess_extension(guess_mimetype(report_template_id[0]))

            emp_name = emp_rec.name.replace(" ", "_")
            filename = f"{emp_name}_{str(emp_rec.emp_code)}_salary_slip_{year}_{month}{extension}"

            return request.make_response(report_template_id, [('Content-Type', 'application/pdf'),
                                                              ('Content-Disposition', content_disposition(filename))])

        except Exception as e:
            return request.not_found(e)

    @http.route('/ex-employee-last-payslips', type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def api_ex_employee_payslip(self, emp_id=None):
        try:
            emp_rec = request.env['hr.employee'].sudo().search([('id', '=', emp_id), ('active', '=', False)])
            if not emp_rec.exists():
                return {'code': 500, 'message': 'Employee details not found.'}

            payslip = request.env["hr.payslip"].sudo().search(
                [('state', '=', 'done'), ('employee_id', '=', emp_id)], limit=1, order="id desc")
            if not payslip.exists():
                return {'code': 500, 'message': 'Employee\'s last 3 payslips not found.'}

            data_dict = {'code': 200, 'message': 'Success', 'payslips': []}

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            for rec in payslip:
                tmp_data = {
                    'url': f"{base_url}/ex-employee-download-payslip/{emp_id}/{rec.salary_confirm_year}/{rec.salary_confirmation_month}"
                }
                data_dict['payslips'].append(tmp_data)
            return data_dict

        except Exception as e:
            msg_dic = {
                "code": 400,
                "message": str(e)
            }
