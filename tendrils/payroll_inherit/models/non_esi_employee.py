from odoo import fields, models, api
from odoo.exceptions import ValidationError


class NonEsiEmployee(models.Model):
    _name = 'non_esi_employee_report'
    _description = 'Non Esi Employee'

    employee_id = fields.Many2one('hr.employee',string='Employee')
    emp_code = fields.Char(string='Code',related='employee_id.emp_code')
    department_id = fields.Many2one('hr.department',string='Department')
    previous_salary = fields.Float(string='Previous Salary')
    current_salary = fields.Float(string='Current Salary')
    state = fields.Selection([('ESI', 'ESI'), ('Upgrade-To-GHI', 'Upgrade-To-GHI'),('GHI','GHI')])
    fiscalyr = fields.Many2one('account.fiscalyear')

    # @api.multi
    # def report_non_esi_employees(self):
    #     self.env.cr.execute('''
    #             WITH EmployeeSalaries AS (
    #             SELECT 
    #                 he.id AS employee_id,
    #                 he.emp_code AS emp_code,
    #                 he.name AS name,
    #                 he.department_id AS department_id,  
    #                 hp.date_to AS payslip_date,
    #                 hpl.total AS salary,
    #                 pgdr.status AS state,
    #                 ROW_NUMBER() OVER (PARTITION BY he.id ORDER BY hp.date_to DESC) AS rn
    #             FROM 
    #                 hr_employee he
    #             JOIN 
    #                 hr_payslip hp ON hp.employee_id = he.id AND hp.state = 'done'
    #             JOIN 
    #                 hr_payslip_line hpl ON hpl.slip_id = hp.id AND hpl.code = 'GROSS'
    #             LEFT JOIN 
    #                 payroll_ghi_details_report pgdr ON pgdr.employee_id = he.id 
    #             WHERE 
    #                 he.active = TRUE AND he.esi_applicable = TRUE
    #         )
    #         SELECT 
    #             es_current.employee_id,
    #             es_current.emp_code,
    #             es_current.name,
    #             es_current.department_id,
    #             COALESCE(es_previous.salary, 0) AS previous_salary,
    #             es_current.salary AS current_salary,
    #             es_current.state AS state 
    #         FROM 
    #             EmployeeSalaries es_current
    #         LEFT JOIN 
    #             EmployeeSalaries es_previous ON es_current.employee_id = es_previous.employee_id AND es_previous.rn = es_current.rn + 1
    #         WHERE 
    #             es_current.rn = 1
    #         ORDER BY 
    #             es_current.emp_code, es_current.salary, es_current.department_id
    #     ''')
    #     result = self.env.cr.dictfetchall()
    #     self.env['non_esi_employee_report'].search([]).unlink()
    #     for res in result:
    #         self.env['non_esi_employee_report'].create(res)
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'ESI Employee Report',
    #         'view_mode': 'tree',
    #         'res_model': 'non_esi_employee_report',
    #         'target': 'current',
    #     }
