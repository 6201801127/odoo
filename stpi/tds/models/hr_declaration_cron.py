from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from time import sleep
from math import ceil

class HrDeclarationCron(models.Model):
    _inherit = 'hr.declaration'


    def _current_fy(self):
        curr_date = date.today()
        dateRangeObj = self.env['date.range'].sudo().search([('type_id.name', '=', 'Fiscal Year'),
                                                                ('date_start', '<=', curr_date),
                                                                ('date_end', '>=', curr_date)])
        if not dateRangeObj:
            raise ValidationError('Please set date range for current financial year')
        return dateRangeObj

    def _previous_fy(self, current_fy):
        start_dt, end_dt = (current_fy.date_start) - relativedelta(years=1), (current_fy.date_end) - relativedelta(years=1)
        dateRangeObj = self.env['date.range'].sudo().search([('type_id.name', '=', 'Fiscal Year'),
                                                                ('date_start', '=', start_dt),
                                                                ('date_end', '=', end_dt)])
        if not dateRangeObj:
            raise ValidationError('Please set date range for current financial year')
        return dateRangeObj


    def hr_declaration_cron(self):
        current_date = fields.Date.today()
        current_year = current_date.year
        current_fy_id = self._current_fy()
        previous_fy_id = self._previous_fy(current_fy_id)
        finance_start_dt = date(current_year, 4, 1)
        emps_id_lis, limit = [], 50
        domain = ['|',('employee_type', '=', 'regular'),
                    '&',('employee_type', '=', 'contractual_with_stpi'),
                        ('tds_applicable', '=', True)]
        # if current_date > finance_start_dt:
        #     nextcall_dt = datetime.strptime('{}-{}-{} {}:{}:{} {}'\
        #                             .format((current_year + 1), 4, 1, 0, 0, 0, 'AM'),\
        #                                 '%Y-%m-%d %H:%M:%S %p')
        # else:
        #     nextcall_dt = datetime.strptime('{}-{}-{} {}:{}:{} {}'\
        #                             .format(current_year, 4, 1, 1, 0, 0, 'AM'),\
        #                                 '%Y-%m-%d %H:%M:%S %p')

        if current_date == finance_start_dt:
            emps = self.env['hr.employee'].search(domain)
            for _ in range(ceil(len(emps)/limit)):
                domain += [('id', 'not in', emps_id_lis)]
                emps_limit = self.env['hr.employee'].search(domain, limit=limit)
                for emp in emps_limit:
                    prev_tds = self.search([('employee_id', '=', emp.id), 
                                            ('date_range', '=', previous_fy_id.id)])
                    data = {'employee_id': emp.id,
                            'which_it': prev_tds.which_it if prev_tds else 'old',
                            'date_range': current_fy_id.id}
                    current_tds = self.create(data)
                    current_tds.button_compute_tax()
                emps_id_lis.extend(emps_limit.mapped('id'))
                sleep(limit)
        # tds_cron = self.env.ref('tds.hr_declaration_cron')
        # print('nextcall_dt ==>', nextcall_dt)
        # tds_cron.write({'nextcall': nextcall_dt})
        return True


    # def hr_declaration_cron(self):
    #     search_id = self.env['hr.declaration'].search(
    #         [('state', 'not in', ['approved', 'rejected'])])
    #     for rec in search_id:
    #         sum = 0
    #         for lines in rec.rent_paid_ids:
    #             if lines.date_to <= datetime.now().date():
    #                 sum += lines.amount
    #         rec.rent_paid = round(sum)
    #         if rec.rent_paid > 100000.00:
    #             rec.rent_paid_attach_files = True
    #         else:
    #             rec.rent_paid_attach_files = False
    #         bs = 0.00
    #         da = 0.00
    #         dstart = rec.date_range.date_start
    #         dend = rec.date_range.date_end
    #         prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                             ('slip_id.state', '=', 'done'),
    #                                                             ('slip_id.date_from', '>=', dstart),
    #                                                             ('slip_id.date_to', '<=', dend),
    #                                                             # ('slip_id.date_to', '<=', datetime.now().date())
    #                                                             ], order="date_to desc")
    #         for pr in prl_id:
    #             if pr.code == 'BASIC':
    #                 bs += pr.amount
    #             elif pr.code == 'DA':
    #                 da += pr.amount
    #         rec.basic_salary = round(bs)
    #         rec.da_salary = round(da)
    #         sum = 0
    #         proll = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                            ('slip_id.state', '=', 'done'),
    #                                                            ('code', '=', 'NET'),
    #                                                            ('slip_id.date_to', '>', rec.date_range.date_start)
    #                                                            ], order="date_to desc", limit=1)
    #         for pr in proll:
    #             rec.forecast_gross = round(pr.amount * 12)

    #         sum = 0
    #         dstart = rec.date_range.date_start
    #         dend = rec.date_range.date_end
    #         proll = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                            ('slip_id.state', '=', 'done'),
    #                                                            ('salary_rule_id.taxable_percentage', '>', 0),
    #                                                            ('slip_id.date_from', '>=', dstart),
    #                                                            ('slip_id.date_to', '<=', dend)], order="date_to desc")
    #         for i in proll:
    #             sum += i.taxable_amount
    #         rec.tax_salary_final = round(sum)
    #         # rec.income_after_rebate = rec.tax_salary_final - rec.net_allowed_rebate
    #         age = 0
    #         if rec.employee_id.birthday:
    #             age = ((datetime.now().date() - rec.employee_id.birthday).days) / 365

    #         # inc_tax_slab =  self.env['income.tax.slab'].sudo().search([('salary_from', '<=', rec.tax_salary_final),
    #         #                                                     ('salary_to', '>=', rec.tax_salary_final),
    #         #                                                     ('age_from', '<=', age),
    #         #                                                     ('age_to', '>=', age)],order ="create_date desc",
    #         #                                                    limit=1)
    #         # for tax_slab in inc_tax_slab:
    #         #     t1 = (tax_slab.tax_rate * (rec.tax_salary_final/100))
    #         #     t2 = (t1 * (1 + tax_slab.surcharge / 100))
    #         #     t3 = (t2 * (1 + tax_slab.cess / 100))
    #         #     rec.tax_payable = round(t3)
    #         # tax_salary_final = 0.00
    #         # if rec.tax_salary_final <= 250000.00:
    #         #     tax_salary_final = 0.00
    #         # elif rec.tax_salary_final > 250000.00 and rec.tax_salary_final <= 500000.00 :
    #         #     tax_salary_final = (rec.tax_salary_final - 250000.00) * 5/100
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 4/100)
    #         # elif rec.tax_salary_final > 500000.00 and rec.tax_salary_final <= 1000000.00:
    #         #     tax_salary_final = ((rec.tax_salary_final - 500000.00) * 20/100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final *4/100)
    #         #     tax_salary_final = tax_salary_final + 13000.00
    #         # elif rec.tax_salary_final > 1000000.00 and rec.tax_salary_final <= 5000000.00:
    #         #     tax_salary_final = ((rec.tax_salary_final - 1000000.00) * 30 / 100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 4/100)
    #         #     tax_salary_final = tax_salary_final + 13000.00 + 104000.00
    #         # elif rec.tax_salary_final > 5000000.00 and rec.tax_salary_final <= 10000000.00:
    #         #     tax_salary_final = ((rec.tax_salary_final - 5000000.00) * 30 / 100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 4/100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 10/100)
    #         #     tax_salary_final = tax_salary_final + 13000.00 + 104000.00 + 1248000.00
    #         # elif rec.tax_salary_final > 10000000.00:
    #         #     tax_salary_final = ((rec.tax_salary_final - 10000000.00) * 30 / 100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #         #     tax_salary_final = tax_salary_final + (tax_salary_final * 15 / 100)
    #         #     tax_salary_final = tax_salary_final + 13000.00 + 104000.00 + 1248000.00 + 1716000.00
    #         # rec.tax_payable = round(tax_salary_final)
    #         # if rec.tax_payable <= 0.00:
    #         #     rec.tax_payable_zero = False
    #         #     rec.tax_payable = 0.00
    #         # else:
    #         #     rec.tax_payable_zero = True
    #         rec.std_ded_ids.unlink()
    #         rec.exemption_ids.unlink()
    #         rec.rebate_ids.unlink()
    #         rec.slab_ids.unlink()
    #         ex_std_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'Std. Deduction'), ('it_rule', '=', 'mus10ale')], limit=1)
    #         my_investment = 0.00
    #         if ex_std_id:
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             if rec.tax_salary_final >= ex_std_id.rebate:
    #                 my_investment = ex_std_id.rebate
    #             else:
    #                 my_investment = rec.tax_salary_final

    #             if my_investment <= ex_std_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_std_id.rebate
    #             std_ded_ids = []
    #             std_ded_ids.append((0, 0, {
    #                 'std_ded_id': rec.id,
    #                 'it_rule': 'mus10ale',
    #                 'saving_master': ex_std_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.std_ded_ids = std_ded_ids
    #         ex_child_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'Child Education Allowance & Hostel Expenditure Allowance'),
    #              ('it_rule', '=', 'mus10ale')], limit=1)
    #         child_id = self.env['employee.relative'].sudo().search(
    #             [('employee_id', '=', rec.employee_id.id)])
    #         prl_id = self.env['hr.payslip.line'].sudo().search(
    #             [('slip_id.employee_id', '=', rec.employee_id.id), ('slip_id.state', '=', 'done'), ('code', '=', 'CCA'),
    #              ('slip_id.date_from', '>', rec.date_range.date_start),
    #              ('slip_id.date_to', '<', rec.date_range.date_end)], order="date_to desc")
    #         count = 0
    #         my_investment = 0.00
    #         my_allowed_rebate = 0.00
    #         pl_amount = 0.00
    #         count_paylines = 0.00
    #         if ex_child_id:
    #             for cc in child_id:
    #                 if cc.relate_type_name == 'Son' or cc.relate_type_name == 'Daughter':
    #                     count += 1
    #             for pl in prl_id:
    #                 count_paylines += 1
    #                 pl_amount += pl.amount
    #             if rec.employee_id.date_of_join and rec.date_range.date_start < rec.employee_id.date_of_join <= rec.date_range.date_end:
    #                 nm = ((rec.date_range.date_end - rec.employee_id.date_of_join).days) / 30
    #                 relative_sum = count * 100 * int(nm)
    #             else:
    #                 relative_sum = count * 100 * int(count_paylines)
    #             if pl_amount < relative_sum:
    #                 my_investment = pl_amount
    #             else:
    #                 my_investment = relative_sum

    #             if my_investment <= ex_child_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_child_id.rebate
    #             exemption_ids = []
    #             exemption_ids.append((0, 0, {
    #                 'exemption_id': rec.id,
    #                 'it_rule': 'mus10ale',
    #                 'saving_master': ex_child_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.exemption_ids = exemption_ids
    #         ex_hra_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'HRA Exemption'), ('it_rule', '=', 'mus10ale')], limit=1)
    #         prl_id = self.env['hr.payslip.line'].sudo().search(
    #             [('slip_id.employee_id', '=', rec.employee_id.id), ('slip_id.state', '=', 'done'), ('code', '=', 'HRA'),
    #              ('slip_id.date_from', '>', rec.date_range.date_start),
    #              ('slip_id.date_to', '<', rec.date_range.date_end)], order="date_to desc")
    #         sum_bs = 0.00
    #         sum_rent = 0.00
    #         sum_prl = 0.00
    #         sum = 0.00
    #         my_investment = 0.00
    #         my_allowed_rebate = 0.00
    #         sum_list = []
    #         for cc in prl_id:
    #             sum_prl += cc.amount
    #         if rec.employee_id.branch_id.city_id.metro == True:
    #             sum_bs = ((rec.basic_salary + rec.da_salary) * 50) / 100
    #         else:
    #             sum_bs = ((rec.basic_salary + rec.da_salary) * 40) / 100
    #         sum_rent = rec.rent_paid - (((rec.basic_salary + rec.da_salary) * 10) / 100)

    #         sum_list.append(sum_prl)
    #         sum_list.append(sum_bs)
    #         sum_list.append(sum_rent)
    #         # print('=============================================================================',sum_list)
    #         compare = 0.00
    #         compare_value = 10000000000000.00
    #         for i in sum_list:
    #             if compare_value > i and i > compare:
    #                 compare_value = i
    #         sum = compare_value
    #         if ex_hra_id:
    #             my_investment = sum
    #             if my_investment <= ex_hra_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_hra_id.rebate

    #             exemption_ids = []
    #             exemption_ids.append((0, 0, {
    #                 'exemption_id': rec.id,
    #                 'it_rule': 'mus10ale',
    #                 'saving_master': ex_hra_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.exemption_ids = exemption_ids
    #         ex_lunch_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'Lunch Subsidy Allowance'), ('it_rule', '=', 'mus10ale')], limit=1)
    #         reimbursement_id = self.env['reimbursement'].sudo().search(
    #             [('employee_id', '=', rec.employee_id.id), ('name', '=', 'lunch'),
    #              ('date_range.date_start', '>', rec.date_range.date_start),
    #              ('date_range.date_end', '<', rec.date_range.date_end), ('state', '=', 'approved')])
    #         sum = 0.00
    #         my_investment = 0.00
    #         my_allowed_rebate = 0.00
    #         for cc in reimbursement_id:
    #             sum += float(cc.lunch_tds_amt)
    #         if ex_lunch_id:
    #             my_investment = sum
    #             if my_investment <= ex_lunch_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_lunch_id.rebate
    #             exemption_ids = []
    #             exemption_ids.append((0, 0, {
    #                 'exemption_id': rec.id,
    #                 'it_rule': 'mus10ale',
    #                 'saving_master': ex_lunch_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.exemption_ids = exemption_ids
    #         ex_rebate_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'Revised Rebate under Section 87A (2019-20)'), ('it_rule', '=', 'section87a')],
    #             limit=1)
    #         my_investment = 0.00
    #         my_allowed_rebate = 0.00
    #         if ex_rebate_id:
    #             if rec.tax_salary_final <= 500000:
    #                 my_investment = ex_rebate_id.rebate
    #             else:
    #                 my_investment = 0.00
    #             if my_investment <= ex_rebate_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_rebate_id.rebate
    #             rebate_ids = []
    #             rebate_ids.append((0, 0, {
    #                 'rebate_id': rec.id,
    #                 'it_rule': ex_rebate_id.it_rule,
    #                 'saving_master': ex_rebate_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.rebate_ids = rebate_ids
    #         ex_80_c_id = self.env['saving.master'].sudo().search(
    #             [('saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution'),
    #              ('it_rule', '=', '80_c')], limit=1)
    #         prl_80c_id = self.env['hr.payslip.line'].sudo().search(
    #             [('slip_id.employee_id', '=', rec.employee_id.id),
    #              ('slip_id.state', '=', 'done'),
    #              ('salary_rule_id.pf_register', '=', True),
    #              ('slip_id.date_from', '>', rec.date_range.date_start),
    #              ('slip_id.date_to', '<', rec.date_range.date_end)], order="date_to desc")
    #         sum = 0
    #         for sr in prl_80c_id:
    #             if sr.code == 'CEPF' or sr.code == 'VCPF':
    #                 sum += sr.amount
    #         my_investment = 0.00
    #         my_allowed_rebate = 0.00
    #         if ex_80_c_id:
    #             my_investment = sum
    #             if my_investment <= ex_80_c_id.rebate:
    #                 my_allowed_rebate = my_investment
    #             else:
    #                 my_allowed_rebate = ex_80_c_id.rebate
    #             slab_ids = []
    #             slab_ids.append((0, 0, {
    #                 'slab_id': rec.id,
    #                 'it_rule': '80_c',
    #                 'saving_master': ex_80_c_id.id,
    #                 'investment': my_investment,
    #                 'allowed_rebate': my_allowed_rebate,
    #             }))
    #             rec.slab_ids = slab_ids
    #         exempt_am = 0.00
    #         std_am = 0.00
    #         sum_pt = 0.00
    #         for std in rec.std_ded_ids:
    #             std_am += std.allowed_rebate
    #         for ex in rec.exemption_ids:
    #             exempt_am += ex.allowed_rebate
    #         pr_pt_id = self.env['hr.payslip.line'].sudo().search(
    #             [('slip_id.employee_id', '=', rec.employee_id.id), ('slip_id.state', '=', 'done'), ('code', '=', 'PTD'),
    #              ('slip_id.date_from', '>', rec.date_range.date_start),
    #              ('slip_id.date_to', '<', rec.date_range.date_end)], order="date_to desc")
    #         for pt in pr_pt_id:
    #             sum_pt += pt.amount
    #         if (rec.tax_salary_final + rec.previous_employer_income - exempt_am) > 0.00:
    #             rec.income_after_exemption = round(rec.tax_salary_final + rec.previous_employer_income - exempt_am)
    #         else:
    #             rec.income_after_exemption = 0.00
    #         if rec.income_after_exemption - std_am > 0.00:
    #             rec.income_after_std_ded = round(rec.income_after_exemption - std_am)
    #         else:
    #             rec.income_after_std_ded = 0.00
    #         if rec.income_after_std_ded - sum_pt > 0.00:
    #             rec.income_after_pro_tax = round(rec.income_after_std_ded - sum_pt)
    #         else:
    #             rec.income_after_pro_tax = 0.00
    #         if (rec.income_after_pro_tax - rec.total_tds_paid - (
    #                 rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg + rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr)) > 0.00:
    #             rec.taxable_income = round(rec.income_after_pro_tax - rec.total_tds_paid - (
    #                         rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg + rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr))
    #         else:
    #             rec.taxable_income = 0.00

    #         tax_salary_final = 0.00
    #         if rec.taxable_income <= 250000.00:
    #             tax_salary_final = 0.00
    #         elif rec.taxable_income > 250000.00 and rec.taxable_income <= 500000.00:
    #             tax_salary_final = (rec.taxable_income - 250000.00) * 5 / 100
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #         elif rec.taxable_income > 500000.00 and rec.taxable_income <= 1000000.00:
    #             tax_salary_final = ((rec.taxable_income - 500000.00) * 20 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #             tax_salary_final = tax_salary_final + 13000.00
    #         elif rec.taxable_income > 1000000.00 and rec.taxable_income <= 5000000.00:
    #             tax_salary_final = ((rec.taxable_income - 1000000.00) * 30 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #             tax_salary_final = tax_salary_final + 13000.00 + 104000.00
    #         elif rec.taxable_income > 5000000.00 and rec.taxable_income <= 10000000.00:
    #             tax_salary_final = ((rec.taxable_income - 5000000.00) * 30 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 10 / 100)
    #             tax_salary_final = tax_salary_final + 13000.00 + 104000.00 + 1248000.00
    #         elif rec.taxable_income > 10000000.00:
    #             tax_salary_final = ((rec.taxable_income - 10000000.00) * 30 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 4 / 100)
    #             tax_salary_final = tax_salary_final + (tax_salary_final * 15 / 100)
    #             tax_salary_final = tax_salary_final + 13000.00 + 104000.00 + 1248000.00 + 1716000.00
    #         rec.tax_payable = round(tax_salary_final)
    #         if rec.tax_payable <= 0.00:
    #             rec.tax_payable_zero = False
    #             rec.tax_payable = 0.00
    #         else:
    #             rec.tax_payable_zero = True
    #         sum_rbt = 0.0
    #         for rbt in rec.rebate_ids:
    #             sum_rbt += rbt.allowed_rebate

    #         if rec.tax_payable >= sum_rbt:
    #             rec.tax_payable_after_rebate = rec.tax_payable - sum_rbt
    #             rec.rebate_received = sum_rbt
    #         else:
    #             rec.tax_payable_after_rebate = 0.00
    #             rec.rebate_received = rec.tax_payable
    #         rec.tax_computed_bool = True

    #         for lines in rec.tax_payment_ids:
    #             if lines.paid == False:
    #                 lines.unlink()
    #         edate = rec.date_range.date_end
    #         date = datetime.now().date().replace(day=1)+ relativedelta(months=1)
    #         month_cal = ((edate - date).days)/30
    #         if month_cal > 0:
    #             amount = (rec.pending_tax)/month_cal
    #             for i in range(int(month_cal)):
    #                 self.env['tax.payment'].create({
    #                     'tax_payment_id': rec.id,
    #                     'date': date,
    #                     'amount': amount,
    #                 })
    #                 date = date + relativedelta(months=1)
    #     return True





    def send_reminder_action_button_cron(self):
        id_dec = self.env['hr.declaration'].search([('state', 'in', ['draft','to_approve','approved'])])
        for rec in id_dec:
            template_id = rec.env.ref('tds.email_template_tds').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
