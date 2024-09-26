from odoo import models, fields, api, tools
from odoo.exceptions import  ValidationError
from datetime import datetime,date, timedelta
class kw_appraisal_goal(models.Model):
    _inherit = 'kw_appraisal_goal'
    _description = 'Performance Navigator Goal'


    def get_default_period(self):
        return self.env['kw_assessment_period_master'].sudo().search([],order='id desc',limit=1).id

    appraisal_period = fields.Many2one('kw_assessment_period_master', string='Appraisal Period',default=get_default_period)
    goal_milestone_accepted = fields.Boolean('Goal Accepted',default=False)
    goal_milestone_bool = fields.Boolean('Goal Accepted', compute='check_user', store=False)
    is_goal_user = fields.Boolean('Is user', compute='check_user', store=False)
    goal_progress_hide =fields.Boolean('Progress hide',compute='check_milestones_completed', store=False)
    division_id = fields.Many2one('hr.department',string='Division',related='employee_id.division')
    # validation for Each employee can have only one goal per appraisal period
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    
    
    @api.depends('goal_milestone_accepted','employee_id')
    def _compute_css(self):
        for rec in self:
            existing_app = self.env['hr.appraisal'].sudo().search([('emp_id', '=', rec.employee_id.id)])
            if existing_app or  rec.goal_milestone_accepted == True and (rec.create_uid.employee_ids == rec.employee_id.parent_id == self.env.user.employee_ids):
                rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'

    @api.constrains('appraisal_period')
    def check_goal_appraisal_period(self):
        for record in self:
            existing_goal = self.env['kw_appraisal_goal'].sudo().search([
                ('employee_id', '=', record.employee_id.id),
                ('appraisal_period', '=', record.appraisal_period.id),
                ('id', '!=', record.id)
            ])
            if existing_goal:
                raise ValidationError('Each employee can have only one goal per appraisal period.')
            
    # view details after goal & milestone progress completion       
    @api.multi
    def view_goal_milestone_details(self):
        self.ensure_one()
        form_res = self.env['ir.model.data'].get_object_reference('kw_performance_navigator', 'kw_performance_navigator_goal_update_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Goal & Milestone Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'current',
            'context':{'create':False,'edit':False}
            }
    # update progress for goal milestone present
    @api.multi
    def update_goal_milestone(self):
        self.ensure_one()
        form_res = self.env['ir.model.data'].get_object_reference('kw_performance_navigator', 'kw_performance_navigator_goal_update_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Update Goal Progress',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'current',
            'flags':{'mode':'edit',}
            }

    # checking users for button invisible
    @api.depends('employee_id')
    def check_user(self):
        for rec in self:
            current_employee = rec.employee_id
            appraisal_count = self.env['hr.appraisal'].sudo().search([('emp_id', '=', current_employee.id)])
            if appraisal_count:
                rec.goal_milestone_bool = True
                rec.goal_milestone_accepted = False
            else:
                rec.goal_milestone_bool=False

             # Check if the logged-in user is the same as the employee_id
            if rec.env.user.employee_ids.id == rec.employee_id.id and not appraisal_count:
                rec.is_goal_user = True
            else:
                rec.is_goal_user = False

    # checking for update progress button hide if milestones completed 
    @api.depends('milestone_id.status')
    def check_milestones_completed(self):
        for goal in self:
            all_milestones_completed = all(milestone.status for milestone in goal.milestone_id)
            goal.goal_progress_hide = all_milestones_completed
         
    # RA adding goal and milestone for new employees completing probation period
    @api.onchange('appraisal_period')
    def onchange_appraisal_period(self):
        user = self.env.user
        appraisal_data = self.env['hr.appraisal'].sudo().search([]) 
        subordinates = []
        if user.employee_ids.child_ids:
            subordinates = user.employee_ids.child_ids.ids

        no_appr_subordinates = self.env['hr.employee'].search([('id', 'not in', appraisal_data.mapped('emp_id').ids), ('id', 'in', subordinates)])
        assessment_completion_records = self.env['assessment_completion_details'].search([
            ('assessment_complete_boolean', '=', True)
        ])
        allowed_subordinates = no_appr_subordinates.filtered(
            lambda emp: emp.id in assessment_completion_records.mapped('employee_id').ids
        ).ids
        # allowed_subordinates = no_appr_subordinates.ids
        return {'domain': {'employee_id': [('id', 'in', allowed_subordinates)]}}
    
    # user accepting goals
    @api.multi
    def accept_goal_milestone(self):
        action_id =self.env.ref('kw_performance_navigator.kw_performance_navigator_goal_action_window').id
        for rec in self:
            if self.env.user.employee_ids.id != rec.employee_id.id:
                raise ValidationError("Concerned employee need to accept his/her goals")
            else:
                rec.goal_milestone_accepted = True
                # return {
                #             'type': 'ir.actions.act_url',
                #             'tag': 'reload',
                #             'url': f'/web#action={action_id}&model=kw_appraisal_goal&view_type=list',
                #             'target': 'self',
                #         }
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Goal is Accepted.',
                        'img_url':  '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                    }
                }

    @api.model
    def create(self, vals):
        record = super(kw_appraisal_goal, self).create(vals)
        email_cc = ''
        employee_id = vals.get('employee_id')
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if employee.parent_id and employee.parent_id.user_id.id == self.env.uid:
                template = self.env.ref('kw_performance_navigator.goal_acceptance_reminder_email_template')
                manager_group = self.env.ref('kw_performance_navigator.group_performance_navigator_manager')
                manager_emails = manager_group.users.mapped('email') if manager_group else []
                parent_email = employee.parent_id.user_id.email
                if parent_email:
                    manager_emails.append(parent_email)
                email_cc = ','.join(manager_emails)
                template.with_context(cc=email_cc, employee=employee).send_mail(
                    record.id, notif_layout="kwantify_theme.csm_mail_notification_light"
                ) 
        return record

         

    # Goal and KRA reminder till user accepts or agree
    @api.model
    def send_goal_reminder_emails(self):
        email_cc = ''
        goals = self.search([('goal_milestone_accepted', '=', False)])
        kra_emp = self.env['kw_appraisal_kra_emp'].sudo().search([('kra_agree_or_disagree','=',False),('assign_template_kra_not_appraisal','=',True)])
        for goal in goals:
            employee = goal.employee_id
            if employee.user_id:
                template = self.env.ref('kw_performance_navigator.milestone_reminder_email_template')
                manager = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                email_cc = ','.join(manager.mapped("email")) if manager else ''
                template.with_context(cc=email_cc,employee=employee).send_mail(goal.id,notif_layout="kwantify_theme.csm_mail_notification_light")  
        email_cc = ''
        if kra_emp:
            for kra in kra_emp:
                emp = kra.emp_id
                if emp.user_id:
                    template = self.env.ref('kw_performance_navigator.kra_agree_reminder_email_template')
                    manager = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                    email_cc = ','.join(manager.mapped("email")) if manager else ''
                    template.with_context(cc=email_cc,employee=emp).send_mail(kra.id,notif_layout="kwantify_theme.csm_mail_notification_light")  

    # milestone reminder before 5 days of deadline
    @api.multi
    def milestone_achievement_reminder_mail(self):
        today = fields.Date.today()
        reminder_date = today + timedelta(days=5)
        milestone_ids = self.env['kw_appraisal_milestone'].search([('milestone_date', '>=', today),('milestone_date', '<=', reminder_date),('status', '=', False),])
        for milestone in milestone_ids:
            # print("Reminder email should be sent for milestone:", milestone.name)
            template = self.env.ref('kw_appraisal.milestone_reminder_email_template')
            manager = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
            email_cc = ','.join(manager.mapped("email")) if manager else ''
            template.with_context(cc=email_cc,employee=milestone.goal_id.employee_id,achievement_date=milestone.milestone_date).send_mail(milestone.goal_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")    
    # Search methods to see records as per cxo configuration and other domain
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is None:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(kw_appraisal_goal, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(kw_appraisal_goal, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def _get_access_domain(self):
        user = self.env.user
        domain = [('employee_id.user_id', '!=', user.id)] 
        
        # checking RA,Division head,department head
        if self.env.context.get('type'):
            initial_domain = ['|', '|', '|','|',
                        ('employee_id.user_id', '=', user.id),
                        ('employee_id.parent_id.user_id', '=', user.id),
                        ('employee_id.parent_id.parent_id.user_id', '=', user.id),
                        ('employee_id.division.manager_id.user_id', '=', user.id),
                        ('employee_id.department_id.manager_id.user_id', '=', user.id)]
            access_config = self.env['appraisal_cxo_configuration'].sudo().search([('employee_id', '=', user.employee_ids.id)])

            # Check if the user has manager access or all access in configuration
            if user.has_group('kw_performance_navigator.group_performance_navigator_manager') or (access_config and access_config.name == 'all'):
                domain = []
            else:
                access_config_domain = []
                if access_config:
                    access_type = access_config.name
                    if access_type == 'other':
                        department_ids = access_config.department_id.ids
                        access_config_domain = ['|', '|', '|',
                                        ('employee_id.department_id', 'in', department_ids),
                                        ('employee_id.division', 'in', department_ids),
                                        ('employee_id.section', 'in', department_ids),
                                        ('employee_id.practise', 'in', department_ids)]
                all_domain = ['|'] + access_config_domain + initial_domain if access_config_domain else initial_domain
                if all_domain:
                    domain = ['&'] + domain + all_domain

        else:
            domain = [('employee_id.user_id', '=', user.id)]

        return domain   


