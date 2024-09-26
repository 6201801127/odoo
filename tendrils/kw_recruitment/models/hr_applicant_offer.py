# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime, date, timedelta
import base64
import math
from odoo.addons.kw_utility_tools import kw_helpers
from odoo.tools.misc import formatLang


class hr_applicant_offer(models.Model):
    _name = "hr.applicant.offer"
    _description = 'Offer Letter'
    _rec_name = "ref_code"
    _order = "id desc"

    # @api.model
    # def _get_no_month(self):
    #     return [(str(x), str(x)) for x in range(1, 25)]

    offer_type = fields.Selection(
        [('Intern', 'Intern'), ('Lateral', 'Lateral'), ('RET', 'RET'), ('Offshore', 'Offshore')],
        string='Offer Letter Type', default='Intern')
    ref_code = fields.Char("Reference No.")
    current_date = fields.Date('Date')
    salutation = fields.Many2one('res.partner.title', track_visibility='always')
    name = fields.Char('Name')
    designation = fields.Many2one('hr.job', string='Job Position')
    department = fields.Many2one('hr.department', string='Department', domain=[('parent_id', '=', False)])
    job_location = fields.Many2one('kw_res_branch', string="Base Branch")
    job_location_id = fields.Many2one('kw_recruitment_location', string="Job Location")
    joining_date = fields.Date('Joining Date')
    city_id = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    currency_id = fields.Many2one('res.currency', 'Currency', default=20)
    first_amount = fields.Integer('Monthly Stipend')
    revised_amount = fields.Integer('Revised Monthly CTC', help="Based on the positive feedback of your multiple technical assessments, the monthly stipend will be revised i.e Revised Monthly CTC")
    annual_amount = fields.Integer('Annual CTC After Traineeship')
    annual_amount_lateral = fields.Integer('Monthly CTC')
    annual_amount_offshore = fields.Integer('Monthly CTC')
    monthly_ctc = fields.Integer('Monthly CTC')
    annual_amount_ret = fields.Integer('Total CTC')
    months = fields.Char('No of months', help='These months are in which one go for Probation/Training.')
    days = fields.Char('No of days', help='These days are in which one go for Offshore.')
    # months = fields.Selection('_get_no_month', 'No of months', help='These months are in which one go for Probation/Training.')
    agreement_months = fields.Char('Agreement Months')
    contract_expiry_ret = fields.Selection([('Month', 'Month'), ('Date', 'Date')], string='Expiry Type (Months/Date)', default="Month")
    contract_end_date_ret = fields.Date('Contract End Date')

    type_dmy = fields.Selection([('Month', 'Month'), ('Year', 'Year')], string='Type(Months/Years)', default="Month")
    acceptance_date = fields.Datetime('Acceptance Date')
    contact_no = fields.Char('Contact No.')
    update_basic = fields.Integer(string='Percentage of basic (%)', default=40)
    annexture_offer1 = fields.One2many('offer.details', 'offer_id')
    annexure_offer2 = fields.One2many('offer.details', 'offer_id1')
    annexure_offer3 = fields.One2many('offer.details', 'offer_id2')

    average_1_month = fields.Integer('Total Compensation Per Month', compute="total_calculation")
    average_1_year = fields.Integer('Total Compensation Per Year', compute="total_calculation")

    average_2_month = fields.Integer('Statutory Deductions (E = B + D) Per Month', compute="total_calculation")
    average_2_year = fields.Integer('Statutory Deductions (E = B + D) Per Year', compute="total_calculation")

    average_3_month = fields.Integer('Net Salary (F = C - E) Per Month', compute="total_calculation")
    average_3_year = fields.Integer('Net Salary (F = C - E) Per Year', compute="total_calculation")

    avail_pf_benefit = fields.Boolean('Avail PF Benefits', default=True)
    avail_health_insurance = fields.Boolean('Avail Health Insurance', default=True)
    active = fields.Boolean('Active', default=True)
    budget_amount = fields.Integer(string='Budget Amount', readony=True, related="applicant_id.budget_amount")
    pf_deduction = fields.Selection([('basicper', "12 % of basic"), ('avail1800', 'Flat 1,800/-')],
                                    string='PF Deduction', default='basicper')
    notice_period_days = fields.Char("Notice period(in days)", default=90)
    professional_tax_applicable = fields.Boolean('Professional Tax Applicable', default=True)
    gratuity_applicable = fields.Boolean('Gratuity Applicable', default=True)
    email_of_applicant = fields.Char(related="applicant_id.email_from",string="Email")

    relevant_exp_year = fields.Integer(string="Year(s)", required=False)
    relevant_exp_month = fields.Integer(string="Month(s)", required=False)
    create_user_offer = fields.Boolean(string="Create offer", compute="get_offer_create_user_check")
    struct_id = fields.Many2one('hr.payroll.structure', track_visibility='always', string="Payroll Structure")

    def get_offer_create_user_check(self):
        for rec in self:
            if self.env.user.has_group('kw_recruitment.group_offer_created_user'):
                rec.create_user_offer = True

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.amount_in_word = kw_helpers.num_to_words(rec.first_amount) + ' only'

    @api.multi
    def _compute_amount_in_word_revised(self):
        for rec in self:
            rec.amount_in_word_reviised = kw_helpers.num_to_words(rec.revised_amount) + ' only'

    @api.multi
    def _compute_amount_in_word_annual(self):
        for rec in self:
            rec.amount_in_word_annual = kw_helpers.num_to_words(rec.annual_amount) + ' only'

    @api.multi
    def _compute_amount_in_word_annual_lat(self):
        for rec in self:
            rec.amount_in_word_annual_lat = kw_helpers.num_to_words(rec.annual_amount_lateral) + ' only'

    @api.multi
    def _compute_amount_in_word_annual_ret(self):
        for rec in self:
            rec.amount_in_word_annual_ret = kw_helpers.num_to_words(rec.annual_amount_ret) + ' only'

    @api.multi
    def _compute_amount_in_word_month_ret(self):
        for rec in self:
            rec.amount_in_word_month_ret = kw_helpers.num_to_words(rec.monthly_ctc) + ' only'

    @api.multi
    def _compute_amount_in_word_month_off(self):
        for rec in self:
            rec.amount_in_word_month_off = kw_helpers.num_to_words(rec.annual_amount_offshore) + ' only'

    amount_in_word = fields.Char('Amount in Words', compute='_compute_amount_in_word')
    amount_in_word_reviised = fields.Char('Revised Amount in Words', compute='_compute_amount_in_word_revised')
    amount_in_word_annual = fields.Char('Annual Amount in Words', compute='_compute_amount_in_word_annual')
    amount_in_word_annual_lat = fields.Char('Monthly Amount in Words', compute='_compute_amount_in_word_annual_lat')
    amount_in_word_month_ret = fields.Char('Monthly Amount in Words', compute='_compute_amount_in_word_month_ret')
    amount_in_word_annual_ret = fields.Char('Annual Amount in Words', compute='_compute_amount_in_word_annual_ret')
    amount_in_word_month_off = fields.Char('Monthly Amount in Words', compute='_compute_amount_in_word_month_off')
    average_1_year_in_word = fields.Char('Total Compensation Per Year in Word',
                                         compute="total_calculation")

    applicant_id = fields.Many2one('hr.applicant', "Applicant")
    pt_type = fields.Selection([('Probation', 'Probation'), ('Traineeship', 'Traineeship')],
                               string='Probation/Traineeship')
    offer_accpet_bool = fields.Boolean('Offer Acceptance', compute="compute_offer_acceptance")
    resend_mail_bool = fields.Boolean('Resend Boolean')
    status = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')],
                              string='Status', default="draft")
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)
    companys_contribution = fields.Integer(
        "Company's contribution towards benefits for Medical & Accident Insurance",
        compute='_compute_company_contribution')
    companys_accidental_contribution = fields.Integer("Company's contribution towards benefits for Accident Insurance",
                                                      compute='_compute_company_contribution')
    annual_remuneration = fields.Integer('Total CTC (Cost-to-Company)', compute='_compute_company_contribution')
    emp_band = fields.Many2one('kwemp_band_master', string='Band')
    grade = fields.Many2one('kwemp_grade_master', string='Grade')
    tmp_has_band = fields.Boolean('Has Band')
    # earned_leaves = fields.Float('Earned Leaves', compute="get_leaves_allocated", digits=(5, 0), store=True)
    # medical_leave = fields.Float('Medical Leaves', compute="get_leaves_allocated", digits=(5, 0), store=True)
    # casual_leave = fields.Float('Casual Leaves', compute="get_leaves_allocated", digits=(5, 0), store=True)

    earned_leaves = fields.Selection(string='Earned Leaves', selection=[(0, 0), (8, 8), (10, 10), (12, 12), (15, 15)])
    medical_leave = fields.Selection(string='Medical Leaves', selection=[(15, 15)], default=15)
    casual_leave = fields.Selection(string='Casual Leaves', selection=[(6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])

    @api.onchange('update_basic')
    def _onchange_update_basic(self):
        for rec in self:
            if not 0 <= rec.update_basic <= 100:
                raise ValidationError('The percentage of Basic should be between 0 to 100.')
    # @api.depends("grade")
    # def get_leaves_allocated(self):
    #     for rec in self:
    #         leave_quantity = 0.00
    #         # earned_leaves = medical_leaves = casual_leaves = remaining_set = False
    #         leaves = self.env['kw_leave_type_config'].sudo().search(
    #             [('leave_type_id.leave_code', 'in', ['ML', 'EL', 'CL']), ('branch_id', '=', rec.job_location.id)])
    #         remaining_set = {'ML', 'EL', 'CL'} - {rec.leave_type_id.leave_code for rec in leaves} if leaves else False
    #         # print("leaves >>>>>>>> 1 ", leaves, remaining_set)
    #         if (not leaves or len(leaves) < 3) and remaining_set:
    #             # print("remaining_set >>>>>>>> 2 ", remaining_set)
    #             leaves += self.env['kw_leave_type_config'].sudo().search(
    #                 [('leave_type_id.leave_code', 'in', list(remaining_set))])
    #         # print("leaves >>>>>>>> 3", leaves)
    #     # for rec in self:
    #         for rec_leaves in leaves:
    #             leave_quantity = 0
    #             for rec_lines in rec_leaves.grade_wise_leaves:
    #                 # print('rec_lines',rec.grade.id,rec.emp_band.id, rec_lines.grade_ids.ids, rec_lines.band_ids.ids)
    #                 if rec.grade and rec.emp_band:
    #                     if (rec.grade.id in rec_lines.grade_ids.ids) and (rec.emp_band.id in rec_lines.band_ids.ids):
    #                         # print('======================', rec_leaves.leave_type_id.leave_code, rec_lines.quantity)
    #                         leave_quantity = rec_lines.quantity
    #                 else:
    #                     if rec.grade and (rec.grade.id in rec_lines.grade_ids.ids):
    #                         # print('=======else', rec_leaves.leave_type_id.leave_code, rec_lines.quantity)
    #                         leave_quantity = rec_lines.quantity
    #             if rec_leaves.leave_type_id.leave_code == 'EL':
    #                 rec.earned_leaves = leave_quantity
    #             elif rec_leaves.leave_type_id.leave_code == 'CL':
    #                 rec.casual_leave = leave_quantity
    #             elif rec_leaves.leave_type_id.leave_code == 'ML':
    #                 rec.medical_leave = leave_quantity
    #
    # @api.onchange('emp_band')
    # def onchange_band(self):
    #     for rec in self:
    #         rec.get_leaves_allocated()

    @api.onchange('grade')
    def onchange_tmp_grade(self):
        for rec in self:
            rec.emp_band = False
            if rec.grade.has_band:
                rec.tmp_has_band = True
            else:
                rec.tmp_has_band = False
            # rec.get_leaves_allocated()

    @api.multi
    def write(self, values):
        # rec = self.env['hr.applicant.offer'].sudo().search([('id', '=', self.id)])
        result = super(hr_applicant_offer, self).write(values)
        for rec in self:
            # applicant_id = self.env['hr.applicant'].sudo().search([('id', '=', rec.applicant_id.id)])
            if rec.applicant_id:
                rec.applicant_id.write({'department_id': rec.department.id,
                                        'job_id': rec.designation.id,
                                        'joining_date': rec.joining_date,
                                        'relevant_exp_month': rec.relevant_exp_month,
                                        'relevant_exp_year': rec.relevant_exp_year})
        self.env.user.notify_success(message='Offer updated successfully.')
        return result

    def compute_offer_acceptance(self):
        for rec in self:
            OA_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'OA')])
            if rec.applicant_id.stage_id == OA_stage:
                rec.offer_accpet_bool = True
                # rec.offer_accpet_bool = False

    def _compute_company_contribution(self):
        for rec in self:
            health_conf = self.env['hr.recruitment.health.insurance.config'].search(
                [('from_date', '<=', rec.current_date), ('to_date', '>=', rec.current_date)])
            health_conf_acci = self.env['hr.recruitment.health.accidental.insurance.config'].search(
                [('from_date', '<=', rec.current_date), ('to_date', '>=', rec.current_date)])
            # print('rec.current_date ', rec.current_date)
            # print('health_conf ', health_conf)
            # print('health_conf_acci ', health_conf_acci)
            # print('rec.avail_health_insurance ', rec.avail_health_insurance)
            gross = rec.average_1_year
            employer_epf, gratuity = 0, 0
            for rec_line in rec.annexure_offer2:
                employer_epf = rec_line.per_year
            for rec_line in rec.annexure_offer3:
                if rec_line.code == 'gratuity':
                    gratuity = rec_line.per_year
            ctc_per_year = gross + employer_epf + gratuity
            if rec.avail_health_insurance is True:
                health_insurance_for_offshore = health_conf.filtered(lambda x: x.offer_type == 'Offshore')
                health_insurance_for_lir = health_conf.filtered(lambda x: x.offer_type != 'Offshore')
                # for record in health_rec:
                if rec.offer_type == "Offshore":
                    if rec.average_1_month >= 21000:
                        rec.companys_contribution = health_insurance_for_offshore.amount
                    rec.annual_remuneration = ctc_per_year
                elif rec.offer_type in ['Lateral', 'Intern', 'RET']:
                    if rec.average_1_month >= 21000:
                        rec.companys_contribution = health_insurance_for_lir.amount
                    rec.annual_remuneration = ctc_per_year + rec.companys_contribution
            elif rec.average_1_month <= 21000:
                rec.companys_accidental_contribution = health_conf_acci.amount
                rec.annual_remuneration = ctc_per_year + rec.companys_accidental_contribution
            else:
                rec.annual_remuneration = ctc_per_year + rec.companys_contribution

    # def compute_current_date(self):
    #     for rec in self:
    #         if rec.applicant_id.offer_date:
    #             rec.current_date = rec.applicant_id.offer_date
    #         else:
    #             rec.current_date = datetime.now().date()

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('hr.applicant.offer') or 'New'
        # active = self.env['hr.applicant.offer'].browse()
        list_no = str(values.get('current_date')).split('-')

        if values.get('department') and values.get('job_location_id'):
            dept = self.env['hr.department'].browse([values.get('department')])
            job = self.env['kw_recruitment_location'].browse([values.get('job_location_id')])
            new_code = 'CSMPL/OL/' + job.kw_branch_id.recruitment_ref + '/' + dept.code + '/' + list_no[2] + '-' + list_no[1] + '/' + code
            values['ref_code'] = new_code

        result = super(hr_applicant_offer, self).create(values)
        return result

    @api.constrains('offer_type', 'revised_amount', 'annual_amount', 'annual_amount_lateral', 'annual_amount_offshore', 'annual_amount_ret')
    def check_budget_amount(self):
        for rec in self:
            if rec.offer_type == 'Intern':
                annual_amount = rec.revised_amount
            elif rec.offer_type == 'Lateral':
                annual_amount = rec.annual_amount_lateral
            elif rec.offer_type == 'Offshore':
                annual_amount = rec.annual_amount_offshore
            elif rec.offer_type == 'RET':
                annual_amount = rec.monthly_ctc
            if rec.budget_amount < annual_amount:
                raise ValidationError("Monthly CTC cannot exceed Budget Amount.")

    @api.onchange('monthly_ctc')
    def _onchange_monthly_ctc(self):
        for rec in self:
            rec.annual_amount_ret = rec.monthly_ctc * 12

    @api.onchange('offer_type')
    def _onchange_offer_type(self):
        kpi_kpa = []
        kpi_kpa1 = []
        kpi_kpa3 = []
        contact_code = False

        master_data = self.env['offer.details.master'].search([('id', '=', 1)])
        emp_data = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])

        if emp_data:
            # print('emp_data.epbx_noemp_data.epbx_noemp_data.epbx_no', emp_data)
            if not emp_data.epbx_no:
                emp_data.epbx_no = '5934'
            emp = emp_data.epbx_no.split(' ')[0][0]
            emp1 = emp_data.epbx_no.split(' ')[0][1:4]
            # print('empempempempemp',emp, emp1)
            contact_code = '0674-663' + str(emp) + '-' + str(emp1)
            # print('contact_description contact_description', contact_description)
        for rec in self:
            rec.contact_no = contact_code
            # if rec.applicant_id:
            #     if rec.applicant_id.requisition_type == 'project':
            #         if rec.offer_type == 'Intern':
            #             rec.first_amount = rec.applicant_id.budget_amount
            #         if rec.offer_type == 'Lateral':
            #             rec.annual_amount_lateral = rec.applicant_id.budget_amount * 12
            #         if rec.offer_type == 'RET':
            #             rec.monthly_ctc = rec.applicant_id.budget_amount

            #  Annex 1
            rec.update_basic = master_data.annexture_offer1.filtered(lambda x: x.code == 'basic').percentage
            if not rec.annexture_offer1:
                for offer1 in master_data.annexture_offer1:
                    kpi_kpa.append((0, 0, {
                        'offer_id': rec.id,
                        'component': offer1.component,
                        'description': offer1.description,
                        'percentage': offer1.percentage,
                        'code': offer1.code
                    }))
                rec.annexture_offer1 = kpi_kpa
            else:
                for config in master_data.annexture_offer1:
                    for annex1 in rec.annexture_offer1:
                        if config.description == annex1.description:
                            annex1.percentage = config.percentage
                            annex1.code = config.code
            # Annex 2
            if not rec.annexure_offer2:
                for offer2 in master_data.annexture_offer2:
                    kpi_kpa1.append((0, 0, {
                        'offer_id1': rec.id,
                        'component': offer2.component,
                        'description': offer2.description,
                        'percentage': offer2.percentage,
                        'code': offer2.code
                    }))
                rec.annexure_offer2 = kpi_kpa1
            else:
                for config in master_data.annexture_offer2:
                    for annex2 in rec.annexure_offer2:
                        if config.description == annex2.description:
                            annex2.percentage = config.percentage
                            annex2.code = config.code

            # check for Offshore type offer letter for Annex 3
            if rec.offer_type == 'Offshore':
                annexure_offer3 = master_data.annexture_offer3
            else:
                annexure_offer3 = master_data.annexture_offer3.filtered(lambda x: x.code != 'hi')
            if not rec.annexure_offer3:
                for offer3 in annexure_offer3:
                    kpi_kpa3.append((0, 0, {
                        'offer_id2': rec.id,
                        'component': offer3.component,
                        'description': offer3.description,
                        'percentage': offer3.percentage,
                        'code': offer3.code
                    }))
                rec.annexure_offer3 = kpi_kpa3
            else:
                # Update annexure code and percentage
                for config in annexure_offer3:
                    for annex3 in rec.annexure_offer3:
                        if config.description == annex3.description:
                            annex3.percentage = config.percentage
                            annex3.code = config.code

                # Adding missing records in annexure 3
                missing_records = list(set(annexure_offer3.mapped('code')) - set(rec.annexure_offer3.mapped('code')))
                if missing_records:
                    for offer3 in annexure_offer3:
                        if offer3.code in missing_records:
                            kpi_kpa3.append((0, 0, {
                                'offer_id2': rec.id,
                                'component': offer3.component,
                                'description': offer3.description,
                                'percentage': offer3.percentage,
                                'code': offer3.code
                            }))
                    rec.annexure_offer3 = kpi_kpa3

                # removing extra records from annexure 3
                extra_records = list(set(rec.annexure_offer3.mapped('code')) - set(annexure_offer3.mapped('code')))
                if extra_records:
                    for offer3 in rec.annexure_offer3:
                        if offer3.code in extra_records:
                            kpi_kpa3.append((2, offer3.id, ))
                    rec.annexure_offer3 = kpi_kpa3

    @api.onchange('job_location_id')
    def _onchange_job_location_id(self):
        for rec in self:
            if rec.job_location_id:
                rec.job_location = rec.job_location_id.kw_branch_id.id
                rec.city_id = rec.job_location_id.name
                rec.state_id = rec.job_location_id.kw_branch_id.state_id.id

    @api.depends('annexture_offer1', 'annexure_offer2', 'annexure_offer3')
    def total_calculation(self):
        for rec in self:
            final_gross = 0
            final_gross_month = 0
            total_ctc = 0
            total_ctc_month = 0
            allowance = 0
            deductions = 0
            allowance_month = 0
            deductions_month = 0
            deductions2 = 0
            deductions2_month = 0
            net_inhand = 0
            net_inhand_month = 0
            deductions2_year =0
            for line in rec.annexture_offer1:
                if line.per_year:
                    final_gross += int(line.per_year)
                    final_gross_month += int(line.per_month)
                    allowance = final_gross
                    allowance_month = final_gross_month
            for line in rec.annexure_offer2:
                if line.per_year:
                    deductions += int(line.per_year)
                    deductions_month += int(line.per_month)
            for line in rec.annexure_offer3:
                if line.per_year and line.code == 'gratuity':
                        deductions2_year = int(line.per_year)
                if line.per_year and line.code != 'gratuity':
                    deductions2 += int(line.per_year)
                    deductions2_month += int(line.per_month)
            total_ctc = allowance + deductions + deductions2_year
            total_ctc_month = allowance_month + deductions_month
            # print("allowance_month >> ", allowance_month, deductions_month, deductions2_month)
            rec.average_1_year = allowance
            rec.average_1_year_in_word = kw_helpers.num_to_words(total_ctc) + ' only'
            rec.average_1_month = allowance_month

            rec.average_2_year = deductions2
            rec.average_2_month = deductions2_month

            net_inhand = rec.average_1_year - rec.average_2_year
            net_inhand_month = rec.average_1_month - rec.average_2_month
            rec.average_3_month = net_inhand_month
            rec.average_3_year = net_inhand_month * 12

    def button_send_email(self):
        template_id = self.env.ref('kw_recruitment.offer_letter_email_template')
        action_id = self.env.ref('hr_recruitment.crm_case_categ0_act_job').id
        # action_id = self.env['ir.actions.act_window'].search([('view_id', '=', recruitmentview.id)], limit=1).id
        db_name = self._cr.dbname

        recruitment_group = self.env.ref('kw_recruitment.group_hr_recruitment_offer_letter_notification')
        recruitment_emp = recruitment_group.users and recruitment_group.users.mapped('employee_ids') or False
        email_cc_users = recruitment_emp and recruitment_emp.mapped('work_email') or []
        email_cc_users.append(self.create_uid.email)
        cc_emails = ','.join(set(email_cc_users))
        # print(f"email_cc_users  >>> {email_cc_users} >>>> {cc_emails }")
        # return 0

        # logtable = self.env['hr_applicant_offer'].search([('applicant_id', '=', record.id)])
        # template_obj = self.env.ref('kw_recruitment.approve_forward_request_template')
        if self.applicant_id:
            offer_letter_token = self.env['kw_recruitment_requisition_approval'].create(
                {'applicant_id': self.applicant_id.id, 'offer_id': self.id})
            # print("token created-",cc_emails,db_name,action_id,offer_letter_token)

            mail_res = template_id.sudo().with_context(extra_params=cc_emails,
                                                       dbname=db_name,
                                                       action_id=action_id,
                                                       token=offer_letter_token.access_token,
                                                       id=self.id).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("Mail sent successfully.")

            # update offer letter status
            self.write({'status': 'sent'})

            # update applicant's stage to offer release stage
            for rec in self:
                offer_release_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'OR')])
                rec.applicant_id.stage_id = offer_release_stage.id
                # rec.applicant_id.stage_id = self.env.ref('hr_recruitment.stage_job4').id

    def auto_calculate(self):
        # lta_applicant = [{'min': 700000, 'max': 999999, 'amount': 5000},
        #                  {'min': 1000000, 'max': 1499999, 'amount': 5000},
        #                  {'min': 1500000, 'max': 10000000, 'amount': 6000}]
        # pp_applicant = [{'min': 700000, 'max': 999999, 'amount': 4000},
        #                 {'min': 1000000, 'max': 1499999, 'amount': 5000},
        #                 {'min': 1500000, 'max': 10000000, 'amount': 5000}]
      
        for rec in self:
            for record in rec.annexture_offer1:
                if record.code == 'basic':
                    record.percentage = rec.update_basic
        sum_month = 0
        sum_month1 = 0
        basic = self.env['offer.details'].search([('code', '=', 'basic'), ('offer_id', '=', self.id)])
        for rec in self.annexture_offer1:
            rec.per_month = 0
            rec.per_year = 0
            if rec.code == 'basic':
                if self.offer_type == 'Intern':
                    rec.per_month = (rec.offer_id.revised_amount * rec.percentage) / 100
                elif self.offer_type == 'Lateral':
                    # rec.per_month = ((rec.offer_id.annual_amount_lateral / 12) * rec.percentage) / 100
                    rec.per_month = (rec.offer_id.annual_amount_lateral * rec.percentage) / 100
                elif self.offer_type == 'Offshore':
                    # rec.per_month = ((rec.offer_id.annual_amount_offshore / 12) * rec.percentage) / 100
                    rec.per_month = (rec.offer_id.annual_amount_offshore * rec.percentage) / 100
                elif self.offer_type == 'RET':
                    rec.per_month = (rec.offer_id.monthly_ctc * rec.percentage) / 100

            if rec.percentage > 0.00:
                if rec.per_month:
                    rec.per_year = rec.per_month * 12
                if rec.code == 'hra':
                    rec.per_month = (basic.per_month * rec.percentage) / 100
                    if rec.per_month:
                        rec.per_year = rec.per_month * 12
                if rec.code == 'conv':
                    rec.per_month = (basic.per_month * rec.percentage) / 100
                    if rec.per_month:
                        rec.per_year = rec.per_month * 12
            # print("rec.per_month >>> ",rec.code,  rec.per_month)
            sum_month += rec.per_month
        for rec in self.annexure_offer2:
            rec.per_month = 0
            rec.per_year = 0
            if self.pf_deduction == 'avail1800':
                for rec_line in self.annexture_offer1:
                    if rec_line.code == 'basic':
                        if rec_line.per_month >= 15000:
                            if rec.percentage > 0:
                                rec.per_month = 1800
                            else:
                                rec.per_month = 0
                                rec.per_year = 0
                            if rec.per_month:
                                rec.per_year = rec.per_month * 12
                        if rec_line.per_month <= 15000:
                            self.pf_deduction = 'basicper'
                            raise ValidationError("You can not set Flat 1,800/- as basic amount is less than 15,000/-")
                        # else:
                        #     raise ValidationError('The basic amount should be greater than 15000.')
            if self.pf_deduction == 'basicper':
                if rec.percentage > 0.00:
                    rec.per_month = (basic.per_month * rec.percentage) / 100
                else:
                    rec.per_month = 0
                    rec.per_year = 0
                if rec.per_month:
                    rec.per_year = rec.per_month * 12

        sum_month1 += sum_month + self.annexure_offer2.per_month
        # print("self.annexure_offer2.per_month >>> ", self.annexure_offer2.per_month, self.annexure_offer2.code)
        # LTA and Professional Persuit#
        annual_amount = 0
        if self.offer_type == 'Intern':
            annual_amount = self.annual_amount
        elif self.offer_type == 'Lateral':
            annual_amount = self.annual_amount_lateral * 12
        elif self.offer_type == 'Offshore':
            annual_amount = self.annual_amount_offshore * 12
        elif self.offer_type == 'RET':
            annual_amount = self.annual_amount_ret

        lta_pp_setting = self.env['hr_applicant_offer_lta_pp_setting'].search(
            [('min_value', '<=', annual_amount), ('max_value', '>=', annual_amount)])
        # lta_amount_ls = [x['amount'] for x in lta_applicant if annual_amount and (x['min'] <= annual_amount <= x['max']) if x['min'] > 0 and x['max'] > 0]
        # lta_amount = int(lta_amount_ls[0]) if len(lta_amount_ls) > 0 else 0
        # pp_amount_ls = [x['amount'] for x in pp_applicant if annual_amount and (x['min'] <= annual_amount <= x['max']) if x['min'] > 0 and x['max'] > 0]
        # pp_amount = int(pp_amount_ls[0]) if len(pp_amount_ls) > 0 else 0
        lta_amount = lta_pp_setting.lta_amount
        pp_amount = lta_pp_setting.pp_amount

        # print("self.annual_amount >> ", annual_amount)
        # print("lta_amount >> ", lta_amount)
        # print("pp_amount >> ", pp_amount)

        # gross = basic + hra + conv + lta + pp
        sum_month1 = sum_month1 + (lta_amount + pp_amount)
        # print("sum_month1 >> ", sum_month1, self.annual_amount_lateral)
        gratuity = 0
        if self.gratuity_applicable is True:
            for rec in self.annexure_offer3:
                if rec.code == 'gratuity':
                    # basic = self.env['offer.details'].search([('code', '=', 'basic'), ('offer_id', '=', self.id)])
                    basic = self.annexture_offer1.filtered(lambda x: x.code == 'basic')
                    if rec.percentage > 0.00:
                        gratuity = round((basic.per_month * rec.percentage) / 100)
                        rec.per_month = gratuity
                        rec.per_year = gratuity * 12
                    else:
                        rec.per_month = 0
                        rec.per_year = 0
        # gratuity = 0
        # for rec in self.annexure_offer3:
        #     if rec.code == 'gratuity':
        #         gratuity = rec.per_month
        sum_month1 += gratuity
        # print('gratuity ..>> ', gratuity)
        # pb_cb_total = ctc - gross - emp_epf - gratuity
        # print("pc_cb_total >>> ", self.annual_amount_lateral, sum_month1, self.annual_amount_lateral - sum_month1)
        # INTERN
        prod_allow = math.ceil((self.revised_amount - sum_month1) / 2)
        commi_allow = math.floor((self.revised_amount - sum_month1) / 2)
        # LATERAL
        prod_allow_lat = math.ceil(((self.annual_amount_lateral) - sum_month1) / 2)
        commi_allow_lat = math.floor(((self.annual_amount_lateral) - sum_month1) / 2)
        # OFFSHORE
        prod_allow_off = math.ceil(((self.annual_amount_offshore) - sum_month1) / 2)
        # commi_allow_off = math.floor(((self.annual_amount_offshore / 12) - sum_month1) / 2)
        commi_allow_off = math.floor(((self.annual_amount_offshore) - sum_month1) / 2)
        # RET
        prod_allow_ret = math.ceil((self.monthly_ctc - sum_month1) / 2)
        commi_allow_ret = math.floor((self.monthly_ctc - sum_month1) / 2)
        # print("prod_allow_ret >> ", self.monthly_ctc,sum_month1, prod_allow_ret, commi_allow_ret)

        for rec in self.annexture_offer1:
            if self.offer_type == 'Intern':
                if rec.code == 'lta':
                    rec.per_month = lta_amount
                    rec.per_year = lta_amount * 12
                if rec.code == 'pp':
                    rec.per_month = pp_amount
                    rec.per_year = pp_amount * 12
                if rec.code == 'pb':
                    rec.per_month = prod_allow
                    rec.per_year = rec.per_month * 12
                if rec.code == 'cb':
                    rec.per_month = commi_allow
                    rec.per_year = rec.per_month * 12
            if self.offer_type == 'Lateral':
                if rec.code == 'lta':
                    rec.per_month = lta_amount
                    rec.per_year = lta_amount * 12
                if rec.code == 'pp':
                    rec.per_month = pp_amount
                    rec.per_year = pp_amount * 12
                if rec.code == 'pb':
                    rec.per_month = prod_allow_lat
                    rec.per_year = rec.per_month * 12
                if rec.code == 'cb':
                    rec.per_month = commi_allow_lat
                    rec.per_year = rec.per_month * 12
            if self.offer_type == 'Offshore':
                if rec.code == 'lta':
                    rec.per_month = lta_amount
                    rec.per_year = lta_amount * 12
                if rec.code == 'pp':
                    rec.per_month = pp_amount
                    rec.per_year = pp_amount * 12
                if rec.code == 'pb':
                    rec.per_month = prod_allow_off
                    rec.per_year = rec.per_month * 12
                if rec.code == 'cb':
                    rec.per_month = commi_allow_off
                    rec.per_year = rec.per_month * 12
            if self.offer_type == 'RET':
                if rec.code == 'lta':
                    rec.per_month = lta_amount
                    rec.per_year = lta_amount * 12
                if rec.code == 'pp':
                    rec.per_month = pp_amount
                    rec.per_year = pp_amount * 12
                if rec.code == 'pb':
                    rec.per_month = prod_allow_ret
                    rec.per_year = rec.per_month * 12
                if rec.code == 'cb':
                    rec.per_month = commi_allow_ret
                    rec.per_year = rec.per_month * 12
            # if rec.code == 'gratuity':
            #     if rec.percentage > 0:
            #         rec.per_month = (basic.per_month * rec.percentage) / 100
            #         rec.per_year = rec.per_month * 12
            #     else:
            #         rec.per_month = 0
            #         rec.per_year = 0
        tax_amount = 0
        for rec in self.annexure_offer2:
            if (self.average_1_month - rec.per_month) <= 21000:
                tax_amount = (self.average_1_month - rec.per_month)
        # print("tax_amounttax_amounttax_amount", tax_amount,self.average_1_month,rec.per_month,)

        health_conf = self.env['hr.recruitment.health.insurance.config'].search([('from_date', '<=', self.current_date),
                                                                                 ('to_date', '>=', self.current_date)])
        # print('health_confhealth_confhealth_conf', health_conf)

        health_rec = self.env['hr.recruitment.health.insurance.config'].search([('offer_type', '=', self.offer_type)])
        for rec in self.annexure_offer3:
            rec.per_month = 0
            rec.per_year = 0
            basic = self.env['offer.details'].search([('code', '=', 'basic'), ('offer_id', '=', self.id)])

            if rec.code == 'pfe':
                if self.pf_deduction == 'avail1800':
                    for rec_line in self.annexture_offer1:
                        if rec_line.code == 'basic':
                            if rec_line.per_month >= 15000:
                                if rec.percentage > 0:
                                    rec.per_month = 1800
                                else:
                                    rec.per_month = 0
                                    rec.per_year = 0
                                if rec.per_month:
                                    rec.per_year = rec.per_month * 12
                            if rec_line.per_month <= 15000:
                                self.pf_deduction = 'basicper'
                                self.env.user.notify_danger("You can not set Flat 1,800/- as basic amount is less than 15,000/-")
                if self.pf_deduction == 'basicper':
                    if rec.percentage > 0.00:
                        rec.per_month = round((basic.per_month * rec.percentage) / 100)
                    else:
                        rec.per_month = 0
                        rec.per_year = 0
                    if rec.per_month:
                        rec.per_year = round(rec.per_month * 12)

            if rec.code == 'gratuity':
                if rec.percentage > 0.00 and self.gratuity_applicable is True:
                    rec.per_month = round((basic.per_month * rec.percentage) / 100)
                else:
                    rec.per_month = 0
                    rec.per_year = 0
            if rec.code == 'esi':
                if self.offer_type == 'Intern':
                    rec.per_month = math.ceil((tax_amount * rec.percentage) / 100)
                if self.offer_type == 'Lateral':
                    rec.per_month = math.ceil((tax_amount * rec.percentage) / 100)
                if self.offer_type == 'Offshore':
                    rec.per_month = math.ceil((tax_amount * rec.percentage) / 100)
                if self.offer_type == 'RET':
                    rec.per_month = math.ceil((tax_amount * rec.percentage) / 100)
            if rec.per_month:
                rec.per_year = rec.per_month * 12
            if rec.code == 'pt':
                offer_annual_amount = 0
                if self.offer_type == 'Intern':
                    offer_annual_amount = self.annual_amount
                elif self.offer_type == 'Lateral':
                    offer_annual_amount = self.annual_amount_lateral * 12
                elif self.offer_type == 'Offshore':
                    offer_annual_amount = self.annual_amount_offshore * 12
                elif self.offer_type == 'RET':
                    offer_annual_amount = self.annual_amount_ret
                if self.professional_tax_applicable is True:
                    if offer_annual_amount > 300000:
                        rec.per_month = 200
                        rec.per_year = 2500
                    elif 160000 < offer_annual_amount <= 300000:
                        rec.per_month = 125
                        rec.per_year = 1500
                    elif offer_annual_amount < 160000:
                        rec.per_month = 0
                        rec.per_year = 0
                else:
                    rec.per_month = 0
                    rec.per_year = 0

            if self.offer_type == 'Offshore':
                if rec.code == 'hi':
                    if self.avail_health_insurance is True:
                        # rec.per_month = health_rec.amount
                        # rec.per_year = rec.per_month * 12
                        rec.per_month = health_rec.amount
                        rec.per_year = health_rec.amount * 12
                    else:
                        rec.per_month = 0
                        rec.per_year = 0

        # for record in self:
        #     if record.offer_type == 'Intern':
        #         if record.annual_amount != record.average_1_year:
        #             # print('printannualamount', self.annexture_offer1)
        #             for rec in self.annexture_offer1[-1]:
        #                 rec.per_month = rec[-1].per_month + 1
        #                 rec.per_year = rec.per_month * 12
        #     elif record.offer_type == 'Lateral':
        #         if record.annual_amount_lateral * 12 != record.average_1_year:
        #             # print('printannualamount', self.annexture_offer1[-1])
        #             for rec in self.annexture_offer1[-1]:
        #                 rec.per_month = rec[-1].per_month + 1
        #                 rec.per_year = rec.per_month * 12
        #     elif record.offer_type == 'Offshore':
        #         if record.annual_amount_offshore * 12 != record.average_1_year:
        #             # print('printannualamount', self.annexture_offer1[-1])
        #             for rec in self.annexture_offer1[-1]:
        #                 rec.per_month = rec[-1].per_month + 1
        #                 rec.per_year = rec.per_month * 12
        #     elif record.offer_type == 'RET':
        #         if record.annual_amount_ret != record.average_1_year:
        #             # print('printannualamount', self.annexture_offer1[-1])
        #             for rec in self.annexture_offer1[-1]:
        #                 rec.per_month = rec[-1].per_month + 1
        #                 rec.per_year = rec.per_month * 12

        if self.average_1_month and self.average_1_year:
            current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
            budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(
                [('mrf_id', '=', self.applicant_id.mrf_id.id), ('fiscalyr', '=', current_fiscal_year_id.id),
                 ('offer_id', '=', False)], order='department_sequence asc')

            # print("budget==============",budget_lines)
            if budget_lines:
                for rec in budget_lines:
                    rec.write({
                        'offer_id': self.id,
                    })
                    return
        self._onchange_avail_pf_benefit()
        self._compute_company_contribution()

    @api.onchange('avail_pf_benefit')
    def _onchange_avail_pf_benefit(self):
        for rec in self:
            basic = rec.annexture_offer1.filtered(lambda x: x.code == 'basic')
            if basic.exists() and basic.per_month <= 15000 and rec.avail_pf_benefit is False:
                rec.avail_pf_benefit = True
                # raise ValidationError('You cannot remove PF as basic is less than Rs. 15,000.')
                self.env.user.notify_danger("You cannot remove PF as basic is less than Rs. 15,000.")
            if rec.avail_pf_benefit is False:
                for line in rec.annexture_offer1:
                    if line.code == 'pb':
                        line.per_month = (line.per_month + (rec.annexure_offer2.per_month / 2))
                        line.per_year = line.per_month * 12
                    if line.code == 'cb':
                        line.per_month = (line.per_month + (rec.annexure_offer2.per_month / 2))
                        line.per_year = line.per_month * 12
                for line_comp in rec.annexure_offer2:
                    line_comp.per_month = 0
                    line_comp.per_year = 0
                for line1 in rec.annexure_offer3:
                    if line1.code == 'pfe':
                        line1.per_month = 0
                        line1.per_year = 0
                rec.pf_deduction = 'basicper'

    @api.onchange('avail_health_insurance')
    def _onchange_avail_health_insurance(self):
        for rec in self:
            health_conf = self.env['hr.recruitment.health.insurance.config'].search(
                [('offer_type', '=', 'Offshore'),
                 ('from_date', '<=', rec.current_date), ('to_date', '>=', rec.current_date)])
            if health_conf.exists():
                for record in health_conf:
                    for line in rec.annexure_offer3:
                        # and record.offer_type == 'Offshore'
                        if line.code == 'hi' and rec.offer_type == 'Offshore':
                            if rec.avail_health_insurance is True:
                                line.per_month = record.amount
                                line.per_year = line.per_month * 12
                            else:
                                line.per_month = 0
                                line.per_year = 0
                        else:
                            line.per_month = 0
                            line.per_year = 0

    def format_number(self, amount):
        return formatLang(self.env, amount, digits=0)


