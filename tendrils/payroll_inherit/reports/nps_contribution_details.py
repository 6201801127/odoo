from odoo import fields, models, api, tools
from datetime import date, datetime

class combined_nps_cont_model(models.Model):
    _name = 'combined_nps_cont_model'


    payslip_id = fields.Many2one('hr.payslip', string="Payslip",default=lambda self: self.env.context.get('payslip_id'))
    cont_type = fields.Selection([('current', 'Current'), ('arrear', 'Arrear')],default=lambda self: self.env.context.get('cont_type'),required=True)
    remark = fields.Char('Remark')

   

    @api.model
    def create(self, vals):
        if not vals.get('payslip_id'):
            vals['payslip_id'] = self.env.context.get('payslip_id')
        existing_record = self.env['combined_nps_cont_model'].search([('payslip_id', '=', vals.get('payslip_id'))], order='id desc', limit=1)
        if existing_record:
            existing_record.write({'cont_type': vals.get('cont_type'),'remark': vals.get('remark')})
            return existing_record
        else:
            record = super(combined_nps_cont_model, self).create(vals)
            return record




    def check_combined_nps_cont(self):
        pass







class nps_contribution_details(models.Model):
    _name = 'nps_contribution_details'
    _description = 'NPS Contribution Report'
    _auto = False

    MONTH_LIST = [
            (1, 'January'), (2, 'February'),
            (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'),
            (11, 'November'), (12, 'December')]


    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_code = fields.Char('Emp Code')
    employee_name = fields.Char('Emp Name')
    date_of_birth = fields.Date('DOB')
    pran_no = fields.Char(string="PRAN")
    employers_contribution = fields.Float('Employers Contribution')
    employee_contribution = fields.Float('Employee Contribution')
    gross_contribution = fields.Float('Gross Contribution')
    cho_reg_no = fields.Char('CHO Reg No')
    cbo_reg_no = fields.Char('CBO Reg No')
    tier_flag = fields.Char('Tier Flag')
    month = fields.Selection(MONTH_LIST, string='Pay Month')
    year = fields.Char('Pay Year')
    cont_type = fields.Selection([('current', 'Current'), ('arrear', 'Arrear')],default='current')
    remark = fields.Char('Remark')



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
            SELECT 
                hp.id as id,
                hc.employee_id AS employee_id,
                emp.emp_code as employee_code,
                emp.name as employee_name,
                emp.birthday as date_of_birth,
                hc.pran_no AS pran_no,
                0.0 AS employers_contribution,
                hpl.amount AS employee_contribution,
                hpl.amount + 0.0 AS gross_contribution,
                'T1' AS tier_flag,
                hp.salary_confirmation_month as month,
                hp.salary_confirm_year as year,
                (SELECT value FROM ir_config_parameter WHERE key = 'NPS CHO NO' LIMIT 1) AS cho_reg_no,
                (SELECT value FROM ir_config_parameter WHERE key = 'NPS CBO NO' LIMIT 1) AS cbo_reg_no,
                
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM combined_nps_cont_model 
                        WHERE payslip_id = hp.id 
                    ) 
                    THEN (SELECT cont_type FROM combined_nps_cont_model 
                          WHERE payslip_id = hp.id LIMIT 1)
                    ELSE 'current'
                END AS cont_type,

                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM combined_nps_cont_model 
                        WHERE payslip_id = hp.id 
                    ) 
                    THEN (SELECT remark FROM combined_nps_cont_model 
                          WHERE payslip_id = hp.id LIMIT 1)
                    ELSE NULL
                END AS remark

            FROM 
                hr_contract hc
            JOIN 
                hr_payslip hp ON hc.id = hp.contract_id
            JOIN 
                hr_employee emp ON hc.employee_id = emp.id
            JOIN 
                hr_payslip_line hpl ON hpl.slip_id = hp.id
                    AND hpl.code = 'NPS'
                    AND hpl.amount > 0
                    AND hc.is_nps = 'Yes'
            )
        """)







    def action_change_cont_type(self):
        view_id = self.env.ref("payroll_inherit.combined_nps_cont_model_form").id
        action = {
            'name': 'Cont Type',
            'type': 'ir.actions.act_window',
            'res_model': 'combined_nps_cont_model',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'edit': False, 'create': False, 'delete': False,'payslip_id':self.id}
        }
        return action
    



