from odoo import models, fields, api, tools
from odoo.exceptions import  ValidationError
from datetime import datetime,date, timedelta


class kw_appraisal_competencies(models.Model):
    _name = 'kw_appraisal_empl_competencies'
    _description = 'Performance Navigator Competencies'
    _auto = False
    _rec_name = "emp_id"

    emp_pl_id = fields.Many2one('kw_appraisal_employee', string="Employee Appraisal")
    survey_id = fields.Many2one('survey.survey',string="Assign Survey")
    emp_id = fields.Many2one('hr.employee',string="Employee")
    department_id = fields.Many2one('hr.department',string="Department")
    division =fields.Many2one('hr.department',string="Division")
    job_id =fields.Many2one('hr.job',string="Designation")
    name = fields.Char(string="Name",related="emp_id.name")
    emp_code = fields.Char(string="Code",related="emp_id.emp_code")
    appraisal_period = fields.Char(string='Appraisal Period',compute='get_default_period')

    @api.depends('emp_id')
    def get_default_period(self):
        for rec in self:
            rec.appraisal_period = self.env['kw_assessment_period_master'].sudo().search([],order='id desc',limit=1).assessment_period
    
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT ROW_NUMBER() OVER () as id,
                ael.hr_employee_id as emp_id,
                ss.id as survey_id,
                ae.id as emp_pl_id,
                (select a.department_id from hr_employee a where  a.id = ael.hr_employee_id) as department_id,
                (select a.division from hr_employee a where  a.id = ael.hr_employee_id) as division,
                (select a.job_id from hr_employee a where  a.id = ael.hr_employee_id) as job_id
                FROM survey_survey ss 
                LEFT JOIN kw_appraisal_employee as ae on ae.kw_survey_id = ss.id
                LEFT JOIN kw_appraisal_employee_rel ael on ael.employee = ae.id where  ae.id is not null
                GROUP BY ae.id, ael.hr_employee_id,ss.id 
                )"""
        self.env.cr.execute(query)
        
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is False:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(kw_appraisal_competencies, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(kw_appraisal_competencies, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _get_access_domain(self):
        user = self.env.user
        if self.env.context.get('type'):     
            domain = [('emp_id.user_id', '!=', user.id)] 
            domains = ['|', '|', '|','|',
                    ('emp_id.user_id', '=', user.id),
                    ('emp_id.parent_id.user_id', '=', user.id),
                    ('emp_id.parent_id.parent_id.user_id', '=', user.id),
                    ('emp_id.division.manager_id.user_id', '=', user.id),
                    ('emp_id.department_id.manager_id.user_id', '=', user.id)]
            access_config = self.env['appraisal_cxo_configuration'].sudo().search([('employee_id', '=', user.employee_ids.id)])

            if user.has_group('kw_appraisal.group_appraisal_manager') or (access_config and access_config.name == 'all'): # Manager will see all records
                domains=[]
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

                all_domain = ['|'] + access_config_domain + domains if access_config_domain else domains

                if all_domain:
                    domain = ['&'] + domain + all_domain

        else:
            domain = [('emp_id.user_id', '=', user.id)]

        return domain
    

    def get_emp_competencies_details(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_employee_competencies_tree').id
        appriasal_data = self.env['kw_empl_apprasial_details_competencies'].sudo().search([('emp_pl_id', '=', self.emp_pl_id.kw_survey_id.id), ('emp_id', '=', self.emp_id.id)])
        return {
            'name': f'Competencies Details of {self.name}',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'res_model': 'kw_empl_apprasial_details_competencies',
            'target': 'new',
            'domain': [('id','in',appriasal_data.ids),],
        }

class KwEmpAppraisalDetailsCompetencies(models.Model):
    _name = "kw_empl_apprasial_details_competencies"
    _description = "Employee Appraisal Competencies Details"
    _auto = False
    
    
    emp_pl_id = fields.Many2one('survey.survey', string="Employee Appraisal")
    emp_id = fields.Many2one('hr.employee',string="Employee")
   
    survey_indicate = fields.Text(string="Indicator")
    survey_qus = fields.Char(string="Question")
    question_max_value = fields.Float(string="Question Max Value")
    question_min_value = fields.Float(string="Question Min Value")
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT ROW_NUMBER() OVER () as id,
                ke.kw_survey_id as emp_pl_id,
                ael.hr_employee_id as emp_id,
                sq.indicator as survey_indicate,
                sq.question as survey_qus,
                sq.validation_max_float_value as question_max_value,
                sq.validation_min_float_value as question_min_value 
                from survey_question sq join survey_page sp on sp.id=sq.page_id 
                JOIN survey_survey ss on ss.id=sp.survey_id JOIN kw_appraisal_employee ke on ke.kw_survey_id=ss.id 
                JOIN kw_appraisal_employee_rel ael on ael.employee = ke.id where sq.type='simple_choice'
                )"""
        self.env.cr.execute(query)
        


