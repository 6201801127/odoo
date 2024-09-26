from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class nps_pran_details(models.Model):
    _name = 'nps_pran_details'
    _description = 'NPS PRAN Report'
    _auto = False



    nps_id = fields.Integer()
    employee_id = fields.Many2one('hr.employee', string="Name")
    employee_code = fields.Char('Emp Code')
    employee_name = fields.Char('Emp Name')
    job_id = fields.Many2one('hr.job', string="Designation",related='employee_id.job_id')
    department_id = fields.Many2one('hr.department', string="Department")
    job_branch_id = fields.Many2one('kw_res_branch', string="Location")
    work_email = fields.Char('E-mail')
    date_of_joining = fields.Date('Date of joining')
    birthday = fields.Date('Date of Birth')
    apply_date = fields.Datetime('Date of Apply')
    action_taken_date = fields.Datetime('Action taken Date')
    is_nps = fields.Selection([('Yes', 'Yes'),('No','No')],string="NPS")
    contribution = fields.Selection([(5, '5 % of Basic Salary'),(7, '7 % of Basic Salary'),(10, '10 % of Basic Salary'),(14, '14 % of Basic Salary')],string="NPS Contribution")
    pran_no = fields.Char(string="PRAN")
    state = fields.Selection([('Running', 'Active'),('Requested','Under Process'),('Not_started', 'Not Started')],string="PRAN Status") 


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT row_number() OVER () AS id,
                    nps.id AS nps_id,
                    nps.employee_id AS employee_id,
                    hr_emp.emp_code AS employee_code,
                    hr_emp.name AS employee_name,
                    hr_emp.job_id AS job_id,
                    hr_emp.department_id AS department_id,
                    hr_emp.job_branch_id AS job_branch_id,
                    hr_emp.work_email AS work_email,
                    hr_emp.birthday as birthday,
                    hr_emp.date_of_joining AS date_of_joining,
                    (SELECT create_date FROM nps_update_data WHERE nps_id = nps.id AND is_nps = 'Yes' AND state = 'Approved' LIMIT 1) AS apply_date,
                    (SELECT action_taken_on FROM nps_update_data WHERE nps_id = nps.id AND is_nps = 'Yes' AND state = 'Approved' ORDER BY action_taken_on DESC LIMIT 1) AS action_taken_date,
                    nps.is_nps AS is_nps,
                    nps.contribution AS contribution,
                    nps.pran_no AS pran_no,
                    'Running' AS state
                FROM 
                    nps_employee_data nps
                JOIN 
                    hr_employee hr_emp ON nps.employee_id = hr_emp.id
                JOIN 
                    hr_contract hc ON nps.employee_id = hc.employee_id AND hc.state = 'open'
                WHERE 
                    hc.is_nps = 'Yes' AND hc.contribution IS NOT NULL
                ORDER BY 
                    hr_emp.name
            );
        """)





    def view_all_nps_log(self):
        view_id = self.env.ref("payroll_inherit.nps_update_data_view_nps_log_tree").id
        action = {
            'name': 'Corporate NPS Logs',
            'type': 'ir.actions.act_window',
            'res_model': 'nps_update_data',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'domain':[('nps_id','=',self.nps_id)],
            'context': {'edit': False, 'create': False, 'delete': False}
        }
        return action