class OfferDetails(models.Model):
    _name = 'offer.details'
    _description = 'Offer Details'

    offer_id = fields.Many2one('hr.applicant.offer', string='ID')
    offer_id1 = fields.Many2one('hr.applicant.offer', string='ID')
    offer_id2 = fields.Many2one('hr.applicant.offer', string='ID')
    component = fields.Char('Component')
    description = fields.Char(' ')
    code = fields.Char('Code')
    percentage = fields.Float('Percentage')
    per_month = fields.Integer("Per Month")
    per_year = fields.Integer("Per Year")

    @api.onchange('per_month')
    def onchange_per_year(self):
        for rec in self:
            if rec.per_month:
                rec.per_year = rec.per_month * 12


class OfferDetailsMaster(models.Model):
    _name = 'offer.details.master'
    _description = 'Offer Details Master'

    name = fields.Char('Name')
    annexture_offer1 = fields.One2many('offer.details.master.details', 'master_id')
    annexture_offer2 = fields.One2many('offer.details.master.details', 'master_id2')
    annexture_offer3 = fields.One2many('offer.details.master.details', 'master_id3')


class OfferDetailsMasterDetails(models.Model):
    _name = 'offer.details.master.details'
    _description = 'Offer Details Master Child'

    component = fields.Char('Component')
    code = fields.Char('code')
    description = fields.Char('Description')
    percentage = fields.Float('Percentage')
    master_id = fields.Many2one('offer.details.master')
    master_id2 = fields.Many2one('offer.details.master')
    master_id3 = fields.Many2one('offer.details.master')


class HealthInsuranceConfig(models.Model):
    _name = 'hr.recruitment.health.insurance.config'
    _description = 'Recruitment Health Insurance Config'

    amount = fields.Integer('Amount')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    offer_type = fields.Selection([('Intern', 'Intern'), ('Lateral', 'Lateral'),
                                   ('RET', 'RET'), ('Offshore', 'Offshore')],
                                  string='Offer Letter Type', default='Intern')


class HealthInsuranceAccidentalConfig(models.Model):
    _name = 'hr.recruitment.health.accidental.insurance.config'
    _description = 'Health Insurance Accidental Details'

    amount = fields.Integer('Amount')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')


class ConfigurationLTAAndPP(models.Model):
    _name = "hr_applicant_offer_lta_pp_setting"
    _description = "LTA and PP configuration for employee"

    min_value = fields.Integer(string="Min Value", required=True)
    max_value = fields.Integer(string="Max Value", required=True)
    lta_amount = fields.Integer(string="Leave Travel Allowance Amount", required=True)
    pp_amount = fields.Integer(string="Professional Persuit Amount", required=True)
