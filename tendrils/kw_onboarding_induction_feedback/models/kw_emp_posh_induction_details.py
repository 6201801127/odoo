from datetime import date
from odoo import models, fields, api,tools
from odoo.exceptions import UserError, ValidationError




class PoshInductionAssessment(models.Model):
    _name = "kw_employee_posh_induction_details"
    _description = "POSH Induction"
    _rec_name = 'emp_id'
    
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    induction_id = fields.Many2one('kw_skill_master',string="Induction")
    induction_id_name = fields.Char(string="Induction Name", compute="get_induction_value_name")
    start_date_of = fields.Date(string="Start Date")
    end_date_of = fields.Date(string="End Date")
    test_type = fields.Selection(string="Test Type", selection=[('pre', 'Pre Test'),('post', 'Post Test')],default="post",required=True)
    assessment_type = fields.Selection(string="Assessment Type",
                    selection=[('offline', 'Offline'),('online', 'Online')],
                    default="online")
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
    posh_assign_user = fields.Many2one('hr.employee',string="Assigned by")
    
    time_taken_duration = fields.Char(compute="_test_time_taken_induction", string="Test Time Taken") 
    create_date_ans = fields.Datetime(string="Appeared date") 
    posh_induction_check = fields.Boolean(string="Induction check",default=False)
    induction_complete = fields.Boolean(string="Induction complete check",default=False)
    complete_date = fields.Date(string="induction complete date")
    status_induction = fields.Selection(string="Status",selection=[('Configured','Configured'),('Complete','Complete')],default="Configured")
    
    
    @api.depends('induction_id')
    def get_induction_value_name(self):
        for rec in self:
            if rec.induction_id:
                rec.induction_id_name = rec.induction_id.name
                
    @api.multi
    def _compute_if_user_given_induction(self):
        for assessment in self:
            if assessment.assessment_type == 'online' and assessment.assessment_id:
                # check if user has given assessment
                assessmnet_given = self.env['kw_skill_answer_master'].sudo().search(
                    [('user_id', '=', self._uid), ('set_config_id', '=', assessment.assessment_id.id)])
                if assessmnet_given:
                    assessment.user_has_given_assessment = True
           
            manger_show_result = self.env['kw_skill_answer_master'].sudo().search(
                    [('set_config_id', '=', assessment.assessment_id.id)])
            if manger_show_result:
                assessment.manager_view_score = True
                
    @api.multi
    def _compute_assessment_status(self):
        for assessment in self:
            if assessment.start_date_of and assessment.start_date_of <= date.today():
                assessment.assessment_started = True
                
    @api.multi
    def compute_if_induction_available(self):
        for induction in self: 
            any_test_available = induction.filtered(
                lambda r: r.assessment_id != False and r.user_has_given_assessment == False and r.start_date_of <= date.today())
            if any_test_available:
                induction.test_available = True
    
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
                
    @api.multi
    def _get_duration(self):
        for record in self:
            duration = self.env['kw_skill_question_set_config'].sudo().search([('id', '=', record.assessment_id.id)])
            record.duration = f"{round(int(duration.duration) / 3600, 2)} hour(s)"
            
            
            
    @api.multi
    def action_posh_assessment_test(self):
        if self.assessment_id:
            return self.assessment_id.take_test(extra_params=self.test_type.capitalize()+' Test')