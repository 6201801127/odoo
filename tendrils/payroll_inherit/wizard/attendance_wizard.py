import string
from odoo import fields, models, api
import json
import requests
# from datetime import datetime, date
from dateutil import relativedelta

import calendar
import datetime
from math import ceil,floor


class PayrollData(models.TransientModel):
    _name = "payroll.data"
    _description = "get payroll data from v5"

    employee_id = fields.Many2one('hr.employee', string="User Id")
    year = fields.Selection([('2021', '2021'),
                             ('2022', '2022'),
                             ('2023', '2023'),
                             ('2024', '2024'),
                             ('2025', '2025')], string="Year")
    month = fields.Selection([('1', 'January'),
                              ('2', 'February'),
                              ('3', 'March'),
                              ('4', 'April'),
                              ('5', 'May'),
                              ('6', 'June'),
                              ('7', 'July'),
                              ('8', 'August'),
                              ('9', 'September'),
                              ('10', 'October'),
                              ('11', 'November'),
                              ('12', 'December')], string="Month")
    page_no = fields.Integer(string="Page No")
    page_size = fields.Integer(string="Page Size")

    def get_data(self):
        # Fetch the url
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_payroll_data_url')
        # print(".......................", parameter_url)
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            user_id = self.employee_id.kw_id if self.employee_id else 0
            year = int(self.year) if self.year else 0
            month = int(self.month) if self.month else 0

            # parameters for url
            payroll_data_dict = {
                "UserID": user_id,
                "Year": year,
                "Month": month,
                "PageNo": self.page_no,
                "PageSize": self.page_size,
            }
            resp = requests.post(parameter_url, headers=header, data=json.dumps(payroll_data_dict))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            if json_record:
                emp_rec = self.env['hr.employee'].sudo().search(['|',('active','=',True),('active','=',False)])
                # print('emp_rec============',emp_rec)
                contract_rec = self.env['hr.contract'].sudo().search([('state', '=', 'open')])
                allowance_rec = self.env['allowance_allocation_master'].sudo().search([])
                salary_rules = self.env['hr.salary.rule'].sudo().search([])
                canteen_expenses = self.env['lunch_expenses'].sudo().search([])
                ledger = self.env['kw_payslip_ledger'].sudo().search([])
                # checking the given year month is in which fiscal year
                # get the data of a single employee based on year and month
                query = ""
                if self.year and self.month:
                    # date = datetime.date(year, int(self.month), 16)
                    # current_fiscal = self.env['account.fiscalyear'].search(
                        # [('date_start', '<=', date), ('date_stop', '>=', date)])
                    for rec in json_record:
                        # filter the employee record
                        emp_rec_filter = emp_rec.filtered(lambda x: x.kw_id == int(rec['UserID']))
                        if emp_rec_filter:
                            # filter the Contract record
                            contract_rec_filter = contract_rec.filtered(
                                lambda x: x.employee_id.id == emp_rec_filter.id)
                            if contract_rec_filter:
                                if rec['Basic'] > 0:
                                    productivity = rec['ProductivityBonus']+ceil((rec['Transport']+rec['MedicalReimbursement'])/2)
                                    commitment = rec['Commitmentbonus']+floor((rec['Transport']+rec['MedicalReimbursement'])/2)
                                    query += f"UPDATE hr_contract set current_basic={rec['Basic']}, wage={rec['CTC']}, commitment={commitment}, conveyance={rec['ConveyancePercentage']}, house_rent_allowance_metro_nonmetro={rec['HRAPercentage']}, productivity={productivity} WHERE id = {contract_rec_filter.id};"
                                    query += f"UPDATE hr_employee set current_basic={rec['Basic']}, current_ctc={rec['CTC']}, commitment={commitment}, conveyance={rec['ConveyancePercentage']}, hra={rec['HRAPercentage']}, productivity={productivity},enable_payroll='yes' WHERE id = {emp_rec_filter.id};"

                                # Fetch the employee referral bonus record
                                erbonus = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                 x.year == self.year and x.month == self.month and
                                                                 x.allowance.code == 'ERBONUS')
                                if not erbonus and rec['Employeereferralbonus'] > 0:
                                    salary_rules_erbonus = salary_rules.filtered(lambda x: x.code == 'ERBONUS')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_erbonus.id},{rec['Employeereferralbonus']});"

                                # Fetch the Equitable allowance record
                                equitable = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                   x.year == self.year and x.month == self.month and
                                                                   x.allowance.code == 'EALW')
                                if not equitable and rec['EquitableAllowance'] > 0:
                                    salary_rules_equitable = salary_rules.filtered(lambda x: x.code == 'EALW')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_equitable.id},{rec['EquitableAllowance']});"

                                # Fetch the Special allowance record
                                spcl_allow = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                    x.year == self.year and x.month == self.month and
                                                                    x.allowance.code == 'SALW')
                                if not spcl_allow and rec['SpecialAllowance'] > 0:
                                    salary_rules_spcl = salary_rules.filtered(lambda x: x.code == 'SALW')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_spcl.id},{rec['SpecialAllowance']});"

                                # Fetch the Training Incentive allowance record
                                trng_inc = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                  x.year == self.year and x.month == self.month and
                                                                  x.allowance.code == 'TINC')
                                if not trng_inc and rec['TrainingIncentive'] > 0:
                                    salary_rules_trng_inc = salary_rules.filtered(lambda x: x.code == 'TINC')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_trng_inc.id},{rec['TrainingIncentive']});"

                                # Fetch the Incentve allowance record
                                incentive = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                   x.year == self.year and x.month == self.month and
                                                                   x.allowance.code == 'INC')
                                if not incentive and rec['Incentive'] > 0:
                                    salary_rules_incentive = salary_rules.filtered(lambda x: x.code == 'INC')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_incentive.id},{rec['Incentive']});"

                                #  Fetch the Leave encashment allowance record
                                leave_ench = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                    x.year == self.year and x.month == self.month and
                                                                    x.allowance.code == 'LE')
                                if not leave_ench and rec['LeaveEncashment'] > 0:
                                    salary_rules_leave_ench = salary_rules.filtered(
                                        lambda x: x.code == 'LE')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_leave_ench.id},{rec['LeaveEncashment']});"

                                #  Fetch the Variable allowance record
                                variable = allowance_rec.filtered(lambda x: x.employee.id == emp_rec_filter.id and
                                                                  x.year == self.year and x.month == self.month and
                                                                  x.allowance.code == 'VAR')
                                if not variable and rec['Variable'] > 0:
                                    salary_rules_variable = salary_rules.filtered(
                                        lambda x: x.code == 'VAR')
                                    query += f"INSERT INTO allowance_allocation_master (employee,year,month,allowance,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_variable.id},{rec['Variable']});"

                                #  Fetch the Lunch Expenses record
                                lunch = canteen_expenses.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                  x.year == self.year and x.month == self.month and
                                                                  x.deduction_id.code == 'FC')
                                if not lunch and rec['canteenExpense'] > 0:
                                    salary_rules_lunch = salary_rules.filtered(lambda x: x.code == 'FC')
                                    query += f"INSERT INTO lunch_expenses (employee_id,year,month,deduction_id,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_lunch.id},{rec['canteenExpense']});"

                                #  Fetch the Other Deduction record
                                other_ded = canteen_expenses.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                      x.year == self.year and x.month == self.month and
                                                                      x.deduction_id.code == 'OD')
                                if not other_ded and rec['OtherAdvance'] > 0:
                                    salary_rules_other_ded = salary_rules.filtered(lambda x: x.code == 'OD')
                                    query += f"INSERT INTO lunch_expenses (employee_id,year,month,deduction_id,amount) values ({emp_rec_filter.id},{self.year},{self.month},{salary_rules_other_ded.id},{rec['OtherAdvance']});"

                                #  Fetch the Health Insurance Dependant record
                                health_dependant = ledger.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                             x.year == str(self.year)  and x.month == self.month and
                                                                             x.salary_rule_id.code == 'HID')
                                if not health_dependant and rec['HealthInsuranceDependent'] > 0:
                                    salary_rules_hid = salary_rules.filtered(lambda x: x.code == 'HID')
                                    query += f"INSERT INTO kw_payslip_ledger (employee_id,year,month,salary_rule_id,amount,contract_id) values ({emp_rec_filter.id},{str(self.year)},{self.month},{salary_rules_hid.id},{rec['HealthInsuranceDependent']},{contract_rec_filter.id});"
                                    
                                #  Fetch the Health Insurance Self record
                                health_self = ledger.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                              x.year == str(self.year) and x.month == self.month and
                                                                             x.salary_rule_id.code == 'CMT')
                                if not health_self and rec['HealthInsuranceSelf'] > 0:
                                    salary_rules_self = salary_rules.filtered(lambda x: x.code == 'CMT')
                                    query += f"INSERT INTO kw_payslip_ledger (employee_id,year,month,salary_rule_id,amount,contract_id) values ({emp_rec_filter.id},{str(self.year)},{self.month},{salary_rules_self.id},{rec['HealthInsuranceSelf']},{contract_rec_filter.id});"

                                #  Fetch the IncomeTax record
                                tds = ledger.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                             x.year == str(self.year) and x.month == self.month and
                                                                             x.salary_rule_id.code == 'TDS')
                                if not tds and rec['IncomeTax'] > 0:
                                    salary_rules_tds = salary_rules.filtered(lambda x: x.code == 'TDS')
                                    query += f"INSERT INTO kw_payslip_ledger (employee_id,year,month,salary_rule_id,amount,contract_id) values ({emp_rec_filter.id},{str(self.year)},{self.month},{salary_rules_tds.id},{rec['IncomeTax']},{contract_rec_filter.id});"
                                
                                salary_adv = ledger.filtered(lambda x: x.employee_id.id == emp_rec_filter.id and
                                                                             x.year == str(self.year) and x.month == self.month and
                                                                             x.salary_rule_id.code == 'SALADV')
                                if not salary_adv and rec['SalaryAdvance'] > 0:
                                    salary_rules_adv = salary_rules.filtered(lambda x: x.code == 'SALADV')
                                    query += f"INSERT INTO kw_payslip_ledger (employee_id,year,month,salary_rule_id,amount,contract_id) values ({emp_rec_filter.id},{ str(self.year)},{self.month},{salary_rules_adv.id},{rec['SalaryAdvance']},{contract_rec_filter.id});"

                    # print('length of query1====', len(query), query)
                    if len(query) > 0:
                        self._cr.execute(query)
                        
                else:
                    for rec in json_record:
                        # filter the employee record
                        emp_rec_filter = emp_rec.filtered(lambda x: x.kw_id == int(rec['UserID']))
                        if emp_rec_filter:
                            # filter the Contract record
                            contract_rec_filter = contract_rec.filtered(lambda x: x.employee_id.id == emp_rec_filter.id)
                            if contract_rec_filter:
                                # if contract_rec_filter.current_basic != rec['Basic'] and rec['Basic'] > 0:
                                productivity = rec['ProductivityBonus']+ceil((rec['Transport']+rec['MedicalReimbursement'])/2)
                                commitment = rec['Commitmentbonus']+floor((rec['Transport']+rec['MedicalReimbursement'])/2)
                                query += f"UPDATE hr_contract SET current_basic={rec['Basic']}, wage={rec['CTC']}, commitment={commitment}, conveyance={rec['ConveyancePercentage']}, house_rent_allowance_metro_nonmetro={rec['HRAPercentage']}, productivity={productivity} WHERE id = {contract_rec_filter.id};"
                                query += f"UPDATE hr_employee set current_basic={rec['Basic']}, current_ctc={rec['CTC']}, commitment={commitment}, conveyance={rec['ConveyancePercentage']}, hra={rec['HRAPercentage']}, productivity={productivity},enable_payroll='yes' WHERE id = {emp_rec_filter.id};"
                    # print('length of query2====', len(query), query)
                    if len(query) > 0:
                        self._cr.execute(query)

            self.env['kw_payroll_log'].sudo().create(
                {'request_params': payroll_data_dict, 'response_result': json_record})
