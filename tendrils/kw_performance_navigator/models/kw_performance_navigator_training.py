from odoo import models, fields, api, tools
from datetime import date, datetime, time
from odoo.exceptions import  ValidationError
from datetime import datetime, timedelta



class AppraisalMyTraining(models.Model):
    _name="kw_performance_navigator_training"
    _description = "Employee Training"
    _rec_name="emp_id"
    _auto = False  

    
    emp_id = fields.Many2one('hr.employee',string="Name")
    training_planned_hours = fields.Char(string='Training Planned Hours')
    training_achieved_hours = fields.Char(string="Training Achieved Hours",compute="get_attended_hours")
    appraisal_period = fields.Many2one('account_fiscalyear')
    appraisal_period_name = fields.Char(string='Appraisal Period')
    training_id = fields.Many2one('kw_training',string="Training Id")
    training_percentage = fields.Float(string="Training Percentage", compute="compute_training_percentage")


    @api.model_cr
    def init(self):
        self.env.cr.execute(f"""
            DROP VIEW IF EXISTS {self._table} CASCADE;
            CREATE VIEW {self._table} AS (
                SELECT 
                    ROW_NUMBER() OVER (PARTITION BY af.name ORDER BY hk.hr_employee_id) AS id,
                    af.id AS appraisal_period,
                    af.name AS appraisal_period_name,
                    hk.hr_employee_id AS emp_id,
                    SUM(ktp.id) AS training_id,  
                    TO_CHAR(INTERVAL '1 second' * SUM(EXTRACT(EPOCH FROM (ks.to_time::time - ks.from_time::time))), 'HH24:MI:SS') AS training_planned_hours
                FROM kw_training kt
                JOIN kw_training_plan ktp ON ktp.training_id = kt.id
                JOIN kw_training_schedule ks ON kt.id = ks.training_id
                JOIN hr_employee_kw_training_plan_rel hk ON hk.kw_training_plan_id = ktp.id
                JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop
                GROUP BY af.id, hk.hr_employee_id
            )
        """)
        

    
    @api.depends('emp_id')
    def get_attended_hours(self):
        for record in self:
            employee_id = self.env.user.employee_ids.id if self.env.user.employee_ids else None
            appraisal_period = record.appraisal_period.id
            if employee_id and appraisal_period:
                self.env.cr.execute(f"""
                    SELECT TO_CHAR(INTERVAL '1 second' * SUM(
                        CASE WHEN ktd.attended THEN EXTRACT(EPOCH FROM (ka.to_time::time - ka.from_time::time)) 
                        ELSE 0 END), 'HH24:MI:SS') AS training_achieved_hours 
                    FROM kw_training kt 
                    JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop 
                    JOIN kw_training_attendance ka ON ka.training_id = kt.id 
                    JOIN kw_training_attendance_details ktd ON ktd.attendance_id = ka.id 
                    WHERE af.id = %s AND ktd.participant_id = %s 
                    GROUP BY af.name, ktd.participant_id
                """, (appraisal_period, employee_id))
                result = self.env.cr.fetchone()
                record.training_achieved_hours = result[0]


    @api.depends('training_planned_hours', 'training_achieved_hours')
    def compute_training_percentage(self):
        for record in self:
            planned_hours = self._convert_time_to_seconds(record.training_planned_hours)
            achieved_hours = self._convert_time_to_seconds(record.training_achieved_hours)
            if planned_hours > 0:
                record.training_percentage = (achieved_hours / planned_hours) * 100
            else:
                record.training_percentage = 0

    def _convert_time_to_seconds(self, time_str):
        if time_str:
            h, m, s = map(int, time_str.split(':'))
            data=h * 3600 + m * 60 + s
            return data
        return 0


    def get_view_of_training(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_training_schedule_tree').id
        data_in_plan = self.env['kw_training_plan'].sudo().search([('financial_year', '=', self.appraisal_period.id),('participant_ids','=',self.emp_id.id)])
        plan_ids = data_in_plan.mapped('training_id.id')
        data_in_training = self.env['kw_training'].sudo().search([('id','in',plan_ids)])
        training_ids = data_in_training.ids
        action = {
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'kw_training_schedule',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('training_id', 'in', training_ids)],
            'context': {'create': False,'edit': False,'delete': False,},
            'views': [(tree_view_id, 'tree')],
        }
        return action
    
    def get_view_of_policies(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_emp_handbook_policy_view_tree').id
        handbook_data = self.env['kw_emp_handbook_policy'].sudo().search([('emp_id','=',self.emp_id.id)])
        action = {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_emp_handbook_policy',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('emp_id', '=', self.emp_id.id)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
            'views': [(tree_view_id, 'tree')],
        }
        return action


class KwEmpAppraisalTraining(models.Model):
    _name = "kw_empl_apprasial_training"
    _description = "Employee Appraisal Training"
    _auto = False
    _rec_name = "emp_id"
    
    
    emp_id = fields.Many2one('hr.employee',string="Name")
    department_id = fields.Many2one('hr.department',string="Department")
    division =fields.Many2one('hr.department',string="Division")
    job_id =fields.Many2one('hr.job',string="Designation")
    emp_code = fields.Char(string="Code",related="emp_id.emp_code")
    training_planned_hours = fields.Char(string='Training Planned Hours')
    training_achieved_hours = fields.Char(string="Training Achieved Hours",compute="get_attended_hours")
    appraisal_period = fields.Many2one('account_fiscalyear')
    appraisal_period_name = fields.Char(string='Appraisal Period')
    training_id = fields.Many2one('kw_training',string="Training Id")
    training_percentage = fields.Float(string="Training Percentage", compute="compute_training_percentage")

    


    @api.model_cr
    def init(self):
        self.env.cr.execute(f"""
            DROP VIEW IF EXISTS {self._table} CASCADE;
            CREATE VIEW {self._table} AS (
                SELECT 
                    ROW_NUMBER() OVER (PARTITION BY af.name ORDER BY hk.hr_employee_id) AS id,
                    af.id AS appraisal_period,
                    af.name AS appraisal_period_name,
                    hk.hr_employee_id AS emp_id,
                    he.emp_code AS emp_code, 
                    he.job_id AS job_id, 
                    he.division AS division,
                    hd.id AS department_id, 
                    SUM(ktp.id) AS training_id,  
                    TO_CHAR(INTERVAL '1 second' * SUM(EXTRACT(EPOCH FROM (ks.to_time::time - ks.from_time::time))), 'HH24:MI:SS') AS training_planned_hours
                FROM kw_training kt
                JOIN kw_training_plan ktp ON ktp.training_id = kt.id
                JOIN kw_training_schedule ks ON kt.id = ks.training_id
                JOIN hr_employee_kw_training_plan_rel hk ON hk.kw_training_plan_id = ktp.id
                JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop
                JOIN hr_employee he ON he.id = hk.hr_employee_id
                JOIN hr_department hd ON hd.id = he.department_id
                WHERE he.active = TRUE
                GROUP BY af.id, hk.hr_employee_id, he.emp_code, he.job_id, he.division, hd.id
            )
        """)

        

    
    @api.depends('emp_id')
    def get_attended_hours(self):
        for record in self:
            appraisal_period = record.appraisal_period.id
            if record.emp_id and appraisal_period:
                record.env.cr.execute("""
                    SELECT TO_CHAR(INTERVAL '1 second' * SUM(
                        CASE WHEN ktd.attended THEN EXTRACT(EPOCH FROM (ka.to_time::time - ka.from_time::time)) 
                        ELSE 0 END), 'HH24:MI:SS') AS training_achieved_hours 
                    FROM kw_training kt 
                    JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop 
                    JOIN kw_training_attendance ka ON ka.training_id = kt.id 
                    JOIN kw_training_attendance_details ktd ON ktd.attendance_id = ka.id 
                    WHERE af.id = %s AND ktd.participant_id = %s 
                    GROUP BY af.name, ktd.participant_id
                """, (appraisal_period, record.emp_id.id))
                results = record.env.cr.fetchall()
                record.training_achieved_hours = ', '.join([res[0] for res in results]) if results else ''

    @api.depends('training_planned_hours', 'training_achieved_hours')
    def compute_training_percentage(self):
        for record in self:
            planned_hours = self._convert_time_to_seconds(record.training_planned_hours)
            achieved_hours = self._convert_time_to_seconds(record.training_achieved_hours)
            if planned_hours > 0:
                record.training_percentage = (achieved_hours / planned_hours) * 100
            else:
                record.training_percentage = 0

    def _convert_time_to_seconds(self, time_str):
        if time_str:
            h, m, s = map(int, time_str.split(':'))
            data=h * 3600 + m * 60 + s
            return data
        return 0

    def get_view_training(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_training_schedule_tree').id
        data_in_plan = self.env['kw_training_plan'].sudo().search([('financial_year', '=', self.appraisal_period.id),('participant_ids','=',self.emp_id.id)])
        plan_ids = data_in_plan.mapped('training_id.id')
        data_in_training = self.env['kw_training'].sudo().search([('id','in',plan_ids)])
        training_ids = data_in_training.ids
        action = {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_training_schedule',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('training_id', 'in', training_ids)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
            'views': [(tree_view_id, 'tree')],
        }
        return action
    
    def get_view_of_policies(self):
        tree_view_id = self.env.ref('kw_performance_navigator.kw_emp_handbook_policy_view_tree').id
        handbook_data = self.env['kw_emp_handbook_policy'].sudo().search([('emp_id','=',self.emp_id.id)])
        action = {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_emp_handbook_policy',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('emp_id', '=', self.emp_id.id)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
            'views': [(tree_view_id, 'tree')],
        }
        return action
        
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is False:
            domain = []
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(KwEmpAppraisalTraining, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        access_domain = self._get_access_domain()
        if access_domain:
            domain.extend(access_domain)
        return super(KwEmpAppraisalTraining, self).read_group(domain=domain, fields=fields, groupby=groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

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
            if user.has_group('kw_appraisal.group_appraisal_manager') or (access_config and access_config.name == 'all'):
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


class KwEmpHandbookPolicy(models.Model):
    _name = "kw_emp_handbook_policy"
    _description = "Employee Handbook Policy"
    _auto = False
    _rec_name = "emp_id"
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    handbook_type_id = fields.Many2one('kw_handbook_type', string="Document Type")
    understood = fields.Boolean("Read and Understood")
    date = fields.Date(string="Date")

    @api.model_cr
    def init(self):
        self.env.cr.execute(f"""
            DROP VIEW IF EXISTS {self._table} CASCADE;
            CREATE VIEW {self._table} AS (
                SELECT 
                    ROW_NUMBER() OVER () AS id,  
                    hr.id AS emp_id,
                    kh.handbook_type_id AS handbook_type_id,
                    kh.understood AS understood,
                    kh.date AS date
                FROM hr_employee hr
                JOIN kw_handbook kh ON kh.employee_id = hr.id
            )
        """)







