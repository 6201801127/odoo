from datetime import date
from odoo import models, fields, api,tools
from odoo.exceptions import UserError, ValidationError
import requests, json
import base64


class kw_question_set_config_induction(models.Model):
    _inherit = 'kw_skill_question_set_config'
    
    
    induction_code = fields.Char(string="Code")
class Employeedata(models.Model):
    _name = "employee_data_model"
    _description = "POSH Induction"
    _auto = False
    
   
    emp_code = fields.Char(string="Employee Code")
    name = fields.Char(string="Name")
    department_id = fields.Many2one('hr.department',string="Department")
    division = fields.Char(string="Division")
    section = fields.Char(string="Section")
    practise = fields.Char(string="practise")
    job_id = fields.Many2one('hr.job', string="Designation")
    date_of_joining = fields.Date(string="Date of Joining")
    status = fields.Selection(string="Status",selection=[('Not Configured','Not Configured'),('Configured','Configured'),('Complete','Complete')],
                              default='Not Configured',compute="get_update_status")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'employee_data_model')
        self._cr.execute("""
            CREATE OR REPLACE VIEW employee_data_model AS (
                SELECT
                    emp.id as id,
                    emp.emp_code as emp_code,
                    emp.name as name,
                    emp.department_id as department_id,
                    (select name from hr_department where id = emp.division) as division ,
                   (select name from hr_department where id = emp.section) as section,
                    (select name from hr_department where id = emp.practise) as practise ,
                    emp.job_id as job_id,
                    null as status,
                    emp.date_of_joining as date_of_joining
                FROM hr_employee emp
                WHERE emp.active = True AND emp.employement_type != (select id from kwemp_employment_type where code='O')
            )
        """)
        
    @api.multi
    def get_update_status(self):
        induction_details =  self.env['kw_employee_posh_induction_details'].sudo()
        for rec in self:
            rec.status = 'Not Configured'
            if induction_details.search([('emp_id','=',rec.id),('posh_induction_check','=',True),('induction_complete','=',False)]):
                rec.status = 'Configured'
            elif induction_details.search([('emp_id','=',rec.id),('posh_induction_check','=',True),('induction_complete','=',True)]):
                rec.status = 'Complete'
       
 
class EmployeePoshDataWizard(models.TransientModel):
    _name = 'employee_posh_data_wizard'
    _description = "Employee Posh Data Wizard"

    employee_ids = fields.Many2many('employee_data_model', string="Employees")
    induction_id = fields.Many2one('kw_skill_master', required=True,string="Induction", domain=[('skill_type', '=', 'Induction')])
    date_of_induction = fields.Date(string="Start Date",required=True)

    @api.model
    def default_get(self, fields):
        res = super(EmployeePoshDataWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'employee_ids': active_ids,
        })
        return res
    
    def update_employee_posh_data(self):
        self.emp_send_mail = True
        induction_emp = self.env['kw_employee_posh_induction_details'].sudo().search([('emp_id','in',self.employee_ids.ids),('posh_induction_check','=',True)])
        if induction_emp.exists():
            raise ValidationError("Induction is already configured")
        else:
            employee_id = []
            department_id = []
            if self.employee_ids:

                for recc in self.employee_ids:
                    # employee_rec = self.env['hr.employee'].sudo().search([('onboarding_id','=',recc.onboard_id.id)])
                    # if not employee_rec.exists():
                    #     raise ValidationError("Please create the Employee first then, You can configured the Induction Assessment")
                    # else:
                    employee_rec = self.env['hr.employee'].sudo().browse(recc.id)
                    user = employee_rec.user_id

                    employee_id.append(recc.id)
                    department_id.append(recc.department_id.id)
                    user_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
                    skill_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')
                    # user = self.env['res.users'].sudo().search([('partner_id', '=', recc.user_id.partner_id.id)])
                    if user:
                        groups_to_add = []
                        if user_group.id not in user.groups_id.ids:
                            groups_to_add.append((4, user_group.id))
                        if skill_user_group.id not in user.groups_id.ids:
                            groups_to_add.append((4, skill_user_group.id))

                        if groups_to_add:
                            user.write({
                                'groups_id': groups_to_add
                            })  
                for rec in self.induction_id:
                    qus_set_config_record = self.env['kw_skill_question_set_config'].sudo().create({
                        'name': rec.name,
                        'dept': [(4, id, False) for id in department_id],
                        'skill_types': rec.skill_type.id,
                        'skill': rec.id,
                        'induction_code' : 'POSH',
                        'applicable_candidate': '3',
                        'frequency': "o",
                        'select_individual': [(4, id, False) for id in employee_id],
                        'assessment_type': 'Induction',
                        'duration': rec.assessment_duration,
                        'add_questions':[  (0, 0, {
                            'question_type': 1,
                            'no_of_question': rec.no_of_qus})],
                        'state': '2',
                        'active': True
                    })
                    recc = self.env['hr.employee'].sudo().search([('id','=',recc.id)])
                    if recc:
                        self.env['kw_employee_posh_induction_details'].sudo().create({'emp_id':recc.id,
                                        'induction_id':rec.id,
                                        'start_date_of':self.date_of_induction,
                                        'assessment_id': qus_set_config_record.id,
                                        'posh_induction_check':True,'posh_assign_user':self.env.user.employee_ids.id})
            if self.emp_send_mail == True:
                if self.employee_ids:
                    for rec in self.employee_ids:
                        employee_rec = self.env['hr.employee'].sudo().search([('id','=',rec.id)])
                        action_id = self.env.ref('kw_onboarding_induction_feedback.action_posh_induction_user_readonly_act_window').id
                        if employee_rec:
                            employee_name = employee_rec.name
                            email_from=self.env.user.employee_ids.work_email
                            email_to = employee_rec.work_email
                            extra_params= {'email_to':email_to,'cc_mail':email_from,
                            'email_from':email_from,'record_id': rec.id,
                            'emp_name':employee_name,'action_id':action_id,
                            }
                            self.env['hr.contract'].contact_send_custom_mail(res_id=rec.id,
                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                            template_layout='kw_onboarding_induction_feedback.kw_induction_posh_email_template',
                                                                            ctx_params=extra_params,
                                                                            description="Induction Assessment")
                self.env.user.notify_success("Mail Sent successfully.")
               
