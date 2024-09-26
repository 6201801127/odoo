from odoo import models, fields, api, tools
from datetime import date, datetime, time
from odoo.exceptions import  ValidationError


class KwEmpAppraisalKRA(models.Model):
    _name = "kw_empl_apprasial_kra"
    _description = "Employee Appraisal KRA"
    _auto = False
    _rec_name = "emp_id"
    
    
    
    # question_name = fields.Char(string="Goal")
    # kra_score = fields.Float(string="KRA Score")
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
        
      # Search methods to see records as per cxo configuration and other domain
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is False:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(KwEmpAppraisalKRA, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(KwEmpAppraisalKRA, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

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

            if user.has_group('kw_performance_navigator.group_performance_navigator_manager') or (access_config and access_config.name == 'all'): # Manager will see all records
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
    
        
        
    def get_emp_kra_details(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_employee_kra_tree').id
        appriasal_data = self.env['kw_empl_apprasial_details_kra'].sudo().search([('emp_pl_id', '=', self.emp_pl_id.kw_survey_id.id), ('emp_id', '=', self.emp_id.id)])
       
        return {
            'name': f'KRA Details of {self.name}',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'res_model': 'kw_empl_apprasial_details_kra',
            'target': 'new',
            'domain': [('id','in',appriasal_data.ids),],
        }
        
        

        
        
class KwEmpAppraisalDetailsKRA(models.Model):
    _name = "kw_empl_apprasial_details_kra"
    _description = "Employee Appraisal Details KRA"
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
                JOIN kw_appraisal_employee_rel ael on ael.employee = ke.id where sq.type='numerical_box'
                )"""
        self.env.cr.execute(query)
        
        
        
        
class AppraisalMyKRA(models.Model):
    _name="kw_appraisal_kra_emp"
    _description = "Employee KRA"
    _rec_name="emp_id"
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    emp_code = fields.Char(related='emp_id.emp_code',string="Code")
    name = fields.Char(related='emp_id.name',string="Name")
    company_id = fields.Many2one('res.company',string="Company",related="emp_id.company_id",store=True)
    kw_survey_id = fields.Many2one('survey.survey', string="Appraisal Form", required=True,domain=[('survey_type.code', '=', 'appr')])
    kra_create_bool = fields.Boolean(string="create bool",default=False)
    kra_accepted = fields.Boolean(string="Agree kra",default=False)
    kra_disagree = fields.Boolean(string="Disagree kra",default=False)
    kra_agree_or_disagree = fields.Boolean(string="Check kra",default=False)
    status = fields.Char(string="Status")
    action_log_ids = fields.One2many('kw_appraisal_kra_emp_log','kra_log_emp',string="Action log")
    assign_template_kra_not_appraisal = fields.Boolean(string="Not Appraisal",default=False)
    appraisal_period = fields.Char(string='Appraisal Period',compute='get_default_period')
    first_send_mail = fields.Boolean(default=False)
    
    @api.depends('emp_id')
    def get_default_period(self):
        for rec in self:
            rec.appraisal_period = self.env['kw_assessment_period_master'].sudo().search([],order='id desc',limit=1).assessment_period
    
    
    def action_kra_create_check_server_action(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_create_kra_tree').id
        assign_tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_assign_kra_tree').id
        # form_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_create_kra_form').id
        appraisal_data = self.env['hr.appraisal'].sudo().search([('emp_id','=',self.env.user.employee_ids.id)],order='id desc',limit=1)
        user = self.env.user.employee_ids.id
        action = {}
        kra = self.env['kw_appraisal_kra_emp'].search([('emp_id','=',user)])
        kra_data =  self.env['kw_appraisal_employee'].sudo().search([('employee_id','in',appraisal_data.emp_id.id)])
        if appraisal_data:
            if not self.search([('emp_id','=',user)]):
                self.sudo().create({'emp_id':appraisal_data.emp_id.id,'kw_survey_id':kra_data.kw_survey_id.id})
            else :
                kra=kra.search([('emp_id','=',user)])
                kra.sudo().search([('emp_id','=',user),('kw_survey_id','!=',kra_data.kw_survey_id.id)]).write({'kw_survey_id':kra_data.kw_survey_id.id})
                
            action = {
                    'type': 'ir.actions.act_window',
                    'name': 'MY KRA',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_id' : self.id,
                    'res_model': 'kw_appraisal_kra_emp',
                    'target': 'main',
                    # 'context':{'type':'view'},
                    'domain':[('emp_id','=',self.env.user.employee_ids.id)]
                }
            return action
        elif self.kra_agree_or_disagree == False:
            kra_data =  self.env['kw_appraisal_employee'].sudo().search([('employee_id','in',user)])
            if not kra:
                if kra_data:
                    self.create({'emp_id':user,'kw_survey_id':kra_data.kw_survey_id.id,'kra_create_bool':True,'assign_template_kra_not_appraisal':True})
            elif kra_data.change_kra == True:
                    kra.search([('kw_survey_id','=',kra_data.kw_survey_id.id),('kra_agree_or_disagree','=',True)]).write({'kra_create_bool':True,'kra_agree_or_disagree':False,'status':''})
                    kra_data.change_kra = False
            elif kra :
                if kra_data.kw_survey_id.id == kra.kw_survey_id.id and kra.kra_agree_or_disagree == False:
                    pass
                elif kra_data.kw_survey_id.id != kra.kw_survey_id.id and kra.kra_agree_or_disagree == True and kra.status == 'Disagree':
                    kra.write({'emp_id':user,'kw_survey_id':kra_data.kw_survey_id.id,'kra_create_bool':True,'status': '','kra_agree_or_disagree':False,'assign_template_kra_not_appraisal':True})
            action = {
                    'type': 'ir.actions.act_window',
                    'name': 'MY KRA',
                    'views': [(assign_tree_view_id, 'tree')],
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_id' : self.id,
                    'res_model': 'kw_appraisal_kra_emp',
                    'target': 'main',
                    'domain': [('emp_id','=',self.env.user.employee_ids.id)]
                }
            return action
        
        
     # Search methods to see records as per cxo configuration and other domain
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is False:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(AppraisalMyKRA, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(AppraisalMyKRA, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

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

            if user.has_group('kw_performance_navigator.group_performance_navigator_manager') or (access_config and access_config.name == 'all'): # Manager will see all records
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
    
    
    def get_view_kra_appraisal(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_performance_navigator_employee_kra_tree').id
        appriasal_data = self.env['kw_empl_apprasial_details_kra'].sudo().search([('emp_pl_id', '=', self.kw_survey_id.id), ('emp_id', '=', self.emp_id.id)])
        if appriasal_data:
            return {
                'name': 'KRA',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'views': [(tree_view_id, 'tree')],
                'res_model': 'kw_empl_apprasial_details_kra',
                'target': 'new',
                'domain': [('id','in',appriasal_data.ids),],
            }
        else:
            raise ValidationError("You can't view as you have already disagree.")
        
    @api.multi
    def kra_acceptance_reminder_mail(self):
        app=[]
        appraisal_records = self.env['hr.appraisal'].sudo().search([])
        apps = appraisal_records.mapped('emp_id').id
        app.append(apps)
        var = self.env['kw_appraisal_kra_emp'].sudo().search([])
        for rec in var:
            if rec.emp_id.active and rec.emp_id.id not in app:
                if not rec.first_send_mail:
                    rec.first_send_mail = True
                    manager_user = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                    email_cc = ','.join(manager_user.mapped("email")) if manager_user else ''
                    template = self.env.ref('kw_performance_navigator.kra_agree_email_template')
                    template.with_context(cc=email_cc, employee=rec.emp_id).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                if rec.first_send_mail and not rec.kra_accepted:
                    manager_user = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                    email_cc = ','.join(manager_user.mapped("email")) if manager_user else ''
                    template = self.env.ref('kw_performance_navigator.kra_agree_reminder_email_template')
                    template.with_context(cc=email_cc, employee=rec.emp_id).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")





        
    def get_emp_agree_appraisal(self):
        template = self.env.ref('kw_performance_navigator.kra_agree_email_template')
        if self.kw_survey_id and self.emp_id:
            if self.env.user.employee_ids.id != self.emp_id.id:
                raise ValidationError("Concerned employee need to Agree his/her KRA")
            else:
                self.write({'kra_accepted':True,'kra_agree_or_disagree':True,'status':'Agree',
                            'action_log_ids':[[0,0,{'emp_id':self.emp_id.id,
                                                    'assign_template_id':self.kw_survey_id.id,
                                                    'status':'Agree',
                                                    'date_agree_disagree':date.today(),}]]
                            })
                if template:
                    manager_user = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                    email_cc = ','.join(manager_user.mapped("email")) if manager_user else ''
                    emp_name = self.emp_id.name
                    emp=self.emp_id
                    template.with_context(cc=email_cc,employee=emp,
                                       emp_name=emp_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'KRA is Accepted.',
                        'img_url':  '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                    }
                }

               
    def get_emp_disagree_appraisal(self):
        template = self.env.ref('kw_performance_navigator.kra_disagree_email_template')
        
        if self.kw_survey_id and self.emp_id:
            if self.env.user.employee_ids.id != self.emp_id.id:
                raise ValidationError("Concerned employee need to Disagree his/her KRA")
            else:
                self.write({'kra_disagree':True,'kra_agree_or_disagree':True,'status':'Disagree',
                            'action_log_ids':[[0,0,{'emp_id':self.emp_id.id,
                                                    'assign_template_id':self.kw_survey_id.id,
                                                    'status':'Disagree',
                                                    'date_agree_disagree':date.today(),}]]})
                if template:
                    manager_user = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                    email_to = ','.join(manager_user.mapped("email")) if manager_user else ''
                    emp_name = self.emp_id.name
                    template.with_context(email_to=email_to,
                                       emp_name=emp_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    
class Kw_Survey_kra(models.Model):
    _inherit = "survey.survey"  
    
    
    def write(self,vals):
        tagged_emp = self.env['kw_appraisal_employee'].sudo().search([('kw_survey_id','=',self.id)])
        if 'page_ids' in vals and tagged_emp and tagged_emp.employee_id :
            for item in vals['page_ids']:
                if isinstance(item[2], dict):
                    for key, value in item[2].items():
                        for r in value:
                            if isinstance(r[2], dict):
                                key_of = list(r[2].keys())
                                value_of = list(r[2].values())
                                if key_of[0] == 'type' and value_of[0] == 'numerical_box':
                                    tagged_emp.change_kra = True
                                elif key_of[0] == 'type' and value_of[0] == 'simple_choice':
                                    tagged_emp.change_compt = True
                            else:
                                pass

            # for page in vals['page_ids']:

            #     if isinstance(page, (list, tuple)):
            #         if page[0] in (4, 5):  # Existing ID
            #             page_ids.append(page[1])
               
            #     if isinstance(page, (list, tuple)) and len(page) > 2:
            #         # The third element (index 2) should be a dictionary containing question_ids
            #         page_data = page[2]
            #         tagged_emp.change_kra = True
             
        return super(Kw_Survey_kra, self).write(vals)
                    
class ActionKRAlog(models.Model):
    _name="kw_appraisal_kra_emp_log"
    _description = "Employee KRA create log"
    
    
    
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    assign_template_id = fields.Many2one('survey.survey', string="Appraisal Form",)
    status = fields.Char(string='Status')
    date_agree_disagree = fields.Date(string="Date")
    kra_log_emp = fields.Many2one('kw_appraisal_kra_emp',string="kRA Accept")
    
               
    
    
    
    
        
        
        
   