class AppraisalMycompetencies(models.Model):
    _name="kw_appraisal_my_competensies"
    _description = "MY Competensies"
    _rec_name="emp_id"
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    company_id = fields.Many2one('res.company',string="Company",related="emp_id.company_id",store=True)
    kw_survey_id = fields.Many2one('survey.survey', string="Appraisal Form", required=True,domain=[('survey_type.code', '=', 'appr')])
    compt_create_bool = fields.Boolean(string="create bool",default=False)
    compt_accepted = fields.Boolean(string="Agree Competen",default=False)
    compt_disagree = fields.Boolean(string="Disagree Competen",default=False)
    compt_agree_or_disagree = fields.Boolean(string="Check Competen",default=False)
    status = fields.Char(string="Status")
    assign_template_compet_not_appraisal = fields.Boolean(string="Not Appraisal",default=False)
    
    
    def action_competen_create_check_server_action(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_create_competencies_tree').id
        assign_tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_assign_competencies_tree').id
        appraisal_data = self.env['hr.appraisal'].sudo().search([('emp_id','=',self.env.user.employee_ids.id)],order='id desc',limit=1)
        user = self.env.user.employee_ids.id
        action = {}
        compt = self.env['kw_appraisal_my_competensies'].search([('emp_id','=',user)])
        compt_data =  self.env['kw_appraisal_employee'].sudo().search([('employee_id','in',appraisal_data.emp_id.id)])
        if appraisal_data:
            if not self.search([('emp_id','=',user)]):
                self.sudo().create({'emp_id':appraisal_data.emp_id.id,'kw_survey_id':compt_data.kw_survey_id.id})
            else :
                compt=compt.search([('emp_id','=',user)])
                compt.sudo().search([('emp_id','=',user),('kw_survey_id','!=',compt_data.kw_survey_id.id)]).write({'kw_survey_id':compt_data.kw_survey_id.id})
                
            action = {
                    'type': 'ir.actions.act_window',
                    'name': 'MY Competencies',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_id' : self.id,
                    'res_model': 'kw_appraisal_my_competensies',
                    'target': 'main',
                    # 'context':{'type':'view'},
                    'domain':[('emp_id','=',self.env.user.employee_ids.id)]
                }
            return action
        elif self.compt_agree_or_disagree == False:
            compt_data =  self.env['kw_appraisal_employee'].sudo().search([('employee_id','in',user)])
            if not compt:
                if compt_data:
                    self.sudo().create({'emp_id':user,'kw_survey_id':compt_data.kw_survey_id.id,'compt_create_bool':True,'assign_template_compet_not_appraisal':True})
            elif compt_data.change_compt == True:
                    compt.search([('kw_survey_id','=',compt_data.kw_survey_id.id),('compt_agree_or_disagree','=',True)]).write({'compt_create_bool':True,'compt_agree_or_disagree':False,'status':''})
                    compt_data.change_compt = False
            elif compt :
                if compt_data.kw_survey_id.id == compt.kw_survey_id.id and compt.compt_agree_or_disagree == False:
                    pass
                elif compt_data.kw_survey_id.id != compt.kw_survey_id.id and compt.compt_agree_or_disagree == True and compt.status == 'Disagree':
                    compt.write({'emp_id':user,'kw_survey_id':compt_data.kw_survey_id.id,'compt_create_bool':True,'status': '','compt_agree_or_disagree':False,'assign_template_kra_not_appraisal':True})
            action = {
                    'type': 'ir.actions.act_window',
                    'name': 'MY Competencies',
                    'views': [(assign_tree_view_id, 'tree')],
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_id' : self.id,
                    'res_model': 'kw_appraisal_my_competensies',
                    'target': 'main',
                    'domain': [('emp_id','=',self.env.user.employee_ids.id)]
                }
            return action
        
    def get_view_my_competencies_appraisal(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_employee_competencies_tree').id
        appriasal_data = self.env['kw_empl_apprasial_details_competencies'].sudo().search([('emp_pl_id', '=', self.kw_survey_id.id), ('emp_id', '=', self.emp_id.id)])
        if appriasal_data:
            return {
                'name': 'Competencies',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'views': [(tree_view_id, 'tree')],
                'res_model': 'kw_empl_apprasial_details_competencies',
                'target': 'new',
                'domain': [('id','in',appriasal_data.ids),],
            }
        else:
            raise ValidationError("You can't view as you have already disagree.")
        
    def get_emp_agree_compten_appraisal(self):
        template = self.env.ref('kw_performance_navigator.competencies_agree_email_template')
        if self.kw_survey_id and self.emp_id:
            if self.env.user.employee_ids.id != self.emp_id.id:
                raise ValidationError("Concerned employee need to Agree his/her Competencies")
            else:
                self.write({'compt_agree_or_disagree':True,'status':'Agree',
                            })
                if template:
                    manager_user = self.env.ref('kw_appraisal.group_appraisal_manager').users
                    email_cc = ','.join(manager_user.mapped("email")) if manager_user else ''
                    emp_name = self.emp_id.name
                    emp = self.emp_id
                    template.with_context(cc=email_cc,employee=emp,
                                       emp_name=emp_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
               
    def get_emp_compten_disagree_appraisal(self):
        template = self.env.ref('kw_performance_navigator.competencies_disagree_email_template')
        if self.kw_survey_id and self.emp_id:
            if self.env.user.employee_ids.id != self.emp_id.id:
                raise ValidationError("Concerned employee need to Disagree his/her Competencies")
            else:
                self.write({'compt_agree_or_disagree':True,'status':'Disagree',
                            })
                if template:
                    manager_user = self.env.ref('kw_appraisal.group_appraisal_manager').users
                    email_to = ','.join(manager_user.mapped("email")) if manager_user else ''
                    emp_name = self.emp_id.name
                    template.with_context(email_to=email_to,
                                       emp_name=emp_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
    
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is False:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(AppraisalMycompetencies, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(AppraisalMycompetencies, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _get_access_domain(self):
        user = self.env.user
        if self.env.context.get('type'):     
            domain = [('emp_id.user_id', '!=', user.id)] 
            domains = ['|', '|', '|',
                    ('emp_id.user_id', '=', user.id),
                    ('emp_id.parent_id.user_id', '=', user.id),
                    ('emp_id.division.manager_id.user_id', '=', user.id),
                    ('emp_id.department_id.manager_id.user_id', '=', user.id)]
            access_config = self.env['appraisal_cxo_configuration'].sudo().search([('employee_id', '=', user.employee_ids.id)])

            if user.has_group('kw_appraisal.group_appraisal_manager') or (access_config and access_config.name == 'all'): # Manager will see all records
                domains=[]
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

                all_domain = ['|'] + access_config_domain + domains if access_config_domain else domains

                if all_domain:
                    domain = ['&'] + domain + all_domain

        else:
            domain = [('emp_id.user_id', '=', user.id)]

        return domain
    
    
        