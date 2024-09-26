from datetime import date
from odoo import models, fields, api,tools
from odoo.exceptions import UserError, ValidationError




class OnboardingInductionAssessment(models.Model):
    _name = "kw_employee_induction_assessment"
    _description = "Onboarding Induction Assessment"
    _rec_name = 'emp_id'
    
    @api.model
    def _get_no_rating(self):
        return [(str(x), str(x)) for x in range(1, 6)]
    
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    onboarding_applicant_id = fields.Many2one('kwonboard_enrollment',related="emp_id.onboarding_id",store=True)
    induction_id = fields.Many2many('kw_skill_master','skill_induction_rel','skill_ind_id','onboard_ind_id',string="Induction")
    induction_id_name = fields.Char(string="Induction Name", compute="get_induction_value_name")
    start_date_of = fields.Date(string="Start Date")
    end_date_of = fields.Date(string="End Date")
    test_type = fields.Selection(string="Test Type", selection=[('pre', 'Pre Test'),('post', 'Post Test')],default="post",required=True)
    assessment_type = fields.Selection(string="Assessment Type",
                    selection=[('offline', 'Offline'),('online', 'Online')],
                    default="online",required=True)
    marks = fields.Integer(string="Full Marks")
    assessment_id = fields.Many2one(string='Assessment',comodel_name='kw_skill_question_set_config')
    # score_id = fields.Many2one('kw_induction_score',string="Score")
    question_bank_id = fields.Many2one('kw_skill_question_bank_master',string="Question Bank")
    user_has_given_assessment = fields.Boolean(string='Assessment Given?', default=False, 
                                                compute="_compute_if_user_given_induction")
    assessment_expired = fields.Boolean(string='Assessment Expired?', default=False,
                                        compute="_compute_assessment_status")
    assessment_started = fields.Boolean(string='Assessment Started?', default=False,
                                        compute="_compute_assessment_status")
    test_available = fields.Boolean(string="Test Available ?",compute="compute_if_induction_available",default=False)
    user_is_participant = fields.Boolean(string="User applicant",compute="_compute_if_applicant",default=False)
    manager_view_score = fields.Boolean(string="Manger score",compute="_compute_if_user_given_induction",default=False)
    hide_reschedule = fields.Boolean(string="Hide schedule", compute="_get_reschedule_assessment")
    after_reschedule = fields.Boolean(string="After reschedule")
    percentage_scored = fields.Float(string="Percentage Scored",compute="_test_time_taken_induction")
    total_mark = fields.Integer(string="Total Mark",compute="_test_time_taken_induction")
    total_mark_obtained = fields.Integer(string="Total Marks Obtained",compute="_test_time_taken_induction",)  
    duration = fields.Char(compute="_get_duration", string="Test Duration")
    time_taken_duration = fields.Char(compute="_test_time_taken_induction", string="Test Time Taken") 
    create_date_ans = fields.Datetime(string="Appeared date") 
    induction_emp_check = fields.Boolean(string="Given assesment check?")
    skips_check = fields.Integer(string="skips", default=0)
    induction_rate = fields.Text(string=" How would you rate the induction overall?")
    induction_rate_no = fields.Selection('_get_no_rating',string="Induction rating")
    valuable_info = fields.Text(string=" Did it provide you with valuable information to help you do your job?")
    valuable_info_no = fields.Selection('_get_no_rating',string="valuable_info rating")
    understand_organisation = fields.Text(string="Did it help you understand more about the organisation?")
    understand_organisation_no = fields.Selection('_get_no_rating',string="understand_organisation rating")
    skill_of_inductor = fields.Text(string="How was the presentation skill of the Inductor?")
    skill_of_inductor_no = fields.Selection('_get_no_rating',string="skill_of_inductor rating")
    handel_queries = fields.Text(string="Did the Inductor handle your queries properly")
    handel_queries_no = fields.Selection('_get_no_rating',string="handel_queries rating")
    induction_coordinated = fields.Text(string="How would you rate the Indution coordinated for you?")
    induction_coordinated_no = fields.Selection('_get_no_rating',string="induction_coordinated rating")
    
    feedback_hide_btn = fields.Boolean(string="feedback",default=False)


    
    
    @api.depends('induction_id')
    def get_induction_value_name(self):
        for rec in self:
            if rec.induction_id:
                rec.induction_id_name = rec.induction_id.name
                    
    
    @api.multi
    def _get_duration(self):
        for record in self:
            duration = self.env['kw_skill_question_set_config'].sudo().search([('id', '=', record.assessment_id.id)])
            record.duration = f"{round(int(duration.duration) / 3600, 2)} hour(s)"
            
    @api.multi
    def _test_time_taken_induction(self):
        answer_count = []
        for rec in self:
            ans_master_record = self.env['kw_skill_answer_master'].sudo().search([('user_id','=',rec.emp_id.user_id.id),('skill_id','=',rec.assessment_id.skill.id),('set_config_id','=',rec.assessment_id.id)])
            for record in ans_master_record:
                answer_count.append('True')
                rec.time_taken_duration = record.time_taken_duration
                rec.create_date_ans = record.create_date
                rec.percentage_scored = record.percentage_scored
                rec.total_mark = record.total_mark
                rec.total_mark_obtained = record.total_mark_obtained
            # from collections import Counter
            # emp_record = self.env['kw_employee_induction_assessment'].search([])
            # induction_count = Counter(record.emp_id.id for record in emp_record)
            # for emp_id, count in induction_count.items():
            #     print(f"Employee ID: {emp_id} - Induction ID count: {count}")
            #     print("answer_count=============",answer_count)
            #     if len(answer_count) == count:
            #         rec.induction_emp_check = True
            #         print("in if length================================",rec.induction_emp_check)

        
        
    @api.multi
    def _compute_if_user_given_induction(self):
        for assessment in self:
            if assessment.assessment_type == 'online' and assessment.assessment_id:
                # check if user has given assessment
                assessmnet_given = self.env['kw_skill_answer_master'].sudo().search(
                    [('user_id', '=', self._uid), ('set_config_id', '=', assessment.assessment_id.id)])
                # print("assessmnet_given---------------------------------------",assessmnet_given)
                if assessmnet_given:
                    assessment.user_has_given_assessment = True
           
            manger_show_result = self.env['kw_skill_answer_master'].sudo().search(
                    [('set_config_id', '=', assessment.assessment_id.id)])
            if manger_show_result:
                assessment.manager_view_score = True
    @api.multi
    def compute_if_induction_available(self):
        for induction in self: 
            any_test_available = induction.filtered(
                lambda r: r.assessment_id != False and r.user_has_given_assessment == False and r.start_date_of <= date.today())
            if any_test_available:
                induction.test_available = True
            # else:
            #     user_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
            #     skill_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')
                
            #     user = self.env['res.users'].sudo().search([('partner_id', '=', induction.emp_id.user_id.partner_id.id)])
            #     if user:
            #         user.write({
            #             'groups_id': [(3, user_group.id), (3, skill_user_group.id)]}) 
    @api.multi
    def _compute_assessment_status(self):
        for assessment in self:
            if assessment.start_date_of and assessment.start_date_of <= date.today():
                assessment.assessment_started = True
                
    @api.multi
    def _get_reschedule_assessment(self):
        for rec in self:
            ans_master_record = self.env['kw_skill_answer_master'].sudo().search([('user_id','=',rec.emp_id.user_id.id),('skill_id','=',rec.assessment_id.skill.id),('set_config_id','=',rec.assessment_id.id)])
            for record in ans_master_record:
                if record.percentage_scored < 60.00:
                    rec.hide_reschedule = True
            
    @api.multi
    def _compute_if_applicant(self):
        current_employee_id = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)
        employee_id = current_employee_id.id if current_employee_id else False
        for assessment in self:
            if employee_id and assessment.emp_id.id :
                employee_participant = assessment.filtered(
                    lambda r: r.emp_id.id == employee_id)
                if employee_participant:
                        assessment.user_is_participant = True
                
   
    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r : r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments
   
    @api.multi
    def action_assessment_test(self):
        if self.assessment_id:
            return self.assessment_id.take_test(extra_params=self.test_type.capitalize()+' Test')
    @api.multi
    def action_feedback_test(self):
        form_view = self.env.ref('kw_onboarding_induction_feedback.induction_feedback_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Feedback',
            'res_model': 'induction_assessment_feedback_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view,
            'target': 'new',
        }
        
        
    @api.multi
    def view_reschdule_induction(self):
        form_view_id = self.env.ref("kw_onboarding_induction_feedback.induction_reschedule_wizard_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reschedule',
            'res_model': 'induction_assessment_wizard_resch',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }
        
    @api.model
    def _get_employee_induction_assessment_page(self, user_id):
        skips_check= 0
        emp_induction_log = self.env['kw_employee_induction_assessment'].sudo().search([('emp_id', '=', user_id.employee_ids.id)])
        for record in emp_induction_log: 
            if record.exists():
                result_url = f"/get-induction_assessment-of-employee"
                return result_url
            
