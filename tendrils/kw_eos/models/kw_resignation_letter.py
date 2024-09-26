# -*- coding: utf-8 -*-
import base64
from ast import literal_eval
from datetime import datetime, date
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
import uuid


class kw_resignation_experience_letter(models.Model):
    _name = "kw_resignation_experience_letter"
    _description = "Experience Letter"
    _rec_name = 'ref_code'
    _order = "id desc"

    def _default_access_token(self):
        return uuid.uuid4().hex

    ref_code = fields.Char("Reference No.")
    date = fields.Date('Issue Date', default=date.today())
    salutation = fields.Many2one('res.partner.title', track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id, reaonly="1")
    alias = fields.Char("Alias")
    generate_for = fields.Selection([('resign_applied', 'Employee'), ('ex_employee', 'Ex-Employee')],
                                    string='Generate For', default='resign_applied', store=True)
    active = fields.Boolean(string="Active", default=True)
    employee_id = fields.Many2one("hr.employee", "Employee")
    employee_personal_email = fields.Char("Personal Email")
    text_id = fields.Text(string="Note")

    job_location_id = fields.Many2one('kw_res_branch', string="Job Location")
    base_branch_id = fields.Many2one('kw_res_branch', 'Location', track_visibility='onchange')

    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange', )
    job_id = fields.Many2one('hr.job', string="Job Position", track_visibility='onchange', )
    report_employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type',
                                              track_visibility='onchange', )
    date_of_joining = fields.Date('Date of Joining', )
    last_working_date = fields.Date(string='Last Working Date', track_visibility='onchange', )
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')], string='State', default="draft")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('both', 'Both'), ], string='Gender')

    exp_accept_bool = fields.Boolean('Experience Acceptance')
    emp_project_id = fields.Many2one('crm.lead', string="Project Name/Code")
    start_date = fields.Date(string='Contract Start Date', track_visibility='always')
    end_date = fields.Date(string='Contract End Date', track_visibility='always')
    exp_letter_type = fields.Selection(
        [('complete', 'Complete Info'), ('minimum', 'Minimum Info'), ('internship', 'Internship')],
        string='Exp. Letter with', default='complete', store=True)
    record_check = fields.Boolean('Record Check')
    clearance_type = fields.Selection([('with_clearance', 'With Clearance'),
                                       ('without_clearance', 'Without Clearance')],
                                      string='Clearance', default='with_clearance')
    token = fields.Char(string="Token", default=_default_access_token)
    otp = fields.Char(string="OTP")
    expire_time = fields.Datetime(string="Expire Time")

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('kw_resignation_experience_letter') or 'New'
        list_no = str(values.get('date')).split('-')

        employee_id = values.get('employee_id', self.employee_id)
        exemp_id = self.env['hr.employee'].sudo().search([('active', '=', False), ('id', '=', employee_id)])
        emp_resignation_id = self.env['kw_resignation'].sudo().search([('applicant_id', '=', employee_id)],
                                                                      limit=1, order='id desc')
        eos_employee = self.env['kw_eos_checklist'].sudo().search(
            [('applicant_id', '=', employee_id), ('application_id', '=', emp_resignation_id.id)],
            limit=1, order='id desc')
        clearance_employee = self.env['hr.employee.clearance'].sudo().search(
            [('employee_id', '=', employee_id), ('resignation_id', '=', emp_resignation_id.id)],
            limit=1, order='id desc')
        # print('date......', emp_resignation_id,eos_employee, clearance_employee,values.get('last_working_date'), limit=1)

        last_working_date = values.get('last_working_date', self.last_working_date)
        if exemp_id:
            if exemp_id.last_working_day != last_working_date:
                exemp_id.last_working_day = last_working_date
        if emp_resignation_id:
            if emp_resignation_id.last_working_date != last_working_date:
                emp_resignation_id.last_working_date = last_working_date
        if eos_employee:
            if eos_employee.last_working_date != last_working_date:
                eos_employee.last_working_date = last_working_date
        if clearance_employee:
            if clearance_employee.last_day_of_service != last_working_date:
                clearance_employee.last_day_of_service = last_working_date

        if values.get('department_id') and values.get('job_location_id'):
            dept = self.env['hr.department'].browse([values.get('department_id')])
            job = self.env['kw_res_branch'].browse([values.get('job_location_id')])
            new_code = 'CSM/EL/' + (job.recruitment_ref or '') + '/' + (dept.code or '') + '/' + list_no[2] + '-' + \
                       list_no[1] + '/' + code
            values['ref_code'] = new_code
        else: 
            new_code = 'CSM/EL/' + '/' + '/' + list_no[2] + '-' + list_no[1] + '/' + code
            values['ref_code'] = new_code   
        values['exp_accept_bool'] = True
        values['token'] = self._default_access_token()

        result = super(kw_resignation_experience_letter, self).create(values)
        self.env.user.notify_success(message='Experience Letter generated successfully.')
        return result

    @api.multi
    def write(self, values):
        self.ensure_one()
        values['exp_accept_bool'] = True

        employee_id = self.employee_id.id
        exemp_id = self.env['hr.employee'].sudo().search([('active', '=', False), ('id', '=', employee_id)])
        emp_resignation_id = self.env['kw_resignation'].sudo().search([('applicant_id', '=', employee_id)], limit=1,
                                                                      order='id desc')
        eos_employee = self.env['kw_eos_checklist'].sudo().search(
            [('applicant_id', '=', employee_id), ('application_id', '=', emp_resignation_id.id)],
            limit=1, order='id desc')
        clearance_employee = self.env['hr.employee.clearance'].sudo().search(
            [('employee_id', '=', employee_id), ('resignation_id', '=', emp_resignation_id.id)],
            limit=1, order='id desc')
        # print('date......', date, self.last_working_date, values.get('last_working_date'), limit=1)

        last_working_date = values.get('last_working_date', self.last_working_date)
        # print("last_working_date  >>>>> ", last_working_date, values.get('last_working_date'))
        if exemp_id:
            if exemp_id.last_working_day != last_working_date:
                exemp_id.last_working_day = last_working_date
        if emp_resignation_id:
            if emp_resignation_id.last_working_date != last_working_date:
                emp_resignation_id.last_working_date = last_working_date
        if eos_employee:
            if eos_employee.last_working_date != last_working_date:
                eos_employee.last_working_date = last_working_date
        if clearance_employee:
            if clearance_employee.last_day_of_service != last_working_date:
                clearance_employee.last_day_of_service = last_working_date

        if (values.get('date') and self.date != values.get('date')) \
                or (values.get('job_location_id') and self.job_location_id.id != values.get('job_location_id')):
            dept = self.department_id
            if values.get('date') and self.date != values.get('date'):
                list_no = str(values.get('date')).split('-')
            else:
                list_no = str(self.date).split('-')

            if values.get('job_location_id', False) and self.job_location_id.id != values.get('job_location_id'):
                job = self.env['kw_res_branch'].browse([values.get('job_location_id')])
            else:
                job = self.job_location_id

            new_code = 'CSM/EL/' + (job.recruitment_ref or '') + '/' + (dept.code or '') + '/' + list_no[2] + '-' + \
                       list_no[1] + '/' + str(self.ref_code.rpartition('/')[-1])
            values['ref_code'] = new_code
            # if not values.get('department_id') and not values.get('job_location_id'):
            #     new_code = 'CSM/EL/' + '/' + '/' + list_no[2] + '-' + \
            #            list_no[1] + '/' + str(self.ref_code.rpartition('/')[-1]) 
            #     values['ref_code'] = new_code
        if not self.token:
            values['token'] = self._default_access_token()

        super(kw_resignation_experience_letter, self).write(values)
        self.env.user.notify_success(message='Experience Letter updated successfully.')
        return True

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee_id = self.employee_id.id
        exemp_id = self.env['hr.employee'].sudo().search([('active', '=', False), ('id', '=', employee_id)])
        employee_resig_id = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', employee_id), ('state', 'in', ('apply','confirm', 'grant'))], limit=1, order='id desc')
        duplicate_employee = self.env['kw_resignation_experience_letter'].sudo().search([('employee_id', '=', employee_id)])
        # print(f"exemp_id >> {exemp_id}")
        # print(f"employee_resig_id >> {employee_resig_id}")
        if duplicate_employee:
            raise ValidationError(f"Experience Letter for {duplicate_employee.employee_id.name} already exits : {duplicate_employee.ref_code}")
        for rec in self:
            if rec.employee_id:
                rec.base_branch_id = rec.employee_id.base_branch_id.id
                rec.job_location_id = rec.employee_id.base_branch_id.id
                rec.department_id = rec.employee_id.department_id.id
                rec.job_id = rec.employee_id.job_id.id
                rec.report_employement_type = rec.employee_id.employement_type.id
                rec.date_of_joining = rec.employee_id.date_of_joining
                rec.employee_personal_email = rec.employee_id.personal_email
                rec.last_working_date = exemp_id.last_working_day if rec.generate_for == 'ex_employee' else employee_resig_id.last_working_date
                rec.gender = rec.employee_id.gender
                if rec.employee_id.employement_type:
                    rec.emp_project_id = rec.employee_id.emp_project_id.id
                    rec.start_date = rec.employee_id.start_date
                    rec.end_date = rec.employee_id.end_date
        if self.base_branch_id.id and self.department_id.id and self.job_id.id and self.report_employement_type.id:
            self.record_check = True
        else:
            self.record_check = False

    @api.onchange('generate_for')
    def onchange_generate_for(self):
        if self.generate_for == 'ex_employee':
            # emp_lst = self.env['hr.employee'].sudo().search([('active', '=', False)])
            return {'domain': {'employee_id': [('active', '=', False)]}}
        else:
            emp_list = []
            emp_lst = self.env['kw_resignation'].sudo().search([('state', 'in', ('apply','confirm', 'grant'))])
            for rec in emp_lst:
                emp_list.append(rec.applicant_id.id)
            # print("mang,emo", emp_list)
            return {'domain': {'employee_id': [('id', 'in', emp_list)]}}

    def button_send_email(self):
        template_id = self.env.ref('kw_eos.experience_letter_to_employee_email_template')
        action_id = self.env.ref('kw_eos.kw_resignation_experience_letter_action').id
        db_name = self._cr.dbname
        # for rec in self:
        # report_template_id = self.env.ref('kw_eos.report_letter_experience_letter').render_qweb_pdf(self.id)
        # data_record = base64.b64encode(report_template_id[0])
        # # print("data_recorddata_recorddata_record", data_record)
        # ir_values = {
        #     'name': "Experience Letter",
        #     'type': 'binary',
        #     'datas': data_record,
        #     'datas_fname': f"{self.employee_id.name.replace(' ', '-')}-Experience-Letter.pdf",
        #     'mimetype': 'application/x-pdf',
        # }
        # data_id = self.env['ir.attachment'].create(ir_values)
        # template_id.attachment_ids = [(6, 0, [data_id.id])]
        # email_list = []
        # param = self.env['ir.config_parameter'].sudo()
        # cc_group = literal_eval(param.get_param('kw_eos.notify_cc'))
        # if cc_group:
        #     empls_ids = self.env['hr.employee'].browse(cc_group)
        #     empls = self.env['hr.employee'].search([('id', 'in', empls_ids.ids)])
        #     if empls:
        #         email_list += [emp.work_email for emp in empls if emp.work_email]
        # cc_emails = email_list and ",".join(email_list) or ''
        # cc_emails = "manasi.das@csm.tech,pratima.mahapatra@csm.tech"

        experience_letter_notify_group = self.env.ref('kw_eos.group_kw_eos_experience_letter_notify')
        experience_letter_notify_group_emp = experience_letter_notify_group.users and experience_letter_notify_group.users.mapped('employee_ids') or False
        email_list = experience_letter_notify_group_emp and experience_letter_notify_group_emp.mapped('work_email') or []
        cc_emails = email_list and ",".join(email_list) or ''
        # cc_emails.append(self.create_uid.email)

        if self.id:
            mail_res = template_id.sudo().with_context(extra_params=cc_emails,
                                                       email_from=self.env.user.employee_ids.work_email,
                                                       dbname=db_name,
                                                       action_id=action_id,
                                                       token=self.token,
                                                       id=self.id).send_mail(self.id,
                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")
            # print(f"mail_res {mail_res}")
            # template_id.attachment_ids = [(3, data_id.id)]
            self.env.user.notify_success("Mail sent successfully.")
            # update offer letter status
            self.write({'state': 'sent'})
            
    def get_update_ex_employee_info(self):
        employee_id = self.employee_id
        exemp_id = self.env['hr.employee'].sudo().search([('id', '=', employee_id.id), '|', ('active', '=', True), ('active', '=', False)])
        employee_resig_id = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', employee_id.id), ('state', 'in', ('confirm', 'grant'))], limit=1, order='id desc')
        if exemp_id:
            self.write({
                'base_branch_id': exemp_id.base_branch_id.id or self.base_branch_id.id,
                'department_id': exemp_id.department_id.id or self.department_id.id,
                'job_id': exemp_id.job_id.id or self.job_id.id,
                'report_employement_type': exemp_id.employement_type.id or self.report_employement_type,
                'date_of_joining': exemp_id.date_of_joining or self.date_of_joining,
                'employee_personal_email': exemp_id.personal_email or self.employee_personal_email,
                'last_working_date': exemp_id.last_working_day if self.generate_for == 'ex_employee' else employee_resig_id.last_working_date,
                'gender': exemp_id.gender or self.gender,
                'emp_project_id': exemp_id.emp_project_id.id or self.emp_project_id,
                'start_date': exemp_id.start_date or self.start_date,
                'end_date': exemp_id.end_date or self.end_date,
            })
        if self.base_branch_id.id and self.department_id.id and self.job_id.id and self.report_employement_type.id:
            self.record_check = True
