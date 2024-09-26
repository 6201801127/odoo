from odoo import models, fields, api, tools, _


class EmpAppraisalProgressReport(models.Model):
    _name = "employee_appraisal_progress_report"
    _description = "Employee Appraisal Year Wise Report"
    _order = 'period desc'
    _auto = False

    emp_name = fields.Many2one('hr.employee',string="Employee Name")
    emp_code = fields.Char(string="Employee Code")
    designation = fields.Many2one('hr.job',string="Designation")
    department = fields.Many2one('hr.department', string="Department")

    period = fields.Many2one('kw_assessment_period_master',string='Period')
    total_score = fields.Float(string='Score')
    stage = fields.Selection([
        ('a', 'Ignorant'),
        ('b', 'Learner'),
        ('c', 'Practitioner'),
        ('d', 'Expert'),
        ('e', 'Role Model')
        ])
    current_year = fields.Boolean(string='Current Year', compute='_compute_financial_year',search="_appraisal_search_current_financial_year")
    previous_year = fields.Boolean(string='Previous Year', compute='_compute_financial_year',search="_appraisal_search_previous_financial_year")

    
    @api.multi
    def _appraisal_search_current_financial_year(self,operator, value):
        query = "select row_number() over(order by id desc) as slno, id from kw_assessment_period_master"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        
        return [('period','=', int(ids[0]['id']) if 'id' in ids[0] else 0)]
        
    @api.multi
    def _appraisal_search_previous_financial_year(self,operator, value):
        query = "select row_number() over(order by id desc) as slno, id from kw_assessment_period_master"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        
        return [('period','=', int(ids[1]['id']) if 'id' in ids[1] else 0)]

    @api.multi
    def _compute_financial_year(self):
        pass
    

                        
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
                    
        SELECT row_number() over(order by pm.id desc) as id,
            hr.emp_code as emp_code,
            hr.id as emp_name,
            hr.job_id as designation,
            hr.department_id as department,
            pm.id as period,
            b.total_score as total_score,
            CASE 
                WHEN 0  <= CEIL(b.total_score) AND 20  >=  CEIL(b.total_score) THEN 'a'
                WHEN 21 <= CEIL(b.total_score) AND 40  >=  CEIL(b.total_score) THEN 'b'
                WHEN 41 <= CEIL(b.total_score) AND 60  >=  CEIL(b.total_score) THEN 'c'
                WHEN 61 <= CEIL(b.total_score) AND 80  >=  CEIL(b.total_score) THEN 'd'
                WHEN 81 <= CEIL(b.total_score) AND 100 >=  CEIL(b.total_score) THEN 'e'
            END as stage
        FROM hr_appraisal b
        LEFT JOIN hr_employee as hr ON hr.id = b.emp_id
        left join kw_assessment_period_master as pm on b.appraisal_year_rel = pm.id
        ORDER BY pm.id DESC
        )""" % (self._table))   
        # where b.state in ({self.env.ref('kw_appraisal.hr_appraisal_completed').id},{self.env.ref('kw_appraisal.hr_appraisal_published').id})
