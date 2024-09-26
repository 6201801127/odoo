from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class OnboardingGenaralConfiguration(models.Model):
    _name = "kw_onboarding_induction_configuration"
    _description = "Onboarding Induction General Configuration"
    _rec_name = ''

    cc_notify = fields.Many2many('hr.employee', 'kw_onboard_induction_employee_rel1', 'employee_id',
                                 'res_id', string='CC Notify',
                                 help='Select the employee to be added ')
    admin_reviewer = fields.Many2many('hr.employee', 'kw_onboard_induction_employee_rel4', 'employee_id',
                                      'induction_onboard_id3', string='Onboard Reviewer',
                                      help='Select the employee to be added')
    @api.model
    def create(self, vals):
        existing_record = self.env['kw_onboarding_induction_configuration'].search([], limit=1)
        if existing_record:
            raise UserError("Only one record allowed.")
        
        res = super(OnboardingGenaralConfiguration, self).create(vals)

        return res


class EmployeeInduction(models.Model):
    _name = "kw_onboard_induction_emp_tagged"
    _description = "Employee Onboarding Induction"
    _rec_name = "number"

    number = fields.Char("Sequence", default="New", readonly=True)
    emp_ids = fields.Many2many('hr.employee', 'kw_onboard_induction_tagged_emp_rel', 'employee_id',
                               'tagged_induction_id', string="Employee")
    user_access_id = fields.Many2many('res.users','kw_onboard_ind_user_rel','user_access_id','onboard_feedback_id',string="User")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    feedback_form_tagged = fields.Many2many('onboard_survey_type_master', string="Feedback Form")
    after_save_bool = fields.Boolean(string="save bool")
    confirmed_bool = fields.Boolean(default=False)
    status_submit = fields.Selection(string='Status',
                                     selection=[('configured', 'Configured'), ('reasssign', 'Reassign'),
                                                ('completed', 'Completed'), ('inprogress', 'Inprogress')])
    log_feedback_ids = fields.One2many('feedback_assessment_feedback_log', 'tagged_feedback_id',
                                       string="Feedback Assessment Log")

    @api.model
    def create(self, vals):
        app_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
        vals['after_save_bool'] = True
        seq = self.env['ir.sequence'].next_by_code('self.kw_onboard_induction_emp_tagged') or '/'
        vals['number'] = f" Tagged/{seq}"
        # for rec in vals['emp_ids']:
        #     rec.write({'groups_id': [(4, app_group.id)]})

        res = super(EmployeeInduction, self).create(vals)

        return res

    @api.constrains('start_date', 'end_date')
    def validate_start_end_date(self):
        if self.start_date and self.end_date:
            if self.start_date < date.today() or self.start_date > self.end_date:
                raise ValidationError(
                    f'Please Check the start date : {self.start_date} and end date: {self.end_date}.'
                )

    def mail_send_employee(self):
        # for rec in self:
        #     if rec.confirmed_bool == True and self.search([('emp_ids', 'in', rec.emp_ids.ids), ('feedback_form_tagged', 'in', rec.feedback_form_tagged.ids),('status_submit','=','configured')]):
        #         raise ValidationError("Record already configured!")
        template_obj = self.env.ref("kw_onboarding_induction_feedback.config_mail_to_employee")
        app_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
        confirmed_bool = False
        for rec in self.emp_ids:
            tree_view_id = self.env.ref('kw_onboarding_induction_feedback.kw_onboarding_feedback_form').id
            act_id = self.env.ref("kw_onboarding_induction_feedback.onboarding_induction_feedback_action_window").id
            if rec.user_id.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user'):
                form_list = [code_rec.code for code_rec in self.feedback_form_tagged]
                record = self.env['kw_onboarding_feedback'].sudo().create({'emp_id': rec.id,
                               'tagged_id': self.id,
                               'form_assign': [(6, 0, self.feedback_form_tagged.ids)],
                               'onboard_ind_bool': True if 'OF' in form_list else False,
                               'status_feedback': 'Configured' if self.status_submit != 'reasssign' else 'Reasssign',
                               'required': True})
                
                confirmed_bool = True
                if self.status_submit == 'reasssign':
                    status_submit = 'reasssign'
                else:
                    status_submit = 'configured'
                mail_to = ','.join(rec.mapped('work_email'))
                if template_obj:
                    template_obj.with_context(email_to=mail_to,
                                              mail_from=self.env.user.employee_ids.work_email,
                                              record_id=record.id,
                                              employee_id=rec.id,
                                              view_id=tree_view_id,
                                              action_id=act_id,
                                              cc_mail=self.env.user.employee_ids.work_email,
                                              name=rec.name).send_mail(self.id,
                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")

            else:
                user = self.env['res.users'].sudo().search([('partner_id', '=', rec.user_id.partner_id.id)])
                if user:
                    user.write({'groups_id': [(4, app_group.id)]})
                form_list = [code_rec.code for code_rec in self.feedback_form_tagged]
                record = self.env['kw_onboarding_feedback'].sudo()
                record.create({'emp_id': rec.id,
                               'tagged_id': self.id,
                               'form_assign': [(6, 0, self.feedback_form_tagged.ids)],
                               'onboard_ind_bool': True if 'OF' in form_list else False,
                               'status_feedback': 'Configured',
                               'required': True})
                confirmed_bool = True
                status_submit = 'configured'
                mail_to = ','.join(rec.mapped('work_email'))
                if template_obj:
                    template_obj.with_context(email_to=mail_to,
                                               mail_from=self.env.user.employee_ids.work_email,
                                              record_id=self.id,  # Pass the record ID to the controller
                                              employee_id=rec.id,
                                              action_id=act_id,
                                              name=rec.name).send_mail(self.id,
                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")
        update_rec = []
        for record in self.feedback_form_tagged:
            for rec in self.emp_ids:
                update_rec.append([0, 0, {
                    'emp_name': rec.id,
                    'status_feedback': 'Configured' if status_submit == 'configured' else 'Reasssign',
                    'assign_feedback_form': record.id
                }])
        self.write({
            'confirmed_bool': confirmed_bool,
            'status_submit': status_submit,
            'log_feedback_ids': update_rec
        })
    def manage_user_access(self):
        app_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
        if self.emp_ids:
            for rec in self.emp_ids:
                if not rec.user_id:
                    continue  # Skip employees without a user account
                user = rec.user_id
                if not any(group == app_group for group in user.groups_id):
                    user.write({'groups_id': [(4, app_group.id)]})
                self.user_access_id |= user
        
    def user_access_induction_feedback(self):
        app_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
        user_config_ids = self.env['kw_onboard_induction_emp_tagged'].sudo().search([('status_submit', 'in', ['configured'])])

        for rec in user_config_ids:
            for employee in rec.emp_ids:
                if not employee.user_id:
                    continue  # Skip employees without a user account
                user = employee.user_id
                # print("user===================",user)
                if not any(group == app_group for group in user.groups_id):
                    user.write({'groups_id': [(4, app_group.id)]})
                # print("Granted access to user:", user.name)




class FeedbackInductionLog(models.Model):
    _name = "feedback_assessment_feedback_log"
    _description = "Feedback assessment Log"

    emp_name = fields.Many2one('hr.employee', string="Employee")
    dept_id = fields.Many2one('hr.department', string='Department', related="emp_name.department_id")
    deg_id = fields.Many2one('hr.job', string='Designation', related="emp_name.job_id")
    status_feedback = fields.Char(string="Status")
    assign_feedback_form = fields.Many2one('onboard_survey_type_master')
    tagged_feedback_id = fields.Many2one('kw_onboard_induction_emp_tagged')


class ConfirmationEmployeeTagged(models.TransientModel):
    _name = "confirm_employee_wizard"
    _description = "Tagged  Wizard"

    tagged_id = fields.Many2one('kw_onboard_induction_emp_tagged', 'Tagged',
                                default=lambda self: self._context.get('current_record'))
    note = fields.Text('Comment', size=40)

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