class kw_induction_assessment_type(models.Model):
    _inherit = 'kw_skill_master'
    
    skill_type = fields.Many2one('kw_skill_type_master', string="Skill Category", required=True)
    no_of_qus = fields.Integer(string="No of Question",required=True)
    assessment_duration = fields.Selection(string="Duration", required=True,
                                selection=[('900', '15 mins'), ('1800', '30 mins'), ('2700', '45 mins'),
                                           ('3600', '1 hour'),
                                           ('5400', '1 hour 30 mins'), ('7200', '2 hours'),
                                           ('10800', '3 hours')])
    pass_percentage = fields.Float(string="Passing percentage",required=True)
    
    
    @api.model
    def default_get(self, fields):
        res = super(kw_induction_assessment_type, self).default_get(fields)
        type_id = self.env.context.get('default_skill_type')
        res['skill_type'] = self.env['kw_skill_type_master'].sudo().search([('skill_type', '=', type_id)]).id
        return res
class OnboardingInductionAssessmentConfiguration(models.Model):
    _name = "kw_employee_assessment_configuration"
    _description = "Onboarding Induction Assessment Configuration"
    _auto = False
    
   
    onboard_id = fields.Many2one('kwonboard_enrollment',string="Onboard Id")
    # code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='onboard_id.name', string='Applicant Name')
    department_id = fields.Many2one('hr.department', string='Department')
    division = fields.Many2one('hr.department', string="Division",related='onboard_id.division')
    section = fields.Many2one('hr.department', related='onboard_id.practise')
    practise = fields.Many2one('hr.department', related='onboard_id.section')
    job_id = fields.Many2one('hr.job', string="Designation",related='onboard_id.job_id')
    date_of_joining = fields.Date(string="Date of joining")
    induction_config_status = fields.Char(string="Status",default="Not configured",compute = "get_status_of_induction")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
          SELECT row_number() OVER() AS id,
            hr.id as onboard_id,
            hr.dept_name AS department_id,
            hr.tmp_join_date AS date_of_joining,
           	'Not Configured' AS induction_config_status
            FROM kwonboard_enrollment AS hr
			left join kw_induction_plan_data ind on hr.id = ind.applicant_induction_id
            WHERE EXTRACT(MONTH FROM hr.tmp_join_date) IN (2,3, 4, 5, 6, 7, 8,9)  AND EXTRACT(YEAR FROM hr.tmp_join_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            OR ind.status_of_induction = 'Completed' AND hr.state in ('4','5')
        )""" % (self._table))
        
        
    def get_status_of_induction(self):
        for record in self:
            induction_status = 'Not Configured'
            record_induction_data = self.env['kw_employee_induction_assessment'].search([('onboarding_applicant_id','=',record.onboard_id.id)])
            if record_induction_data:
                induction_status = 'Configured'
            record.induction_config_status = induction_status
       
       