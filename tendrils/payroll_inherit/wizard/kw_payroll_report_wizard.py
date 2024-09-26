from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime,date
import calendar



MONTH_LIST = [
    ('1', 'January'), ('2', 'February'),
    ('3', 'March'), ('4', 'April'),
    ('5', 'May'), ('6', 'June'),
    ('7', 'July'), ('8', 'August'),
    ('9', 'September'), ('10', 'October'),
    ('11', 'November'), ('12', 'December')
]
def get_years():
    year_list = []
    start_year = (date.today().year - (date.today().year - 2000))
    for i in range ((date.today().year + 30),1997,-1):
        year_list.append((i, str(i)))
    return year_list
    
class kw_payroll_report(models.TransientModel):
    _name = 'kw_payroll_reports'
    _description = 'Finanacial Year And Months'

    year = fields.Selection(get_years(), string='Year',default=date.today().year)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)

    def get_payroll_report_data(self):
        cuur_year = self.year
        curr_month = int(self.month)
        num_days = calendar.monthrange(cuur_year, curr_month)
        lst_day = list(num_days)[1]
        first_day = date(cuur_year,curr_month, 5)
        last_day = date(cuur_year, curr_month, lst_day)
            
        if self._context.get('hr_block_salary'):
            record_data = self.env['hr_block_salary'].sudo().search([('year','=',cuur_year),('month','=',curr_month)])
            tree_view_id = self.env.ref('payroll_inherit.block_salary_record_view_tree').id
            form_view_id = self.env.ref('payroll_inherit.hr_block_salary_view_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Payroll Block Salary Report',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'hr_block_salary',
                'target': 'main',
            }
            if len(record_data) == 0:
                return action
            else:
                action['domain'] = [('id','in',record_data.ids)]
                return action

        if self._context.get('kw_payslip_ledger'):
            tree_view_id = self.env.ref('payroll_inherit.payslip_ledger_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Payslip Ledger Report',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'kw_payslip_ledger',
                'target': 'main',
                'search_view_id': self.env.ref('payroll_inherit.payslip_ledger_view_search').id,
            }
            record_data = self.env['kw_payslip_ledger'].sudo().search([('month','=',str(self.month))])
            current_fiscal = self.env['account.fiscalyear'].search([('date_start','<=',first_day),('date_stop','>=',first_day)])
            if record_data:
                ledger_list = []
                for rec in record_data:
                    if rec.year.id == current_fiscal.id:
                        ledger_list.append(rec.id)
                action['domain'] = [('id','in',ledger_list)]
            return action
           
        if self._context.get('payroll_attendance_report'):
            record_data = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('attendance_year','=',cuur_year),('attendance_month','=',curr_month)])
            tree_view_id = self.env.ref('payroll_inherit.view_kw_payroll_monthly_attendance_report_tree').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Payroll Attendance Report',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'kw_payroll_monthly_attendance_report',
                'target': 'main',
                'search_view_id': self.env.ref('payroll_inherit.view_kw_payroll_monthly_attendance_report_search').id,
            }
            if len(record_data) ==0:
                return action
            else:
                action['domain'] = [('id','in',record_data.ids)]
                return action
        if self._context.get('lunch_expenses'):
            tree_view_id = self.env.ref('payroll_inherit.lunch_expenses_list').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Payroll Expenses Report',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'lunch_expenses',
                'target': 'main',
                'search_view_id': self.env.ref('payroll_inherit.lunch_expenses_view_search').id,
            }
            record_data = self.env['lunch_expenses'].sudo().search([('year','=',cuur_year),('month','=',curr_month)])
            if len(record_data) ==0:
                return action
            else:
                action['domain']= [('id','in',record_data.ids)]
                return action
        if self._context.get('allowance_allocation_master'):
            tree_view_id = self.env.ref('payroll_inherit.allowance_allocation_master_view_tree').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Payroll Allowance Allocation Report',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'allowance_allocation_master',
                'target': 'main',
                'search_view_id': self.env.ref('payroll_inherit.allowance_allocation_master_view_search').id,
            }
            record_data = self.env['allowance_allocation_master'].sudo().search([('year','=',cuur_year),('month','=',curr_month)])
            if len(record_data) == 0:
                return action
            else:
                action['domain'] = [('id','in',record_data.ids)]
                return action
