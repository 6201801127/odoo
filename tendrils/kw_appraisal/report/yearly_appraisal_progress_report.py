from odoo import models, fields, api, tools, _
from odoo.addons import decimal_precision as dp


class YearlyAppraisalProgressReport(models.Model):
    _name = "yearly_appraisal_progress_report"
    _description = "Yearly Appraisal Progress Report"
    _auto = False

     
    financial_year = fields.Many2one('kw_assessment_period_master',string="Financial Year")
    level = fields.Many2one('kw_grade_level',string="Level")
    total_emp = fields.Integer(string="Total Employee")
    male_total = fields.Integer(string="Male Total")
    female_total = fields.Integer(string="Female Total")
    age_group = fields.Char(string="Age Group")
    tenure_in_csm = fields.Char(string="Tenure (Years) in CSM")

    ignorant = fields.Char(string="Ignorant")
    ignorant_per = fields.Float(string="Ignorant Percentage(%)",compute='_compute_rating_percentage')
    ign = fields.Char(string="Ignorant Percentage(%)",compute='_compute_get_per')

    learner = fields.Char(string="Learner")
    learner_per = fields.Float(string="Learner Percentage(%)",compute='_compute_rating_percentage')
    lern = fields.Char(string="Learner Percentage(%)",compute='_compute_get_per')

    practitioner = fields.Char(string="Practitioner")
    practitioner_per = fields.Float(string="Practitioner Percentage(%)",compute='_compute_rating_percentage')
    prac = fields.Char(string="Practitioner Percentage(%)",compute='_compute_get_per')


    expert = fields.Char(string="Expert")
    expert_per = fields.Float(string="Expert Percentage(%)",compute='_compute_rating_percentage')
    expt = fields.Char(string="Expert Percentage(%)",compute='_compute_get_per')


    role_model = fields.Char(string="Role Model")
    role_model_per = fields.Float(string="Role Model Percentage(%)",compute='_compute_rating_percentage')
    rlmdl = fields.Char(string="Role Model Percentage(%)",compute='_compute_get_per')


    current_year = fields.Boolean(string='Current Year', compute='_compute_financial_year',search="_appraisal_search_current_financial_year")
    previous_year = fields.Boolean(string='Previous Year', compute='_compute_financial_year',search="_appraisal_search_previous_financial_year")

    
    @api.multi
    def _appraisal_search_current_financial_year(self,operator, value):
        query = "select row_number() over(order by id desc) as slno, id from kw_assessment_period_master"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        
        return [('financial_year','=', int(ids[0]['id']) if 'id' in ids[0] else 0)]
        
    @api.multi
    def _appraisal_search_previous_financial_year(self,operator, value):
        query = "select row_number() over(order by id desc) as slno, id from kw_assessment_period_master"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        
        return [('financial_year','=', int(ids[1]['id']) if 'id' in ids[1] else 0)]

    @api.multi
    def _compute_financial_year(self):
        pass

    @api.multi
    def _compute_rating_percentage(self):
        for rec in self:
            if rec.ignorant:
                ign_per = (int(rec.ignorant)/rec.total_emp) * 100
                rec.ignorant_per = round(ign_per)

            if rec.learner:
                lern_per = (int(rec.learner)/rec.total_emp) * 100
                rec.learner_per = round(lern_per)

            if rec.practitioner:
                prac_per = (int(rec.practitioner)/rec.total_emp) * 100
                rec.practitioner_per = round(prac_per)

            if rec.expert:
                expt_per = (int(rec.expert)/rec.total_emp) * 100
                rec.expert_per = round(expt_per)

            if rec.role_model:
                rlmdl_per = (int(rec.role_model)/rec.total_emp) * 100
                rec.role_model_per = round(rlmdl_per)


    @api.depends('ignorant','ignorant_per','learner','learner_per','practitioner','practitioner_per','expert','expert_per','role_model','role_model_per')
    def _compute_get_per(self):
        for rec in self:
            if rec.ignorant and rec.ignorant_per:
                rec.ign =rec.ignorant +' ('+ str(rec.ignorant_per )+'%'+')'

            if rec.learner and rec.learner_per:
                rec.lern =rec.learner +' ('+ str(rec.learner_per )+'%'+')'

            if rec.practitioner and rec.practitioner_per:
                rec.prac =rec.practitioner +' ('+ str(rec.practitioner_per )+'%'+')'

            if rec.expert and rec.expert_per:
                rec.expt =rec.expert +' ('+ str(rec.expert_per )+'%'+')'

            if rec.role_model and rec.role_model_per:
                rec.rlmdl =rec.role_model +' ('+ str(rec.role_model_per )+'%'+')'

    @api.multi
    def check_ignorant(self):
        view_id = self.env.ref('kw_appraisal.hr_appraisal_tree_view').id    
        appraisal_data = self.env['hr.appraisal'].sudo().search([('total_score', '<=', 20), ('appraisal_year_rel', '=', self.financial_year.id)]) 
        employees = appraisal_data.filtered(lambda rec: rec.emp_id and rec.emp_id.level == self.level).mapped('emp_id')
        employee_names = "\n".join([emp.name for emp in employees])
        context = {
            'default_level': self.level.id,
            'default_employee_names': employee_names,
        }
        action = {
            'name': _('Employee Appraisal Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'views': [(view_id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
            'context': context,
            'domain': [('total_score', '<=', 20), ('appraisal_year_rel', '=', self.financial_year.id), ('emp_id.level', '=', self.level.id)]
            
        }
        return action
    
    @api.multi
    def check_learner(self):
        view_id = self.env.ref('kw_appraisal.hr_appraisal_tree_view').id    
        appraisal_data = self.env['hr.appraisal'].sudo().search([('total_score', '>', 20), ('total_score', '<=', 40), ('appraisal_year_rel', '=', self.financial_year.id)]) 
        employees = appraisal_data.filtered(lambda rec: rec.emp_id and rec.emp_id.level == self.level).mapped('emp_id')
        employee_names = "\n".join([emp.name for emp in employees])
        context = {
            'default_level': self.level.id,
            'default_employee_names': employee_names,
        }
        action = {
            'name': _('Employee Appraisal Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'views': [(view_id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
            'context': context,
            'domain': [('total_score', '>', 20), ('total_score', '<=', 40), ('appraisal_year_rel', '=', self.financial_year.id), ('emp_id.level', '=', self.level.id)]
            
        }
        return action
    
    @api.multi
    def check_practitioner(self):
        view_id = self.env.ref('kw_appraisal.hr_appraisal_tree_view').id    
        appraisal_data = self.env['hr.appraisal'].sudo().search([('total_score', '>', 40), ('total_score', '<=', 60), ('appraisal_year_rel', '=', self.financial_year.id)]) 
        employees = appraisal_data.filtered(lambda rec: rec.emp_id and rec.emp_id.level == self.level).mapped('emp_id')
        employee_names = "\n".join([emp.name for emp in employees])
        context = {
            'default_level': self.level.id,
            'default_employee_names': employee_names,
        }
        action = {
            'name': _('Employee Appraisal Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'views': [(view_id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
            'context': context,
            'domain': [('total_score', '>', 40), ('total_score', '<=', 60), ('appraisal_year_rel', '=', self.financial_year.id), ('emp_id.level', '=', self.level.id)]
            
        }
        return action
    
    @api.multi
    def check_expert(self):
        view_id = self.env.ref('kw_appraisal.hr_appraisal_tree_view').id    
        appraisal_data = self.env['hr.appraisal'].sudo().search([('total_score', '>', 60), ('total_score', '<=', 80), ('appraisal_year_rel', '=', self.financial_year.id)]) 
        employees = appraisal_data.filtered(lambda rec: rec.emp_id and rec.emp_id.level == self.level).mapped('emp_id')
        employee_names = "\n".join([emp.name for emp in employees])
        context = {
            'default_level': self.level.id,
            'default_employee_names': employee_names,
        }
        action = {
            'name': _('Employee Appraisal Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'views': [(view_id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
            'context': context,
            'domain': [('total_score', '>', 60), ('total_score', '<=', 80), ('appraisal_year_rel', '=', self.financial_year.id), ('emp_id.level', '=', self.level.id)]
            
        }
        return action
    
    @api.multi
    def check_role_model(self):
        view_id = self.env.ref('kw_appraisal.hr_appraisal_tree_view').id    
        appraisal_data = self.env['hr.appraisal'].sudo().search([('total_score', '>', 80), ('total_score', '<=', 100), ('appraisal_year_rel', '=', self.financial_year.id)]) 
        employees = appraisal_data.filtered(lambda rec: rec.emp_id and rec.emp_id.level == self.level).mapped('emp_id')
        employee_names = "\n".join([emp.name for emp in employees])
        context = {
            'default_level': self.level.id,
            'default_employee_names': employee_names,
        }
        action = {
            'name': _('Employee Appraisal Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'views': [(view_id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
            'context': context,
            'domain': [('total_score', '>', 80), ('total_score', '<=', 100), ('appraisal_year_rel', '=', self.financial_year.id), ('emp_id.level', '=', self.level.id)]
            
        }
        return action


                    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
        SELECT 
            ROW_NUMBER() OVER (order by pm.id desc) AS id,
            pm.id AS financial_year,
            hr.level AS level,
            SUM(CASE WHEN hr.gender = 'male' THEN 1 ELSE 0 END) AS male_total,
            SUM(CASE WHEN hr.gender = 'female' THEN 1 ELSE 0 END) AS female_total,
            COUNT(*) AS total_emp,
            CONCAT(
                FLOOR(MIN(DATE_PART('year', AGE(CURRENT_DATE, hr.birthday))))::text,
                '-',
                CEIL(MAX(DATE_PART('year', AGE(CURRENT_DATE, hr.birthday))))::text
            ) AS age_group,
            CONCAT(
                FLOOR(MIN(DATE_PART('year', AGE(CURRENT_DATE, hr.date_of_joining))))::text,
                '-',
                CEIL(MAX(DATE_PART('year', AGE(CURRENT_DATE, hr.date_of_joining))))::text
            ) AS tenure_in_csm,
            COUNT(*)  FILTER (WHERE ap.total_score between 0 and 20) as ignorant,
            COUNT(*)  FILTER (WHERE ap.total_score between 21 and 40) as learner,   
            COUNT(*)  FILTER (WHERE ap.total_score between 41 and 60) as practitioner,
            COUNT(*)  FILTER (WHERE ap.total_score between 61 and 80) as expert,
            COUNT(*)  FILTER (WHERE ap.total_score between 81 and 100) as role_model
        FROM hr_appraisal AS ap
        JOIN hr_employee AS hr ON hr.id = ap.emp_id
        JOIN kw_assessment_period_master AS pm ON pm.id = ap.appraisal_year_rel
        GROUP BY pm.id, hr.level
        ORDER BY pm.id DESC, hr.level DESC
        )""" % (self._table))   
