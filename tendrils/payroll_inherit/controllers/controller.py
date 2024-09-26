# -*- coding: utf-8 -*-
import base64
import json
from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import datetime
from datetime import datetime, date
import unicodedata
import re
import werkzeug
from odoo import _
import odoo.http as http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.main import ExcelExport

class NPSController(http.Controller):


    @http.route('/skip-nps-details', auth='user', website=True, csrf=False)
    def nps_skip(self, **args):
        emp_rec = request.env.user.employee_ids
        skip_log = None
        if emp_rec:
            employee_id = emp_rec[0]
            skip_log = http.request.env['kw_employee_update_nps_log'].search([('employee_id', '=', employee_id.id)],
                                                                             limit=1)

            if not skip_log:
                skip_log = http.request.env['kw_employee_update_nps_log'].create(
                    {'employee_id': emp_rec.id, 'skips_check': 1})

            elif skip_log.skips_check < 3:
                skip_log.write({'skips_check': skip_log.skips_check + 1})

            http.request.session['skip_pan'] = True
            
            return http.request.redirect('/web')
        
    @http.route('/nps-update-form/', type='http', auth='user', csrf=False, website=True)
    def update_nps_details(self, **args):
        try:
            # Fetch employee details
            employee_id = request.env.user.employee_ids.id
            nps_data = request.env['nps_employee_data'].sudo().search([('employee_id', '=', employee_id)], limit=1)
            emp_profile_id = request.env['kw_emp_profile'].sudo().search([('emp_id', '=', employee_id)], limit=1).id
            emp_contract_id = request.env['hr.contract'].sudo().search([('employee_id', '=', employee_id), ('state', '=', 'open')], limit=1)
            # Update or create nps_data record
            # {'NPS_Interested': 'Yes', 'Percentage': '7% of Basic Salary', 'Have_Pran': 'No', 'Pran_Number': ''}
            Percentage = args.get('Percentage', False)
            contribution = ''
            nps = 0
            percentage_mapping = {
            '5% of Basic Salary': '5',
            '7% of Basic Salary': '7',
            '10% of Basic Salary': '10',
            '14% of Basic Salary': '14'
            }

            contribution = percentage_mapping.get(Percentage, '')
                
            if nps_data:
                nps_data.write({
                    'is_nps': args.get('NPS_Interested', 'No'),
                    'contribution': contribution,
                    'existing_pran_no': args.get('Have_Pran', 'No'),
                    'pran_no': args.get('Pran_Number', ''),
                    'is_popup_submitted': True,
                    # 'state':'Requested'
                })
            else:
                nps = request.env['nps_employee_data'].sudo().create({
                    'is_nps': args.get('NPS_Interested', 'No'),
                    'contribution': contribution,
                    'existing_pran_no': args.get('Have_Pran', False),
                    'pran_no': args.get('Pran_Number', ''),
                    'is_popup_submitted': True,
                    'employee_id': employee_id,
                    'emp_profile_id': emp_profile_id if emp_profile_id else False,
                    'emp_contract_id': emp_contract_id.id if emp_contract_id else False,
                    'state':'Requested' if args.get('NPS_Interested') == 'Yes' else 'Not_started',
                })
                # print('nps=========',nps)
            if args.get('NPS_Interested') and 'NPS_Interested' in args and args.get('NPS_Interested') == 'Yes':
                request.env['nps_update_data'].sudo().create({
                        'employee_id': employee_id,
                        'is_nps': 'Yes',
                        'contribution': contribution,
                        'existing_pran_no': args.get('Have_Pran', False),
                        'pran_no': args.get('Pran_Number', ''),
                        'is_popup_submitted': True,
                        'emp_profile_id': emp_profile_id if emp_profile_id else False,
                        'emp_contract_id': emp_contract_id.id if emp_contract_id else False,
                        'state':'Requested',
                        'after_login':'Yes' if args.get('NPS_Interested') == 'Yes' else 'No',
                        'nps_id':nps.id if nps else nps_data.id if nps_data else 0,
                        'remark':'NPS approval request'
                    })
            if emp_contract_id and 'NPS_Interested' in args and args.get('NPS_Interested') == 'No':
                emp_contract_id.write({
                    'is_nps':nps.is_nps if nps.is_nps else False,
                })
            
            # Return JSON response with redirect URL
            return json.dumps({'status': 'success', 'redirect': '/thank-you-for-nps-details-update'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    @http.route('/thank-you-for-nps-details-update', type='http', auth='user', csrf=False, website=True)
    def thank_you_for_nps_details_update(self):
        return request.render("payroll_inherit.nps_details_submission_template")
    
    @http.route('/update-nps-details/<model("hr.employee"):employee_id>', type='http', auth='user', csrf=False ,methods=['GET'],website=True)
    def redirect_nps_screen(self, employee_id,**args):
        employee = employee_id
        master_data = {}
        if employee:
            skip_log = http.request.env['kw_employee_update_nps_log'].search([('employee_id', '=', employee_id.id)],
                                                                             limit=1)
            return http.request.render("payroll_inherit.update_nps_details_web_template", {'skip_log': skip_log})
        else:
            return http.request.redirect('/web')
class ExcelExport(http.Controller):
    
    @http.route('/update-bank-details/<model("hr.employee"):employee_id>', type='http', auth='user', csrf=False ,methods=['GET'],website=True)
    def redirect_bank_screen(self, employee_id,**args):
        employee = employee_id
        master_data = {}
        banks = request.env['res.bank'].sudo().search([('account_type','=','csmacc')])
        master_data['banks'] = banks
        if employee:
            return http.request.render("payroll_inherit.update_bank_details_web_template",master_data)
        else:
            return http.request.redirect('/web')
        

    @http.route('/skip-bank-details/', type='http', auth='user', csrf=False ,website=True)
    def bank_skip(self, **args):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            return http.request.redirect('/web')
        
    @http.route('/cancel-bank-details/', type='http', auth='user', csrf=False ,website=True)
    def bank_cancel(self, **args):
        master_data = {}
        banks = request.env['res.bank'].sudo().search([('account_type','=','csmacc')])
        master_data['banks'] = banks
        return http.request.render("payroll_inherit.update_bank_details_web_template",master_data)
        
    @http.route('/bank-update-form/', type='http', auth='user', csrf=False ,website=True)
    def bank_confirm(self, **args):
        if args['account_number_hidden'] and args['bank_names_res_hidden']:
            contract = request.env['hr.contract'].sudo().search(
                [('employee_id', '=', request.env.user.employee_ids.id), ('state', '=', 'open')])
            bank = request.env['res.bank'].sudo().search([('id', '=', int(args['bank_names_res_hidden']))], limit=1)
            if contract and bank:
                request.env['bank_details_update'].sudo().create(
                    {'employee_id': contract.employee_id.id,
                     'bank_account': args['account_number_hidden'],
                     'bank_id': bank.id,
                     'old_bank_id': contract.bank_id.id,
                     'old_bank_account': contract.bank_account})
                contract.sudo().write({
                    'bank_id': bank.id,
                    'bank_account': args['account_number_hidden'],
                })
                contract.employee_id.sudo().write({
                    'bankaccount_id': bank.id,
                    'bank_account': args['account_number_hidden'],
                })

            return http.request.redirect('/thank-you-for-bank-details-update')
        else:
            return http.request.redirect('/web')
        
    @http.route('/thank-you-for-bank-details-update', type='http', auth='user', csrf=False ,website=True)
    def thank_you_for_bank_details_update(self):
        return http.request.render("payroll_inherit.bank_details_submission_template")

    @http.route('/export-payslip-summary/<model("hr.payslip.run"):batch_id>', type='http', auth='user')
    def export_xls_view(self, batch_id):
        payslip_batch = batch_id
        file_name = self.slugify(payslip_batch.name) + ".xlsx"
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)

        heading_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 14})
        heading_format.set_border()

        cell_text_format_n = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, })
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': False, 'size': 9, })
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 9, })
        cell_text_format.set_border()

        cell_text_format_new = workbook.add_format({'align': 'left', 'size': 9, })
        cell_text_format_new.set_border()

        cell_number_format = workbook.add_format({'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_number_format.set_border()

        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9, })
        normal_num_bold.set_border()
        
        structure_list = payslip_batch.slip_ids.mapped('struct_id')
        for structure in structure_list:
            structure_payslips = payslip_batch.slip_ids.filtered(lambda x : x.struct_id.id == structure.id)

            worksheet = workbook.add_worksheet(f'{structure.name} Payroll Report')

            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 20)
            worksheet.set_column('J:J', 20)
            worksheet.set_column('K:K', 20)
            worksheet.set_column('L:L', 20)
            worksheet.set_column('M:M', 20)
            worksheet.set_column('N:N', 20)

            if payslip_batch.date_start and payslip_batch.date_end:
                date_2 = datetime.strftime(payslip_batch.date_end, '%d-%b-%Y')
                date_1 = datetime.strftime(payslip_batch.date_start, '%d-%b-%Y')
                payroll_month = payslip_batch.date_start.strftime("%B")

                worksheet.merge_range('A1:F2', '%s' % (payslip_batch.name,), heading_format)
                row = 2
                column = 0
                # worksheet.write(row, 0, 'Company', cell_text_format)
                # worksheet.merge_range('B3:D3', '%s' % ("CSM Technologies",), cell_text_format_new)

                worksheet.write(0, 6, 'Date From', cell_text_format)
                worksheet.write(0, 7, date_1 or '', cell_text_center_normal)
                # row += 1
                worksheet.write(1, 6, 'Date To', cell_text_format)
                worksheet.write(1, 7, date_2 or '', cell_text_center_normal)
                row += 1
            
                rule_lst = []
                # structure_list = payslip_batch.slip_ids.mapped('struct_id')
                # for structure in structure_list:
                for rule in structure.rule_ids:
                    rule_lst.append(rule.id)
                    
            
                heads = request.env['hr.salary.rule'].search([('id','in',rule_lst)],order='sequence asc')
                res = [[head.name, head.code] for head in heads]
                # print("res >> ", res)

                """columns label set"""
                worksheet.write(row, 0, 'Employee', cell_text_format)
                worksheet.write(row, 1, 'Code', cell_text_format)
                worksheet.write(row, 2, 'Department', cell_text_format)
                worksheet.write(row, 3, 'Employment Type', cell_text_format)

                row_set = row
                column = 4
                # to write salary rules names in the row
                for vals in res:
                    worksheet.write(row, column, vals[0], cell_text_format)
                    column += 1

                row += 1
                col = 0
                ro = row

                if structure_payslips:
                    for payslip in structure_payslips:
                        name = payslip.employee_id.name
                        emp_code = payslip.employee_id.emp_code
                        department_id = payslip.employee_id.department_id.name
                        emp_type = payslip.employee_id.employement_type.name

                        worksheet.write(ro, col, name or '', cell_text_format_new)
                        worksheet.write(ro, col + 1, emp_code or '', cell_text_format_new)
                        worksheet.write(ro, col + 2, department_id or '', cell_text_format_new)
                        worksheet.write(ro, col + 3, emp_type or '', cell_text_format_new)
                        ro = ro + 1

                    col = col + 4
                    colm = col

                    # for slip in structure_payslips:
                    for payslip in structure_payslips:
                        # print('payslip======',payslip)
                        # for vals in res:
                        check = False
                        for line in payslip.line_ids:
                            # if line.code == vals[1]:
                            check = True
                            r = line.total
                            # worksheet.write(row, col, r, cell_number_format)
                            if check is True:
                                worksheet.write(row, col, r, cell_number_format)
                            else:
                                worksheet.write(row, col, 0, cell_number_format)

                            col += 1
                        row += 1
                        col = colm

                # calculating sum of column
                # roww = row
                # worksheet.write(row, 0, '', cell_text_format)
                # worksheet.write(row, 1, '', cell_text_format)
                # worksheet.write(row, 2, '', cell_text_format)
                worksheet.write(row, 3, 'Total', cell_text_format)

            columnn = 4
            # print("row_set >> ", row_set, row)
            for vals in res:
                cell1 = xl_rowcol_to_cell(row_set + 1, columnn)
                cell2 = xl_rowcol_to_cell(row - 1, columnn)
                worksheet.write_formula(row, columnn, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                columnn += 1

        workbook.close()
        # construct response
        fp.seek(0)

        return request.make_response(
            fp.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"' % (file_name,)),
                ('Content-Type', "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            ],
        )

    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

    @http.route('/health-insurance-for-dependant', auth='user', website=True, csrf=False)
    def health_insurance_form(self, employee=False, **kw):
        if not request.env.user.employee_ids:
            return werkzeug.utils.redirect('/web')

        return request.render("payroll_inherit.health_insurance_form", {'emp': request.env.user.employee_ids[0].name})

    @http.route('/health-insurance-for-dependant/skip-submit', auth='user', website=True, csrf=False)
    def skip_submit(self, **kw):
        try:
            request.session['skip_health_insurance'] = True
            return http.request.redirect('/web')
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
