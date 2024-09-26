from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date


class KwSkillSheet(models.Model):
    _name = 'kw_skill_sheet'
    _description = "Skill Sheet"
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
    
    def _default_primary_skill(self):
        resource_rec = self.env['resource_skill_data'].search([('employee_id', '=', self.env.user.employee_ids.id)],limit=1)
        pskill_result= self.env['kw_skill_master'].search([('id', '=', resource_rec.primary_skill_id.id)])
        return pskill_result
       
    
    def _default_secondary_skill(self):
        resource_rec = self.env['resource_skill_data'].search([('employee_id', '=', self.env.user.employee_ids.id)], limit=1)
        sskill_result = self.env['kw_skill_master'].search([('id', '=', resource_rec.secondary_skill_id.id)])
        return sskill_result

    def _default_tertial_skill(self):
        resource_rec = self.env['resource_skill_data'].search([('employee_id', '=', self.env.user.employee_ids.id)], limit=1)
        tskill_result = self.env['kw_skill_master'].search([('id', '=', resource_rec.tertial_skill_id.id)])
        return tskill_result
    
    def _check_lnk_user(self):
        for record in self:
            if self.env.user.has_group('kw_resource_management.group_l_and_K_dept'):
                record.is_lnk_user = True
    @api.depends('date_')
    def _compute_current_quarter_domain(self):
        for rec in self:
            today = fields.Date.today()
            start_date = date(today.year, (today.month - 1) // 3 * 3 + 1, 1)
            end_date = start_date + relativedelta(months=3, days=-1)
            rec.start_date = start_date
            rec.end_date = end_date

    def get_current_quarter(self):
        today = date.today()
        year = today.year

        if today >= date(year, 1, 1) and today <= date(year, 3, 31):
            start_date = date(year, 1, 1)
            end_date = date(year, 3, 31)
        elif today >= date(year, 4, 1) and today <= date(year, 6, 30):
            start_date = date(year, 4, 1)
            end_date = date(year, 6, 30)
        elif today >= date(year, 7, 1) and today <= date(year, 9, 30):
            start_date = date(year, 7, 1)
            end_date = date(year, 9, 30)
        elif today >= date(year, 10, 1) and today <= date(year, 12, 31):
            start_date = date(year, 10, 1)
            end_date = date(year, 12, 31)

        return {
            'start_date': start_date,
            'end_date': end_date,
        }
    
    def _get_default_fiscal_year(self):
        fiscal_year = self.env['account.fiscalyear'].search([
            ('date_start', '<=', fields.Date.today()),
            ('date_stop', '>=', fields.Date.today())
        ], limit=1)
        return fiscal_year
    def get_fiscal_quarter(self):
        date = datetime.now()
        if date.month in (4,5,6):
            return 1
        if date.month in (7,8,9):
            return 2
        if date.month in (10,11,12):
            return 3
        if date.month in (1,2,3):
            return 4
    
    # start_date = fields.Date(compute='_compute_current_quarter_domain',store=True)
    # end_date = fields.Date(compute='_compute_current_quarter_domain',store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', required=True , default=_default_employee)
    job_name = fields.Char(rstring='Designation', readonly=True)
    department_name = fields.Char(string='Department', readonly=True)
    code = fields.Char(string='Employee Code', readonly=True)
    location = fields.Char(string='Location', readonly=True)
    section = fields.Char(string='Section', readonly=True)
    grade = fields.Char(string='Grade', readonly=True)
    state = fields.Selection(string="State", selection=[('1', 'Draft'), ('2', 'Submitted'), ('3', 'RA Approved'), ('4', 'L & K Approved')], required=True, default='1')
    submit_data_readonly = fields.Boolean(default=False)
    ra_submit_data_bool = fields.Boolean(default=False)
    lnk_submit_data_bool = fields.Boolean(default=False)
    is_lnk_user = fields.Boolean(compute="_check_lnk_user")
    date_ = fields.Date(default=date.today())
    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill',default=_default_primary_skill)
    secondary_skill_id = fields.Many2one('kw_skill_master',string='Secondary Skill',default=_default_secondary_skill )
    tertial_skill_id = fields.Many2one('kw_skill_master',string='Tertiarry Skill',default=_default_tertial_skill)
    self_primary_skill_id_score = fields.Float( string='Self Primary Skill Score')
    self_secondary_skill_id_score = fields.Float(string='Self Secondary Skill Score' )
    self_tertial_skill_id_score = fields.Float(string='Self Tertiarry Skill Score')
    ra_primary_skill_id_score = fields.Float( string='RA Primary Skill Score')
    ra_secondary_skill_id_score = fields.Float(string='RA Secondary Skill Score' )
    ra_tertial_skill_id_score = fields.Float(string='RA Tertiarry Skill Score')
    lnk_primary_skill_id_score = fields.Float( string='L & K Primary Skill Score')
    lnk_secondary_skill_id_score = fields.Float(string='L & K Secondary Skill Score' )
    lnk_tertial_skill_id_score = fields.Float(string='L & K Tertiarry Skill Score')
    btn_visibility_status = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility_status")
    default_fiscal_year = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        default=lambda self: self._get_default_fiscal_year())
    
    fiscal_quarter = fields.Selection(string="Quarter",selection=[(1, 'First Quarter'),(2, 'Second Quarter'),(3, 'Third Quarter'),(4, 'Fourth Quarter')], default=get_fiscal_quarter)

    @api.model
    def create(self, vals):
        current_date = date.today()
        allowed_date = self.env['kw_skill_date_configuration'].search([])
        if allowed_date and allowed_date.user_from_date <= current_date <= allowed_date.user_to_date:
            return super(KwSkillSheet, self).create(vals)
        else:
            raise ValidationError('You are allowed to create self skill sheet from {} to {}'.format(allowed_date.user_from_date, allowed_date.user_to_date))

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != '1':
                raise ValidationError('The Record Will not be delete once you Submited.')
        return super(KwSkillSheet, self).unlink()
    
    
    @api.onchange('employee_id')
    def get_emp_details(self):
        for rec in self:
            if rec.employee_id:
                rec.code = rec.employee_id.emp_code
                rec.location = rec.employee_id.job_branch_id.city
                rec.section = rec.employee_id.section.name
                rec.job_name = rec.employee_id.job_id.name
                rec.department_name = rec.employee_id.department_id.name
                rec.grade = rec.employee_id.grade.name

    @api.constrains('self_primary_skill_id_score','self_secondary_skill_id_score','self_tertial_skill_id_score')
    def check_self_skill_score(self):
        for rec in self:
            # score_list = [1,2,3,4,5]
            if rec.primary_skill_id and  rec.state=='1' and  rec.self_primary_skill_id_score >5 :
                raise ValidationError("Please enter the score between 1 to 5.")
            elif rec.secondary_skill_id and  rec.state=='1' and  rec.self_secondary_skill_id_score >5 :
                raise ValidationError("Please enter the score between 1 to 5.")
            elif rec.tertial_skill_id and  rec.state=='1' and  rec.self_tertial_skill_id_score >5 :
                raise ValidationError("Please enter the score between 1 to 5.")
            
            
    @api.constrains('employee_id', 'date_')
    def check_current_quarter_rec(self):
        for record in self:
            current_quarter = self.get_current_quarter()
            existing_records = self.env['kw_skill_sheet'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date_', '>=', current_quarter['start_date']),
                ('date_', '<=', current_quarter['end_date']),
            ])
            if len(existing_records) > 1:
                raise ValidationError("You can't take more than one assessment in a single quarter.")
    
    def self_mark_sheet_submit(self):
        current_date = date.today()
        allowed_date = self.env['kw_skill_date_configuration'].sudo().search([])
        if allowed_date and allowed_date.user_from_date <= current_date <= allowed_date.user_to_date:
            for rec in self:
                rec.state = '2'
                rec.submit_data_readonly = True
                self.env.user.notify_success("Self Skill Score Successfully Submited.")
        else:
            raise ValidationError('You are allowed to submit self skill sheet from {} to {}'.format(allowed_date.user_from_date, allowed_date.user_to_date))

    def _compute_button_visibility_status(self):
        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids
            emp_check = self._context.get('login_emp_check')
            if emp_check:
                rec.btn_visibility_status = True
            else:
                rec.btn_visibility_status = True if rec.employee_id.parent_id.id in emp_ids and rec.state == '2' else False

    def ra_mark_sheet_submit(self):
        current_date = date.today()
        allowed_date = self.env['kw_skill_date_configuration'].search([])
        if allowed_date and allowed_date.ra_from_date <= current_date <= allowed_date.ra_to_date:
            for rec in self:
                # score_list = [1,2,3,4,5]
                if  rec.state=='2' and rec.primary_skill_id and  rec.ra_primary_skill_id_score > 5 :
                    raise ValidationError("Please enter the score between 1 to 5.")
                elif  rec.state=='2' and rec.secondary_skill_id and  rec.ra_secondary_skill_id_score > 5 :
                    raise ValidationError("Please enter the score between 1 to 5.")
                elif rec.state=='2' and rec.tertial_skill_id and  rec.ra_tertial_skill_id_score > 5 :
                    raise ValidationError("Please enter the score between 1 to 5.")
                else:
                    rec.write(
                        {'state':'3',
                            # 'date_':date.today(),
                            'ra_submit_data_bool':True,
                        }
                    )
                self.env.user.notify_success("Skill Score Successfully Validated.")
        else:
            raise ValidationError('You are allowed to Take Action on skill sheet from {} to {}'.format(allowed_date.ra_from_date, allowed_date.ra_to_date))

    def lnk_mark_sheet_submit(self):
        for rec in self:
            rec.write(
                {'state':'4',
                    # 'date_':date.today(),
                    'lnk_submit_data_bool':True
                }
            )
            self.env.user.notify_success("Skill Score Successfully Validated.")


    def send_quarterly_email_to_user(self):
        # Calculate current quarter
        current_quarter_info = self.get_current_quarter()
        current_quarter_start = current_quarter_info['start_date']
        current_quarter_end = current_quarter_info['end_date']
        user_from_date = self.env.context.get('user_from_date')
        user_to_date = self.env.context.get('user_to_date') 
        # Check if a record already exists for the current quarter for each employee in selected departments
        selected_departments = self.env['hr.department'].browse(self.env.context.get('active_ids', []))
        employees_without_records = self.env['hr.employee']
        employees_in_department = self.env['hr.employee'].search([('department_id', '=', selected_departments.id)])
        act_id = self.env.ref("kw_skill_assessment.kw_skill_sheet_action_window").id
        existing_records = self.env['kw_skill_sheet'].search([
            ('state', 'in', ['2','3','4']),
            ('employee_id', 'in', employees_in_department.ids),
            ('date_', '>=', current_quarter_start),
            ('date_', '<=', current_quarter_end),
        ])
        employees_without_records |= employees_in_department - existing_records.mapped('employee_id')
        template = self.env.ref('kw_skill_assessment.kw_skill_assessment_email_template')
        if template:
            for employee in employees_without_records:
                email_to = employee.work_email
                name = employee.name
                subject = "Self Assessment For Skill Capability of the Organization"
                template.with_context(mail_for="Self", email_to=email_to, name=name, subject=subject,
                                              action_id=act_id, record=employee,from_date=user_from_date,to_date=user_to_date).send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Send To Uers Successfully.")
    
    def send_quarterly_email_to_ra(self):
        current_quarter_info = self.get_current_quarter()
        current_quarter_start = current_quarter_info['start_date']
        current_quarter_end = current_quarter_info['end_date']
        ra_from_date = self.env.context.get('ra_from_date')
        ra_to_date = self.env.context.get('ra_to_date') 
        selected_departments = self.env['hr.department'].browse(self.env.context.get('active_ids', []))
        employees_in_department = self.env['hr.employee'].search([('department_id', '=', selected_departments.id)])
        act_id = self.env.ref("kw_skill_assessment.ra_skill_sheet_take_action_act_window").id
        ra_pending_employees = self.env['kw_skill_sheet'].search([
            ('state', '=', '2'),
            ('employee_id', 'in', employees_in_department.ids),
            ('date_', '>=', current_quarter_start),
            ('date_', '<=', current_quarter_end),
        ])
        # parents_of_employees_with_records = self.env['hr.employee']
        # for ra_pending_employee in ra_pending_employees:
        #     if ra_pending_employee.employee_id.parent_id and ra_pending_employee.employee_id.parent_id not in parents_of_employees_with_records:
        #         parents_of_employees_with_records |= ra_pending_employee.employee_id.parent_id
                
        parents_of_employees_with_records = self.env['hr.employee']
        for ra_pending_employee in ra_pending_employees:
            parent_employee = ra_pending_employee.employee_id.parent_id
            if parent_employee and parent_employee not in parents_of_employees_with_records:
                parents_of_employees_with_records |= parent_employee
        template = self.env.ref('kw_skill_assessment.kw_skill_assessment_email_template')
        if template:
            for parent_employee in parents_of_employees_with_records:
                if parent_employee.parent_id:
                    email_to = parent_employee.work_email
                    name = parent_employee.name
                    subject = "Subordinate's Skill Validation For Skill Capability of the Organization"
                    template.with_context(
                        mail_for="ra",email_to=email_to,name=name,subject=subject,action_id=act_id,record=parent_employee,from_date=ra_from_date,to_date=ra_to_date
                    ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("Mail Sent To Users Successfully.")

class SkillMasterMarkSheet(models.Model):
    _name = 'kw_skill_mark_sheet_table'
    _description = 'one2many table for mark'
    _order = 'skill_type_id asc'

    kw_skill_emp_id = fields.Many2one('kw_skill_sheet')
    skill_type_id = fields.Many2one('kw_skill_type_master', string='Skill Type', required=True)
    skills_id = fields.Many2one('kw_skill_master', string='Skills', required=True)
    mark = fields.Float(string='Mark (Percentage)', required=True)

    @api.onchange('skill_type_id')
    def get_skill(self):
        list_data = []
        for rec in self:
            if rec.skill_type_id:
                dataa = self.env['kw_skill_master'].sudo().search([('skill_type', '=', rec.skill_type_id.id),
                                                                   ('active', '=', True)])
                for data in dataa:
                    list_data.append(data.id)
        return {'domain': {'skills_id': [('id', 'in', list_data)]}}

    @api.onchange('mark')
    def get_mark(self):
        if self.mark:
            if self.mark > 5:
                raise ValidationError('Maximum mark Percentages is 5%')

    @api.constrains('skills_id')
    def prevent_duplicate_skill(self):
        for rec in self:
            old_data = []
            data = self.env['kw_skill_mark_sheet_table'].sudo().search([('kw_skill_emp_id', '=', rec.kw_skill_emp_id.id)]) - rec
            for recc in data:
                old_data.append(recc.skills_id.id)
            if rec.skills_id.id in old_data:
                raise ValidationError(f'{rec.skills_id.name} Already Exist')

class SkillAssessmentNotifyMailWizard(models.TransientModel):
    _name = 'skill_assessment_mail_notify_wizard'
    _description = 'Send Mail to all users To fill skill assessment sheet '

    department_ids = fields.Many2many('hr.department','wizard_dept_rel', 'wizard_dept_id', 'department_id', string="Departments", required=True)

    def action_notify_to_user(self):
        configured_date = self.env['kw_skill_date_configuration'].search([])
        for rec in self.department_ids:
            self.env['kw_skill_sheet'].with_context(active_ids=rec.id,user_from_date=configured_date.user_from_date,user_to_date=configured_date.user_to_date).sudo().send_quarterly_email_to_user()

    def action_notify_to_ra(self):
        configured_date = self.env['kw_skill_date_configuration'].search([])
        for rec in self.department_ids:
            self.env['kw_skill_sheet'].with_context(active_ids=rec.id,ra_from_date=configured_date.ra_from_date,ra_to_date=configured_date.ra_to_date).sudo().send_quarterly_email_to_ra()
        # self.env['kw_skill_sheet'].sudo().send_quarterly_email()












