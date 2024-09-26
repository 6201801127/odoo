# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime,date
from odoo.exceptions import ValidationError
import pytz
import math

class HrAppraisalForm(models.Model):
    _name = 'hr.appraisal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'emp_id'
    _description = 'Annual Appraisal'
    _order = 'id desc'

    @api.model
    def _read_group_stage_ids(self, categories, domain, order):
        """ Read all the stages and display it in the kanban view, even if it is empty."""
        category_ids = categories._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    def _default_stage_id(self):
        """Setting default stage"""
        rec = self.env['hr.appraisal.stages'].search([], limit=1, order='sequence ASC')
        return rec.id if rec else None

    appraisal_year_rel = fields.Many2one('kw_assessment_period_master', string="Appraisal relation")
    appraisal_year = fields.Char(string="Appraisal Period")
    kw_ids = fields.Integer(string="kw ids")
    emp_id = fields.Many2one('hr.employee', string="Employee", required=True)
    e_name = fields.Char(string='Employee Name',related='emp_id.name')
    date_of_joining = fields.Date(string="Date of Joining",related='emp_id.date_of_joining')
    employee_ra = fields.Many2one(related='emp_id.parent_id', store=False)
    e_code = fields.Char(string="Employee Code", related="emp_id.emp_code")
    deg_id = fields.Char(related='emp_id.job_id.name',string='Designation')
    dept_id = fields.Char(related='emp_id.department_id.name',string='Department')
    div_id = fields.Char(related='emp_id.division.name',string='Division')
    sec_id = fields.Char(related='emp_id.section.name',string='Section')
    pract_id = fields.Char(related='emp_id.practise.name',string='Practice')
    current_dt = fields.Date(string="Today Date", default=fields.Date.today())
    app_period_from = fields.Date("Start Date", required=True, readonly=False)
    appraisal_deadline = fields.Date(string="End Date", required=True)
    final_interview = fields.Date(string="Final Interview", help="After sending survey link,you can"
                                                                 " schedule final interview date")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    hr_emp = fields.Boolean(string="Self", default=False)
    hr_manager = fields.Boolean(string="LM select", default=False)
    hr_collaborator = fields.Boolean(string="ULM select", default=False)
    hr_colleague = fields.Boolean(string="Colleague(Peer)", default=False)
    hr_manager_id = fields.Many2many('hr.employee', 'manager_appraisal_rel', string="LM",domain=['|',('active','=',True),('active','=',False)])
    hr_collaborator_id = fields.Many2many('hr.employee', 'collaborators_appraisal_rel',
                                          string="ULM",domain=['|',('active','=',True),('active','=',False)])
    manager_survey_id = fields.Many2one('survey.survey', string="Select Manager Opinion Form")
    emp_survey_id = fields.Many2one('survey.survey', string="Appraisal Form")
    collaborator_survey_id = fields.Many2one('survey.survey', string="Select Collaborator Opinion Form")
    colleague_survey_id = fields.Many2one('survey.survey', string="Select Colleague Opinion Form")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    final_evaluation = fields.Text(string="Final Evaluation")
    tot_comp_survey = fields.Integer(string="Count Answers", compute="_compute_completed_survey")
    tot_sent_survey = fields.Integer(string="Count Sent Questions")
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.uid)
    state = fields.Many2one('hr.appraisal.stages', string='Current Stage', track_visibility='onchange', index=True,
                            default=lambda self: self._default_stage_id(),
                            group_expand='_read_group_stage_ids')
    state_sequence = fields.Integer(related='state.sequence')
    # for coloring the kanban box
    color = fields.Integer(string="Color Index")
    kw_appraisal_id = fields.Many2one('kw_appraisal', 'Appraisal IDS')

    # LM & ULM start and end date field
    hr_lm_start_date = fields.Date(string="LM Start Date", required=True)
    hr_lm_end_date = fields.Date(string='LM End Date', required=True)
    hr_ulm_start_date = fields.Date(string='ULM Start Date', required=True)
    hr_ulm_end_date = fields.Date(string='ULM End Date', required=True)
    survey_state_id = fields.Char(string="Current Status", compute='_survey_response_id')
    ra_id = fields.Many2one(comodel_name='hr.employee',string="Assessor Name", compute='_reviewer')
    date_time = fields.Date(string='Current Date', compute='_find_current_date')
    hr_survey_status = fields.Char(string="Status", compute='_hr_survey_state')
    score = fields.Float(string="Competency Score", compute='count_score', store=True,
                         help='Score will visible after publish your appraisal')
    compare_self_date = fields.Boolean(string="Self compare date", compute='_self_compare_date')
    compare_lm_date = fields.Boolean(string="LM compare date", compute='_lm_compare_date')
    compare_ulm_date = fields.Boolean(string="ULM compare date", compute='_ulm_compare_date')
    compare_self_end_date = fields.Boolean(string="Self End Date", compute='_self_end_date')
    compare_lm_end_date = fields.Boolean(string="compare lm End Date", compute='_lm_end_date')
    compare_ulm_end_date = fields.Boolean(string="compare ulm End Date", compute='_ulm_end_date')
    state_compare = fields.Boolean(string="State Compare", compute='_state_compare')
    kra_score = fields.Float(string="KRA Score", help='KRA Score will visible after publish your appraisal')
    hr_end_date = fields.Date(string="End Date", compute='_hr_end_date')
    user_input_ids = fields.One2many('survey.user_input', 'appraisal_id')

    reassessment = fields.Boolean(default=False)
    self_input_id = fields.Many2one('survey.user_input')
    lm_input_id = fields.Many2one('survey.user_input')
    ulm_input_id = fields.Many2one('survey.user_input')
    self_status = fields.Char(string='Self Status',compute='_get_set_status')
    lm_status = fields.Char(string='LM Status',compute='_get_set_status')
    ulm_status = fields.Char(string='ULM Status',compute='_get_set_status')
    total_score = fields.Float(string='Total Score')
    
    total_final_score = fields.Float(string="Total Score",compute="get_increment_amount",store=False)
    increment_percentage = fields.Float(string="Increment(%)",compute="get_increment_amount",store=False)
    employee_ctc = fields.Float(string="CTC",compute="get_current_ctc",store=False)
    final_increment = fields.Float(string="Final Increment")
    update_increment = fields.Boolean(string="Update Increment Flag")
    # increment_amount = fields.Float(string="Increment",compute="get_current_ctc",inverse="_inverse_final_increment")
    new_designation = fields.Many2one('hr.job',string="New Designation")
    new_grade = fields.Many2one('kwemp_grade_master',string="Grade")
    final_ctc = fields.Float(string="Final CTC",store=False)
    applied_eos = fields.Boolean(compute='_compute_eos')
    training_percentage = fields.Float()
    planned_training_hours = fields.Char()
    achieved_duration = fields.Char()
    training_include = fields.Boolean()
    training_score = fields.Float()
    score_calculation = fields.Selection([('lm_ulm', '(LM + ULM) / 2'), ('lm', 'LM')],string='Score Calculation Type')
    

    @api.depends('emp_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.emp_id.id)], limit=1)
            rec.applied_eos = True if resignation else False

    @api.multi
    def _get_set_status(self):
        for record in self:
            if record.self_input_id:
                if record.self_input_id.sudo().state == 'new':
                    record.self_status = 'In Progress'
                elif record.self_input_id.sudo().state == 'skip':
                    record.self_status = 'Draft'
                elif record.self_input_id.sudo().state == 'done':
                    record.self_status = 'Completed'
                else:
                    record.self_status = 'Not Started'
            else:
                record.self_status = 'Not Started'

            if record.lm_input_id:
                if record.lm_input_id.sudo().state == 'new':
                    record.lm_status = 'In Progress'
                elif record.lm_input_id.sudo().state == 'skip':
                    record.lm_status = 'Draft'
                elif record.lm_input_id.sudo().state == 'done':
                    record.lm_status = 'Completed'
                else:
                    record.lm_status = 'Not Started'
            else:
                record.lm_status = 'Not Started'

            if record.ulm_input_id:
                if record.ulm_input_id.sudo().state == 'new':
                    record.ulm_status = 'In Progress'
                elif record.ulm_input_id.sudo().state == 'skip':
                    record.ulm_status = 'Draft'
                elif record.ulm_input_id.sudo().state == 'done':
                    record.ulm_status = 'Completed'
                else:
                    record.ulm_status = 'Not Started'
            else:
                if (record.hr_manager and record.emp_id.parent_id and record.emp_id.parent_id.parent_id and not record.emp_id.parent_id.parent_id.parent_id) or not record.hr_collaborator:
                    record.ulm_status = 'Not Required'
                else:
                    record.ulm_status = 'Not Started'


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            args += [('kw_ids','=',appraisal_id)]
        
        if self._context.get('filter_previous_period'):

            if len(ids) >= 2:
                appraisal_id = int(ids[1]['id']) if 'id' in ids[1] else 0

            args += [('kw_ids','=',appraisal_id)]

        return super(HrAppraisalForm, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            domain += [('kw_ids','=',appraisal_id)]
        
        if self._context.get('filter_previous_period'):

            if len(ids) >= 2:
                appraisal_id = int(ids[1]['id']) if 'id' in ids[1] else 0

            domain += [('kw_ids','=',appraisal_id)]

        return super(HrAppraisalForm, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.multi
    def _hr_end_date(self):
        for record in self:
            if record.state.sequence == 2:
                record.hr_end_date = record.appraisal_deadline
            if record.state.sequence == 3:
                record.hr_end_date = record.hr_lm_end_date
            if record.state.sequence == 4:
                record.hr_end_date = record.hr_ulm_end_date

    @api.model
    def reminder_mail(self):
        # print("method called")
        try:
            period_master = self.env['kw_assessment_period_master'].search([],order='id desc')
            apr_deadline_check = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_master[0].id or False)])

            lm_deadline_appraisals = apr_deadline_check.filtered(lambda r: not date.today() > r.hr_lm_end_date and r.state.sequence == 3\
                    and (r.hr_lm_end_date - date.today()).days <=2 and r.hr_survey_status != 'Completed' and r.reassessment == False)
            lm_hr_managers = lm_deadline_appraisals.mapped('hr_manager_id')
            template = self.env.ref('kw_appraisal.kw_lm_reminder_email_template')
            for hr in lm_hr_managers:
                hr_appraisal_records = lm_deadline_appraisals.filtered(lambda r: r.hr_manager_id == hr)
                template.with_context(hr_manager=hr,appraisal_records =hr_appraisal_records).send_mail(hr_appraisal_records[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")

            ulm_deadline_appraisals = apr_deadline_check.filtered(lambda r: not date.today() > r.hr_ulm_end_date and r.state.sequence == 4\
                    and (r.hr_ulm_end_date - date.today()).days <=2 and r.hr_survey_status != 'Completed')
            ulm_hr_managers = ulm_deadline_appraisals.mapped('hr_collaborator_id')
            template = self.env.ref('kw_appraisal.kw_ulm_reminder_email_template')
            for hr in ulm_hr_managers:
                hr_appraisal_records = ulm_deadline_appraisals.filtered(lambda r: r.hr_collaborator_id == hr)
                template.with_context(hr_manager=hr,appraisal_records =hr_appraisal_records).send_mail(hr_appraisal_records[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")
            
            reassessment_reminder_appraisals = apr_deadline_check.filtered(lambda r: r.state.sequence == 3 and r.reassessment)
            lm_hr_managers = reassessment_reminder_appraisals.mapped('hr_manager_id')
            template = self.env.ref('kw_appraisal.kw_reassessment_reminder_mail_template')
            for hr in lm_hr_managers:
                hr_appraisal_records = reassessment_reminder_appraisals.filtered(lambda r: r.hr_manager_id == hr)
                template.with_context(hr_manager=hr,appraisal_records =hr_appraisal_records).send_mail(hr_appraisal_records[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")
            
            for records in apr_deadline_check:

                if not date.today() > records.appraisal_deadline:
                    diff_self_end_date = (records.appraisal_deadline -  date.today()).days
                    # print("self",diff_self_end_date)
                    if records.state.sequence == 2 and diff_self_end_date <= 2 and records.survey_state_id != 'Completed':
                        template = self.env.ref('kw_appraisal.kw_reminder_self_email_template')
                        template.send_mail(records.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                

        except Exception as e:
            # print("Appraisal cron error: ",e)
            pass

    @api.multi
    def action_send_mail(self):
        # print("Mail Send Successfully...........")
        pass

    @api.multi
    def _ulm_end_date(self):
        for record in self:
            if record.hr_ulm_end_date < record.date_time:
                record.compare_ulm_end_date = True

    @api.multi
    def _lm_end_date(self):
        for record in self:
            if record.hr_lm_end_date < record.date_time:
                record.compare_lm_end_date = True

    @api.multi
    def _self_end_date(self):
        for record in self:
            if record.appraisal_deadline < record.date_time:
                record.compare_self_end_date = True

    @api.multi
    def _state_compare(self):
        for record in self:
            if record.hr_survey_status == "Not Started" or record.hr_survey_status == "Completed":
                record.state_compare = True
            else:
                pass

    @api.multi
    def _self_compare_date(self):
        for record in self:
            if record.app_period_from > record.date_time:
                record.compare_self_date = True

    @api.multi
    def _lm_compare_date(self):
        for record in self:
            if record.hr_lm_start_date > record.date_time:
                record.compare_lm_date = True

    @api.multi
    def _ulm_compare_date(self):
        for record in self:
            if record.hr_ulm_start_date > record.date_time:
                record.compare_ulm_date = True

    @api.multi
    @api.depends('score','kra_score')
    def get_increment_amount(self):
        for record in self:
            # appraisal_final_score = (record.score * 60)/100
            # kra_final_score = (record.kra_score * 40)/100
            # record.total_final_score = appraisal_final_score + kra_final_score
            # record.increment_percentage = (record.total_final_score * 20)/100
            # if record.app_period_from >= date(datetime.today().date().year,1,1):
                record.total_final_score = record.total_score
                kw_appraisal_rec =  self.env['kw_appraisal_employee'].sudo().search([]).filtered(lambda x: record.emp_id.id in x.employee_id.ids)
                if kw_appraisal_rec:
                    ratio = self.env['kw_appraisal_template_score_view'].sudo().search([('survey_id','=',kw_appraisal_rec.kw_survey_id.id)])
                    if ratio:
                        record.increment_percentage =  record.total_final_score * ratio.per_inc/100

    @api.multi
    @api.depends('emp_id','employee_ctc')
    def get_current_ctc(self):
        for record in self:
            contract_id = self.env['hr.contract'].sudo().search([('employee_id','=',record.emp_id.id),('state','=','open')],limit=1)
            if contract_id:
                record.employee_ctc = contract_id.wage
                # record.increment_amount = (record.employee_ctc * record.increment_percentage) / 100
                record.final_ctc = record.employee_ctc + record.final_increment

    # def _inverse_final_increment(self):
    #     for rec in self:
    #         rec.final_increment = rec.increment_amount

    @api.multi
    @api.depends('state')
    def count_score(self):
        for record in self:
            try:
                if record.state.sequence in [5,6]:
                    total_score = 0
                    questions = 0.0
                    number = 0
                    numeric_total = 0
                    for records in record.hr_manager_id:
                        user_input_line = self.env['survey.user_input_line'].sudo().search(
                            [('user_input_id', '=', record.lm_input_id.id)])

                        if len(user_input_line):
                            for lines in user_input_line:
                                if record.ulm_input_id:
                                    self.env.cr.execute(f"SELECT CEIL(SUM(individual_average)) AS final_average FROM (SELECT CEIL(SUM(quizz_mark) / COUNT(DISTINCT question_id) / 2) AS individual_average FROM survey_user_input_line WHERE user_input_id IN ({record.lm_input_id.id}, {record.ulm_input_id.id}) AND answer_type = 'suggestion'  GROUP BY question_id ) AS subquery")
                                    score_dict = self._cr.dictfetchall()
                                    total_score = score_dict[0]['final_average']
                                    self.env.cr.execute(f"SELECT SUM(individual_average) AS final_average FROM (SELECT CEIL(SUM(value_number) / COUNT(DISTINCT question_id))/2 AS individual_average FROM survey_user_input_line WHERE user_input_id IN ({record.lm_input_id.id}, {record.ulm_input_id.id}) AND answer_type = 'number'  GROUP BY question_id ) AS subquery")
                                    number_score = self._cr.dictfetchall()
                                    number = number_score[0]['final_average']
                                else:
                                    total_score += lines.quizz_mark
                                    number += lines.value_number
                                for quest_ids in lines.question_id:
                                    if quest_ids.type == 'simple_choice':
                                        for labels in quest_ids:
                                            questions += max(float(marks.quizz_mark) for marks in labels.labels_ids)
                                    if quest_ids.type == 'numerical_box':
                                        numeric_total += quest_ids.validation_max_float_value
                    if questions !=0:
                        score = (total_score/questions)*100 
                        record.score = '%.3f'%(score)
                    if record.training_include == False:
                        record.training_score = 100
                    else:
                        record.training_score = math.ceil(record.training_percentage)
                    if numeric_total > 0:
                        record.write({
                        'kra_score': (number / numeric_total) * 100,
                        'score_calculation':'lm_ulm'
                    })
                    
                    record._count_final_score()
                else:
                    record.write({
                        'total_score':0.0
                    })
                    pass
            except Exception as e:
                # print("Error in Appraisal- ",record.emp_id.name,str(e))
                continue
        
    # def _count_final_score(self):
    #     for record in self:
    #         if record.state and record.state.sequence in [4,5,6]:
    #             ratio = self.env['kw_appraisal_ratio'].sudo().search([
    #                 ('department','=',record.emp_id.department_id.id if record.emp_id.department_id else False),
    #                 ('division','=',record.emp_id.division.id if record.emp_id.division else False),
    #                 ('section','=',record.emp_id.section.id if record.emp_id.section else False),
    #                 ('practice','=',record.emp_id.practise.id if record.emp_id.practise else False),
    #             ],limit=1)
    #             if ratio:
    #                 appraisal_score = record.score * ratio.per_appraisal / 100
    #                 kra_score = record.kra_score * ratio.per_kra / 100
    #                 final_score = appraisal_score + kra_score
    #                 if final_score > 0:
    #                     record.write({'total_score':final_score})
    def _count_final_score(self):
        for record in self:
            if record.state and record.state.sequence in [4,5,6]:
                kw_appraisal_rec =  self.env['kw_appraisal'].sudo().search([('id','=',record.kw_ids)])
                for rec in  kw_appraisal_rec.employee:
                    for res in rec.employee_id:
                        if res.id == record.emp_id.id:
                            ratio = self.env['kw_appraisal_template_score_view'].sudo().search([('survey_id','=',rec.kw_survey_id.id)])
                            if ratio:
                                # abc = record.score/10 * 9 + record.training_percentage/10 if record.training_include == True else record.score
                                appraisal_score = record.score * ratio.per_appraisal / 100
                                kra_score = record.kra_score * ratio.per_kra / 100
                                training_score = record.training_score * ratio.per_training / 100
                                print('kra_score=====================',kra_score,appraisal_score,training_score)
                                final_score = appraisal_score + kra_score + training_score
                                if final_score > 0:
                                    record.write({'total_score':final_score})

    @api.multi
    def _hr_survey_state(self):
        for record in self:
            survey_emp = record.self_input_id.sudo()
            survey_lm = record.lm_input_id.sudo()
            survey_ulm = record.ulm_input_id.sudo()

            if record.state.sequence == 2:
                record.hr_survey_status = survey_emp.state
            if record.state.sequence == 3:
                record.hr_survey_status = survey_lm.state
            if record.state.sequence == 4:
                record.hr_survey_status = survey_ulm.state

            if record.hr_survey_status == False:
                record.hr_survey_status = "Not Started"
            elif record.hr_survey_status == 'new':
                record.hr_survey_status = "In Progress"
            elif record.hr_survey_status == 'skip':
                record.hr_survey_status = "Draft"
            elif record.hr_survey_status == 'done':
                record.hr_survey_status = "Completed"
            if record.state.sequence == 5:
                record.hr_survey_status = "Completed"
            if record.state.sequence == 6:
                record.hr_survey_status = "Published"

    @api.constrains('app_period_from', 'appraisal_deadline')
    def date_constrains(self):
        for rec in self:
            if rec.appraisal_deadline < rec.app_period_from:
                raise ValidationError('Self Appraisal End Date Must be greater Than Start Date...')

    @api.constrains('hr_lm_start_date', 'hr_lm_end_date')
    def lmdate_constrains(self):
        for rec in self:
            if rec.hr_lm_end_date < rec.hr_lm_start_date:
                raise ValidationError('LM Appraisal End Date Must be greater Than Start Date...')

    @api.constrains('hr_ulm_start_date', 'hr_ulm_end_date')
    def ulmdate_constrains(self):
        for rec in self:
            if rec.hr_ulm_end_date < rec.hr_ulm_start_date:
                raise ValidationError('ULM Appraisal End Date Must be greater Than Start Date...')

    @api.multi
    def _find_current_date(self):
        for record in self:
            current_dt = date.today()
            record.date_time = current_dt

    @api.multi
    def _reviewer(self):
        for record in self:
            if record.state.sequence == 2:
                record.ra_id = record.emp_id.id
            elif record.state.sequence == 3:
                record.ra_id = record.hr_manager_id.id
            elif record.state.sequence == 4:
                record.ra_id = record.hr_collaborator_id.id
            else:
                record.ra_id = False

    @api.model
    def check_groups(self, vals):
        """here groups_ext_ids is a list of groups(external_id may be)"""
        if not vals.get('user_id'):
            return False
        else:
            user = self.env['res.users'].browse(int(vals['user_id']))
            if user.has_group('kw_appraisal.group_appraisal_manager'):
                return True
            else:
                return False

    @api.multi
    def _survey_response_id(self):
        for record in self:
            survey_status = ''
            if record.state.sequence == 2:
                survey_status = record.self_input_id.sudo().state
            elif record.state.sequence == 3:
                survey_status = record.lm_input_id.sudo().state
            elif record.state.sequence == 4:
                survey_status = record.ulm_input_id.sudo().state
            elif record.state.sequence == 5:
                survey_status = 'completed'
            elif record.state.sequence == 6:
                survey_status = 'published'

            if survey_status == 'new':
                record.survey_state_id = "In Progress"
            elif survey_status == 'skip':
                record.survey_state_id = "Draft"
            elif survey_status == 'done':
                record.survey_state_id = "Completed"
            elif survey_status == 'completed':
                record.survey_state_id = "Completed"
            elif survey_status == 'published':
                record.survey_state_id = "Published"
            else:
                record.survey_state_id = "Not Started"

    @api.multi
    def action_call_edit_appraisal(self):
        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'hr_appraisal_action_edit_appraisal_wizard')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Allow Edit',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'hr.appraisal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'new'
            }

    @api.multi
    def action_edit_appraisal(self):
        if self.state.sequence == 3:
            self.edit_for_self()
        elif self.state.sequence == 4:
            self.edit_for_lm()
        elif self.state.sequence == 5:
            if not self.hr_collaborator_id.parent_id:
                self.edit_for_lm()
            else:
                self.edit_for_ulm()
        return

    def scheduler_edit_appraisal(self):
        stages = self.env['hr.appraisal.stages'].sudo()
        self_stage_id = stages.search([('sequence','=',2)],limit=1)
        lm_stage_id = stages.search([('sequence','=',3)],limit=1)
        ulm_stage_id = stages.search([('sequence','=',4)],limit=1)

        current_appraisal_id =  self.env['kw_appraisal'].search([],order="id desc", limit=1)
        self_appraisal_ids = self.env['hr.appraisal'].search([('state.sequence','=',3),('self_input_id.state','=','skip'),('appraisal_year_rel','=',current_appraisal_id.year.id)])
        lm_appraisal_ids = self.env['hr.appraisal'].search([('state.sequence','in',[4,5]),('lm_input_id.state','=','skip'),('appraisal_year_rel','=',current_appraisal_id.year.id)])
        ulm_appraisal_ids = self.env['hr.appraisal'].search([('state.sequence','=',5),('ulm_input_id.state','=','skip'),('appraisal_year_rel','=',current_appraisal_id.year.id)])
        self_str = str(tuple(self_appraisal_ids.mapped('id')))
        lm_str = str(tuple(lm_appraisal_ids.mapped('id')))
        ulm_str = str(tuple(ulm_appraisal_ids.mapped('id')))

        if self_str[-2] == ',':
            len_self_cycle_ids = len(self_str)
            final_self_str = self_str[:len_self_cycle_ids - 2]
            self_cycle_ids = final_self_str + ')'
        else:
            self_cycle_ids = self_str

        if lm_str[-2] == ',':
            len_lm_cycle_ids = len(lm_str)
            final_lm_str = lm_str[:len_lm_cycle_ids - 2]
            lm_cycle_ids = final_lm_str + ')'
        else:
            lm_cycle_ids = lm_str
        
        if ulm_str[-2] == ',':
            len_ulm_cycle_ids = len(ulm_str)
            final_ulm_str = ulm_str[:len_ulm_cycle_ids - 2]
            ulm_cycle_ids = final_ulm_str + ')'
        else:
            ulm_cycle_ids = ulm_str
        

        if self_appraisal_ids:
            query = f"update hr_appraisal set state = {self_stage_id.id} where id in {self_cycle_ids}"
            self._cr.execute(query)
        
        if lm_appraisal_ids:
            query = f"update hr_appraisal set state = {lm_stage_id.id} where id in {lm_cycle_ids}"
            self._cr.execute(query)
        if ulm_appraisal_ids:
            query = f"update hr_appraisal set state = {ulm_stage_id.id} where id in {ulm_cycle_ids}"
            self._cr.execute(query)
        
      
    
    @api.multi
    def edit_for_self(self):
        stages = self.env['hr.appraisal.stages'].sudo()
        stage_id = stages.search([('sequence','=',2)],limit=1)
        self.state = stage_id.id
        if self.self_input_id:
            survey_user_input_partner_id = self.self_input_id.sudo()
        else:
            survey_user_input_partner_id = self.env['survey.user_input'].sudo().search(
                ['&', ('partner_id', '=', self.emp_id.user_id.partner_id.id), ('appraisal_id', '=', self.id)],
                limit=1)
        if survey_user_input_partner_id:
            survey_user_input_partner_id.state = 'skip'
            survey_user_input_partner_id.last_displayed_page_id = 0

    @api.multi
    def edit_for_lm(self):
        stages = self.env['hr.appraisal.stages'].sudo()
        stage_id = stages.search([('sequence','=',3)],limit=1)
        self.state = stage_id.id
        if self.lm_input_id:
            survey_user_input_partner_id1 = self.lm_input_id.sudo()
        else:
            survey_user_input_partner_id1 = self.env['survey.user_input'].sudo().search(
                ['&', ('partner_id', '=', self.hr_manager_id.user_id.partner_id.id),
                    ('appraisal_id', '=', self.id)], limit=1)
        if survey_user_input_partner_id1:
            survey_user_input_partner_id1.state = 'skip'
            survey_user_input_partner_id1.last_displayed_page_id = 0

    @api.multi
    def edit_for_ulm(self):
        stages = self.env['hr.appraisal.stages'].sudo()
        stage_id = stages.search([('sequence','=',4)],limit=1)
        self.state = stage_id.id
        if self.ulm_input_id:
            survey_user_input_partner_id2 = self.ulm_input_id.sudo()
        else:
            survey_user_input_partner_id2 = self.env['survey.user_input'].sudo().search(
                ['&', ('partner_id', '=', self.hr_collaborator_id.user_id.partner_id.id),
                    ('appraisal_id', '=', self.id)], limit=1)
        if survey_user_input_partner_id2:
            survey_user_input_partner_id2.state = 'skip'
            survey_user_input_partner_id2.last_displayed_page_id = 0

    @api.multi
    def action_start_appraisal(self):
        if self.emp_id.user_id and self.emp_id.user_id.id == self.env.user.id and self.hr_emp and self.emp_survey_id:
            # print("Self is :", self.emp_id.name)
            if self.self_input_id and self.self_input_id.sudo().partner_id.id == self.emp_id.user_id.partner_id.id:
                self.self_input_id.sudo().write({'deadline': self.appraisal_deadline})
                token = self.self_input_id.sudo().token
            else:
                token = self.get_appraisal_details(self.emp_id, 'SELF')
            return self.emp_survey_id.with_context(survey_token=token,
                                                   employee_id=self.emp_id.id).action_test_kw_survey()
        for lms in self.hr_manager_id:
            if lms.user_id and lms.user_id.id == self.env.user.id and self.hr_manager and self.manager_survey_id:
                # print("Lm is :", lms.name)
                if self.lm_input_id and self.lm_input_id.sudo().partner_id.id == lms.user_id.partner_id.id:
                    self.lm_input_id.sudo().write({'deadline': self.hr_lm_end_date})
                    token = self.lm_input_id.sudo().token
                else:
                    token = self.get_appraisal_details(lms, 'LM')
                return self.manager_survey_id.with_context(survey_token=token,
                                                           employee_id=self.emp_id.id).action_test_kw_survey()
        for ulms in self.hr_collaborator_id:
            if ulms.user_id and ulms.user_id.id == self.env.user.id and self.hr_collaborator and self.collaborator_survey_id:
                # print("Ulm is :", ulms.name)
                if self.ulm_input_id and self.ulm_input_id.sudo().partner_id.id == ulms.user_id.partner_id.id:
                    self.ulm_input_id.sudo().write({'deadline': self.hr_ulm_end_date})
                    token = self.ulm_input_id.sudo().token
                else:
                    token = self.get_appraisal_details(ulms, 'ULM')
                return self.collaborator_survey_id.with_context(survey_token=token,
                                                                employee_id=self.emp_id.id).action_test_kw_survey()

    @api.multi
    def get_appraisal_details(self, values, checker):
        user_input = self.env['survey.user_input'].sudo()
        survey_rel_id = user_input.search(
            ['&', ('appraisal_id', '=', self.id), ('partner_id', '=', values.user_id.partner_id.id)], limit=1)
        if checker == 'SELF':
            if len(survey_rel_id):
                # print("Self")
                self.self_input_id = survey_rel_id.id
                survey_rel_id.sudo().write({'deadline': self.appraisal_deadline})
                token = survey_rel_id.token
            else:
                # print("Else Self")
                response = user_input.sudo().create(
                    {'survey_id': self.emp_survey_id.id,
                     'partner_id': values.user_id.partner_id.id if values.user_id.partner_id else False,
                     'appraisal_id': self.ids[0], 'deadline': self.appraisal_deadline,
                     'email': values.work_email if values.work_email else False,
                     'emp_code': values.emp_code if values.emp_code else False})
                self.self_input_id = response.id
                return response.token
        elif checker == 'LM':
            if len(survey_rel_id):
                # print("LM")
                self.lm_input_id = survey_rel_id.id
                survey_rel_id.sudo().write({'deadline': self.hr_lm_end_date})
                token = survey_rel_id.token
            else:
                # print("Else LM")
                response = user_input.sudo().create(
                    {'survey_id': self.manager_survey_id.id,
                     'partner_id': values.user_id.partner_id.id if values.user_id.partner_id else False,
                     'appraisal_id': self.ids[0], 'deadline': self.hr_lm_end_date,
                     'email': values.work_email if values.work_email else False,
                     'emp_code': values.emp_code if values.emp_code else False})
                self.lm_input_id = response.id
                return response.token
        elif checker == "ULM":
            if len(survey_rel_id):
                # print("ULM")
                self.ulm_input_id = survey_rel_id.id
                survey_rel_id.sudo().write({'deadline': self.hr_ulm_end_date})
                token = survey_rel_id.token
            else:
                # print("Else ULM")
                response = user_input.sudo().create(
                    {'survey_id': self.collaborator_survey_id.id,
                     'partner_id': values.user_id.partner_id.id if values.user_id.partner_id else False,
                     'appraisal_id': self.ids[0], 'deadline': self.hr_ulm_end_date,
                     'email': values.work_email if values.work_email else False,
                     'emp_code': values.emp_code if values.emp_code else False})
                self.ulm_input_id = response.id
                return response.token

    def UpdateExistingRecordCron(self):
        appr = self.env['hr.appraisal'].search([])
        user_input = self.env['survey.user_input'].sudo()
        user_input_line = self.env['survey.user_input_line'].sudo()
        for appr_records in appr:
            # print(appr_records," Appraisal record")
            vals = {}
            user_inputs = user_input.search([('appraisal_id', '=', appr_records.id)])
            for inputs in user_inputs:
                # print(inputs," UserInputs")
                input_lines_employee = user_input_line.search([('user_input_id', '=', inputs.id), (
                'user_input_id.appraisal_id.emp_id.user_id.partner_id.id', '=', inputs.partner_id.id)])
                # print(input_lines_employee," employee")
                input_lines_manager = user_input_line.search(['&', '&', ('user_input_id', '=', inputs.id), (
                'user_input_id.appraisal_id.emp_id.user_id.partner_id.id', '!=', inputs.partner_id.id),
                                                              ('value_suggested', '!=', False)])
                # print(input_lines_manager," LM")
                input_lines_collaborator = user_input_line.search(['&', '&', '&', ('user_input_id', '=', inputs.id), (
                'user_input_id.appraisal_id.emp_id.user_id.partner_id.id', '!=', inputs.partner_id.id), (
                                                                   'user_input_id.appraisal_id.hr_manager_id.user_id.partner_id.id',
                                                                   '!=', inputs.partner_id.id),
                                                                   ('value_suggested', '=', False)])
                # print(input_lines_collaborator," ULM")

                if len(input_lines_employee):
                    # print('emp_came')
                    vals.update({'self_input_id': inputs.id})
                if len(input_lines_manager):
                    # print('lm_came')
                    vals.update({'lm_input_id': inputs.id})
                if len(input_lines_collaborator):
                    # print('ulm_came')
                    vals.update({'ulm_input_id': inputs.id})
                # print(vals)
                appr_records.write(vals)

    @api.multi
    def view_results(self):
        user_input = self.env['survey.user_input'].sudo().search(
            ['&', '&', ('partner_id', '=', self.emp_id.user_id.partner_id.id), ('appraisal_id', '=', self.id),
             ('survey_id', '=', self.emp_survey_id.id)])
        token = user_input.token
        # print(token)
        return self.emp_survey_id.with_context(survey_token=token, employee_id=self.emp_id.id,
                                               appraisal_year_rel=self.appraisal_year_rel.id).action_kw_survey_result()

    @api.multi
    def view_score(self):
        user_input = self.env['survey.user_input'].sudo().search(
            ['&', '&', ('partner_id', '=', self.emp_id.user_id.partner_id.id), ('appraisal_id', '=', self.id),
             ('survey_id', '=', self.emp_survey_id.id)])
        token = user_input.token
        # print(token)
        return self.emp_survey_id.with_context(survey_token=token, employee_id=self.emp_id.id,
                                               appraisal_year_rel=self.appraisal_year_rel.id).action_kw_survey_score()
    @api.multi
    def get_current_url(self):
        user_input = self.env['survey.user_input'].sudo().search(
            ['&', '&', ('partner_id', '=', self.emp_id.user_id.partner_id.id), ('appraisal_id', '=', self.id),
             ('survey_id', '=', self.emp_survey_id.id)])
        token = user_input.token
        # print(token)
        return self.emp_survey_id.with_context(survey_token=token, employee_id=self.emp_id.id,
                                               appraisal_year_rel=self.appraisal_year_rel.id).get_survey_url()

    @api.multi
    def action_get_answers(self):
        """ This function will return all the answers posted related to this appraisal."""

        tree_res = self.env['ir.model.data'].get_object_reference('survey', 'survey_user_input_tree')
        tree_id = tree_res and tree_res[1] or False
        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_survey_user_input_form_inherits')
        form_id = form_res and form_res[1] or False
        return {
            'model': 'ir.actions.act_window',
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'survey.user_input',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('state', '=', 'done'), ('appraisal_id', '=', self.ids[0])],
        }

    @api.multi
    def _compute_completed_survey(self):
        for record in self:
            # print("Compute field called.............")
            answers = self.env['survey.user_input'].sudo().search(
                [('state', '=', 'done'), ('appraisal_id', '=', record.ids[0])])
            record.tot_comp_survey = len(answers)

    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['kw_ids', 'e_code', 'current_dt', 'app_period_from', 'appraisal_deadline', 'final_interview',
                          'company_id', 'hr_emp', 'hr_manager', 'hr_collaborator', 'hr_colleague', 'manager_survey_id',
                          'emp_survey_id', 'collaborator_survey_id', 'colleague_survey_id', 'response_id',
                          'final_evaluation', 'tot_comp_survey', 'tot_sent_survey', 'created_by', 'color',
                          'kw_appraisal_id', 'hr_lm_start_date', 'hr_lm_end_date', 'hr_ulm_start_date',
                          'hr_ulm_end_date', 'ra_id', 'created_by', 'message_needaction', 'create_date',
                          'message_follower_ids', 'message_channel_ids', 'id', 'message_is_follower',
                          'message_main_attachment_id', 'message_has_error', 'message_ids', 'create_uid',
                          'message_partner_ids', 'write_uid', 'website_message_ids', 'id', 'activity_user_id',
                          'activity_type_id', 'activity_summary', 'activity_date_deadline', 'activity_ids',
                          'appraisal_year_rel']
        res = super(HrAppraisalForm, self).fields_get()
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res

    def UpdateRAManagerRecordCron(self):
        appr = self.env['hr.appraisal'].search([])
        complete_stage = self.env['hr.appraisal.stages'].search([('sequence','=',5)])
        try:
            for appraisal_record in appr:
                if appraisal_record.state.sequence == 4 and appraisal_record.emp_id.parent_id and appraisal_record.emp_id.parent_id.parent_id and not appraisal_record.emp_id.parent_id.parent_id.parent_id:
                    # print(appraisal_record.emp_id.name,"ubiu")
                    appraisal_record.write({'state':complete_stage.id})
        except Exception as e:
            pass
                

class AppraisalStages(models.Model):
    _name = 'hr.appraisal.stages'
    _description = 'Appraisal Stages'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string='Folded in Appraisal Pipeline',
                          help='This stage is folded in the kanban view when '
                               'there are no records in that stage to display.')


# current financial year logic ----------
            # current_date = date.today()
            # year_of_date= current_date.year
            # financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
            # final_date = ''
            # if current_date < financial_year_start_date:
            #     start_date = str(financial_year_start_date.year-1)
            #     end_date = str(financial_year_start_date.year)[-2:]
            #     final_date = start_date+'-'+ end_date
            # else:
            #     start_date = str(financial_year_start_date.year)
            #     end_date = str(financial_year_start_date.year+1)[-2:]
            #     final_date = start_date+'-'+ end_date