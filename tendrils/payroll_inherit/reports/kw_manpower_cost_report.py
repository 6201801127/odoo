from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time
from dateutil import relativedelta


class KWManpowerCostReport(models.Model):
    _name = 'kw_manpower_cost_report_view'
    _description = 'Total Manpower Cost To Compare The Budget And Actual Report'
    _auto = False
    # _order = 'date_to asc'

  
    department_id = fields.Many2one('hr.department', string='Department')
    old_emp = fields.Integer("Existing Employee Count")
    old_emp_ctc = fields.Float("Existing Employee CTC")
    new_emp = fields.Integer("New Employee Count")
    new_emp_ctc = fields.Float("New Employee CTC")
    new_ex_emp = fields.Integer("New-EX Employee Count")
    new_ex_emp_ctc = fields.Float("New-Ex Employee CTC")
    old_ex_emp = fields.Integer("Existing-EX Employee Count")
    old_ex_emp_ctc = fields.Float("Existing-Ex Employee CTC")
    date_to = fields.Date()
    total_emp = fields.Integer(string='Total Employee')
    total_ctc = fields.Float("Total CTC")
    
    # @api.depends('old_emp','new_emp','new_ex_emp','old_ex_emp')
    # def _calculate_total_emp(self):
    #     for rec in self:
    #         rec.total_emp_count = rec.old_emp + rec.new_emp + rec.new_ex_emp + rec.old_ex_emp
    
    @api.model_cr
    def init(self):
        date_stop = self.env.context.get('date_stop') if self.env.context.get('date_stop') else date((date.today().year)+1,3,31)
        date_start = self.env.context.get('date_start') if self.env.context.get('date_start') else date((date.today().year),4,1)
        previous_month = date(date_stop.year-1,3,31)
        current_company = self.env.context.get('company_id') if self.env.context.get('company_id') else 1
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT
          row_number() OVER () AS id,
            department_id,
            date_to,
            new_emp,
            new_emp_ctc,
            new_ex_emp,
            new_ex_emp_ctc,
            old_emp,
            old_emp_ctc,
            old_ex_emp,
            old_ex_emp_ctc,
            new_emp + new_ex_emp + old_emp + old_ex_emp AS total_emp,
            COALESCE(new_emp_ctc, 0) + COALESCE(new_ex_emp_ctc, 0) + COALESCE(old_emp_ctc, 0) + COALESCE(old_ex_emp_ctc, 0) AS total_ctc
            FROM (
                SELECT
                    row_number() OVER () AS row_num,
                    department_id,
                    date_to,
                    new_emp,
                    new_emp_ctc,
                    new_ex_emp,
                    new_ex_emp_ctc,
                    old_emp,
                    old_emp_ctc,
                    old_ex_emp,
                    old_ex_emp_ctc
                    FROM (
                        SELECT
                            row_number() OVER () AS id,
                            e.department_id AS department_id,
                            a.date_to AS date_to,
                            COUNT(CASE WHEN e.date_of_joining BETWEEN fy.date_start AND a.date_to and e.id=a.employee_id and (e.last_working_day not between fy.date_start and a.date_to or e.last_working_day is null) THEN a.id END) AS new_emp,
                            SUM(h.amount) FILTER (WHERE e.date_of_joining BETWEEN fy.date_start AND a.date_to and e.id=a.employee_id and (e.last_working_day not between fy.date_start and a.date_to or e.last_working_day is null)) AS new_emp_ctc,
                            COUNT(CASE WHEN e.date_of_joining BETWEEN fy.date_start AND a.date_to and e.id=a.employee_id and 
								  (e.last_working_day  between fy.date_start and a.date_to) THEN a.id END) AS new_ex_emp,
                            SUM(h.amount) FILTER (WHERE e.date_of_joining BETWEEN fy.date_start AND a.date_to and e.id=a.employee_id and 
								(e.last_working_day  between fy.date_start and a.date_to)) AS new_ex_emp_ctc,
						
                            COUNT(a.id) FILTER (WHERE e.date_of_joining < fy.date_start and e.id=a.employee_id AND (e.last_working_day > a.date_to OR e.last_working_day IS NULL)) AS old_emp,
                            SUM(h.amount) FILTER (WHERE e.date_of_joining < fy.date_start and e.id=a.employee_id AND (e.last_working_day > a.date_to OR e.last_working_day IS NULL)) AS old_emp_ctc,
                            
						    COUNT(a.id) FILTER (WHERE e.date_of_joining < fy.date_start and e.id=a.employee_id AND (e.last_working_day  between fy.date_start and a.date_to)) AS old_ex_emp,
                            SUM(h.amount) FILTER (WHERE e.date_of_joining < fy.date_start and e.id=a.employee_id AND (e.last_working_day  between fy.date_start and a.date_to)) AS old_ex_emp_ctc
                            FROM
                                hr_payslip a
                                JOIN hr_payslip_line h ON a.id = h.slip_id
                                JOIN hr_employee e ON h.employee_id = e.id
                                JOIN account_fiscalyear fy ON a.date_to BETWEEN fy.date_start AND fy.date_stop AND fy.date_start = '{date_start}' AND fy.date_stop = '{date_stop}'
                            WHERE
                                a.state = 'done' AND h.code = 'CTC' and a.company_id = {current_company}
                            GROUP BY
                                e.department_id, a.date_to

                            UNION ALL
                            SELECT
                                row_number() OVER () AS id,
                                e.department_id AS department_id,
                                a.date_to AS date_to,
                                0 AS new_emp,
                                0 AS new_emp_ctc,
								0 as new_ex_emp,
				                0 as new_ex_emp_ctc,
                                COUNT(a.id) FILTER (WHERE a.date_to = '{previous_month}' and e.id=a.employee_id AND (e.last_working_day > '{previous_month}' OR e.last_working_day IS NULL)) AS old_emp,
                                SUM(h.amount) FILTER (WHERE a.date_to = '{previous_month}' and e.id=a.employee_id AND (e.last_working_day > '{previous_month}' OR e.last_working_day IS NULL)) AS old_emp_ctc,
                                0 AS old_ex_emp,
                                0 AS old_ex_emp_ctc
                            FROM
                                hr_payslip a
                                JOIN hr_payslip_line h ON a.id = h.slip_id
                                JOIN hr_employee e ON h.employee_id = e.id
                            WHERE
                                a.state = 'done' AND h.code = 'CTC' AND a.date_to = '{previous_month}' and a.company_id = {current_company}
                            GROUP BY
                                e.department_id, a.date_to,a.company_id
                        ) AS subquery
                    ) AS final_query
                    ORDER BY date_to asc
            )""" % (self._table))
class ManPowerCostWizard(models.TransientModel):
    _name = 'kw_manpower_cost_wizard'
    _description = 'Manpower Cost Report Filter'

    def _default_financial_yr(self):
          current_fiscal = self.env['account.fiscalyear'].search(
              [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
          return current_fiscal
      
    def _default_company(self):
        current_company = self.env['res.company'].search([('id', '<=', self.env.user.employee_ids.company_id.id)])
        return current_company

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                  default=_default_financial_yr,required=True)
    company_id =  fields.Many2one('res.company','Company',required=True,default=_default_company)
    
    
    def button_submit(self):
          if self.date_range:
            self.env['kw_manpower_cost_report_view'].with_context(date_stop=self.date_range.date_stop,date_start= self.date_range.date_start,company_id=self.company_id.id).init()
            view_id = self.env.ref('payroll_inherit.kw_manpower_cost_report_view_tree').id
            return {
                'name':'Manpower Cost Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'kw_manpower_cost_report_view',
                'view_id': view_id,
                'target': 'current',
                'context':{'search_default_date_to_report':1,'search_default_report_dept':1}
            }