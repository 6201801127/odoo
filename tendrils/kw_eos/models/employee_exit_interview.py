# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from ast import literal_eval
from datetime import datetime, date, timedelta

available_priorities = [('0', 'Very Poor'),
                        ('1', 'Poor'),
                        ('2', 'Fair'),
                        ('3', 'Good'),
                        ('4', 'Excellent')]


class ReasonForLeaving(models.Model):
    _name = 'reason.for.leaving'
    _description = "Reason For Leaving"

    name = fields.Char('Reason')


class EmployeeExitInterview(models.Model):
    _name = 'employee.exit.interview'
    _description = "Employee Exit Interview"
    _order = 'id desc'
    _rec_name = 'employee_id'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade', track_visibility='onchange')
    employee_name = fields.Char(related='employee_id.name', string="Name")
    employee_code = fields.Char(related='employee_id.emp_code', string="Code")

    resignation_id = fields.Many2one('kw_resignation', ondelete='restrict', string='Offboarding Reference id')
    reg_ref_no = fields.Many2one(related="resignation_id.offboarding_type", string='Offboarding Type')
    # offboarding_id = fields.Many2one('hr.offboarding', ondelete='restrict', string='Voluntary Separation Request')
    job_title = fields.Many2one(related="employee_id.job_id", string='Job Title', store=True, readonly=True)
    department_id = fields.Many2one(related="employee_id.department_id", string='Department', store=True, readonly=True)
    division = fields.Many2one(related="employee_id.division", string='Division', store=True, readonly=True)
    section = fields.Many2one(related="employee_id.section", string='Section', store=True, readonly=True)
    practise = fields.Many2one(related="employee_id.practise", string='Practise', store=True, readonly=True)
    from_date = fields.Date(string="Period of Service From", required=False, copy=False)
    to_date = fields.Date(string="Period of Service To", required=False, copy=False)
    manager_id = fields.Many2one(related="employee_id.parent_id", string='Manager/Supervisor', store=True,
                                 readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 required=True)
    date_of_completion = fields.Date(string="Date Of Completion")
    reason_leaving = fields.Text(string="1 What are the reasons for leaving?")
    other_opportunities = fields.Text(string="2 At what point did you start to consider other opportunities?")
    decision_to_leave = fields.Text(
        string="3 What critical incident had the final impact on your decision to leave? (e.g. interpersonal conflict, salary, performance review, low team spirit etc)")
    making_decision = fields.Text(
        string="4 Before making the decision to leave, did you explore other opportunities within the company?")
    making_decision_type = fields.Selection([('yes', 'Yes'),
                                             ('no', 'No')], 'Making The Decision Type')
    reason_not_do = fields.Text(
        string="5 If yes, what steps did you take and what was the outcome? If not, for what reason did you not do so?")
    attempts_stay = fields.Text(
        string="6 What attempts, if any, have been made by the organisation to encourage you to stay?")
    encouraged_stay = fields.Text(
        string="7 Is there anything TMEA could have done which would have encouraged you to stay?")
    encouraged_stay_type = fields.Selection([('yes', 'Yes'),
                                             ('no', 'No')], 'Encouraged Stay Type')
    adequate_support = fields.Text(
        string="1 Do you believe you received adequate support from management? Please explain.")
    adequate_support_type = fields.Selection([('yes', 'Yes'),
                                              ('no', 'No')], 'Adequate Support Type')
    find_job_challenging = fields.Text(string="2 Did you find your job or your work challenging and rewarding? Why?")
    find_job_challenging_type = fields.Selection([('yes', 'Yes'),
                                                  ('no', 'No')], 'Find Job Challenging Type')
    expected_type = fields.Selection([('yes', 'Yes'),
                                      ('no', 'No')], 'Expected Type')
    experience_comments = fields.Text(string="Comments")
    other_comments = fields.Text(string="Any other comments")
    particularly_well = fields.Text(string="1 What do you think your department does particularly well?")
    department_improve = fields.Text(string="2 What do you think your department can improve on?")
    work_provided = fields.Selection(available_priorities, string="The work provided was interesting and challenging.")
    remuneration = fields.Selection(available_priorities,
                                    string="Remuneration was equitable in comparison to the market.")
    career_development = fields.Selection(available_priorities,
                                          string="Career development and proactive performance management was encouraged.")
    performance_measures = fields.Selection(available_priorities, string="Performance measures were mutually agreed.")
    opportunity_prove = fields.Selection(available_priorities,
                                         string="The opportunity to prove your ability was provided.")
    morale_team = fields.Selection(available_priorities, string="Morale within the team.")
    fairness_work = fields.Selection(available_priorities, string="Fairness of work/assignment distribution.")
    work_environment = fields.Selection(available_priorities, string="Work environment.")
    good_tmea = fields.Text(string="1 What was good about your stay at TMEA?")
    recommend_tmea = fields.Text(string="2 Would you recommend TMEA as a place to work to others? Please elaborate.")
    suggestions_tmea = fields.Text(string="3 What suggestions do you have to make TMEA a better place to work?")
    street = fields.Char(string='street')
    street2 = fields.Char(string='street2')
    zip = fields.Char(string='zip')
    city = fields.Char(string='city')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    email = fields.Char(string='E-mail Address')
    phone = fields.Char(string='Contact Number')
    new_position = fields.Char('If applicable, new organisation and position')
    # responsibility_center_id = fields.Many2one(related='employee_id.working_country_id', string='Responsibility Center',
    #                                            store=True, readonly=True)
    reason_for_leaving_id = fields.Many2one('reason.for.leaving', string='Reason For Leaving',
                                            track_visibility='onchange')

    type_of_work = fields.Selection([('yes', 'Yes'),
                                     ('no', 'No')], 'Type of Work')
    working_conditions = fields.Selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Working Conditions (Setting, schedule, Travel, Flexibility)')
    pay = fields.Selection([('yes', 'Yes'),
                            ('no', 'No')], 'Pay')
    supervisor = fields.Selection([('yes', 'Yes'),
                                   ('no', 'No')], 'Supervisor')

    location = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')], 'Location')
    cost_of_living = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No')], 'Cost of living in area')
    additional_comments = fields.Text('Additional Comments')

    type_of_work_performed = fields.Selection([('vpoor', 'Very Poor'),
                                               ('poor', 'Poor'),
                                               ('average', 'Average'),
                                               ('good', 'Good'),
                                               ('excellent', 'Excellent')
                                               ], 'Type of work performed')

    fairness_work_load = fields.Selection([('vpoor', 'Very Poor'),
                                           ('poor', 'Poor'),
                                           ('average', 'Average'),
                                           ('good', 'Good'),
                                           ('excellent', 'Excellent')
                                           ], 'Fairness of workload')
    salary = fields.Selection([('vpoor', 'Very Poor'),
                               ('poor', 'Poor'),
                               ('average', 'Average'),
                               ('good', 'Good'),
                               ('excellent', 'Excellent')
                               ], 'Salary')
    working_condition = fields.Selection([('vpoor', 'Very Poor'),
                                          ('poor', 'Poor'),
                                          ('average', 'Average'),
                                          ('good', 'Good'),
                                          ('excellent', 'Excellent')
                                          ], 'Working Conditions')
    infra_provided = fields.Selection([('vpoor', 'Very Poor'),
                                       ('poor', 'Poor'),
                                       ('average', 'Average'),
                                       ('good', 'Good'),
                                       ('excellent', 'Excellent')
                                       ], 'Infra Provided')
    training_received = fields.Selection([('vpoor', 'Very Poor'),
                                          ('poor', 'Poor'),
                                          ('average', 'Average'),
                                          ('good', 'Good'),
                                          ('excellent', 'Excellent')
                                          ], 'Training Received')
    co_workers = fields.Selection([('vpoor', 'Very Poor'),
                                   ('poor', 'Poor'),
                                   ('average', 'Average'),
                                   ('good', 'Good'),
                                   ('excellent', 'Excellent')
                                   ], 'Co-Workers')
    additional_comments_3 = fields.Text("Additional Comments")

    performance_feedback = fields.Selection([('never', 'Never'),
                                             ('seldom', 'Seldom'),
                                             ('often', 'Often'),
                                             ('usually', 'Usually'),
                                             ('always', 'Always')
                                             ], 'Gave usable performance feedback')
    accomplishments = fields.Selection([('never', 'Never'),
                                        ('seldom', 'Seldom'),
                                        ('often', 'Often'),
                                        ('usually', 'Usually'),
                                        ('always', 'Always')
                                        ], 'Recognized accomplishments')
    communicated_expectations = fields.Selection([('never', 'Never'),
                                                  ('seldom', 'Seldom'),
                                                  ('often', 'Often'),
                                                  ('usually', 'Usually'),
                                                  ('always', 'Always')
                                                  ], 'Clearly Communicated Expectations')
    treated_you = fields.Selection([('never', 'Never'),
                                    ('seldom', 'Seldom'),
                                    ('often', 'Often'),
                                    ('usually', 'Usually'),
                                    ('always', 'Always')
                                    ], 'Treated you fairly and respectfully')
    coached = fields.Selection([('never', 'Never'),
                                ('seldom', 'Seldom'),
                                ('often', 'Often'),
                                ('usually', 'Usually'),
                                ('always', 'Always')
                                ], 'Coached,Trained & Developed you')
    resolved_concerns = fields.Selection([('never', 'Never'),
                                          ('seldom', 'Seldom'),
                                          ('often', 'Often'),
                                          ('usually', 'Usually'),
                                          ('always', 'Always')
                                          ], 'Resolved Concerns promptly')
    listened_suggestions = fields.Selection([('never', 'Never'),
                                             ('seldom', 'Seldom'),
                                             ('often', 'Often'),
                                             ('usually', 'Usually'),
                                             ('always', 'Always')
                                             ], 'Listened to suggestions & feedback')
    worklife_balance = fields.Selection([('never', 'Never'),
                                         ('seldom', 'Seldom'),
                                         ('often', 'Often'),
                                         ('usually', 'Usually'),
                                         ('always', 'Always')
                                         ], 'Supported work-life balance')
    Provided_assignment = fields.Selection([('never', 'Never'),
                                            ('seldom', 'Seldom'),
                                            ('often', 'Often'),
                                            ('usually', 'Usually'),
                                            ('always', 'Always')
                                            ], 'Provided Appropriate & Challenging assignment ')
    additional_comments_4 = fields.Text("Your Suggestions for your Line Manager")

    upper_performance_feedback = fields.Selection([('never', 'Never'),
                                                   ('seldom', 'Seldom'),
                                                   ('often', 'Often'),
                                                   ('usually', 'Usually'),
                                                   ('always', 'Always')
                                                   ], 'Gave usable performance feedback')
    upper_accomplishments = fields.Selection([('never', 'Never'),
                                              ('seldom', 'Seldom'),
                                              ('often', 'Often'),
                                              ('usually', 'Usually'),
                                              ('always', 'Always')
                                              ], 'Recognized accomplishments')
    upper_communicated_expectations = fields.Selection([('never', 'Never'),
                                                        ('seldom', 'Seldom'),
                                                        ('often', 'Often'),
                                                        ('usually', 'Usually'),
                                                        ('always', 'Always')
                                                        ], 'Clearly Communicated Expectations')
    upper_treated_you = fields.Selection([('never', 'Never'),
                                          ('seldom', 'Seldom'),
                                          ('often', 'Often'),
                                          ('usually', 'Usually'),
                                          ('always', 'Always')
                                          ], 'Treated you fairly and respectfully')
    upper_coached = fields.Selection([('never', 'Never'),
                                      ('seldom', 'Seldom'),
                                      ('often', 'Often'),
                                      ('usually', 'Usually'),
                                      ('always', 'Always')
                                      ], 'Coached,Trained & Developed you')
    upper_resolved_concerns = fields.Selection([('never', 'Never'),
                                                ('seldom', 'Seldom'),
                                                ('often', 'Often'),
                                                ('usually', 'Usually'),
                                                ('always', 'Always')
                                                ], 'Resolved Concerns promptly')
    upper_listened_suggestions = fields.Selection([('never', 'Never'),
                                                   ('seldom', 'Seldom'),
                                                   ('often', 'Often'),
                                                   ('usually', 'Usually'),
                                                   ('always', 'Always')
                                                   ], 'Listened to suggestions & feedback')
    upper_worklife_balance = fields.Selection([('never', 'Never'),
                                               ('seldom', 'Seldom'),
                                               ('often', 'Often'),
                                               ('usually', 'Usually'),
                                               ('always', 'Always')
                                               ], 'Supported work-life balance')
    upper_Provided_assignment = fields.Selection([('never', 'Never'),
                                                  ('seldom', 'Seldom'),
                                                  ('often', 'Often'),
                                                  ('usually', 'Usually'),
                                                  ('always', 'Always')
                                                  ], 'Provided Appropriate & Challenging assignment ')
    additional_comments_5 = fields.Text("Your Suggestions for your upper Line Manager")

    equal_treatment = fields.Selection([('never', 'Never'),
                                        ('seldom', 'Seldom'),
                                        ('often', 'Often'),
                                        ('usually', 'Usually'),
                                        ('always', 'Always')
                                        ], 'Give Fair and equal treatment ')
    discuss_issues = fields.Selection([('never', 'Never'),
                                       ('seldom', 'Seldom'),
                                       ('often', 'Often'),
                                       ('usually', 'Usually'),
                                       ('always', 'Always')
                                       ], 'Was available to discuss job related issues')
    encourageed_feedback = fields.Selection([('never', 'Never'),
                                             ('seldom', 'Seldom'),
                                             ('often', 'Often'),
                                             ('usually', 'Usually'),
                                             ('always', 'Always')
                                             ], 'Encouraged Feedback and suggestions')
    consistent_policies = fields.Selection([('never', 'Never'),
                                            ('seldom', 'Seldom'),
                                            ('often', 'Often'),
                                            ('usually', 'Usually'),
                                            ('always', 'Always')
                                            ], 'Maintained consistent policies and practices')
    recognition = fields.Selection([('never', 'Never'),
                                    ('seldom', 'Seldom'),
                                    ('often', 'Often'),
                                    ('usually', 'Usually'),
                                    ('always', 'Always')
                                    ], 'Provided recognition for achievements')
    gave_opportunities = fields.Selection([('never', 'Never'),
                                           ('seldom', 'Seldom'),
                                           ('often', 'Often'),
                                           ('usually', 'Usually'),
                                           ('always', 'Always')
                                           ], 'Gave opportunities to develop')
    additional_comments_6 = fields.Text("Your Suggestions on improvement in our Management style")
    contact_no = fields.Char(string='Personal contact Number')
    email = fields.Char(string='Personal Email ID')

    _sql_constraints = [
        ('exit_interview_date_check', "CHECK ((from_date <= to_date))",
         "The Period of service From date must be earlier than the Period of service to date."),
    ]

    def get_url(self):
        self.ensure_one()
        get_url = str(
            self.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value) + '/web?#id=' + str(
            self.id) + '&view_type=form&model=employee.exit.interview&action=' + str(
            self.env.ref('indimedi_hr_offboarding.action_employee_exit_interview').id) + '&menu_id='
        return get_url

    # @api.model
    # def default_get(self, fields):
    #     res = super(EmployeeExitInterview, self).default_get(fields)
    #     if not res.get('employee_id'):
    #         employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #         if employee_id:
    #             res.update({'employee_id': employee_id.id})
    #     return res

    @api.onchange('employee_id')
    def onchange_employee(self):
        if not self.employee_id:
            return {}
        self.department_id = self.employee_id.department_id.id
        self.job_title = self.employee_id.job_id.id
        self.manager_id = self.employee_id.parent_id.id
        self.division = self.employee_id.division.id
        self.section = self.employee_id.section.id
        self.practise = self.employee_id.practise.id

    #         self.street2 = self.employee_id.street2
    #         self.zip = self.employee_id.zip
    #         self.city = self.employee_id.city
    #         self.state_id = self.employee_id.state_id.id
    #         self.country_id = self.employee_id.country_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('employee.exit.interview') or _('New')
        res = super(EmployeeExitInterview, self).create(vals)
        return res

    @api.multi
    def action_submit(self):
        if (not self.type_of_work_performed
                or not self.fairness_work_load
                or not self.salary
                or not self.working_condition
                or not self.infra_provided
                or not self.training_received
                or not self.co_workers
                or not self.performance_feedback
                or not self.accomplishments
                or not self.communicated_expectations
                or not self.treated_you
                or not self.coached
                or not self.resolved_concerns
                or not self.listened_suggestions
                or not self.worklife_balance
                or not self.Provided_assignment
                or not self.upper_performance_feedback
                or not self.upper_accomplishments
                or not self.upper_communicated_expectations
                or not self.upper_treated_you
                or not self.upper_coached
                or not self.upper_resolved_concerns
                or not self.upper_listened_suggestions
                or not self.upper_worklife_balance
                or not self.upper_Provided_assignment
                or not self.equal_treatment
                or not self.discuss_issues
                or not self.encourageed_feedback
                or not self.consistent_policies
                or not self.recognition
                or not self.gave_opportunities):
            raise Warning(_("Please answer to all questions."))
        else:
            employee = self.employee_id
            record = self.env['kw_eos_checklist'].search([('applicant_id', '=', employee.id), ('state', '=', 'Draft')])
            upper_ra = False
            attendance = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', employee.parent_id.id), ('attendance_recorded_date', '=', datetime.today().date())])
            if attendance and attendance.status == 'On Leave':
                upper_ra = employee.parent_id.parent_id

            if record:
                eos_chklst_log = self.env['kw_eos_checklist_log']
                eos_log = {
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.effective_form,
                    'last_working_date': self.resignation_id.last_working_date,
                    'eos_id': record.id,
                }
                if record.offboarding_type.offboarding_type.name == 'Termination':
                    remark = f'Granted By {self.env.user.employee_ids.name}'
                    approved_by = self.env.user.employee_ids
                    """ Update EOS log """
                    eos_log['remark'] = f'Granted By {self.env.user.employee_ids.name}'
                    eos_log['state'] = 'Granted'
                    eos_chklst_log.sudo().create(eos_log)
                    """ EOS Method is called 
                        1) Grant the eos record
                        2) Fire mails to respective authorities 
                    """
                    mail_to = self.employee_id.parent_id.work_email
                    record.action_dept_head_remark_grant(remark, approved_by, mail_to)
                else:
                    """ Update EOS record """
                    record.write({'state': 'Applied',
                                  'action_to_be_taken_by': upper_ra.id if upper_ra else employee.parent_id.id})
                    """ Update EOS log """
                    eos_log['remark'] = f'Applied By {self.env.user.employee_ids.name}'
                    eos_log['state'] = 'Applied'
                    eos_chklst_log.sudo().create(eos_log)
                    """ mail fired to ra to approved applied record """
                    # cc = self.grt_interview_cc(deg_group=True, coach=True, hod=True)
                    cc = ''
                    mail_to = record.get_cc(deg_group=True, hrd=True, account=True, it=True, admin=True, upper_ra=True, ra=True)
                    template_obj = self.env.ref('kw_eos_integrations.eos_apply_mail_template')
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc,
                                                                                          mail_to=mail_to,
                                                                                          applicant_name=record.applicant_id.name,
                                                                                          code=record.applicant_id.emp_code,
                                                                                          branch_alias=record.base_branch_id.alias,
                                                                                          department_id=record.department_id.name,
                                                                                          division=record.division.name,
                                                                                          section=record.section.name,
                                                                                          practise=record.practise.name,
                                                                                          job_id=record.job_id.name,
                                                                                          action_taken_by=record.action_to_be_taken_by.name,
                                                                                          last_working_date=datetime.strptime(str(record.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                          ).send_mail(record.eos_log_ids[0].id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                """ Created eos log """
                """ EOS record Changed to Granted  """
                offboard_rec = self.env['kw_resignation'].sudo().search(
                    [('applicant_id', '=', employee.id), ('state', '=', 'grant')])
                clearance = self.env['hr.employee.clearance'].sudo().search([('resignation_id', '=', offboard_rec.id)])
                if not clearance.exists():
                    # print("clearance================================in eos===========",clearance)
                    clearance = self.env['hr.employee.clearance'].sudo().create({
                        'employee_id': employee.id,
                        'resignation_id': offboard_rec.id,
                        'last_day_of_service': offboard_rec.last_working_date,
                        'hr_unit_date': offboard_rec.last_working_date,
                        'eos_id': record.id})

                admin_list = []
                admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
                admin_list += admin.filtered(lambda r: r.work_email != False).mapped('work_email')
                admin_lists = admin_list and ",".join(admin_list) or ''
                template_obj = self.env.ref('kw_eos_integrations.clearance_admin_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=admin_lists,
                                                                                      applicant_name=record.applicant_id.name,
                                                                                      code=record.applicant_id.emp_code,
                                                                                      branch_alias=record.base_branch_id.alias,
                                                                                      department_id=record.department_id.name,
                                                                                      division=record.division.name,
                                                                                      section=record.section.name,
                                                                                      practise=record.practise.name,
                                                                                      job_id=record.job_id.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(record.last_working_date),
                                                                                          "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                      ).send_mail(clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

                it_list = []
                it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
                it_list += it.filtered(lambda r: r.work_email != False).mapped('work_email')
                it_lists = it_list and ",".join(it_list) or ''
                template_obj = self.env.ref('kw_eos_integrations.clearance_it_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=it_lists,
                                                                                      applicant_name=record.applicant_id.name,
                                                                                      code=record.applicant_id.emp_code,
                                                                                      branch_alias=record.base_branch_id.alias,
                                                                                      department_id=record.department_id.name,
                                                                                      division=record.division.name,
                                                                                      section=record.section.name,
                                                                                      practise=record.practise.name,
                                                                                      job_id=record.job_id.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(record.last_working_date),
                                                                                          "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                      ).send_mail(clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

                account_list = []
                accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
                account_list += accaunt.filtered(lambda r: r.work_email != False).mapped('work_email')
                account_lists = account_list and ",".join(account_list) or ''
                template_obj = self.env.ref('kw_eos_integrations.clearance_account_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=account_lists,
                                                                                      applicant_name=record.applicant_id.name,
                                                                                      code=record.applicant_id.emp_code,
                                                                                      branch_alias=record.base_branch_id.alias,
                                                                                      department_id=record.department_id.name,
                                                                                      division=record.division.name,
                                                                                      section=record.section.name,
                                                                                      practise=record.practise.name,
                                                                                      job_id=record.job_id.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(record.last_working_date),
                                                                                          "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                      ).send_mail(clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

                manager_list = []
                manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
                manager_list += manager.filtered(lambda r: r.work_email != False).mapped('work_email')
                manager_lists = manager_list and ",".join(manager_list) or ''
                template_obj = self.env.ref('kw_eos_integrations.clearance_manager_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=manager_lists,
                                                                                      applicant_name=record.applicant_id.name,
                                                                                      code=record.applicant_id.emp_code,
                                                                                      branch_alias=record.base_branch_id.alias,
                                                                                      department_id=record.department_id.name,
                                                                                      division=record.division.name,
                                                                                      section=record.section.name,
                                                                                      practise=record.practise.name,
                                                                                      job_id=record.job_id.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(record.last_working_date),
                                                                                          "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                      ).send_mail(clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)

                ra_email = upper_ra.work_email if upper_ra else record.applicant_id.parent_id.work_email
                template_obj = self.env.ref('kw_eos_integrations.clearance_ra_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=ra_email,
                                                                                      applicant_name=record.applicant_id.name,
                                                                                      code=record.applicant_id.emp_code,
                                                                                      branch_alias=record.base_branch_id.alias,
                                                                                      department_id=record.department_id.name,
                                                                                      division=record.division.name,
                                                                                      section=record.section.name,
                                                                                      practise=record.practise.name,
                                                                                      job_id=record.job_id.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(record.last_working_date),
                                                                                          "%Y-%m-%d").strftime("%d-%b-%Y") if record.last_working_date else False,
                                                                                      ).send_mail(clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Mail sent successfully.")

                action_id = self.env.ref('kw_eos.eos_checklist_action').id
                menu_id = self.env.ref('kw_eos.kw_resignation_menu_root').id
                return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=employee.exit.interview&view_type=list&menu_id={menu_id}',
                    'target': 'self',
                }

    def grt_interview_cc(self, hrd=False, hod=False, coach=False, deg_group=False):
        email_list = []
        param = self.env['ir.config_parameter'].sudo()
        if hrd:
            hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
            empls = self.env['hr.employee'].search([('id', 'in', hrd_group), ('active', '=', True)])
            email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')

        if hod:
            if self.employee_id.department_id.manager_id and self.employee_id.department_id.manager_id.active == True:
                email_list.append(self.employee_id.department_id.manager_id.work_email)

        if coach:
            if self.employee_id.coach_id and self.employee_id.coach_id != self.employee_id.parent_id and self.employee_id.coach_id.active == True:
                email_list.append(self.employee_id.coach_id.work_email)

        """Notify CC users"""
        if deg_group:
            cc_group = literal_eval(param.get_param('kw_eos.notify_cc'))
            if cc_group:
                all_jobs = self.env['hr.job'].browse(cc_group)
                empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
                if empls:
                    email_list += [emp.work_email for emp in empls if emp.work_email]

            hrd_cc_group = self.env.ref('kw_eos.group_kw_resignation_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

        cc = email_list and ",".join(email_list) or ''
        return cc
