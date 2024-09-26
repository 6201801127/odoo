import pytz
import math
from datetime import datetime, date
from werkzeug import urls

from odoo import models, fields, api, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError


class kw_feedback_details(models.Model):
    _name = "kw_feedback_details"
    _description = "Assessment"
    _rec_name = "assessee_id"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('login', False):
            ids = []
            if self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_manager'):
                args += [('feedback_status', '!=', '0'),
                         ('assessment_tagging_id.assessment_type', '=', 'probationary')]
            #     query = f"select a.id from kw_feedback_details  as a  join kw_feedback_assessment as b on b.id = a.assessment_tagging_id where a.feedback_status != '0' and b.assessment_type = 'probationary'"
            #     self._cr.execute(query)
            #     ids = self._cr.fetchall()
            #     args += [('id','in',ids)]
            # else:
            elif not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_manager'):
                if (not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_approval_manager')
                        and not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_manager')
                        and not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_pip_manager')
                        and not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_report_manager')):
                    if (self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_assessee')
                            and not self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_assessor')):
                        args += [('assessee_id', 'child_of', self.env.user.employee_ids.ids),
                                 ('feedback_status', '=', '6'), ]
                    elif self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_assessor'):
                        args += [('assessor_id', 'child_of', self.env.user.employee_ids.ids),
                                 ('feedback_status', 'in', ('3', '4', '5', '6')), ]
                # ('assessor_id', 'child_of', self.env.user.employee_ids.ids), ('feedback_status', '=', '3'),
                args += [('prob_status', 'in', ['completed', 'extended','failed_prob']),
                         ('assessment_tagging_id.assessment_type', '=', 'probationary')]
                # print("args >> ", args)

        return super(kw_feedback_details, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                        access_rights_uid=access_rights_uid)

    @api.model
    def _read_group_stage_ids(self, categories, domain, order):
        """ Read all the stages and display it in the kanban view, even if it is empty."""
        category_ids = categories._search([], order="id DESC", access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    assessor_id = fields.Many2many('hr.employee', 'kw_feedback_details_assessor_rel', 'feedback_details_id',
                                   'employee_id', string='Assessor', domain="[('id','!=',assessee_id)]")
    assessee_id = fields.Many2one('hr.employee', string='Assessee', required=True)
    ra_id = fields.Many2one('hr.employee', string="Reporting Authority", related="assessee_id.parent_id")
    assessee_job_id = fields.Many2one('hr.job', string="Designation", related="assessee_id.job_id")
    department = fields.Char(string="Department", compute="compute_department")
    image_small = fields.Binary(related='assessee_id.image', store=False)
    period_id = fields.Many2one('kw_feedback_assessment_period', ondelete='restrict')
    survey_id = fields.Many2one(comodel_name='survey.survey', string='Template Type',
                                domain="[('survey_type.code','=','assessment_feedback')]", required=True)

    assessment_tagging_id = fields.Many2one(comodel_name='kw_feedback_assessment', string='Assessment Type',
                                            required=True, ondelete='restrict')
    bench_mark = fields.Float(related='assessment_tagging_id.benchmark')
    assessment_from_date = fields.Date(string='Start Date', autocomplete="off")
    assessment_to_date = fields.Date(string='End Date', autocomplete="off")
    assessment_date = fields.Date(string='Assessment Date', autocomplete="off")
    rrule_type = fields.Selection(related='assessment_tagging_id.frequency', string='Recurrence')
    assessment_type = fields.Selection(related='assessment_tagging_id.assessment_type', string='Type')
    practical_test = fields.Boolean(related='assessment_tagging_id.practical_test', string='Machine Test')

    feedback_status = fields.Selection(string='Status',
                                       selection=[('0', 'Not Scheduled'), ('1', 'Scheduled'), ('2', 'Draft'),
                                                  ('3', 'Completed'), ('4', 'Sent for Approval'), ('5', 'Approved'),
                                                  ('6', 'Published')], default='0')
    view_feedback_url = fields.Char("Assessment Feedback View Result", compute="_compute_feedback_url")

    final_remark = fields.Text(string='Final Remark')
    total_score = fields.Float(string='Avg. Score (in %)', help='Score will visible after complete your feedback')
    positive_area = fields.Text(string='Positive Area')
    weak_area = fields.Text(string='Weak Area')
    suggestion_remark = fields.Text(string='Suggestion')
    weightage_id = fields.Many2one(comodel_name='kw_feedback_weightage_master', string='Performance Grade',
                                   ondelete='restrict', group_expand='_read_group_stage_ids')
    weightage_value = fields.Char(string="Value", related="weightage_id.value")
    weightage_from_range = fields.Float(string="From Range", related="weightage_id.from_range")
    weightage_to_range = fields.Float(string="To Range", related="weightage_id.to_range")
    color = fields.Integer("Color Index", compute="change_color")
    count_score = fields.Boolean(compute='compute_count_score', store=False)
    compute_final_state = fields.Boolean(compute='_compute_final_state', store=False)
    compute_weightage = fields.Boolean(compute='_compute_weightage_value', store=False)

    feedback_final_config_id = fields.One2many('kw_feedback_final_config', 'feedback_details_id',
                                               string='Assessor Feedback')

    goal_id = fields.Many2one(comodel_name='kw_feedback_goal_and_milestone', string='Goal Name', ondelete='restrict')
    default_goal = fields.Boolean(compute='_set_default_goal')
    goal_name = fields.Char(string='Goal', related='goal_id.goal_name')
    milestones = fields.One2many(string='Milestone', related='goal_id.milestones')
    goal_state = fields.Selection(related='goal_id.state', string='Goal Status', store=True)
    approval_user = fields.Many2one('hr.employee', string='Pending at/Approved by')
    approval_status = fields.Selection(string='Approval Status',
                                       selection=[('revert', 'Revert'), ('approved', 'Approved')])
    approve_remark = fields.Text(string='Remark')
    revert_remark = fields.Text(string='Remark')

    meeting_id = fields.Many2one(comodel_name='kw_meeting_events', string='Meeting Name', ondelete='restrict')
    meeting_date = fields.Date(related='meeting_id.kw_start_meeting_date')
    meeting_time = fields.Selection(related='meeting_id.kw_start_meeting_time')
    meeting_duration = fields.Selection(related='meeting_id.kw_duration')
    meeting_room = fields.Many2one(comodel_name='kw_meeting_room_master', related='meeting_id.meeting_room_id')

    prob_status = fields.Selection(string='Confirmation Status',
                                   selection=[('extended', 'Extended'), ('completed', 'Confirmed'),('failed_prob','Failed Probation Confirmation')])
    # new designation added to update in employee 26 Feb 2021 (Gouranga)
    job_id = fields.Many2one('hr.job', 'New Designation')
    # new effective_from_date added to update in employee 4 March 2021 (Gouranga)
    effective_from_date = fields.Date('Effective From')
    extend_date = fields.Date(string='Extended Probation Completion Date')
    next_assessment_date = fields.Date(string='Next Assessment Date')

    is_machine_test_required = fields.Boolean(string='Practical Test Required')
    machine_test_result = fields.Float(string='Practical Test Score (in %)')

    assessment_feedback_type = fields.Selection(string="Assessment Type",
                                                selection=[('internship', 'Internship'),
                                                           ('probationary', 'Probationary'),('traineeship','Traineeship')],
                                                compute="_compute_assessment_feedback_type")
    is_publish_hr = fields.Boolean(string="publish", compute="_manager_test_value")
    emp_code = fields.Char(string="code", related='assessee_id.emp_code')
    active = fields.Boolean(string="Active", default=True)

    def toggle_active(self):
        if self.active == True:
            self.write({'active': False})
        else:
            self.write({'active': True})

    @api.multi
    def _manager_test_value(self):
        for rec in self:
            has_group_manager = self.env.user.has_group('kw_assessment_feedback.group_assessment_feedback_manager')
            if has_group_manager:
                rec.is_publish_hr = True
    '''
    added on 5 March 2021 (Gouranga) 
    if first word of assessment_tagging_id.name == probationary then probationary
    elif first word of assessment_tagging_id.name == internship then internship
    '''

    @api.multi
    def _compute_assessment_feedback_type(self):
        for feedback in self:
            if feedback.assessment_tagging_id:
                if feedback.assessment_tagging_id.name[0:12].lower() == "probationary":
                    feedback.assessment_feedback_type = "probationary"

                elif feedback.assessment_tagging_id.name[0:10].lower() == "internship":
                    feedback.assessment_feedback_type = "internship"
                    
                elif feedback.assessment_tagging_id.name[0:11].lower() == "traineeship":
                    feedback.assessment_feedback_type = "traineeship"

    @api.constrains('machine_test_result', 'is_machine_test_required')
    def _machine_test_validation(self):
        for record in self:
            if record.is_machine_test_required and record.machine_test_result > 100:
                raise ValidationError("Practical test score should not greater than 100%.")

    @api.onchange('is_machine_test_required')
    def _change_machine_test_value(self):
        if not self.is_machine_test_required:
            self.machine_test_result = 0

    @api.model
    def create(self, vals):
        new_record = super(kw_feedback_details, self).create(vals)
        if new_record.assessment_tagging_id and new_record.assessment_tagging_id.practical_test:
            new_record.is_machine_test_required = True
        else:
            new_record.is_machine_test_required = False

        return new_record

    @api.onchange('prob_status')
    def change_etend_date(self):
        for record in self:
            if record.prob_status == 'completed':
                record.extend_date = False
                record.next_assessment_date = False
            elif record.prob_status == 'failed_prob':
                record.extend_date = False
                record.next_assessment_date = False
                
            else:
                record.job_id = False
                record.effective_from_date = False

    @api.constrains('prob_status')
    def _validate_probation(self):
        for feedback in self:
            is_scored = True
            # print("scroed===============",is_scored)
            # if feedback.prob_status:
            #     if feedback.total_score < 60 and feedback.prob_status != 'extended':
            #         raise ValidationError("Confirmation Status must be 'Extended' due to 'Avg. Score (in %)' is less than 60.")

            #     elif feedback.total_score >= 60 and feedback.prob_status != 'completed':
            #         raise ValidationError("Confirmation Status must be 'Confirmed' due to 'Avg. Score (in %)' is more than 60.")
            for rec in feedback.feedback_final_config_id:
                if rec.total_score < 60 and feedback.prob_status == 'completed':
                    raise ValidationError("Confirmation Status must be 'Extended' due to one of the 'Score' is less than 60.")
                if rec.total_score < 60 and feedback.prob_status == 'extended':
                    is_scored = False
                # elif rec.total_score >= 60 and feedback.prob_status == 'extended':
                    # raise ValidationError("Confirmation Status must be 'Confirmed' due to one of the 'Score' is more than 60.")
            # if feedback.total_score >= 60 and feedback.prob_status == 'extended':
                # raise ValidationError("Confirmation Status must be 'Confirmed' due to 'Avg. Score (in %)' is more than 60.")
            if is_scored is True and feedback.prob_status == 'extended':
                raise ValidationError("Confirmation Status must be 'Confirmed' due to  'Score' is more than 60.")

    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r: r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments
    
    @api.multi
    def compute_department(self):
        for rec in self:
            if rec.assessee_id.department_id:
                department = self.get_root_departments(rec.assessee_id.department_id)
                if department:
                    rec.department = department.name

    @api.multi
    def _set_default_goal(self):
        for record in self:
            record._get_goal_details()

    def _get_goal_details(self):
        if not self.goal_id and self.assessment_tagging_id.is_goal:
            goal_record = self.env['kw_feedback_goal_and_milestone'].search(
                [('emp_id', '=', self.assessee_id.id),
                 ('year', '=', self.period_id.period_date.year),
                 ('months', '=', self.period_id.period_date.month)], limit=1)
            self.write({'goal_id': goal_record.id if goal_record else False})

    @api.constrains('assessor_id')
    def assessor_validation(self):
        for record in self:
            if not record.assessor_id and record.feedback_status in ['0', '1', '2']:
                pass
                # raise ValidationError("Minimum one Assessor must be assigned to the Assessee.")
        
    @api.onchange('assessment_from_date', 'assessment_to_date')
    def date_validation(self):
        if self.assessment_from_date and self.assessment_to_date:
            if self.assessment_from_date > self.assessment_to_date:
                raise ValidationError('End Date must be greater than start date.')
            if self.assessment_from_date and self.period_id.period_date:
                if self.assessment_from_date.month != self.period_id.period_date.month:
                    raise ValidationError("Start Date's month should be equal to assessment period date's month.")
                if self.assessment_to_date.month != self.period_id.period_date.month:
                    raise ValidationError("End Date's month should be equal to assessment period date's month.")
        
    # @api.onchange('assessment_date')
    # def date_validation(self):
    #     if self.assessment_date and self.period_id.period_date and (self.assessment_date < self.period_id.period_date):
    #         raise ValidationError('Assessment Date must be greater period date.')

    @api.multi
    def change_color(self):
        for record in self:
            color = 0
            if record.feedback_status == '1':
                color = 1
            elif record.feedback_status == '2':
                color = 3
            elif record.feedback_status == '3':
                color = 4
            elif record.feedback_status == '4':
                color = 10
            record.color = color

    @api.multi
    def _compute_feedback_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.view_feedback_url = urls.url_join(base_url, "kw/feedback/final_feedback/%s" % (slug(record)))

    @api.multi
    def view_feedback(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'View Assessment Feedback',
            'target': 'self',
            'url': self.with_context(relative_url=True).view_feedback_url
        }

    @api.multi
    @api.depends('feedback_final_config_id')
    def _compute_final_state(self):
        for record in self:
            record._get_final_status()

    def _get_final_status(self):
        if self.feedback_final_config_id and self.feedback_status not in ['4', '5', '6']:
            if any(config_data.feedback_status in ['2', '3'] for config_data in self.feedback_final_config_id):
                self.write({'feedback_status': '2'})
            if all(config_data.feedback_status == '3' for config_data in self.feedback_final_config_id):
                self.write({'feedback_status': '3'})
                self._get_final_sccore()
                self._get_goal_details()
    
    @api.multi
    def _get_compiled_remarks(self):
        for record in self:
            if record.feedback_final_config_id and record.feedback_status not in ['4', '5', '6']:
                positive = '\n'.join(str(config_record.positive_remark) for config_record in record.feedback_final_config_id if config_record.positive_remark)
                record.write({'positive_area': positive})

                weak = '\n'.join(str(config_record.weak_remark) for config_record in record.feedback_final_config_id if config_record.weak_remark)
                record.write({'weak_area': weak})

                suggestion = '\n'.join(str(config_record.improve_remark) for config_record in record.feedback_final_config_id if config_record.improve_remark)
                record.write({'suggestion_remark': suggestion})

    @api.multi
    @api.depends('feedback_status', 'feedback_final_config_id')
    def compute_count_score(self):
        for record in self:
            record._get_final_sccore()

    def _get_final_sccore(self):
        score = 0
        if self.feedback_status in ['3', '4'] and self.feedback_final_config_id:
            score += sum(float(scores.total_score) for scores in self.feedback_final_config_id)
            self.write({'total_score': '%.2f' % (score / len(self.feedback_final_config_id))})
            self._get_final_weightage()

    @api.multi
    @api.depends('total_score')
    def _compute_weightage_value(self):
        for record in self:
            record._get_final_weightage()

    def _get_final_weightage(self):
        weightage_master = self.env['kw_feedback_weightage_master']

        if self.total_score:
            weightage_range = weightage_master.search(
                [('from_range', '<=', math.floor(self.total_score)), ('to_range', '>=', math.floor(self.total_score))])
            self.write({'weightage_id': weightage_range.id})
        else:
            self.write({'weightage_id': False})

    @api.multi
    def take_action_feedback(self):
        self.ensure_one()
        form_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback', 'kw_feedback_approve_feedback_form_view')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_feedback_details',
            'res_id': self.id,
            'views': [(form_id, 'form')],
            'target': 'current'
        }

    def _get_state_action(self, state):
        if state == 'approve':
            form_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback',
                                                                      'kw_assessment_feedback_approval_form')
            form_id = form_res and form_res[1] or False
        else:
            form_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback',
                                                                      'kw_assessment_feedback_revert_form')
            form_id = form_res and form_res[1] or False

        actions = {
            'name': 'Action Approve' if state == 'approve' else 'Action Revert',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_feedback_details',
            'res_id': self.id,
            'views': [(form_id, 'form')],
            'target': 'new'
        }

        return actions

    @api.multi
    def approve_feedback(self):
        self.ensure_one()
        action = self._get_state_action('approve')
        return action

    @api.multi        
    def revert_feedback(self):
        self.ensure_one()
        action = self._get_state_action('revert')
        return action

    @api.multi
    def action_approve_feedback(self):
        self.ensure_one()
        self.write({'feedback_status': '5', 'revert_remark': False, 'approval_status': 'approved'})
        self.env.user.notify_success("Assessment approved successfully.")
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_revert_feedback(self):
        self.ensure_one()
        self.write({'feedback_status': '3', 'approve_remark': False, 'approval_status': 'revert'})
        self.env.user.notify_success("Assessment reverted successfully.")
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def manage_feedback_meeting(self):
        self.ensure_one()
        participants = []

        if self.assessor_id:
            participants = self.assessor_id.ids

        participants += self.assessee_id.ids

        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        assessment_tag = self.env.ref('kw_meeting_schedule.meeting_type_63')

        context = {
            'create': False,
            'default_kw_start_meeting_date': self.assessment_date,
            'default_name': f'{self.assessment_tagging_id.name}',
            'default_email_subject_line': f'{self.assessment_tagging_id.name}',
            'default_employee_ids': [(6, 0, participants)],
            'default_meeting_category': 'general',
            'default_agenda_ids': [[0, 0, {'name': self.assessment_tagging_id.name}]],
            'default_meeting_type_id': assessment_tag.id,
            'default_categ_ids': [(6, 0, assessment_tag.ids)],
            'default_location_id': self.env.user.branch_id.id,
        }

        _action = {
            'name': 'Assessment Meeting Schedule',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'flags': {'action_buttons': False, 'mode': 'edit', 'toolbar': False, },
        }

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        dt = datetime.now(timezone)

        if (self.meeting_id and self.meeting_id.start_datetime
                and self.meeting_id.start_datetime.astimezone(timezone) >= dt):
            _action['res_id'] = self.meeting_id.id
        else:
            self.meeting_id = False
            _action['res_id'] = False

        if not self.meeting_id or (self.meeting_id and self.meeting_id.start_datetime
                                   and self.meeting_id.start_datetime.astimezone(timezone) < dt):
            _action['context'] = context
        else:
            _action['context'] = {'create': False}

        return _action

    @api.multi
    def write(self, vals):
        temp_val = 0
        if self.feedback_status in ['0', '1', '2'] and not self.assessor_id:
            vals['assessor_id'] = [(6, 0, [self.assessee_id.parent_id.id])]
            temp_val = 1
        update_data = super(kw_feedback_details, self).write(vals)

        if self.feedback_status in ['1', '2'] and ('assessor_id' in vals
                                                   or 'survey_id' in vals
                                                   or 'assessment_from_date' in vals
                                                   or 'assessment_to_date' in vals
                                                   or 'assessment_date' in vals):
            self.update_feedback()
            
        # if self.assessment_type in 'periodic' and temp_val == 1 and self.feedback_status in ['0','1','2']:
        #     template = self.env.ref('kw_assessment_feedback.kw_schedule_periodic_feedback_email_template')
        #     if template:
        #         template.send_mail(self.feedback_final_config_id.ids[0], notif_layout="kwantify_theme.csm_mail_notification_light")
        # if self.assessment_type in 'probationary' and temp_val == 1 and self.feedback_status in ['0','1','2']:
        #     template = self.env.ref('kw_assessment_feedback.kw_schedule_probationary_feedback_email_template')
        #     if template:
        #         template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        return update_data
    
    def update_feedback(self):
        final_config = self.env['kw_feedback_final_config']

        for new_records in self:
            duplicate_rec = final_config.search([('feedback_details_id', '=', new_records.id)])

            if duplicate_rec:
                assessor_rec = duplicate_rec.filtered(lambda record: record.assessor_id.id not in new_records.assessor_id.ids or record.assessee_id.id != new_records.assessee_id.id)

                if assessor_rec:
                    self.env.cr.execute(f""" delete from kw_feedback_final_config where feedback_details_id = {new_records.id}""")
                    # assessor_rec.unlink()

            for assessor in new_records.assessor_id:

                vals = {}
                existing_records = final_config.search(
                    [('assessor_id', '=', assessor.id), ('assessee_id', '=', new_records.assessee_id.id),
                     ('feedback_details_id', '=', new_records.id)])

                # # if feedback not started then update survey_id else don't
                if existing_records:
                    for existing_record in existing_records:
                        if existing_record.feedback_status == '1':
                            existing_record.update({'survey_id': new_records.survey_id.id})
                        else:
                            pass

                        # # If existing record then update the dates and tag id
                        existing_record.write({
                            'assessment_from_date': new_records.assessment_from_date if new_records.assessment_from_date else False, 
                            'assessment_to_date': new_records.assessment_to_date if new_records.assessment_to_date else False,
                            'assessment_date': new_records.assessment_date if new_records.assessment_date else False,
                            })
                else:
                    vals = {
                        'assessor_id': assessor.id,
                        'assessee_id': new_records.assessee_id.id,
                        'survey_id': new_records.survey_id.id,
                        'assessment_from_date': new_records.assessment_from_date if new_records.assessment_from_date else False,
                        'assessment_to_date': new_records.assessment_to_date if new_records.assessment_to_date else False,
                        'assessment_date': new_records.assessment_date if new_records.assessment_date else False,
                        'feedback_details_id': new_records.id
                    }

                    final_config.create(vals)
        return True

    @api.model
    def get_cc_emails(self):
        return ','.join(set(user_email.work_email for user_email in self.assessor_id if user_email.work_email) |
                    {self.env.user.employee_ids.work_email} if self.env.user.employee_ids and self.env.user.employee_ids.work_email else set() |
                    {self.period_id.create_uid.email} if self.period_id.create_uid.id not in [1, 2] and self.period_id.create_uid.email else set())
        # values = ','.join(str(user_email.work_email) for user_email in self.assessor_id)
        # values += ',' + self.env.user.employee_ids.work_email if self.env.user.employee_ids else False
        # if self.period_id.create_uid.id not in [1, 2]:
        #     values += ',' + self.period_id.create_uid.email
        # return values

    def _get_name(self):
        """ Utility method to allow name_get to be override without re-browse the partner """

        probationary = self
        name = probationary.name or ''
        if self._context.get('probationary_name'):
            name = 'Final ' + self.period_id.name + '-' + self.assessee_id.name
        return name

    # #send custom email by changing the model description
    def assessment_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                                    notif_layout=False, template_layout=False, ctx_params=None, description=False):

        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)

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
            return mail.id  
