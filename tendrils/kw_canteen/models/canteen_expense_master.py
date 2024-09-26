import string
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


class BeverageType(models.Model):
    _name = "kw_canteen_expense_master"
    _description = "Canteen Expense"
    _rec_name = "expense_type_id"

    expense_type_id = fields.Many2one('kw_canteen_expense_type_master', string="Expenses Head")
    expense_date = fields.Date(string="Expense Date")
    expense_description = fields.Text(string="Description")
    expense_price = fields.Float(string="Amount")

    def get_forward_month_list(self,d):
        return [[(d + relativedelta(months=i)).strftime('%b') for i in range(12)],[(d + relativedelta(months=i)) for i in range(12)]]
    
    def update_employee_meal_collection(self):
        current_date = date.today()
        current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search([('date_start','<=',current_date),('date_stop','>=',current_date)],limit=1)
        months = self.get_forward_month_list(current_fiscal_year_id.date_start)
        for m in months[1]:
            _, num_days = calendar.monthrange(m.year, m.month)
            first_day = date(m.year, m.month, 1)
            last_day = date(m.year, m.month, num_days)
            self.env['kw_canteen_expense_wizard'].sudo().employee_meal_collection(first_day,last_day)
        view_id = self.env.ref('kw_canteen.kw_canteen_monthly_expense__report_pivot').id
        return {
            'name':'Expense Analysis',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'pivot',
            'views': [(view_id, 'pivot')],
            'res_model': 'kw_canteen_expense_master',
            'view_id': view_id,
            'target': 'self',
            'context':{'search_default_this_year_expense_report': 1}
        }

class MealExpenseHeadWizard(models.TransientModel):
    _name = 'kw_canteen_expense_wizard'
    _description = 'kw_canteen_expense_wizard'


    MONTH_LIST = [
        ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 2020, -1)]

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year),
                            required=True)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)

    def get_employee_collection(self):
        start_date = date(int(self.year),int(self.month),1)
        last_day = date(int(self.year),int(self.month),calendar.monthrange(int(self.year),int(self.month))[1])
        self.employee_meal_collection(start_date,last_day)
            
    # def get_forward_month_list(self,d):
    #     return [[(d + relativedelta(months=i)).strftime('%b') for i in range(12)],[(d + relativedelta(months=i)) for i in range(12)]]
  
    # def update_employee_meal_collection(self):
    #     current_date = date.today()
    #     current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search([('date_start','<=',current_date),('date_stop','>=',current_date)],limit=1)
    #     months = self.get_forward_month_list(current_fiscal_year_id.date_start)
    #     for m in months[1]:
    #         _, num_days = calendar.monthrange(m.year, m.month)
    #         first_day = datetime.date(m.year, m.month, 1)
    #         last_day = datetime.date(m.year, m.month, num_days)
    #         self.employee_meal_collection(first_day,last_day)
    #         view_id = self.env.ref('kw_canteen.kw_canteen_monthly_expense__report_pivot').id
    #         return {
    #             'name':'Claim',
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'pivot',
    #             'views': [(view_id, 'pivot')],
    #             'res_model': 'kw_canteen_expense_master',
    #             'view_id': view_id,
    #             'target': 'self',
    #             # 'context':{'edit':False,'create':False,'delete':False}
    #         }
        

        
    def employee_meal_collection(self,start_date,last_date):
        total_meal_price = 0
        meal_rec = self.env['meal_bio_log'].sudo().search([('recorded_date','>=',start_date),('recorded_date','<=',last_date)]).mapped('total_price')
        total_meal_price = -sum(meal_rec)
        expense_type = self.env['kw_canteen_expense_type_master'].sudo().search([('expense_head_code','=','CFEM')]).id
        expense_rec = self.env['kw_canteen_expense_master'].sudo().search([('expense_date','>=',start_date),('expense_date','<=',last_date),('expense_type_id','=',expense_type)],limit=1)
        expense_data = {
            'expense_date':last_date,
            'expense_price':total_meal_price,
            'expense_type_id':expense_type
        }
        if expense_rec:
            expense_rec.sudo().write(expense_data)
        else:
            self.env['kw_canteen_expense_master'].sudo().create(expense_data)