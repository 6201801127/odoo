# -*- coding: utf-8 -*-
from calendar import month
from io import BytesIO
from odoo.addons.http_routing.models.ir_http import slug

import xlsxwriter, random, string
import datetime
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import math, secrets
from math import floor,ceil
import requests
import calendar

# from odoo.tools.profiler import profile


class EmployeePayroll(models.Model):
    _name = 'kw_payroll_emp_integration'
    _description = "Payroll Employees"

    def _get_insurance_data(self):
        payroll_details_ids = self.env.context.get('selected_active_ids')
        res = self.env['hr.payslip'].sudo().search([('id', 'in', payroll_details_ids), ('state', '=', 'draft')])
        return res

    payroll_ids = fields.Many2many('hr.payslip', 'kw_employee_payroll_rel', 'payroll_id', 'emp_id', string='Employees',
                                   default=_get_insurance_data)

    def btn_compute_sheet(self):
        if self.payroll_ids:
            self.payroll_ids.filtered(lambda x: x.state == 'draft').compute_sheet()
            self.env.user.notify_success(message='Salary computed successfully!.')
                
    
class HrPayrollAdvices(models.Model):
    _inherit = 'hr.payroll.advice'

    @api.multi
    def compute_advice(self):
        """
        Advice - Create Advice lines in Payment Advice and
        compute Advice lines.
        """
        for advice in self:
            old_lines = self.env['hr.payroll.advice.line'].search([('advice_id', '=', advice.id)])
            if old_lines:
                old_lines.unlink()
            payslips = self.env['hr.payslip'].search(
                [('date_from', '<=', advice.date), ('date_to', '>=', advice.date), ('state', '=', 'done')])
            for slip in payslips:
                if not slip.employee_id.bank_account_number:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name,))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')],
                                                                  limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_number,
                        'ifsc_code': slip.employee_id.ifsc_code or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
                slip.advice_id = advice.id


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    def refund_sheet(self):
        for record in self:
            for rec in record.slip_ids:
                rec.refund_sheet()
            record.state ='close'
       
    @api.onchange('date_start','date_end')
    def _compute_middle_date(self):
        for rec in self:
            rec.middle_date = rec.date_start - relativedelta(months=1) + relativedelta(days=25)

    @api.multi
    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(
                    _("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
            company = self.env.user.company_id
            advice = self.env['hr.payroll.advice'].create({
                'batch_id': run.id,
                'company_id': company.id,
                'name': run.name,
                'date': run.date_end,
                'bank_id': company.partner_id.bank_ids and company.partner_id.bank_ids[0].bank_id.id or False
            })
            for slip in run.slip_ids:
                # TODO is it necessary to interleave the calls ?
                slip.action_payslip_done()
                if not slip.employee_id.bank_account_number:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')],
                                                                  limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_number,
                        'ifsc_code': slip.employee_id.ifsc_code or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
        self.write({'available_advice': True})

    # state = fields.Selection(selection_add=[,('verify', 'Verified')])
    middle_date = fields.Date()
    confirmed_on = fields.Date("Confirmed On")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Verify'),
        ('confirm', 'Confirm')
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    back_date_entry = fields.Boolean()
    remark = fields.Text()
    transaction_date = fields.Date()
    company_id = fields.Many2one('res.company')
    name = fields.Char(required=True,readonly=False)
    

    @api.onchange('back_date_entry')
    def change_remark(self):
        if self.back_date_entry:
            self.remark=False
            self.transaction_date = False

    @api.multi
    def draft_payslip_run(self):
        super(HrPayslipRun, self).draft_payslip_run()
        self.slip_ids.filtered(lambda x: x.state == 'verify').write({'state': 'draft'})

    @api.multi
    def close_payslip_run(self):
        remark = self.remark
        back_date_entry = self.back_date_entry
        transaction_date = self.transaction_date
        self.action_payslip_verified(back_date_entry=back_date_entry,remark=remark,transaction_date=transaction_date)
        return self.write({'state': 'close'})

    def confirm_payslips(self):
        month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                      5: 'May', 6: 'June', 7: 'July', 8: 'Aug',
                      9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        for record in self:
            date_from_month = record.date_start.month
            month = month_dict.get(date_from_month)
            if len(record.slip_ids) == 0:
                raise ValidationError('Please Generate Payslips to Confirm')
            else:
                for rec in record.slip_ids:
                    rec.action_payslip_done()
                    rec.write({
                        'salary_confirmation_month':record.date_end.month,
                        'salary_confirm_year' : record.date_end.year,
                        'salary_month_string' : month,
                        'sal_year' : str(record.date_end.year)
                    })
                record.write({
                        'state':'confirm',
                        'confirmed_on':date.today()
                })

    @api.multi
    def show_payroll_register_report(self):
        for payslip in self:
            val = {
                'name': 'Payroll Register',
                'view_type': 'pivot',
                'view_mode': 'pivot',
                'res_model': 'hr.payslip.line',
                'view_id': self.env.ref('payroll_inherit.hr_payslip_line_report_pivot_view').id,
                'domain': [
                    ('slip_id', 'in', payslip.slip_ids.ids),
                ],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
            return val

    @api.multi
    def download_excel(self):
        for payslip in self:
            val = {
                'name': 'Payroll Report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payroll.report.wiz',
                'view_id': self.env.ref('payroll_inherit.view_payroll_report_view_form').id,
                # 'domain': [
                #     ('slip_id', 'in', payslip.slip_ids.ids),
                # ],
                'context': {'date_start': payslip.date_start,
                            'date_end': payslip.date_end,
                            'payslip_id': payslip.id,
                            'name': payslip.name},
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
            return val

    @api.multi
    def compute_payslips(self):
        self.slip_ids.filtered(lambda x: x.state == 'draft').compute_sheet()
        return True

    @api.multi
    def action_payslip_verified(self,back_date_entry,remark,transaction_date):
        self.slip_ids.filtered(lambda x: x.state == 'draft').action_payslip_verified(back_date_entry,remark,transaction_date)

    @api.multi
    def payslip_excel_download(self):
        self.ensure_one()
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        result_url = f"{base_url}/export-payslip-summary/{self.id}"
        # print('result_url >> ', result_url)
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of Payslip Register",
            # 'target': 'self',
            'url': result_url
        }


class HrPayrollAdviceLine(models.Model):
    """
    Bank Advice Lines
    """
    _inherit = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            rec.name = rec.employee_id.bank_account_number
            rec.ifsc_code = rec.employee_id.ifsc_code or ''


class hr_employee_payroll_in(models.Model):
    _inherit = 'hr.employee'
    
    def send_personal_insurance_expired_mail(self):
        today = date.today()
        target_interval = 60 
        end_date = today + relativedelta(days=target_interval)
        employees = self.env['hr.employee'].sudo().search([
            ('personal_insurance', '=', 'Yes'),
            ('insurance_validate_date', '>=', today),
            ('insurance_validate_date', '<=', end_date)
        ])
        def format_date(date_str):
            return date_str.strftime('%d %b %Y')
        local_employees = employees.filtered(lambda e: e.company_id.id == 1)
        if local_employees:
            local_emp_list = [f"{emp.emp_code}:{emp.name}:{emp.department_id.name}:{format_date(emp.insurance_validate_date)}" for emp in local_employees]
            formatted_date = today.strftime('%d-%m-%Y')
            self._send_emails_to_pms(
                formatted_date,
                local_emp_list,
                'IND',
                'Employee Details | Expiry of Personal Health Insurance'
            )
        international_employees = employees.filtered(lambda e: e.company_id.id != 1)
        if international_employees:
            international_emp_list = [f"{emp.emp_code}:{emp.name}:{emp.department_id.name}:{format_date(emp.insurance_validate_date)}" for emp in international_employees]
            formatted_date = today.strftime('%d-%m-%Y')
            self._send_emails_to_pms(
                formatted_date,
                international_emp_list,
                'OTH',
                'Employee Details | Expiry of International Health Insurance'
            )
    def _send_emails_to_pms(self, formatted_date, emp_list, country, subject, description=False):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        pms_config_ids = ir_config_params.get_param('pms_employee_ids')
        pms_ids = [int(num) for num in pms_config_ids.split(',') if num.isdigit()]
        if pms_ids:
            for pm in pms_ids:
                pm_employee = self.env['hr.employee'].sudo().browse(pm)
                if pm_employee.work_email:
                    extra_params = {
                    'email_to': pm_employee.work_email,
                    'emp_list': emp_list,
                    'country': country,
                    'subject': subject,
                    'insurance_validate_date': formatted_date
                    }
                self.env['hr.employee'].employee_send_custom_mail(
                res_id=pm,
                notif_layout="kwantify_theme.csm_mail_notification_light",
                template_layout='payroll_inherit.personal_insurance_expired_mail_template',
                ctx_params=extra_params,
                description=' '
        )

    # def employee_send_custom_mail(self, res_id, force_send=False,raise_exception=False,email_values=None,notif_layout=False, template_layout=False, ctx_params=None, description=False):
    #     template = self.env.ref(template_layout)
    #     if template:
    #         values = template.with_context(ctx_params).generate_email(res_id)
    #         values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
    #         values.update(email_values or {})
    #         if 'email_from' in values and not values.get('email_from'):
    #             values.pop('email_from')
    #         if notif_layout and values['body_html']:
    #             try:
    #                 notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
    #             except ValueError:
    #                 pass
    #             else:
    #                 record = self.env[template.model].browse(res_id)
    #                 template_ctx = {
    #                     'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
    #                     'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
    #                     'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
    #                 }
    #                 body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
    #                 values['body_html'] = self.env['mail.thread']._replace_local_links(body)
    #         mail = self.env['mail.mail'].create(values)
    #         if force_send:
    #             mail.send(raise_exception=raise_exception)

    #         mail.model = False
    #         return mail.id                                                                        

    @api.multi
    def action_block_salary(self):
        for rec in self:
            view_id = self.env.ref('payroll_inherit.block_salary_view_form').id
            action = {
                'name': 'Block Salary',
                'type': 'ir.actions.act_window',
                'res_model': 'block_salary',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'context': {'employee_id': rec.id},
                'target': 'new',
            }
            return action

    struct_id = fields.Many2one('hr.payroll.structure', string="Payroll Structure", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    payslip_boolean = fields.Boolean(string="Payslip Boolean", compute="check_payslip_group")
    check_user = fields.Boolean(string="Payroll Structure Visibility", compute="show_struct_id")
    num_payslip_count = fields.Integer(compute='_compute_num_payslip_count', string='Payslip Count')
    is_consolidated= fields.Boolean("Is Consolidated ?")
    # account_number_id = fields.Many2one(comodel_name='res.partner.bank', string="Account Number")

    # @api.onchange('is_consolidated')
    # def change_salary_info(self):
    #     if self.is_consolidated == True:
    #         self.enable_epf = 'no'
    #         # self.pf_deduction = 'basicper'
    #         self.enable_gratuity = 'no'
    #         self.esi_applicable = False

    # @api.onchange('enable_epf')
    # def change_epf(self):
    #     if self.enable_epf == 'no':
    #         self.pf_deduction = 'basicper'
    # @api.onchange('bankaccount_id')
    # def onchange_section(self):
    #     self.account_number_id = False
    #     for rec in self:
    #         if rec.bankaccount_id:
    #             acc_list = []
    #             bank_details = self.env['res.partner.bank'].sudo().search([('bank_id', '=', rec.bankaccount_id.id), ('partner_id','=', rec.user_id.partner_id.id)])
    #             for record in bank_details:
    #                 acc_list.append(record.id)
    #             return {'domain': {'account_number_id': [('id', 'in', acc_list)]}}

    @api.multi
    def _compute_num_payslip_count(self):
        for employee in self:
            employee.num_payslip_count = len(employee.slip_ids.filtered(lambda x: x.state == 'done')) if employee.slip_ids.filtered(lambda x: x.state == 'done') else 0

    @api.constrains('current_ctc', 'current_basic', 'hra', 'productivity', 'commitment', 'conveyance')
    def validate_ctc_values(self):
        for rec in self:
            basic = rec.current_basic
            hra = basic * rec.hra / 100
            conveyance = basic * rec.conveyance / 100
            pb = rec.productivity
            cb = rec.commitment
            total = basic + hra + conveyance + pb + cb
            if total > rec.current_ctc:
                raise ValidationError("Total of BASIC, HRA, CONVEYANCE, PB and CB should be less than CTC")

    @api.depends('name')
    def show_struct_id(self):
        for record in self:
            user = self.env.user
            if user.has_group("kw_employee.group_payroll_manager"):
                record.check_user = False

    @api.depends('name')
    def check_payslip_group(self):
        for record in self:
            user = self.env.user
            if record.user_id.id == user.id:
                record.payslip_boolean = True

    def button_payslip_status(self):
        check_payslip = self.env['hr.payslip'].sudo().search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('state', '=', 'done')])
        if check_payslip:
            number = ''
            # otp_value = ''.join(random.choice(string.digits) for _ in range(4))
            otp_value = ''.join(secrets.choice(string.digits) for _ in range(4))
            template_id = self.env.ref('payroll_inherit.payslip_otp_mail_notification')
            email_id = self.env.user.employee_ids.work_email
            name = self.env.user.employee_ids.name
            otp = otp_value
            template_id.with_context(email_id=email_id, name=name, otp=otp).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light",force_send=True)
            model = self.env['payslip_otp_log']
            model.sudo().create({'employee_id': self.env.user.employee_ids.id, 'otp': otp_value})
            view_id = self.env.ref('payroll_inherit.payslip_otp_view_form').id
            try:
                formatted_msg = f"Please use OTP {otp} to view Payslips.\n CSM Technologies"
                html_msg = formatted_msg.replace('\\n', '\n')
                message = html_msg
                # print("message=================", message)
                header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                number = self.env.user.employee_ids.mobile_phone if self.env.user.employee_ids.mobile_phone else ''
                url = f'https://api.bulksmsgateway.in/sendmessage.php?user=csmwebu&password=Csmpl$4980&mobile={number}&message={message}&sender=CSMTEC&type=3&template_id=1207165900901935259'
                response = requests.post(url, headers=header)
            except:
                pass
            action = {
                'name': 'OTP Validation',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'payslip_otp',
                'view_id': view_id,
                'target': 'new',
            }
            return action
        else:
            raise ValidationError(f"You don't have any confirmed payslips yet.")

    """ create employee contract when a employee is created"""

    @api.model
    def create(self, vals):
        emp_rec = super(hr_employee_payroll_in, self).create(vals)

        # salary_structure = self.env['hr.payroll.structure'].sudo().search([('grade','=',emp_rec.grade.id),('band','=',emp_rec.emp_band.id),
        # ('base_branch_id','=',emp_rec.base_branch_id.id),('department_id','=',emp_rec.department_id.id)])
        if emp_rec.enable_payroll == 'yes':
            self.env['hr.contract'].sudo().create({
                'name': f"{emp_rec.name} contract",
                'employee_id': emp_rec.id,
                'state': 'open',
                'department_id': emp_rec.department_id.id,
                'job_id': emp_rec.job_id.id,
                'house_rent_allowance_metro_nonmetro': emp_rec.hra,
                'date_start': emp_rec.date_of_joining,
                'resource_calendar_id': emp_rec.resource_calendar_id.id,
                'wage': emp_rec.current_ctc,
                # 'current_ctc':emp_rec.current_ctc,
                'at_join_time_ctc': emp_rec.at_join_time_ctc,
                'basic_at_join_time': emp_rec.basic_at_join_time,
                'current_basic': emp_rec.current_basic,
                'conveyance': emp_rec.conveyance,
                'productivity': emp_rec.productivity,
                'commitment': emp_rec.commitment,
                'prof_persuit': emp_rec.pp_amount,
                'ltc': emp_rec.lta_amount,
                'struct_id': emp_rec.struct_id.id,
                'enable_epf': emp_rec.enable_epf if emp_rec.enable_epf == 'yes' else 'no',
                'enable_gratuity': emp_rec.enable_gratuity if emp_rec.enable_gratuity == 'yes' else 'no',
                'esi_applicable': emp_rec.esi_applicable,
                'pf_deduction': emp_rec.pf_deduction if emp_rec.pf_deduction else False,
                'uan_id': emp_rec.uan_id,
                'esi_id': emp_rec.esi_id,
                # 'bankaccount_id':emp_rec.bank_account_id.id,
                'is_consolidated': emp_rec.is_consolidated,
                'bank_account': emp_rec.bank_account,
                'bank_id': emp_rec.bankaccount_id.id,
                'personal_bank_name': emp_rec.personal_bank_name,
                'personal_bank_account': emp_rec.personal_bank_account,
                'personal_bank_ifsc': emp_rec.personal_bank_ifsc,
                'eps_enable': True if emp_rec.enable_epf == 'yes' and emp_rec.is_consolidated == False else False,
            })

        return emp_rec

    def daily_esi_scheduler(self):
        month = date.today().month
        day = date.today().day
        employee_list = []
        contract_employee_list = []
        contract_list = []
        ir_config_params = self.env['ir.config_parameter'].sudo()
        esi_start_period = ir_config_params.get_param('payroll_inherit.run_esi_schedule_start_date') or False
        esi_second_period = ir_config_params.get_param('payroll_inherit.run_esi_schedule_end_date') or False
        if esi_start_period != False and esi_second_period != False:
            first_period = datetime.strptime(str(esi_start_period), DEFAULT_SERVER_DATE_FORMAT).date()
            second_period = datetime.strptime(str(esi_second_period), DEFAULT_SERVER_DATE_FORMAT).date()
            if (month == first_period.month and day == first_period.day) or (
                    month == second_period.month and day == second_period.day):
                # employees = self.env['hr.employee'].sudo().search(
                    # [('enable_payroll', '=', 'yes'), ('esi_applicable', '=', True)]).mapped('id')
                # for rec in employees:
                #     employee_list.append(rec.id)
                contract_rec = self.env['hr.contract'].sudo().search(
                    [('state', '=', 'open'), ('esi_applicable', '=', True)])
                if contract_rec:
                    for contract in contract_rec:
                        basic = contract.current_basic
                        hra = contract.current_basic * contract.house_rent_allowance_metro_nonmetro / 100
                        conveyance = contract.current_basic * contract.conveyance / 100
                        pb = contract.productivity
                        cb = contract.commitment
                        bonus = contract.bonus
                        pp = contract.prof_persuit
                        ltc = contract.ltc
                        final_gross = basic + hra + conveyance + pb + cb + bonus + pp + ltc
                        if final_gross > 21000:
                            contract_employee_list.append(contract.employee_id.id)
                            contract_list.append(contract.id)
                            #     contract.employee_id.esi_applicable = True
                        # else:
                        #     contract.employee_id.esi_applicable = False       
                    if contract_employee_list:
                        emp_ids = ",".join(str(v) for v in contract_employee_list)
                        contract_ids = ",".join(str(v) for v in contract_list)
                        # emp_ids_str  = str(emp_ids)
                        query = f"UPDATE hr_employee SET esi_applicable=False WHERE id in ({emp_ids});UPDATE hr_contract SET esi_applicable=False WHERE id in ({contract_ids})"
                        self._cr.execute(query)
    def possible_esi_expire_scheduler(self):
        emp_list = []
        pms_ids = []
        create_query = ''
        emp_list = []
        pms_ids = []
        contract_employee_list = []
        ir_config_params = self.env['ir.config_parameter'].sudo()
        contract_rec = self.env['hr.contract'].sudo().search(
            [('state', '=', 'open'), ('esi_applicable', '=', True)])
        if contract_rec:
            for contract in contract_rec:
                basic = contract.current_basic
                hra = contract.current_basic * contract.house_rent_allowance_metro_nonmetro / 100
                conveyance = contract.current_basic * contract.conveyance / 100
                pb = contract.productivity
                cb = contract.commitment
                bonus = contract.bonus
                pp = contract.prof_persuit
                ltc = contract.ltc
                final_gross = basic + hra + conveyance + pb + cb + bonus + pp + ltc
                if final_gross > 21000:
                    contract_employee_list.append(contract.employee_id.id)
            if contract_employee_list:
                for employee in contract_employee_list:
                    self._cr.execute(f"""
                    SELECT e.emp_code, e.name, j.name as job 
                    FROM hr_employee e 
                    LEFT JOIN hr_department j ON j.id = e.department_id 
                    WHERE e.id = {employee}
                    """)
                    emp_data = self._cr.fetchall()
                    current_fiscal = self.env['account.fiscalyear'].search(
                                    [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
                    check_non_esi = self.env['non_esi_employee_report'].sudo().search([('employee_id','=',employee),('fiscalyr','=',current_fiscal.id)])
                    if not check_non_esi:
                        dept = self.env['hr.employee'].search([('id','=',employee)]).department_id.id
                        create_query += f"INSERT INTO non_esi_employee_report (employee_id,department_id,fiscalyr,state) VALUES ({employee},{dept},{current_fiscal.id},'Upgrade-To-GHI');"

                    for emp in emp_data:
                        emp_list.append(f"{emp[0]}:{emp[1]}:{emp[2]}")
                if len(create_query) > 0:
                    self._cr.execute(create_query)

                if len(emp_list) > 0:
                    pms_config_ids = ir_config_params.get_param('pms_employee_ids')
                    split_ids = pms_config_ids.split(',')
                    pms_ids = [int(num) for num in split_ids]
            if len(pms_ids) > 0:
                for pm in pms_ids:
                    self._cr.execute(f"SELECT work_email FROM hr_employee WHERE id = {pm}")
                    emails = self._cr.fetchall()
                    if emails:
                        pm_email = emails[0][0]
                        pm_emp_id = self.env['hr.employee'].search([('id','=',pm)])
                        template_id = self.env.ref('payroll_inherit.esi_updated_mail_template')
                        template_id.with_context(email_to=pm_email, emp_list=emp_list).sudo().send_mail(pm_emp_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


                      
    # @api.onchange('productivity', 'conveyance', 'commitment', 'current_basic', 'struct_id', 'current_ctc', 'hra',
    #               'at_join_time_ctc', 'basic_at_join_time','enable_epf','pf_deduction','esi_applicable','enable_gratuity','uan_id','esi_id','bank_account_id','is_consolidated')
    # def update_productivity(self):
    #     recid = self._origin.id
    #     for rec in self:
    #         emp_dict = {
    #                     'producontractctivity': rec.productivity,
    #                     'commitment': rec.commitment,
    #                     'conveyance': rec.conveyance,
    #                     'current_basic': rec.current_basic,
    #                     'struct_id': rec.struct_id.id,
    #                     'wage': rec.current_ctc,
    #                     'house_rent_allowance_metro_nonmetro': rec.hra,
    #                     'at_join_time_ctc': rec.at_join_time_ctc,
    #                     'basic_at_join_time': rec.basic_at_join_time,
    #                     'enable_epf' :rec.enable_epf,
    #                     'esi_applicable' : rec.esi_applicable,
    #                     'uan_id': rec.uan_id,
    #                     'esi_id' : rec.esi_id,
    #                     'bankaccount_id': rec.bank_account_id.id,
    #                     'is_consolidated':rec.is_consolidated,
    #                 }
    #         contract_rec = self.env['hr.contract'].sudo().search([('employee_id', '=', recid), ('state', '=', 'open')])
    #         if contract_rec:
    #             if rec.enable_gratuity == 'yes' or rec.enable_gratuity == 'no':
    #                 emp_dict['enable_gratuity'] = rec.enable_gratuity
    #             if rec.pf_deduction == 'basicper' or rec.pf_deduction == 'avail1800':
    #                 emp_dict['pf_deduction'] = rec.pf_deduction
    #             contract_rec.write(emp_dict)


class hr_payslip_line_in(models.Model):
    _inherit = 'hr.payslip.line'

    @api.depends('slip_id')
    def compute_currency(self):
        inr_currency_id = self.env['res.currency'].sudo().search([('name','=','INR')])
        inr_id = inr_currency_id.id if inr_currency_id else False 
        for line in self:
            line.currency_id = line.slip_id.contract_id.currency_id.id if  line.slip_id.contract_id.currency_id.id else inr_id
            
    @api.depends('employee_id')
    def _compute_details(self):
        for rec in self:
            rec.emp = f" {rec.employee_id.name} ({rec.emp_code})-({rec.department_id})-({rec.emp_type})"

    emp_code = fields.Char(string='EMP No.', related='employee_id.emp_code', store=True)
    # epf_number   = fields.Char(string='EPF No.',default='hello')
    location_id = fields.Char(string='Location', related='employee_id.job_branch_id.name', store=True)
    department_id = fields.Char(string='Department', related='employee_id.department_id.name', store=True)
    emp_type = fields.Char(related='employee_id.employement_type.name', store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", compute='compute_currency', store=True)
    emp = fields.Char(string='Employee', compute='_compute_details', store=True)

class hr_payslip_payroll_in(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def calculate_nssf(self,gross,employee_id,year,month,payslipid,enable_nssf,date_to):
        tire_1 = tire_2=0
        self.env.cr.execute(f"select id from nssf_master where payslip_id={payslipid}")
        nssf_dict =  self._cr.dictfetchall()
        # self.env.cr.execute(f"select SUM(CAST(value AS numeric)) filter(where key = 'payroll_inherit.min_value_nssf') as min_value_nssf,SUM(CAST(value AS numeric)) filter(where key = 'payroll_inherit.max_value_nssf') as max_value_nssf from ir_config_parameter")
        self.env.cr.execute(f"select min_value_nssf,max_value_nssf from nssf_configuration where '{date_to}' between date_from and date_to")
        config_nssf =  self._cr.dictfetchall()
        min_value = config_nssf[0]['min_value_nssf'] if len(config_nssf)>0 else 0
        max_value = config_nssf[0]['max_value_nssf'] if len(config_nssf)>0 else 0
        if enable_nssf and min_value and max_value:
            if gross > min_value:
                tire_1 = 2*(min_value*6/100)
                tire_2 = 2*(((max_value-min_value) if gross >=max_value else gross-min_value)*6/100)
            else:
                tire_1 = 2*(gross*6/100)
                tire_2 = 0
            if not nssf_dict:
                self.env.cr.execute(f"insert into nssf_master  (payslip_id,year,month, employee_id,tire_1_pensionable_earnings,tire_1_employee_contribution,tire_1_employer_contribution,tire_1_total_contribution,tire_2_pensionable_earnings,tire_2_employee_contribution,tire_2_employer_contribution,tire_2_total_contribution,total_contribution,total_employee_contribution,total_employer_contribution,gross) VALUES ({payslipid},{str(year)},'{calendar.month_name[month]}',{employee_id},{min_value if gross > min_value else gross},{tire_1 /2},{tire_1 /2},{self.calculate_round_amount(tire_1)},{max_value-min_value if gross >=max_value else gross-min_value if gross > min_value else 0},{tire_2/2},{tire_2/2},{self.calculate_round_amount(tire_2)},{self.calculate_round_amount(tire_1)+ self.calculate_round_amount(tire_2)},{self.calculate_round_amount((tire_1+ tire_2)/2)},{self.calculate_round_amount((tire_1+ tire_2)/2)},{gross})")
            else:
                self.env.cr.execute(f"update nssf_master set tire_1_pensionable_earnings= {min_value if gross > min_value else gross},tire_1_employee_contribution= {tire_1 /2},tire_1_employer_contribution=  {tire_1 /2},tire_1_total_contribution= {self.calculate_round_amount(tire_1)},tire_2_pensionable_earnings= {max_value-min_value if gross >=max_value else gross-min_value if gross > min_value else 0},tire_2_employee_contribution={tire_2/2},tire_2_employer_contribution={tire_2/2},tire_2_total_contribution={self.calculate_round_amount(tire_2)},total_contribution= {self.calculate_round_amount(tire_1)+ self.calculate_round_amount(tire_2)},total_employee_contribution= {self.calculate_round_amount((tire_1+ tire_2)/2)},total_employer_contribution= {self.calculate_round_amount((tire_1+ tire_2)/2)},gross={gross} where id =  {nssf_dict[0]['id']}")
        else:
            if nssf_dict:
                self.env.cr.execute(f"delete from nssf_master where id = {nssf_dict[0]['id']}")
        return self.calculate_round_amount((tire_1+ tire_2)/2)

    @api.model
    def calculate_nhif(self,gross,enable_nhif):
        if enable_nhif:
            self.env.cr.execute(f"select nhif from nhif_master where gross_from <= {gross} and gross_to >= {gross} LIMIT 1")
            nhif_dict =  self._cr.dictfetchall()
            if not nhif_dict:
                return 0
            else:
                return nhif_dict[0]['nhif']
        else:
            return 0
    @api.model
    def calculate_net(self,gross,deduction):
        number = gross - deduction
        formatted_number = str(number)
        decimal_part_length = len(formatted_number.split('.')[1])
        if decimal_part_length > 2:
            truncated_number = int(number * 100) / 100.0
            return (truncated_number)
        else:
            return(number)
    @api.model
    def calculate_paye(self,gross_amt,nssf,nhif,employee_id,year,month,payslipid):
        gross = gross_amt - nssf
        temp_tax_payable = 0
        if gross > 0 and gross <= 24000:
            tds_amount = 24000 - gross
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',0),('amount_to','=',24000)],limit=1)
            temp_tax_payable = tds_amount * tax_slab.rate / 100
        elif gross >= 24001 and gross <= 32333:
            tds_above5 = gross - 24000
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',24001),('amount_to','=',32333)],limit=1)
            tds_above5percentage = tds_above5 * tax_slab.rate / 100
            tax_slab_1 =self.env['kenya_tax_slab'].sudo().search([('amount_from','=',0),('amount_to','=',24000)],limit=1)
            tds_below5percentage = 24000 * tax_slab_1.rate / 100
            temp_tax_payable = tds_above5percentage + tds_below5percentage
        elif gross >= 32334 and gross <= 500000:
            tds_above5 = gross - 32333
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',32334),('amount_to','=',500000)],limit=1)
            tds_above5percentage = tds_above5 * tax_slab.rate / 100
            tax_slab24 = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',24001),('amount_to','=',32333)],limit=1)
            tds_above5percentage24 = 8333 * tax_slab24.rate / 100
            tax_slab_1 =self.env['kenya_tax_slab'].sudo().search([('amount_from','=',0),('amount_to','=',24000)],limit=1)
            tds_below5percentage0 = 24000 * tax_slab_1.rate / 100
            temp_tax_payable = tds_above5percentage + tds_above5percentage24 + tds_below5percentage0
        elif gross >= 500001 and gross <= 800000:
            tax_within_8 = gross - 500000
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',500001),('amount_to','=',800000)],limit=1)
            tax_1 = tax_within_8 * tax_slab.rate/100
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',32334),('amount_to','=',500000)],limit=1)
            tds_above5percentage = 467667 * tax_slab.rate / 100
            tax_slab24 = self.env['kenya_tax_slab'].sudo().search([('amount_from','=',24001),('amount_to','=',32333)],limit=1)
            tds_above5percentage24 = 8333 * tax_slab24.rate / 100
            tax_slab_1 =self.env['kenya_tax_slab'].sudo().search([('amount_from','=',0),('amount_to','=',24000)],limit=1)
            tds_below5percentage0 = 24000 * tax_slab_1.rate / 100
            temp_tax_payable = tds_above5percentage + tds_above5percentage24 + tds_below5percentage0 + tax_1
        elif gross >= 800001:
            tax_after_8 = gross - 800000
            tax_slab_8 = self.env['kenya_tax_slab'].sudo().search([('amount_to','>=',800001)],limit=1)
            tax_2 = tax_after_8 * tax_slab_8.rate/100
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','<=',500001),('amount_to','>=',800000)],limit=1)
            tax_1 = 300000 * tax_slab.rate/100
            tax_slab = self.env['kenya_tax_slab'].sudo().search([('amount_from','<=',32334),('amount_to','>=',500000)],limit=1)
            tds_above5percentage = 467667 * tax_slab.rate / 100
            tax_slab24 = self.env['kenya_tax_slab'].sudo().search([('amount_from','<=',24001),('amount_to','>=',32333)],limit=1)
            tds_above5percentage24 = 8333 * tax_slab24.rate / 100
            tax_slab_1 =self.env['kenya_tax_slab'].sudo().search([('amount_from','<=',0),('amount_to','>=',24000)],limit=1)
            tds_below5percentage0 = 24000 * tax_slab_1.rate / 100
            temp_tax_payable = tds_above5percentage + tds_above5percentage24 + tds_below5percentage0 + tax_1 + tax_2
        personal_relief = 2400
        nhif_relief = nhif * 15/100
        tax = temp_tax_payable-personal_relief-nhif_relief
        self.env.cr.execute(f"select id from tax_master where payslipid={payslipid}")
        tax_dict =  self._cr.dictfetchall()
        if not tax_dict:
            self.env.cr.execute(f"insert into tax_master  (payslipid,year,month, employee_id,personal_relief,nhif,nhif_relief,tax,taxable_income,gross_amt,nssf) VALUES ({payslipid},{str(year)},'{calendar.month_name[month]}',{employee_id},{personal_relief},{nhif},{nhif_relief},{tax if tax > 0 else 0},{temp_tax_payable},{gross_amt},{nssf})")
        else:
            self.env.cr.execute(f"update tax_master set personal_relief={personal_relief},nssf={nssf},gross_amt={gross_amt},nhif={nhif},nhif_relief={nhif_relief},tax={tax if tax > 0 else 0},taxable_income = {temp_tax_payable} where payslipid = {payslipid}")
        if tax > 0:
            return tax
        else:
            return 0
   
    @api.constrains('employee_id')
    def check_block_employee(self):
        for rec in self:
            block_rec = self.env['hr_block_salary'].sudo().search([('employee_id','=',rec.employee_id.id),('year','=',str(rec.date_to.year)),('month','=',str(rec.date_to.month)),('active','=',True)])
            if block_rec:
                raise ValidationError(f'Salary has been blocked for {rec.employee_id.name} from {rec.date_from} - {rec.date_to}')

    department = fields.Char(string='Department Name', related='employee_id.department_id.name', store=True)
    emp_type = fields.Char(string='Employement Type', related='employee_id.employement_type.name', store=True)
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    employement_type = fields.Many2one('kwemp_employment_type', string="Type of Employment")
    employee = fields.Char(related='employee_id.name', string='Employee')
    emp_code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    basic = fields.Float(compute='compute_salary', string='Basic')
    hra = fields.Float(compute='compute_salary', string='HRA')
    conveyance = fields.Float(compute='compute_salary', string='Conveyance')
    pb = fields.Float(compute='compute_salary', string='Productivity Bonus')
    cb = fields.Float(compute='compute_salary', string='Commitment Bonus')
    gross_calc = fields.Float(compute='compute_salary', string='Gross')
    final_gross = fields.Float(compute='compute_salary', string='Final Gross')
    lwop = fields.Float(compute='compute_salary', string='LWOP')
    gratuity = fields.Float(compute='compute_salary', string='Gratuity')
    epf = fields.Float(compute='compute_salary', string='EPF Empr')
    esic = fields.Float(compute='compute_salary', string=' ESIC')
    salary_adv = fields.Float(compute='compute_salary', string='Salary Advance')
    ptd = fields.Float(compute='compute_salary', string='Prof. Tax')
    bonus = fields.Float(compute='compute_salary', string='BONUS')
    
    health_insurance_self = fields.Float(compute='compute_salary', string='Health Insurance Self')
    salary_confirmation_month = fields.Integer(store=True, string='Month')
    salary_confirm_year = fields.Integer(store=True, string='Year')
    branch_id = fields.Many2one("kw_res_branch", "Branch")
    net_salary = fields.Float(compute='compute_salary',string='Net')
    ctc = fields.Float(compute='compute_salary',string='CTC')
    salary_month = fields.Char(compute='compute_salary', string='Month')
    # emp_count = fields.Float(string='Employee')
    lunch_expences = fields.Float(compute='compute_salary', string='Lunch Expenses')
    eepf = fields.Float(compute='compute_salary', string='EPF Empe')
    esi = fields.Float(compute='compute_salary', string='ESIE')
    other_deduction = fields.Float(compute='compute_salary', string='Other Advance')
    health_insurance_dependant = fields.Float(compute='compute_salary', string='Health Insurance Dependent')
    total_deduction = fields.Float(compute='compute_salary', string='Total')
    city_allowances = fields.Float(compute='compute_salary', string='City Allowance')
    incentive_allowances = fields.Float(compute='compute_salary', string='Incentive')
    leave_encachment = fields.Float(compute='compute_salary', string='Leave Encashment')
    er_bonus = fields.Float(compute='compute_salary', string='Employee Referral Bonus')
    variable = fields.Float(compute='compute_salary', string='Variable')
    equitable_allowance = fields.Float(compute='compute_salary', string='Equitable Allowance')
    traning_incentive = fields.Float(compute='compute_salary', string='Training Incentive')
    spl_allowance = fields.Float(compute='compute_salary', string='Special Allowance')
    arrear = fields.Float(compute='compute_salary', string='Arrear')
    total_allowance = fields.Float(compute='compute_salary', string='Total Allowances')
    salary_month_string = fields.Char(compute='compute_salary', string='Month')
    sal_year = fields.Char(compute='compute_year', string='Month', store=True)
    date_start_salary = fields.Date(string='Date From',compute='compute_payslip_date')
    date_end_salary = fields.Date(string='Date To',compute='compute_payslip_date')
    job_id = fields.Many2one(string='Designation', related='employee_id.job_id', store=True)
    hide_refund_boolean = fields.Boolean()
    bank =fields.Char(string='Bank')
    acc_number =fields.Char(string='Account Number')
    ifsc =fields.Char(string='IFSC Number')
    employer_pf = fields.Float(string='Employer PF')
    enable_49 = fields.Boolean()
    state = fields.Selection(selection_add=[('verify', 'Verified')])
    tds = fields.Float(compute='compute_salary', string='TDS')
    ltc = fields.Float(compute='compute_salary',)
    prof_persuit = fields.Float(compute='compute_salary',)
    nps = fields.Float(compute='compute_salary',)

    back_date_entry = fields.Boolean()
    remark = fields.Text()
    transaction_date = fields.Date()
    nssf = fields.Float("NSSF",compute='compute_salary')
    nhif = fields.Float("NHIF",compute='compute_salary')
    paye = fields.Float("PAYE",compute='compute_salary')
    housing_levy = fields.Float("Housing Levy",compute='compute_salary')
    gross_amt = fields.Float("Gross",compute='compute_salary')
    enable_jsw = fields.Boolean(string='Enable Mining Structure')
    actual_nps = fields.Float()
    
    @api.multi
    def action_payslip_verified(self,back_date_entry=False,remark=False,transaction_date=False):
        for rec in self:
            if back_date_entry == True:
                rec.write({'state':'verify','back_date_entry':back_date_entry,'remark':remark,'transaction_date':transaction_date})
            else:
                rec.state='verify'

    # @api.onchange('contract_id')
    # def salary_account(self):
    #     for rec in self:
    #         if rec.contract_id.bank_id and rec.contract_id.bank_account:
    #             rec.bank = rec.contract_id.bank_id.name
    #             rec.acc_number = rec.contract_id.bank_account
    #             rec.ifsc = rec.contract_id.bank_id.bic
    #         else:
    #             if rec.contract_id.personal_bank_name and rec.contract_id.personal_bank_account and rec.contract_id.personal_bank_ifsc:
    #                 rec.bank = rec.contract_id.personal_bank_name
    #                 rec.acc_number = rec.contract_id.personal_bank_account
    #                 rec.ifsc =rec.contract_id.personal_bank_ifsc

    # def _auto_init(self):
    #     super(hr_payslip_payroll_in, self)._auto_init()
    #     self.env.cr.execute("update hr_payslip a set employer_pf = (select total from hr_payslip_line where slip_id = a.id and code='EEPF') where state='done'")

    @api.depends('date_from','date_to')
    def compute_payslip_date(self):
        for rec in self:
            rec.date_start_salary = rec.date_from
            rec.date_end_salary = rec.date_to

    @api.depends('line_ids')
    def compute_salary(self):
        allowance = 0
        gross_gratuity,ctc_gratuity,basic_gratuity= 0,0,0
        for rec in self:
            for line in  rec.line_ids:
                if line.code == 'NSSF':
                    rec.nssf = line.total
                if line.code == 'NHIF':
                    rec.nhif = line.total
                if line.code == 'PAYE':
                    rec.paye = line.total
                if line.code == 'HL':
                    rec.housing_levy = line.total
                if line.code == 'CTC':
                    rec.ctc = line.total
                    ctc_gratuity = line.total
                if line.code == 'GROSS':
                    gross_gratuity = line.total
                    rec.gross_amt  = line.total
                if line.code == 'BASIC':
                    rec.basic = line.total
                    basic_gratuity = line.total
                if gross_gratuity == ctc_gratuity or gross_gratuity + (basic_gratuity * 12 / 100) == ctc_gratuity :
                    rec.gratuity = 0
                else:
                    if rec.contract_id.is_consolidated == False and rec.contract_id.enable_gratuity == 'yes':
                        if rec.enable_49:
                            rec.gratuity = rec.calculate_49_round_amount(round(basic_gratuity*4.81) / 100)
                        else:
                            rec.gratuity = rec.calculate_round_amount(round(basic_gratuity*4.81 / 100))

                    else:
                        rec.gratuity = 0
                # else:
                #     gratuity_amount = (4.81/100)*basic_gratuity
                #     if rec.enable_49:
                #        rec.gratuity = self.calculate_49_round_amount(round(((basic_gratuity/100) * 4.81),1))
                #     else:
                #         rec.gratuity = self.calculate_round_amount(gratuity_amount)
                
            date = rec.date_from.day
            date_from_month = rec.date_from.month
            month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'June', 7: 'July', 8: 'Aug',
                            9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            month = month_dict.get(date_from_month)
            rec.salary_month = f"{month}-{date}"
            rec.salary_month_string = month
            if rec.state in ('done','verify'):
                varalw_rec = rec.line_ids.filtered(lambda x: x.category_id.name == 'Variable Allowance')
                for amt in varalw_rec:
                    allowance += amt.amount

                for record in rec.line_ids:
                    if rec.contract_id.esi_applicable == True:
                        if record.code == 'GROSS':
                            rec.esic = ceil((record.amount - allowance) * 3.25 / 100)
                            gross_gratuity = record.total
                    else:
                        rec.esic = 0
                    if record.code == 'BASIC':
                        rec.basic = record.total
                        basic_gratuity = record.total
                    if record.code == 'HRAMN':
                        rec.hra = record.total
                    if record.code == 'TCA':
                        rec.conveyance = record.total
                    if record.code == 'PBONUS':
                        rec.pb = record.total
                    if record.code == 'CBONUS':
                        rec.cb = record.total
                    if record.code == 'SALADV':
                        rec.salary_adv = record.total
                    if record.code == 'BONUS':
                        rec.bonus = record.total
                    if record.code == 'PTD':
                        rec.ptd = record.total
                    if record.code == 'LTC':
                        rec.ltc = record.total
                    if record.code == 'PP':
                        rec.prof_persuit = record.total
                    rec.gross_calc = rec.basic + rec.hra + rec.pb + rec.cb + rec.conveyance + rec.bonus + rec.ltc + rec.prof_persuit
                    
                    # rec.epf = (rec.basic * 12 / 100) if rec.employee_id.enable_epf == 'yes' else 0
                    if record.code == 'FC':
                        rec.lunch_expences = record.total
                    if record.code == 'EEPF':
                        rec.eepf = record.total
                        rec.epf = rec.eepf
                    if record.code == 'ESI':
                        rec.esi = record.total
                    if record.code == 'OD':
                        rec.other_deduction = record.total
                    if record.code == 'HID':
                        rec.health_insurance_dependant = record.total
                    if record.code == 'CMT':
                        rec.health_insurance_self = record.total
                    if record.code == 'CBDA':
                        rec.city_allowances = record.total
                    if record.code == 'INC':
                        rec.incentive_allowances = record.total
                    if record.code == 'LE':
                        rec.leave_encachment = record.total
                    if record.code == 'ERBONUS':
                        rec.er_bonus = record.total
                    if record.code == 'VAR':
                        rec.variable = record.total
                    if record.code == 'EALW':
                        rec.equitable_allowance = record.total
                    if record.code == 'TINC':
                        rec.traning_incentive = record.total
                    if record.code == 'SALW':
                        rec.spl_allowance = record.total
                    if record.code == 'ARRE':
                        rec.arrear = record.total
                    if record.code == 'LWOP':
                        rec.lwop = record.total
                    if record.code == 'NET':
                        rec.net_salary = record.total
                    if record.code == 'CTC':
                        rec.ctc = record.total
                    if record.code == 'TDS':
                        rec.tds = record.total
                    if record.code == 'NPS':
                        rec.nps = record.total

                    rec.total_deduction = rec.lunch_expences + rec.gratuity + rec.esi + rec.esic + rec.employer_pf + rec.eepf + rec.other_deduction + rec.health_insurance_self + rec.health_insurance_dependant + rec.nps
                    rec.total_allowance = rec.city_allowances + rec.incentive_allowances + rec.leave_encachment + rec.er_bonus + rec.variable + rec.equitable_allowance + rec.traning_incentive + rec.spl_allowance + rec.arrear
                    rec.final_gross = rec.gross_calc + rec.total_allowance


    @api.depends('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id
            rec.employement_type = rec.employee_id.employement_type.id
            rec.branch_id = rec.employee_id.base_branch_id.id
            
    @api.onchange('contract_id')
    def change_currency(self):
        for rec in self:
            rec.currency_id = rec.contract_id.currency_id.id

    @api.depends('date_to')
    def compute_year(self):
        for rec in self:
            rec.sal_year = str(rec.date_to.year)

    @api.multi
    def compute_sheet(self):
        salary_rules = self.env['hr.salary.rule'].sudo().search([])
        res = super(hr_payslip_payroll_in, self).compute_sheet()
        for payslip in self:
            if payslip.contract_id and payslip.contract_id.struct_id:
                if payslip.contract_id.bank_id and payslip.contract_id.bank_account:
                    self.env.cr.execute(f"update hr_payslip set bank = '{payslip.contract_id.bank_id.name}' ,acc_number = '{payslip.contract_id.bank_account}',ifsc = '{payslip.contract_id.bank_id.bic}',enable_jsw = {payslip.contract_id.enable_jsw} where id = {payslip.id}")

                else:
                    if payslip.contract_id.personal_bank_name and payslip.contract_id.personal_bank_account and payslip.contract_id.personal_bank_ifsc:
                        self.env.cr.execute(f"update hr_payslip set bank = '{payslip.contract_id.personal_bank_name}' ,acc_number =' {payslip.contract_id.personal_bank_account}',ifsc = '{payslip.contract_id.personal_bank_ifsc}',enable_jsw = {payslip.contract_id.enable_jsw} where id = {payslip.id}")

                ledger_dict = {}
                actual_nps = 0
                
                for line in payslip.line_ids:
                    if line.code == 'NET' and line.amount < 0:
                        raise ValidationError(f'Negative salary found for {line.employee_id.name}')
                    if line.code == 'BASIC':
                        ledger_dict['basic'] = line.total
                    if line.code == 'EEPF':
                        ledger_dict['eepf'] = line.total
                    if line.code == 'FC':
                        ledger_dict['fc'] = line.total
                    if line.code == "NPS" and payslip.contract_id:
                        self.env.cr.execute(f"select tax_regime from hr_declaration where employee_id = {payslip.employee_id.id} and  date_range = (select id from account_fiscalyear where date_start <= '{payslip.date_from}' and date_stop >= '{payslip.date_to}')")
                        tds_lst = self._cr.dictfetchall()
                        tax_regime = tds_lst[0]['tax_regime']
                        if tax_regime == 'old_regime':
                            if payslip.contract_id.contribution == 14:
                                actual_nps = self.calculate_round_amount(ledger_dict['basic'] * 10 /100)
                            else:
                                actual_nps = line.amount
                        if tax_regime == 'new_regime':
                            actual_nps = line.amount
                        
                        self.env.cr.execute(f"update hr_payslip set actual_nps={actual_nps} where id = {payslip.id}")
                
                if payslip.contract_id:
                    if payslip.contract_id.enable_epf == 'yes' and payslip.contract_id.is_consolidated == False:
                        payslip.employer_pf = payslip.calculate_round_amount(ledger_dict.get('basic') * payslip.contract_id.employer_pf/100 ) if payslip.contract_id.pf_deduction == 'other' else ledger_dict.get('eepf') if  ledger_dict.get('eepf') else 0

                if payslip.payslip_run_id:
                    self.env.cr.execute(f"update hr_payslip set back_date_entry={payslip.payslip_run_id.back_date_entry},remark='{payslip.payslip_run_id.remark}' where id = {payslip.id}")
                to_date = payslip.date_to
                self.env.cr.execute(f"update hr_payslip set salary_confirmation_month={to_date.month},salary_confirm_year='{to_date.year}' where id = {payslip.id}")
                deduction_id = salary_rules.filtered(lambda x: x.code == 'FC').id
                self.env.cr.execute(f"select id from lunch_expenses where year = '{payslip.salary_confirm_year}' and  employee_id = {payslip.employee_id.id} and month= '{payslip.salary_confirmation_month}' and boolean_readonly is false and deduction_id = {deduction_id}")
                canteen_rec = self._cr.dictfetchall()
                
                if not canteen_rec:
                    if ledger_dict.get('fc'):
                        if ledger_dict.get('fc') > 0:
                            canteen_amount = ledger_dict.get('fc')
                            self.env['lunch_expenses'].create({
                                                                'year':str(to_date.year),
                                                                'month':str(to_date.month),
                                                                'employee_id':payslip.employee_id.id,
                                                                'amount':canteen_amount,
                                                                'deduction_id':deduction_id,
                                                                'boolean_readonly':False})
            else:
                raise ValidationError(f"Please update the salary structure in the contract for {payslip.employee_id.name}")

        return True

    @api.model
    # @profile
    
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contracts: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # print('method called')
        for contract in contracts:
            attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
                [('attendance_year', '=', date_to.year),
                 ('attendance_month', '=', date_to.month), ('employee_id', '=', contract.employee_id.id)])
            if attendance_info:
                absent_days = attendance_info.num_absent_days
                total_wpc = attendance_info.num_total_late_days_pc
                # leave_lwop = attendance_info.num_leave_lwop
                total_absent_days = attendance_info.total_pay_cut
                present_days = attendance_info.num_present_days
                maternity_leave = attendance_info.num_mt_leave_days
                actual_working_days = attendance_info.actual_working
                total_days_payable = attendance_info.total_days_payable

                attendances = {
                    'name': _("Shift Working Days"),
                    'sequence': 1,
                    'code': 'WORK100',
                    'number_of_days': attendance_info.num_shift_working_days,
                    # 'number_of_hours': work_data['hours'],
                    'contract_id': contract.id,
                }

                lwop = {
                    'name': _("LWOP"),
                    'sequence': 5,
                    'code': 'WORK100',
                    'number_of_days': total_absent_days,
                    # 'number_of_hours': work_data['hours'],
                    'contract_id': contract.id,
                }

                present_days = {
                    'name': _("Actual Working Days"),
                    'sequence': 6,
                    'code': 'WORK100',
                    'number_of_days': actual_working_days,
                    # 'number_of_hours': work_data['hours'],
                    'contract_id': contract.id,
                }

                total_days_payable = {
                    'name': _("Total Days Payable"),
                    'sequence': 8,
                    'code': 'WORK100',
                    'number_of_days': total_days_payable,
                    # 'number_of_hours': work_data['hours'],
                    'contract_id': contract.id,
                }
                res.append(total_days_payable)
                res.append(attendances)
                res.append(present_days)
                res.append(lwop)

                # print(contract.employee_id.gender)

                if contract.employee_id.gender == 'female':
                    maternity = {
                        'name': _("Maternity Leave"),
                        'sequence': 7,
                        'code': 'WORK100',
                        'number_of_days': maternity_leave,
                        # 'number_of_hours': work_data['hours'],
                        'contract_id': contract.id,
                    }
                    res.append(maternity)

        return res

    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)

    def calculate_49_round_amount(self, amount):
        if amount - int(amount) >= 0.49:
            return ceil(amount)
        else:
            return round(amount)

    @api.model
    # @profile
    def calculate_ctc(self, payslipid, basic, gross,enable_gratuity,is_consolidated,enable_49,enable_epf,pf_deduction,employer_pf):
        if enable_gratuity == 'yes' and is_consolidated == False:
            # rec.calculate_round_amount(round(basic_gratuity*4.81 / 100))
            # gratuity_amount = round(basic*4.81 / 100)
            # gratuity_amount = round(((basic/100) * 4.81),1)
            gratuity_amount = (4.81/100)*basic
            
            if enable_49:
                gratuity = self.calculate_49_round_amount(round(((basic/100) * 4.81),1))
            else:
                gratuity = self.calculate_round_amount(gratuity_amount)
        else:
            gratuity = 0
        if enable_epf == 'yes' and is_consolidated == False:
            if  pf_deduction == 'other':
                if employer_pf:
                    employer_epf = self.calculate_round_amount(basic * employer_pf / 100)
                else:
                    employer_epf = 0
            elif pf_deduction == 'avail1800' and basic >= 15000:
                employer_epf = 1800
            else:
                employer_epf = basic * 12 / 100
        else:
            employer_epf = 0
        amount=gross +  employer_epf + gratuity
        actual_ctc=self.calculate_round_amount(amount)
        return actual_ctc

    @api.model
    # @profile
    def calculate_lunchexp(self, payslipid, varded,employee_id,to_date_year,to_date_month):
        
        previous_month = datetime(int(to_date_year), int(to_date_month)-1, 26) if int(to_date_month) != 1 else datetime(int(to_date_year)-1,12, 26)
        previous_month_date = previous_month.date()
        current_month = datetime(int(to_date_year), int(to_date_month), 25) if int(to_date_month) != 1 else datetime(int(to_date_year)-1,12, 25)
        current_month_date = current_month.date()
        
        self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_canteen_deduction'")
        config_tds =  self._cr.dictfetchall()
        enable_lunch = config_tds[0]['value'] if len(config_tds)>0 else False
        amount = 0
        self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={to_date_year} and attendance_month = {to_date_month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info: 
            return 0
        else:
            if varded == 'FC':
                self.env.cr.execute(f"select amount from lunch_expenses l join hr_salary_rule r on r.id=l.deduction_id where l.month = '{to_date_month}' and l.year = '{to_date_year}' and l.employee_id={employee_id} and l.boolean_readonly is false and r.code='FC'")
                lunch_rec = self._cr.dictfetchall()
                if lunch_rec:
                    return lunch_rec[0]['amount']
                elif enable_lunch != False and varded == 'FC':
                    transaction_rec = self.env['employee_canteen_expense_report'].sudo().search([('employee_id','=',employee_id),('recorded_date','>=',previous_month_date),('recorded_date','<=',current_month_date)])
                    for rec in transaction_rec:
                        amount += rec.tea_coffee_price + rec.b2c_price + rec.regular_meal_price + rec.guest_meal_price
                    return amount
                else:
                    return 0
            else:
                self.env.cr.execute(f"select amount from lunch_expenses l join hr_salary_rule r on r.id=l.deduction_id where l.month = '{to_date_month}' and l.year = '{to_date_year}' and l.employee_id={employee_id} and l.boolean_readonly is false and r.code='OD'")
                other_deduction = self._cr.dictfetchall()
                if other_deduction:
                    return other_deduction[0]['amount']
                else:
                    return 0

    """create contract scheduler"""

    def create_contract(self):
        contract_records = self.env['hr.contract'].sudo().search([('state', '=', 'open')])
        emp_id = contract_records.mapped('employee_id.id')
        employees = self.env['hr.employee'].sudo().search([('id', 'not in', emp_id),('enable_payroll','=', 'yes')])
        salary_structure = self.env['hr.payroll.structure'].sudo().search([], order="id", limit=1)
        if employees:
            for record in employees:
                data = {
                        'name': f"{record.name} contract",
                        'employee_id': record.id,
                        'state': 'open',
                        'department_id': record.department_id.id,
                        'job_id': record.job_id.id,
                        'struct_id': salary_structure.id,
                        'house_rent_allowance_metro_nonmetro': record.hra,
                        'date_start': record.date_of_joining if record.date_of_joining else date.today(),
                        'resource_calendar_id': record.resource_calendar_id.id,
                        'wage': record.current_ctc,
                        'at_join_time_ctc': record.at_join_time_ctc,
                        'basic_at_join_time': record.basic_at_join_time,
                        'current_basic': record.current_basic,
                        'conveyance': record.conveyance,
                        'productivity': record.productivity,
                        'commitment': record.commitment,
                        'enable_epf' :record.enable_epf if record.enable_epf == 'yes' else 'no',
                        'enable_gratuity' :record.enable_gratuity if record.enable_gratuity == 'yes' else 'no',
                        'esi_applicable':record.esi_applicable,
                        'bank_account':record.bank_account,
                        'bank_id':record.bankaccount_id.id,
                        'personal_bank_name':record.personal_bank_name,
                        'personal_bank_account':record.personal_bank_account,
                        'personal_bank_ifsc':record.personal_bank_ifsc,
                        'eps_enable': True if record.enable_epf == 'yes' and record.is_consolidated == False else False,
                }

                if record.pf_deduction == 'basicper' or record.pf_deduction == 'avail1800':
                    data['pf_deduction'] = record.pf_deduction
                    self.env['hr.contract'].sudo().create(data)
                else:
                    data['pf_deduction'] = False
                    self.env['hr.contract'].sudo().create(data)

    # @api.model
    # def calculate_professionaltax(self, payslipid, gross, varalw,employee_id):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     total_gross = gross
    #     to_date = payslip_rec.date_to
    #     from_date = payslip_rec.date_from
    #     professional_tax, gross_price, professional_price = 0, 0, 0
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', to_date.year), ('attendance_month', '=', to_date.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         payslip_ledger = self.env['kw_payslip_ledger'].sudo().search(
    #             [('year', '=', str(to_date.year)),
    #             ('employee_id', '=', payslip_rec.employee_id.id), ('month', '=', str(to_date.month)),
    #             ('salary_rule_id.code', '=', 'PTD'), ('boolean_readonly', '=', False)])
    #         if payslip_ledger:
    #             return payslip_ledger.amount
    #         else:
    #             if payslip_rec.contract_id.is_consolidated == True:
    #                 return 0
    #             if 25000 > total_gross >= 13333 and to_date.month != 3 and payslip_rec.contract_id.is_consolidated == False:
    #                 professional_tax = 125
    #             if 25000 <= total_gross and to_date.month != 3 and payslip_rec.contract_id.is_consolidated == False:
    #                 professional_tax = 200
    #             if to_date.month == 3 and payslip_rec.contract_id.is_consolidated == False and payslip_rec.employee_id.date_of_joining:
    #                 date_start = (from_date.replace(month=4,day=1)) - relativedelta(years=1)
    #                 fy_payslip = self.env['hr.payslip'].sudo().search(
    #                     [('employee_id', '=', employee_id), ('date_from', '>=', date_start), ('state', '=', 'done')])
    #                 employee_rec = payslip_rec.employee_id
    #                 if fy_payslip.exists() and employee_rec.exists() \
    #                         and employee_rec.date_of_joining is not False and employee_rec.date_of_joining < date_start:
    #                     for rec in fy_payslip:
    #                         professional = rec.line_ids.filtered(lambda x: x.code == 'PTD').mapped('total')
    #                         professional_price += sum(professional)
    #                         gross = rec.line_ids.filtered(lambda x:x.code == 'GROSS').mapped('total')
    #                         gross_price += sum(gross)
                            
    #                         if (gross_price + total_gross) >= 300000:
    #                             professional_tax = 2500 - professional_price
    #                         elif 160000 <= (gross_price + total_gross) < 300000:
    #                             professional_tax = 1500 - professional_price
    #                         else:
    #                             professional_tax = 0
    #                 else:
    #                     if 25000 > total_gross >= 13333:
    #                         professional_tax = 125
    #                     elif  25000 <= total_gross:
    #                         professional_tax = 300
    #                     else:
    #                         professional_tax = 0
    #             # else:
    #             #     professional_tax = 0
    #         return professional_tax
    #     else:
    #         return 0
    @api.model
    # @profile
    def calculate_professionaltax(self, gross,employee_id,is_consolidated,date_of_joining,year,month,from_date):
        total_gross = gross
        professional_tax, gross_price, professional_price = 0, 0, 0
        self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            self.env.cr.execute(f"select amount from kw_payslip_ledger l join hr_salary_rule r on r.id = l.salary_rule_id where year = '{year}' and l.employee_id = {employee_id} and l.month='{month}' and l.boolean_readonly = false and r.code='PTD'")
            payslip_ledger = self._cr.dictfetchall()
            if payslip_ledger:
                return payslip_ledger[0]['amount']
            else:
                if is_consolidated == True:
                    return 0
                if 25000 > total_gross >= 13333 and month != 3 and is_consolidated == False:
                    professional_tax = 125
                if 25000 <= total_gross and month != 3 and is_consolidated == False:
                    professional_tax = 200
                    
                if month == 3 and is_consolidated == False and date_of_joining:
                    date_start = (from_date.replace(month=4,day=1)) - relativedelta(years=1)
                    payslips_res = self._cr.dictfetchall()
                    id_values = [d['id'] for d in payslips_res]
                    payslips = tuple(id_values)
                    if payslips and date_of_joining is not False and date_of_joining < date_start:
                        self.env.cr.execute(f"select sum(amount) filter (where code='PTD') as professional_price,sum(amount) filter (where code='GROSS') as gross_amt  from hr_payslip_line where slip_id in {payslips}")
                        amounts = self._cr.dictfetchall()
                        professional_price = amounts[0]['professional_price']
                        gross_price = amounts[0]['gross_amt']
                        
                        if (gross_price + total_gross) >= 300000:
                            professional_tax = 2500 - professional_price
                        elif 160000 <= (gross_price + total_gross) < 300000:
                            professional_tax = 1500 - professional_price
                        else:
                            professional_tax = 0
                    else:
                        if 25000 > total_gross >= 13333:
                            professional_tax = 125
                        elif  25000 <= total_gross:
                            professional_tax = 300
                        else:
                            professional_tax = 0
                # else:
                #     professional_tax = 0
            return professional_tax
            
    @api.model
    def calculate_nps(self,payslip,is_nps,contribution,employee_id,year,month,basic,pran):
        amount = 0
        self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info: 
            return 0
        else:
            if is_nps == 'Yes' and pran and len(pran)==12:
                amount = self.calculate_round_amount(basic * (int(contribution))/100)
                if amount < 500 and amount > 0:
                    return 500
                else:
                    return amount
            else:
                return amount
    @api.model
    # @profile
    def calculate_fixed_allowance(self, payslipid,amount,gender,employee_id,year,month,code,date_to):
        self.env.cr.execute(f"select id,emp_status,attendance_year,attendance_month,num_mt_leave_days,num_shift_working_days,actual_working,month_days,calculation_days from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
            config_month_days =  self._cr.dictfetchall()
            enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
            start_date = date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month'])-1, 26) if int(attendance_info[0]['attendance_month']) != 1 else date(int(attendance_info[0]['attendance_year'])-1,12, 26)
            payroll_end_date =date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month']),25)
            monthly_payable_days = (payroll_end_date - start_date).days + 1
            self.env.cr.execute(f"select employee_id,increment_date from payroll_increment where increment_date between '{start_date}' and '{payroll_end_date}' and employee_id={employee_id}")
            increment_info = self._cr.dictfetchall()
            self.env.cr.execute(f"select prof_persuit,ltc from hr_contract where state='close' and employee_id = {employee_id} order by id desc LIMIT 1")
            exp_productivity_dict = self._cr.dictfetchall()
            contract_value = 0
            if exp_productivity_dict:
                contract_value = exp_productivity_dict[0]['prof_persuit'] if code =='PP' else exp_productivity_dict[0]['ltc']
                contract_value = contract_value if contract_value else 0
            if gender == 'female' and attendance_info[0]['num_mt_leave_days'] > 0:
                if enable_month_days:
                    if attendance_info[0]['emp_status'] == 1:
                        tot_working = monthly_payable_days - attendance_info[0]['num_mt_leave_days']
                        if tot_working >0:
                            if not increment_info:
                                return self.calculate_round_amount(tot_working / monthly_payable_days * amount)
                            else:
                                self.env.cr.execute(f"select id,request_unit_half_to_period,request_date_to,request_date_from from hr_leave where employee_id = {employee_id} and (request_date_to between '{start_date}' and '{payroll_end_date}' or request_date_from between '{start_date}' and '{payroll_end_date}') and state='validate'")
                                leave_info = self._cr.dictfetchall()
                                if leave_info:
                                    if start_date <=leave_info[0]['request_date_to'] <= payroll_end_date:
                                        if leave_info[0]['request_date_to'] < increment_info[0]['increment_date']:
                                            new_days = abs(payroll_end_date - increment_info[0]['increment_date']).days +1
                                            per_day_new_pb = amount/monthly_payable_days
                                            new_pb = per_day_new_pb * new_days
                                            old_days = abs(increment_info[0]['increment_date'] - leave_info[0]['request_date_to']).days -1 
                                            per_day_old_pb = contract_value/monthly_payable_days
                                            old_pb = per_day_old_pb * old_days
                                            if old_pb+new_pb > 0:
                                                return self.calculate_round_amount(old_pb+new_pb)
                                            else:
                                                return 0
                                        else:
                                            left_days = monthly_payable_days - attendance_info[0]['num_mt_leave_days']
                                            per_day_new_pb = amount / monthly_payable_days
                                            left_day_new_pb = per_day_new_pb * left_days
                                            return self.calculate_round_amount(left_day_new_pb)
                                    elif start_date <=leave_info[0]['request_date_from'] <= payroll_end_date:
                                        if leave_info[0]['request_date_from'] < increment_info[0]['increment_date']:
                                            return self.calculate_round_amount(tot_working/ monthly_payable_days * contract_value)
                                        else:
                                            day_count_till_increment = abs(start_date - increment_info[0]['increment_date']).days
                                            day_count_till_leave = abs(leave_info[0]['request_date_from'] - increment_info[0]['increment_date']).days
                                            per_day_old_pb = contract_value/monthly_payable_days
                                            old_pb = per_day_old_pb * day_count_till_increment
                                            per_day_new_pb = amount/monthly_payable_days
                                            new_pb = per_day_new_pb * day_count_till_leave
                                            return self.calculate_round_amount(old_pb+new_pb)
                        else:
                            return 0
                    else:
                        total_working = 0 if (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days'])
                        return self.calculate_round_amount((total_working / monthly_payable_days) * amount)
                else: 
                    if attendance_info[0]['emp_status'] == 1:
                        tot_working = attendance_info[0]['num_shift_working_days'] - attendance_info[0]['num_mt_leave_days']
                        return self.calculate_round_amount(tot_working / attendance_info[0]['num_shift_working_days'] * amount)
                    else:
                        total_working = 0 if (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days'])
                        return self.calculate_round_amount((total_working / attendance_info[0]['num_shift_working_days']) * amount)
            else:
                if attendance_info[0]['emp_status'] == 1:
                    if not increment_info:
                        return self.calculate_round_amount(amount)
                    else:
                        month_days = attendance_info[0]['month_days']
                        old_days = (increment_info[0]['increment_date'].day - 1)
                        old_pb_per_day = contract_value/month_days
                        old_pb = old_pb_per_day * old_days
                        new_days = (date_to - increment_info[0]['increment_date']).days + 1
                        new_pb_per_day = amount/month_days
                        new_pb = new_pb_per_day * new_days
                        return self.calculate_round_amount(old_pb+new_pb)
                else:
                    working_days = attendance_info[0]['month_days'] if enable_month_days else attendance_info[0]['num_shift_working_days']
                    actual_working = attendance_info[0]['calculation_days'] if enable_month_days else  attendance_info[0]['actual_working']
                    return self.calculate_round_amount((actual_working / working_days) * amount)
       
    # @api.model
    # @profile
    # def calculate_fixed_allowance(self, payslipid,code):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_end = payslip_rec.date_to
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
    #         start_date = date(int(attendance_info.attendance_year), int(attendance_info.attendance_month)-1, 26) if int(attendance_info.attendance_month) != 1 else date(int(attendance_info.attendance_year)-1,12, 26)
    #         payroll_end_date =date(int(attendance_info.attendance_year), int(attendance_info.attendance_month),25)
    #         monthly_payable_days = (payroll_end_date - start_date).days + 1
    #         amount = payslip_rec.contract_id.prof_persuit if code == 'PP' else payslip_rec.contract_id.ltc if code =='LTC' else 0
    #         if payslip_rec.employee_id.gender == 'female' and attendance_info.num_mt_leave_days > 0:
    #             if enable_month_days:
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = monthly_payable_days - attendance_info.num_mt_leave_days
    #                     allowance = tot_working / monthly_payable_days * amount
    #                     total = self.calculate_round_amount(allowance)
    #                     return total
    #                 else:
    #                     working_days = monthly_payable_days
    #                     total_working = 0 if (attendance_info.calculation_days - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.calculation_days - attendance_info.num_mt_leave_days)
    #                     emp_allowance = amount
    #                     allowance = (total_working / working_days) * emp_allowance
    #                     total = self.calculate_round_amount(allowance)
    #                     return total
    #             else:
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = attendance_info.num_shift_working_days - attendance_info.num_mt_leave_days
    #                     allowance = tot_working / attendance_info.num_shift_working_days * amount
    #                     total = self.calculate_round_amount(allowance)
    #                     return total
    #                 else:
    #                     working_days = attendance_info.num_shift_working_days
    #                     total_working = 0 if (attendance_info.actual_working - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.actual_working - attendance_info.num_mt_leave_days)
    #                     emp_allowance = amount
    #                     allowance = (total_working / working_days) * emp_allowance
    #                     total = self.calculate_round_amount(allowance)
    #                     return total

    #         else:
    #             if attendance_info.emp_status == 1:
    #                 allowance = amount
    #                 total = self.calculate_round_amount(allowance)
    #                 return total
    #             else:
    #                 working_days = attendance_info.month_days if enable_month_days else attendance_info.num_shift_working_days
    #                 actual_working = attendance_info.calculation_days if enable_month_days else  attendance_info.actual_working
    #                 emp_allowance = amount
    #                 allowance = (actual_working / working_days) * emp_allowance
    #                 total = self.calculate_round_amount(allowance)
    #                 return total
    #     else:
    #         return 0

    @api.model
    # @profile
    def calculate_employee_pf(self, payslipid, basic,is_consolidated,enable_epf,pf_deduction,epf_percent):
        if enable_epf == 'yes' and is_consolidated == False:
            if pf_deduction == 'other':
                if epf_percent:
                    amount = self.calculate_round_amount(basic * epf_percent / 100)
                    return amount
                else:
                    return 0
            elif pf_deduction == 'avail1800' and basic >= 15000:
                return 1800
            else:
                amount = self.calculate_round_amount(basic * 12 / 100)
                return amount
        else:
            return 0

    @api.model
    # @profile
    def calculate_employer_pf(self, payslipid, basic):
        payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
        if payslip_rec.contract_id.enable_epf == 'yes' and payslip_rec.contract_id.is_consolidated == False:
            if payslip_rec.contract_id.pf_deduction == 'other':
                if payslip_rec.contract_id.employer_pf:
                    amount = self.calculate_round_amount(basic * payslip_rec.contract_id.employer_pf / 100)
                    return amount
                else:
                    return 0
            elif payslip_rec.contract_id.pf_deduction == 'avail1800' and basic >= 15000:
                return 1800
            else: 
                amount = self.calculate_round_amount(basic * 12 / 100)
                return amount
        else:
            return 0

    @api.model
    # @profile
    def calculate_allowance(self, alwcode,employee_id,year,month):
        self.env.cr.execute(f"select attendance_year,attendance_month from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            # self.env.cr.execute(f"select amount from allowance_allocation_master where month= '{str(attendance_info[0]['attendance_month'])}' and year='{str(attendance_info[0]['attendance_year'])}' and employee={employee_id} and boolean_readonly=false and allowance = (select id from hr_salary_rule where code = '{alwcode}')")
            alw_rec = self.env['allowance_allocation_master'].sudo().search(
                [('month', '=', str(attendance_info[0]['attendance_month'])), ('year', '=', str(attendance_info[0]['attendance_year'])),
                ('employee', '=', employee_id), ('allowance.code', '=', alwcode),
                ('boolean_readonly', '=', False)])
            # alw_rec = self._cr.dictfetchall()
            if not alw_rec:
                return 0
            else:
                return alw_rec[0]['amount']
        
    # @api.model
    # @profile
    # def calculate_allowance(self, payslipid, alwcode):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     to_date = payslip_rec.date_to
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', to_date.year), ('attendance_month', '=', to_date.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         alw_rec = self.env['allowance_allocation_master'].sudo().search(
    #             [('month', '=', str(to_date.month)), ('year', '=', str(to_date.year)),
    #             ('employee', '=', payslip_rec.employee_id.id), ('allowance.code', '=', alwcode),
    #             ('boolean_readonly', '=', False)])
    #         if alw_rec:
    #             return alw_rec.amount
    #         else:
    #             return 0
    #     else:
    #         return 0

    @api.model
    # @profile
    def calculate_esi(self, payslipid, gross, variablealw, code,esi_applicable,is_consolidated):
        if esi_applicable == True and is_consolidated == False:
            if code == 'ESI':
                return ceil((gross - variablealw) * 0.75 / 100)
            else:
                return ceil((gross - variablealw) * 3.25 / 100)
        else:
            return 0
    
    # @api.model
    # def calculate_esi(self, payslipid, gross, variablealw, code):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     if payslip_rec.contract_id.esi_applicable == True and payslip_rec.contract_id.is_consolidated == False:
    #         if code == 'ESI':
    #             # return (gross - variablealw) * 0.75 / 100
    #             # amount = self.calculate_round_amount((gross - variablealw) * 0.75 / 100)
    #             return ceil((gross - variablealw) * 0.75 / 100)
    #         else:
    #             return ceil((gross - variablealw) * 3.25 / 100)
    #     else:
    #         return 0

    @api.model
    def calculate_gratuity(self, payslipid, basic):
        payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
        if payslip_rec.contract_id.enable_gratuity == 'yes' and payslip_rec.contract_id.is_consolidated == False:
            amount = self.calculate_round_amount((basic/100) * 4.81)
            return amount
        else:
            return 0

    @api.model
    # @profile
    def calculate_selfinsurance(self, payslipid,employee_id,year,month,date_start,to_date):
        self.env.cr.execute(f"select amount from kw_payslip_ledger l join hr_salary_rule r on r.id = l.salary_rule_id where year = '{year}' and l.employee_id = {employee_id} and l.month='{month}' and l.boolean_readonly = false and r.code='CMT'")
        payslip_ledger = self._cr.dictfetchall()
        if payslip_ledger:
            return payslip_ledger[0]['amount']
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.check_health_insurance_self'")
            config_enable_insurance =  self._cr.dictfetchall()
            enable_insurance = config_enable_insurance[0]['value'] if len(config_enable_insurance)>0 else False
            if enable_insurance != False:
                health_self = self.env['health_insurance_self'].sudo().search(
                    [('year.date_start', '<=', date_start),
                     ('employee_id', '=', employee_id), ('year.date_stop', '>=', to_date)])
                if health_self:
                    return health_self.insurance_amount
                else:
                    return 0
            else:
                return 0
            
    # @api.model
    # def calculate_selfinsurance(self, payslipid):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     to_date = payslip_rec.date_to
    #     date_start = payslip_rec.date_from
    #     payslip_ledger = self.env['kw_payslip_ledger'].sudo().search(
    #         [('employee_id', '=', payslip_rec.employee_id.id), ('year', '=', str(to_date.year)),
    #          ('month', '=', str(to_date.month)), ('salary_rule_id.code', '=', 'CMT'), ('boolean_readonly', '=', False)])
    #     if payslip_ledger:
    #         return payslip_ledger.amount
    #     else:
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_insurance = ir_config_params.get_param('payroll_inherit.check_health_insurance_self') or False
    #         if enable_insurance != False:
    #             health_self = self.env['health_insurance_self'].sudo().search(
    #                 [('year.date_start', '<=', date_start),
    #                  ('employee_id', '=', payslip_rec.employee_id.id), ('year.date_stop', '>=', to_date)])
    #             if health_self:
    #                 return health_self.insurance_amount
    #             else:
    #                 return 0
    #         else:
    #             return 0

    @api.model
    # @profile
    def calculate_dependantinsurance(self, payslipid,employee_id,year,month,date_end,date_start):
        self.env.cr.execute(f"select l.amount from kw_payslip_ledger l join hr_salary_rule r on r.id=l.salary_rule_id where l.year='{year}' and l.employee_id={employee_id} and l.month='{month}' and l.boolean_readonly is false and r.code='HID'")
        ledger_dict = self._cr.dictfetchall()
        if ledger_dict:
            return ledger_dict[0]['amount']
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.check_health_insurance'")
            config_insurance =  self._cr.dictfetchall()
            enable_insurance = config_insurance[0]['value'] if len(config_insurance)>0 else False
            if enable_insurance != False:
                self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
                attendance_info = self._cr.dictfetchall()
                if attendance_info:
                    # self.env.cr.execute(f"select id from account_fiscalyear where date_start <= '{date_end}' and date_stop >='{date_end}'")
                    # fy_dict = self._cr.dictfetchall()
                    self.env.cr.execute(f"select id from health_insurance_dependant where employee_id={employee_id} and state='approved' and boolean_readonly is false ORDER BY id DESC LIMIT 1")
                    health_dependant = self._cr.dictfetchall()
                    emi_amount = 0
                    if health_dependant:
                        self.env.cr.execute(f"select sum(installment) as installment from health_insurance_emi where status = 'unpaid' and emi_details_id = {health_dependant[0]['id']} and emi_date between '{date_start}' and '{date_end}'")
                        emi_dict = self._cr.dictfetchall()
                        emi_amount = emi_dict[0]['installment']
                        amount = self.calculate_round_amount(emi_amount if emi_dict[0]['installment'] else 0)
                        return amount
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
    # @api.model
    # def calculate_dependantinsurance(self, payslipid):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_end = payslip_rec.date_to
    #     date_start = payslip_rec.date_from
    #     payslip_ledger = self.env['kw_payslip_ledger'].sudo().search(
    #         [('year', '=', str(date_end.year)),
    #          ('employee_id', '=', payslip_rec.employee_id.id),
    #          ('month', '=', str(date_end.month)), ('salary_rule_id.code', '=', 'HID'),
    #          ('boolean_readonly', '=', False)])
    #     if payslip_ledger:
    #         return payslip_ledger.amount
    #     else:
    #         month_dict = {'January': 1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_insurance = ir_config_params.get_param('payroll_inherit.check_health_insurance') or False
    #         if enable_insurance != False:
    #             attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #             [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #             ('employee_id', '=', payslip_rec.employee_id.id)])
    #             health_dependant = self.env['health_insurance_dependant'].sudo().search(
    #                 [('employee_id', '=', payslip_rec.employee_id.id), ('date_range.date_start', '<=', date_start),
    #                 ('date_range.date_stop', '>=', date_end), ('boolean_readonly', '=', False),
    #                 ('state', '=', 'approved')])
    #             advance_amount = 0
    #             if health_dependant and attendance_info.zero_payslip_boolean == False:
    #                 deduction_rec = health_dependant.emi_details_ids.filtered(lambda r: r.status == 'unpaid' and  int(date_end.month) == month_dict.get(r.month) and r.year == int(date_end.year)).mapped(
    #                 "installment")
    #                 advance_amount += sum(deduction_rec)
    #                 amount = self.calculate_round_amount(advance_amount)
    #                 return amount
    #             elif health_dependant and attendance_info.zero_payslip_boolean == True:
                   
    #                     return 0
    #             else:
    #                 return 0
    #         else:
    #             return 0



class hr_employee_kwantify_payroll_structure(models.Model):
    _inherit = 'hr.payroll.structure'

    grade = fields.Many2one('kwemp_grade_master', string='Grade')
    band = fields.Many2one('kwemp_band_master', string='Band')
    department_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practise")
    practise = fields.Many2one('hr.department', string="Section")
    base_branch_id = fields.Many2one('kw_res_branch', 'Location')

    @api.onchange('department_id')
    def onchange_department(self):
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.department_id.id), ('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.department_id:
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.section:
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}


class hr_contract_payroll(models.Model):
    _inherit = 'hr.contract'

    lwop = fields.Float(string='LWOP')
    salary_adv = fields.Float(string='Salary Advance')
    # current_ctc = fields.Integer(string="Current CTC")
    at_join_time_ctc = fields.Float(string=" CTC At Joining Time",track_visibility='always')
    basic_at_join_time = fields.Float(string="At Joining Time Basic",track_visibility='always')
    current_basic = fields.Float(string="Current Basic",track_visibility='always')
    # hra = fields.Integer(string="HRA(%)")
    conveyance = fields.Float(string="Conveyance",track_visibility='always')
    productivity = fields.Float(string="Productivity Bonus",track_visibility='always')
    commitment = fields.Float(string="Commitment Bonus",track_visibility='always')
    bonus = fields.Float(string="Bonus",track_visibility='always')
    hra_amount = fields.Float(compute='compute_hra_amount',track_visibility='always',string='HRA Amount')
    """ new fixed fields for CSM Dubai Branch """
    da = fields.Float(string="DA")
    conveyance_allowance = fields.Float(string="Conveyance Allowance (vehicle & Fuel)")
    communication_allowance = fields.Float(string="Communication Allowance (Internet/Phone)")
    entertainment_allowance = fields.Float(string="Entertainment Allowance")
    limit_pf_boolean = fields.Boolean(string="Set PF Basic Limit")
    limit_pf_basic = fields.Float(string="PF Basic Amount")
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF",track_visibility='always')
    enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity",track_visibility='always')
    esi_applicable = fields.Boolean(string='ESI APPLICABLE',track_visibility='always')
    pf_deduction = fields.Selection([('basicper', "12 % of basic"), ('avail1800', 'Flat 1,800/-'),('other','Other')] , string="PF Deduction",track_visibility='always')
    uan_id = fields.Char(string="UAN", help="UAN",track_visibility='always')
    esi_id = fields.Char(string="ESI Number", help="ESI Number",track_visibility='always')
    partner_id = fields.Many2one('res.partner',related="employee_id.user_id.partner_id")
    user_id = fields.Many2one('res.users',related="employee_id.user_id")

    bankaccount_id = fields.Many2one('res.partner.bank', string="Partner Bank", domain="[('partner_id','=',partner_id)]",track_visibility='always')
    is_consolidated= fields.Boolean("Is Consolidated ?",track_visibility='always')
    eps_enable = fields.Boolean("Enable EPS",track_visibility='always')
    # esic_number = fields.Char()
    emp_name = fields.Char(string="Employee",related='employee_id.name')
    code = fields.Char(string="Code", related='employee_id.emp_code')
    date_of_joining=fields.Date(string="Date of Joining" ,related='employee_id.date_of_joining' )
    base_branch_id=fields.Char(string="Base Location",related='employee_id.base_branch_id.name')
    bank = fields.Char(compute='update_bank_details',string='Call Onchange')
    bank_account = fields.Char(string="Account No")
    bank_id = fields.Many2one('res.bank', string="Bank",domain=[('account_type','=','csmacc')]) 
    salary_confirmed_bool = fields.Boolean("Check Salary Confirm",compute="_check_salary_confirm")
    personal_bank_name = fields.Char(string="Bank Name",readonly=False)
    personal_bank_account = fields.Char(string="Account No", readonly=False)
    personal_bank_ifsc = fields.Char(string="IFSC Code")
    epf_percent = fields.Float(string="Employee PF(%)",track_visibility='always')
    employer_pf= fields.Float(string ="Employer PF(%)",track_visibility='always')

    prof_persuit = fields.Float(string ="Professional Pursuit",track_visibility='always')
    ltc = fields.Float(string ="LTA (Leave Travel Allowance)",track_visibility='always')
    level = fields.Many2one('kw_grade_level')
    grade = fields.Many2one('kwemp_grade_master',related='employee_id.grade',store=True)\
        
    enable_nssf = fields.Boolean('Enable NSSF',track_visibility='always')
    nssf_no = fields.Char('NSSF No.',track_visibility='always')
    enable_nhif = fields.Boolean('Enable NHIF',track_visibility='always')
    nhif_no = fields.Char('NHIF No.',track_visibility='always')
    
    check_contract_bool = fields.Boolean('Check Contract',compute='_check_indian_contract')
    enable_jsw = fields.Boolean(string='Enable Mining Structure',track_visibility='always')
    jsw_pb_cb = fields.Float(string="Mining Allowance Factor",track_visibility='always')
    
    is_nps = fields.Selection([('Yes', 'Yes'),('No','No')],string="NPS",track_visibility='always')
    contribution = fields.Selection([(5, '5 % of Basic Salary'),(7, '7 % of Basic Salary'),(10, '10 % of Basic Salary'),(14, '14 % of Basic Salary')],string="NPS Contribution",track_visibility='always')
    existing_pran_no = fields.Selection([('Yes', 'Yes'),('No','No')],string="Existing PRAN",track_visibility='always')
    pran_no = fields.Char(string="PRAN",track_visibility='always')
    

    @api.onchange('is_nps')
    def change_nps_details(self):
        if self.is_nps == 'No':
            self.contribution = False
            self.existing_pran_no = False
            self.pran_no = False


    @api.onchange('enable_jsw')
    def change_jsw_amt(self):
        if self.enable_jsw == False:
            self.jsw_pb_cb = 0
    
   

    def update_salary_structure(self):
        if self.enable_jsw == False:
            self.productivity = self.commitment = self.conveyance = self.current_basic = self.house_rent_allowance_metro_nonmetro = self.ltc = self.prof_persuit = 0
            if self.wage > 0:
                pp_lta_slab = self.env['pp_lta_slab'].search([('ctc_from', '<=', (self.wage * 12)),('ctc_to', '>=', (self.wage * 12))], limit=1)
                self.write({
                    'current_basic': self.calculate_round_amount(0.4 * self.wage),
                    'house_rent_allowance_metro_nonmetro':40,
                    'conveyance':10,
                    'ltc':pp_lta_slab.lta if pp_lta_slab else 0,
                    'prof_persuit':pp_lta_slab.pp if pp_lta_slab else 0
                })
                hra_amount = self.calculate_round_amount(0.4 * self.current_basic)
                conveyance = self.calculate_round_amount(0.1 * self.current_basic) 
                if self.enable_gratuity == 'yes' and not self.is_consolidated:
                    gratuity_amount = (4.81/100) * self.current_basic
                    gratuity = self.calculate_round_amount(gratuity_amount)
                else:
                    gratuity = 0
                if self.enable_epf == 'yes' and not self.is_consolidated:
                    if self.pf_deduction == 'other':
                        if self.employer_pf:
                            employer_epf = self.calculate_round_amount(self.current_basic * self.employer_pf / 100)
                        else:
                            employer_epf = 0
                    elif self.pf_deduction == 'avail1800' and self.current_basic >= 15000:
                        employer_epf = 1800
                    else:
                        employer_epf = self.calculate_round_amount(self.current_basic * 12 / 100)
                else:
                    employer_epf = 0
                gross = self.current_basic + hra_amount + conveyance + self.ltc + self.prof_persuit 
                pb_cb_total = self.wage - gross - employer_epf - gratuity
                if pb_cb_total > 0:
                    if pb_cb_total % 2 != 0:
                        self.productivity = int(pb_cb_total / 2) + 1
                        self.commitment = int(pb_cb_total / 2)
                    else:
                        self.productivity = self.commitment = int(pb_cb_total / 2)
        else:
            if self.current_basic:
                self.productivity = self.commitment = self.conveyance = self.house_rent_allowance_metro_nonmetro = self.ltc = self.prof_persuit = 0
                if self.enable_gratuity == 'yes' and not self.is_consolidated:
                    gratuity_amount = (4.81/100) * self.current_basic
                    gratuity = self.calculate_round_amount(gratuity_amount)
                else:
                    gratuity = 0
                if self.enable_epf == 'yes' and not self.is_consolidated:
                    if self.pf_deduction == 'other':
                        if self.employer_pf:
                            employer_epf = self.calculate_round_amount(self.current_basic * self.employer_pf / 100)
                        else:
                            employer_epf = 0
                    elif self.pf_deduction == 'avail1800' and self.current_basic >= 15000:
                        employer_epf = 1800
                    else:
                        employer_epf = self.calculate_round_amount(self.current_basic * 12 / 100)
                else:
                    employer_epf = 0
                gross = self.current_basic
                # pb_cb_total = self.wage - gross - employer_epf - gratuity
                pb_cb_total = round(8.33/100*self.current_basic)+int(self.jsw_pb_cb)+round(((self.current_basic)*(365-52-8)/20/12/26))
                if pb_cb_total > 0:
                    if pb_cb_total % 2 != 0:
                        self.productivity = int(pb_cb_total / 2) + 1
                        self.commitment = int(pb_cb_total / 2)
                    else:
                        self.productivity = self.commitment = int(pb_cb_total / 2)
                self.wage = self.current_basic + self.productivity + self.commitment + employer_epf + gratuity





    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
        
    @api.depends('company_id')
    def _check_indian_contract(self):
        for rec in self:
                rec.check_contract_bool = True if rec.company_id.currency_id.name == 'INR' else False
                
    @api.onchange('grade')
    def onchange_emp_level(self):
        level = self.env['kw_grade_level'].search([('grade_ids', 'in', [self.grade.id])])
        if level.exists():
            self.level = level.id
        else:
            self.level = False

    # @api.onchange('prof_persuit','ltc','productivity')
    # def change_commitment(self):
    #     if self.prof_persuit  or self.ltc or self.productivity:
    #         self.commitment = self.productivity - self.prof_persuit  - self.ltc if (self.productivity - self.prof_persuit  - self.ltc) >=0 else 0

    @api.constrains('bank_account')
    def _check_bank_account(self):
        for rec in self:
            if rec.bank_account:
                record = self.env['hr.contract'].sudo().search([('bank_account', '=', rec.bank_account),('state','=','open')]) - self
                if record:
                    raise ValidationError(f"Duplicate entry found for account number - {record.bank_account}")

    @api.constrains('epf_percent','employer_pf')
    def _check_epf_deduction(self):
        for rec in self:
            if rec.pf_deduction == 'other':
                if rec.epf_percent < 12 or rec.epf_percent > 100:
                    raise ValidationError("Please insert the valid PF percentage.")
                if rec.employer_pf < 12 or rec.employer_pf > 100:
                    raise ValidationError("Please insert the valid Employer PF percentage.")

    # def _auto_init(self):
    #     super(hr_contract_payroll, self)._auto_init()
    #     self.env.cr.execute("update hr_contract a set uan_id = (select uan_id from hr_employee where id = a.employee_id),is_consolidated =(select is_consolidated from hr_employee where id = a.employee_id),enable_epf=(select enable_epf from hr_employee where id = a.employee_id),pf_deduction=(select pf_deduction from hr_employee where id = a.employee_id),enable_gratuity=(select enable_gratuity from hr_employee where id = a.employee_id),esi_applicable=(select esi_applicable from hr_employee where id = a.employee_id),esi_id=(select esi_id from hr_employee where id = a.employee_id),bankaccount_id=(select bank_account_id from hr_employee where id = a.employee_id)")
    
    # def _auto_init(self):
    #     super(hr_contract_payroll, self)._auto_init()
    #     self.env.cr.execute("update hr_contract a set pf_deduction = 'basicper' where pf_deduction = 'False' and state = 'open'")
        
    def _check_salary_confirm(self):
        for rec in self:
            if rec.state == 'open':
                payslip = self.env["hr.payslip"].sudo().search([('state','=','done'),('employee_id' ,'=', rec.employee_id.id )])
                if payslip:
                    rec.salary_confirmed_bool = True
                else :
                    rec.salary_confirmed_bool = False

    @api.onchange('is_consolidated')
    def change_contract_values(self):
        if self.is_consolidated == True:
            self.enable_epf = 'no'
            # self.pf_deduction = 'basicper'
            self.eps_enable = False
            self.enable_gratuity = 'no'
            self.esi_applicable = False
            
    @api.onchange('pf_deduction','is_consolidated','enable_epf')
    def change_pf_deduction(self):
        if self.pf_deduction != 'other' or self.is_consolidated == False or self.enable_epf == 'no':
            self.epf_percent = 0
            self.employer_pf = 0

    @api.depends('house_rent_allowance_metro_nonmetro')
    def compute_hra_amount(self):
        for rec in self:
            if rec.house_rent_allowance_metro_nonmetro:
                rec.hra_amount = rec.calculate_round_amount(rec.current_basic * (rec.house_rent_allowance_metro_nonmetro / 100))

    @api.constrains('state', 'conveyance', 'house_rent_allowance_metro_nonmetro')
    def compute_duplicate_rec(self):
        for res in self:
            contract_ids = self.env['hr.contract'].search(
                [('employee_id', '=', res.employee_id.id), ('state', '=', 'open')])
            if len(contract_ids) > 1:
                raise ValidationError(_('Multiple active contracts are not allowed for same Employee.'))
            if res.conveyance > 100 or res.conveyance < 0:
                raise ValidationError(_('Conveyance can not be more than 100 or less than 0'))
            if res.house_rent_allowance_metro_nonmetro > 100 or res.house_rent_allowance_metro_nonmetro < 0:
                raise ValidationError(_('HRA can not be more than 100 or less than 0'))

    @api.onchange('productivity', 'conveyance', 'current_basic', 'wage', 'house_rent_allowance_metro_nonmetro',
                  'at_join_time_ctc', 'basic_at_join_time', 'enable_epf', 'enable_gratuity', 'esi_applicable','pf_deduction','uan_id','esi_id','is_consolidated','bank_account','bank_id','personal_bank_name','personal_bank_account','personal_bank_ifsc')
    def update_payroll_info(self):
        for rec in self:
            if rec.state == 'open' and rec.employee_id:
                query_1 = ''
                query_1 = f"UPDATE hr_employee SET current_basic = {rec.current_basic}, productivity = {rec.productivity}, conveyance = {rec.conveyance},current_ctc = {rec.wage},hra = {rec.house_rent_allowance_metro_nonmetro},at_join_time_ctc = {rec.at_join_time_ctc},basic_at_join_time = {rec.basic_at_join_time},enable_epf = '{rec.enable_epf}', esi_applicable = '{rec.esi_applicable}',is_consolidated = '{rec.is_consolidated}',personal_bank_ifsc = '{rec.personal_bank_ifsc if rec.personal_bank_ifsc else ''}',personal_bank_name = '{rec.personal_bank_name if rec.personal_bank_name else ''}',personal_bank_account = '{rec.personal_bank_account if rec.personal_bank_account else ''}' WHERE id = {rec.employee_id.id};"
                if rec.enable_gratuity in ['yes','no']:
                    query_1 += f"UPDATE hr_employee SET enable_gratuity = '{rec.enable_gratuity}' WHERE id = {rec.employee_id.id};"
                if rec.pf_deduction in ['basicper','avail1800']:
                    query_1 += f"UPDATE hr_employee SET pf_deduction = '{rec.pf_deduction}' WHERE id = {rec.employee_id.id};"
                if rec.bank_account:
                    query_1 += f"UPDATE hr_employee SET bank_account = '{rec.bank_account}' WHERE id = {rec.employee_id.id};"
                if rec.bank_id:
                    query_1 += f"UPDATE hr_employee SET bankaccount_id = {rec.bank_id.id} WHERE id = {rec.employee_id.id};"
                if rec.uan_id:
                    query_1 += f"UPDATE hr_employee SET uan_id = '{rec.uan_id}' WHERE id = {rec.employee_id.id};"
                else:
                    query_1 += f"UPDATE hr_employee SET uan_id = '' WHERE id = {rec.employee_id.id};"
                if rec.esi_id:
                    query_1 += f"UPDATE hr_employee SET esi_id = '{rec.esi_id}' WHERE id = {rec.employee_id.id};"
                else:
                    query_1 += f"UPDATE hr_employee SET esi_id = '' WHERE id = {rec.employee_id.id};"
                self._cr.execute(query_1)

    @api.depends('bank_account','bank_id')
    def update_bank_details(self):
        for rec in self:
            rec.update_payroll_info()

    @api.multi
    def copy(self, default=None):
        self.state = 'close'
        res = super(hr_contract_payroll, self).copy(default)
        res.date_start = self.date_end
        res.date_end = False
        res.state = 'open'
        return res

    ### Contract End Scheduler
    def contract_end(self):
        previous_month_date = (date.today() - relativedelta(months=1)).replace(day=25)
        employee_model = self.env['hr.employee']
        ex_employee_ids = employee_model.search([('last_working_day','<=',previous_month_date),('active', '=', False)])
        contract = self.env['hr.contract'].sudo().search(['|',('active','=',True),('active', '=', False)])
        for emp in ex_employee_ids:
            contract_id = contract.filtered(lambda x:x.employee_id.id == emp.id and x.state == 'open')
            if contract_id:
                contract_id.write({'state':'close'})
        outsourced_contract = contract.filtered(lambda x:x.employee_id.employement_type.code == 'O' and x.state == 'open')
        if outsourced_contract:
            outsourced_contract.write({'state':'close'})
        archieved_contract = contract.filtered(lambda x: x.active == False)
        if archieved_contract:
            archieved_contract.write({'state':'close','active':True})  

    def contact_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                                  notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
            # print(values)                    

            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)
            mail = self.env['mail.mail'].create(values)
            if force_send:
                mail.send(raise_exception=raise_exception)
            mail.model = False
            return mail.id

    @api.onchange('current_basic')
    def update_hra(self):
        for rec in self:
            if rec.current_basic and rec.house_rent_allowance_metro_nonmetro:
                rec.hra_amount = rec.current_basic * (rec.house_rent_allowance_metro_nonmetro / 100)

    @api.model
    def check_pending_bank_details(self):
        current_employee = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id)],limit=1)
        if not current_employee:
            return False
        else:
            if current_employee.date_of_joining:
                contract = self.env['hr.contract'].sudo().search([('employee_id','=',current_employee.id),('state','=','open')],limit=1)
                if contract:
                    if ((date.today() - current_employee.date_of_joining).days + 1 > 10
                        and (not current_employee.bankaccount_id or not current_employee.bank_account)
                        and current_employee.enable_payroll == 'yes') \
                            or ((date.today() - current_employee.date_of_joining).days + 1 > 10
                                and (not contract.bank_id or not contract.bank_account)
                                and current_employee.enable_payroll == 'yes'):
                        result_url = f"/update-bank-details/{slug(current_employee)}"
                        return result_url             
    
        


    @api.model
    def check_pending_nps_details(self):
        current_employee = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id),('enable_payroll','=','yes')],limit=1)
        if not current_employee:
            return False
        else:
            if current_employee.date_of_joining and current_employee.enable_payroll=='yes':
                contract = self.env['hr.contract'].sudo().search([('employee_id','=',current_employee.id),('state','=','open')],limit=1)
                # payslip =  self.env['hr.payslip'].sudo().search([('employee_id','=',current_employee.id),('state','=','done')],limit=1)
                emp_profile =  self.env['kw_emp_profile'].sudo().search([('emp_id','=',current_employee.id)])
                if contract and emp_profile:
                    if len(emp_profile.employee_nps_id) == 0:
                        result_url = f"/update-nps-details/{slug(current_employee)}"
                        return result_url

class EmployeeResBank(models.Model):
    _inherit = 'res.partner.bank'

    def get_employee(self):
        user = self.env['res.users'].sudo().search([('id', '=', self.env.context.get('active_user'))])
        return user.partner_id

    def get_bank(self):
        bank = self.env['res.bank'].sudo().search([('id', '=', self.env.context.get('user_bank'))])
        return bank

    def get_employee_name(self):
        user = self.env['res.users'].sudo().search([('id', '=', self.env.context.get('active_user'))])
        return user.employee_ids.name

    partner_id = fields.Many2one(comodel_name="res.partner", string="Account Holder", default=get_employee)
    bank_id = fields.Many2one(comodel_name="res.bank", string="Bank", default=get_bank)
    acc_holder_name = fields.Char(string="Account Holder Name", default=get_employee_name)


class payrolladvanceinherit(models.Model):
    _inherit = 'kw_advance_apply_salary_advance'

    kw_id = fields.Integer(string="Tendrils Id")


class PartnerBankInherit(models.Model):
    _inherit = "res.bank"

    def account_set(self):
        if self._context.get('type'):
           return 'csmacc'
        else:
           return 'otheracc'
       
    kw_id = fields.Integer(string='Tendrils Id')
    account_type = fields.Selection([('csmacc','CSM Account'),('otheracc','Other Account')],string="Account Type",default=account_set)

    @api.constrains('bic')
    def validate_ifsc(self):
        for rec in self:
            record = self.env['res.bank'].sudo().search([('bic', '=', rec.bic)]) - self
            if record:
                raise ValidationError(f"Duplicate entry found for IFSC - {rec.bic}.")

