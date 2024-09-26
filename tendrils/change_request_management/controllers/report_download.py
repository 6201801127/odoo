"""
Module containing the DomainBillingController class for managing billing-related HTTP requests.

This module imports necessary dependencies such as datetime, http from Odoo, and request from Odoo's HTTP module.
The DomainBillingController class is responsible for handling HTTP requests related to domain billing.

Example:
    To access domain billing information, one can make HTTP requests to the endpoints defined within this controller.

Usage:
    This module should be imported and used within the Odoo environment for managing domain billing operations.
"""
from datetime import datetime
from odoo import http
from odoo.http import request

class DomainBillingController(http.Controller):
    """
    Controller class for managing domain billing reports in Odoo.
    """
    
    @http.route('/download-report/<string:dt_start>/<string:dt_stop>/<string:mode>', type='http', auth='user')
    def download_report(self, dt_start='', dt_stop='', mode='', **kw):
        dt_start = datetime.strptime(dt_start, '%Y-%m-%d')
        dt_stop = datetime.strptime(dt_stop, '%Y-%m-%d')
        # wiz_data = request.env['domain_billing_filter_wizard'].sudo().search([]).mapped('report_type_selection')
        # print(wiz_data, "wiz_data==================================")
        context = {
            'dt_start': dt_start,
            'dt_stop': dt_stop,
        }
        if mode == 'bill_wise':
            filename = "Domain-Bill-Wise-Report.pdf"
            monthly_data = request.env['bill_wise_data_report'].search(
                [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)], order="bill_no asc")
            report_template_id = request.env.ref('change_request_management.bill_wise_pdf_report').sudo().render_qweb_pdf(monthly_data.ids,
                                                                                            data=context)
        elif mode == 'domain_wise':
            filename = "Domain-Wise-Report.pdf"
            monthly_data = request.env['domain_wise_data_report'].search(
                [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)])
            report_template_id = request.env.ref('change_request_management.domain_wise_pdf_report').sudo().render_qweb_pdf(monthly_data.ids,
                                                                                         data=context)
        elif mode == 'general':
            filename = "Domain-Bill-General-Report.pdf"
            monthly_data = request.env['domain_wise_data_report'].search(
                [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)])
            report_template_id = request.env.ref('change_request_management.domain_bill_general_pdf_report').sudo().render_qweb_pdf(monthly_data.ids,
                                                                                           data=context)
        elif mode == 'monthly':
            filename = "Domain-Billing-Monthly-Report.pdf"
            monthly_data = request.env['monthly_billing_data_report_new'].search(
                [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)])
            report_template_id = request.env.ref('change_request_management.bill_monthly_pdf_report').sudo().render_qweb_pdf(monthly_data.ids, data=context)

        return request.make_response(
            report_template_id[0],
            headers=[('Content-Type', 'application/pdf'),
                     ('Content-Length', len(report_template_id[0])),
                     ('Content-Disposition', f'attachment; filename="{filename}"')]
        )
        # return request.redirect('/')
