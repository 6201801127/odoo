# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug

class TrainingFeedback(models.Model):
    _name = "kw_training_feedback"
    _description = "Kwantify Training Feedback"
    _rec_name = "training_id"

    @api.model
    def _get_default_survey(self):
        training_survey_id = self.env.ref('kw_training.kw_training_survey_feedback_form')
        if training_survey_id:
            return training_survey_id.id
        else:
            return False

    financial_year = fields.Many2one('account.fiscalyear',string="Financial Year",required=True)
    training_id = fields.Many2one(string='Training', comodel_name='kw_training', required=True,)
    instructor_id = fields.Many2one('hr.employee',string="Instructor",domain=['|',('active','=',True),('active','=',False)])
    emp_id = fields.Many2one("hr.employee",string="Employee",domain=['|',('active','=',True),('active','=',False)])
    ext_instructor = fields.Many2one("res.partner",string="Instructor",)
    instructor_name = fields.Char(string="Instructor",compute="_compute_name")
    survey_id = fields.Many2one(string='Survey ID',comodel_name='survey.survey',ondelete='set null',
                                default=lambda self: self._get_default_survey())
    response_id = fields.Many2one(string='Response ID',comodel_name='survey.user_input',ondelete='restrict',)
    feedback_status     = fields.Selection(string='Status',selection=[('1', 'Draft'), ('2', 'Completed')],default='1')
    
    @api.multi
    def _compute_name(self):
        for r in self:
            r.instructor_name = r.instructor_id.name if r.instructor_id else 'External'
            
    @api.onchange('instructor_id')
    def _get_feedback_form(self):
        if self.instructor_id:
            self.feedback_detail_ids=False
            self.ext_instructor=False
            categories = self.env['kw_feedback_category'].search([])
            if categories:
                self.feedback_detail_ids = [(0, 0, {'category_id':c.id,'marks':'','remark':'',
                                                    'description':c.description if c.description else '' }) for c in categories]

    @api.onchange("training_id")
    def _set_instructor_domain(self):
        if self.training_id:
            self.instructor_id=False
            self.ext_instructor=False
            self.feedback_detail_ids = False
            if self.training_id.plan_ids and self.training_id.plan_ids[0].instructor_type=="internal":
                self.instructor_internal=True
                return {'domain': 
                    {'instructor_id': [('id', 'in', [r.id for r in self.training_id.plan_ids[0].internal_user_ids])], }}
            else:
                self.instructor_internal=False
                categories = self.env['kw_feedback_category'].search([])
                if categories:
                    self.feedback_detail_ids = [(0, 0, {'category_id': c.id, 'marks': '', 'remark': '',
                                                    'description': c.description if c.description else ''}) for c in categories]
    @api.multi
    def _compute_instructor(self):
        for r in self:
            if r.training_id and r.training_id.plan_ids and r.training_id.plan_ids[0].instructor_type == "internal":
                r.instructor_internal = True
            else:
                r.instructor_internal=False

    @api.onchange("financial_year")
    def _set_training_domain(self):
        if self.financial_year:
            self.training_id=False
            self.instructor_id=False
            self.ext_instructor=False
            if self.env.user.has_group('kw_training.group_kw_training_manager'):
                return {'domain':
                        {'training_id': [('financial_year.id', '=', self.financial_year.id), ['schedule_ids', '!=', False]], }}
            else:
                emp= self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
                attendances = self.env['kw_training_attendance_details'].search(['&',('participant_id','=',emp.id),('status','=','present')])
                tr_id = []
                for r in attendances:
                    if r.training_id.id not in tr_id:
                        tr_id.append(r.training_id.id)
                return {'domain':
                        {'training_id': [('id', 'in', tr_id), ('financial_year.id', '=', self.financial_year.id), ['schedule_ids', '!=', False]], }}
  

    @api.multi
    def view_emp_feedback(self):
        if not self.response_id:
            raise ValidationError("No feedback given.")
        
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f"/training-feedback-view/{slug(self)}"
        }

    @api.model
    def check_feedback_given(self,args):
        Feedback = self.env['kw_training_feedback']
        training_id = int(args.get('training_id'))
        instructor_type = args.get('instructor_type')
        emp_id = int(args.get('emp_id'))
        instructor_id = int(args.get('instructor_id'))
        if instructor_type == "internal":
            given_status = Feedback.sudo().search(['&', '&', ('training_id', '=', training_id),
                                                   ('emp_id', '=', emp_id), ('instructor_id', '=', instructor_id)])
        else:
            given_status = Feedback.search(['&', '&', ('training_id', '=', training_id),
                                            ('emp_id', '=', emp_id), ('ext_instructor', '=', instructor_id)])
        if len(given_status) > 0:
            return False
        else:
            return True


