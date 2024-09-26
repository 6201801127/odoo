from odoo import api, fields, models, tools
from datetime import datetime, date, timedelta


class YearlyHrDeclaration(models.Model):
    _name = "yearly_hr_declaration"
    _description = "Yearly HR Declaration Details"

    def _default_financial_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal

    employee_id = fields.Many2one('hr.employee', string='Employee')
    job_name = fields.Char(related='employee_id.job_id.name', string='Designation')
    department_name = fields.Char(related='employee_id.department_id.name', string='Department')
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num')
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    state = fields.Selection([('s', 'Submitted'), ('c', 'Approved'), ('ns', 'Not Submitted')
                              ], required=True, string='Status', track_visibility='always')

    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            if rec.employee_id.pan_no:

                rec.pan_number = rec.employee_id.pan_no

    def action_yearly_tds(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        employees = self.env['hr.employee'].sudo().search([])
        view_id = self.env.ref('tds.yearly_hr_declaration_view_tree').id
        rc = {
            'name': 'Yearly IT Declaration',
            'type': 'ir.actions.act_window',
            'res_model': 'yearly_hr_declaration',
            'view_id': view_id,
            'view_mode': 'tree',
            'view_type': 'form',
            # 'res_id': hr_dec.id,
            'target': 'self',
        }
        if employees:
            for emp in employees:
                contract = self.env['hr.contract'].sudo().search([('employee_id', '=', emp.id)], order='id desc',
                                                                 limit=1)
                if contract:
                    ctc = contract.wage
                    yearly_ctc = ctc * 12
                    if yearly_ctc >= 500000:
                        yearly_dec = self.env['yearly_hr_declaration'].sudo().search(
                            [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)], limit=1)
                        if yearly_dec:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)])
                            if hr_declaration:
                                yearly_dec.write(
                                    {'state': 's'}) if hr_declaration.state != 'approved' else yearly_dec.write(
                                    {'state': 'c'})
                            else:
                                yearly_dec.write({'state': 'ns'})
                        else:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)])
                            if hr_declaration:
                                self.env['yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id, 'date_range': current_fiscal.id,
                                     'state': 's'}) if hr_declaration.state != 'approved' else self.env[
                                    'yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id,
                                     'date_range': current_fiscal.id,
                                     'state': 'c'})
                            else:
                                self.env['yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id,
                                     'date_range': current_fiscal.id,
                                     'state': 'ns'})

        return rc

    def yearly_hr_declaration(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        employees = self.env['hr.employee'].sudo().search([])
        if employees:
            for emp in employees:
                contract = self.env['hr.contract'].sudo().search([('employee_id', '=', emp.id), ('state', '=', 'open')])
                if contract:
                    ctc = contract.wage
                    yearly_ctc = ctc * 12
                    if yearly_ctc > 250000:
                        yearly_dec = self.env['yearly_hr_declaration'].sudo().search(
                            [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)])
                        if yearly_dec:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)])
                            if hr_declaration:
                                yearly_dec.write(
                                    {'state': 's'}) if hr_declaration.state != 'approved' else yearly_dec.write(
                                    {'state': 'c'})
                            else:
                                yearly_dec.write({'state': 'ns'})
                        else:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp.id), ('date_range', '=', current_fiscal.id)])
                            if hr_declaration:
                                self.env['yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id, 'date_range': current_fiscal.id,
                                     'state': 's'}) if hr_declaration.state != 'approved' else self.env[
                                    'yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id,
                                     'date_range': current_fiscal.id,
                                     'state': 'c'})
                            else:
                                self.env['yearly_hr_declaration'].sudo().create(
                                    {'employee_id': emp.id,
                                     'date_range': current_fiscal.id,
                                     'state': 'ns'})

    @api.model
    def method_calculate_tax(self, amount):
        if 250000 < amount <= 500000:
            tds_amount = amount - 250000
            tds = tds_amount * 5 / 100
            after_rebate = tds - 12500 if amount < 500000 else 0
            if after_rebate <= 0:
                return 0
            else:
                cess = after_rebate * 4 / 100
                return after_rebate + cess
        elif 500000 < amount <= 1000000:
            tds_above5 = amount - 500000
            tds_above5percentage = tds_above5 * 20 / 100
            tds_below5percentage = 250000 * 5 / 100
            tds = tds_above5percentage + tds_below5percentage
            cess = tds * 4 / 100
            return tds + cess
        elif amount > 1000000:
            tds_above10 = amount - 1000000
            tds_above10percentage = tds_above10 * 30 / 100
            tds_above5percentage = 500000 * 20 / 100
            tds_below5percentage = 250000 * 5 / 100
            tds = tds_above10percentage + tds_above5percentage + tds_below5percentage
            if amount >= 5000000:
                subcharge = tds * 10 / 100
            else:
                subcharge = 0
            cess = tds * 4 / 100
            return tds + cess + subcharge
        else:
            return 0

    def view_yearly_hr_declaration(self):
        pass
        # for rec in self:
        #     # yearly_dec = self.env['yearly_hr_declaration'].sudo().search([('employee_id','=',rec.employee_id.id),('date_range','=',rec.date_range.id)])
        #     hr_dec = self.env['hr.declaration'].sudo().search(
        #         [('employee_id', '=', rec.employee_id.id), ('date_range', '=', rec.date_range.id)])
        #     view_id = self.env.ref('tds.hr_declaration_bifurcation_view_form').id
        #     if hr_dec:
        #         rc = {
        #             'name': 'IT Declaration',
        #             'type': 'ir.actions.act_window',
        #             'res_model': 'hr.declaration',
        #             'view_id': view_id,
        #             'view_mode': 'form',
        #             'view_type': 'form',
        #             'res_id': hr_dec.id,
        #             'target': 'self',
        #         }
        #         return rc
        #     else:
        #         month_dict = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
        #         # month_dict={3:2}
        #         currentMonth = datetime.now().month
        #         currentyear = datetime.now().year
        #         month = month_dict.get(currentMonth)
        #         c = 0
        #
        #         financial_year = rec.date_range
        #
        #         gross = 0.00
        #         total_gross = 0.00
        #         bs = 0.00
        #         house_rent = 0.00
        #         total_basic = 0.00
        #         total_conveyance = 0.00
        #         total_hra = 0.00
        #         total_pb = 0.00
        #         total_cb = 0.00
        #         lwop = 0.00
        #         ptd = 0.00
        #         tds = 0.00
        #         total_after_lwop = 0.00
        #         professional_tax = 0.00
        #         total_after_pt_sd = 0.00
        #         forcast_basic = 0.00
        #         forcast_hra = 0.00
        #         other_allowance = 0.00
        #         tax_payable = 0.00
        #         epf = 0.00
        #
        #         # Fetch all the payslips of the current financial year
        #         payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),
        #                                                         ('state', '=', 'done'),
        #                                                         ('date_from', '>=', financial_year.date_start),
        #                                                         ('date_to', '<=', financial_year.date_stop),
        #                                                         ])
        #         prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
        #                                                             ('slip_id.state', '=', 'done'),
        #                                                             ('slip_id.date_from', '>=',
        #                                                              financial_year.date_start),
        #                                                             ('slip_id.date_to', '<=', financial_year.date_stop),
        #                                                             ])
        #
        #         # Dynamically set remaining month till end of financial year
        #
        #         j_date = rec.employee_id.date_of_joining
        #         if j_date >= financial_year.date_start and j_date <= financial_year.date_stop:
        #             remain_months = (financial_year.date_stop.year - j_date.year) * 12 + (
        #                     financial_year.date_stop.month - j_date.month)
        #             month_limit = int(remain_months) + 1
        #         else:
        #             month_limit = 12
        #
        #         blk_date_lst = []
        #         counter = 0
        #         last_counter = 0
        #         block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id', '=', rec.employee_id.id)])
        #         for blk_payslp in block_payslips:
        #             blk_year = int(blk_payslp.year)
        #             blk_month = int(blk_payslp.month)
        #             blk_date = date(blk_year, blk_month, 1)
        #             blk_date_lst.append(blk_date)
        #         for dates in blk_date_lst:
        #             if financial_year.date_start <= dates <= financial_year.date_stop:
        #                 chk_payslip = payslip.filtered(lambda x: x.date_from <= dates <= x.date_to)
        #                 if not chk_payslip:
        #                     counter += 1
        #         if rec.employee_id.last_working_day:
        #             if financial_year.date_start <= rec.employee_id.last_working_day <= financial_year.date_stop and rec.employee_id.active == False:
        #                 last_counter = (
        #                                            financial_year.date_stop.year - rec.employee_id.last_working_day.year) * 12 + financial_year.date_stop.month - rec.employee_id.last_working_day.month
        #
        #         # New code for remaining month by Abhijit swain on 15 may 2022
        #         # print('last_counter==========',last_counter )
        #
        #         # remaining_month = month_limit - len(payslip) - counter - last_counter
        #         remaining_month = month_limit - len(
        #             payslip) - counter - last_counter if date.today() < financial_year.date_stop else 0
        #
        #         # print('month is ===============',int(month))
        #
        #         # calculate the gross salary of the employee
        #         for pr in prl_id:
        #             if pr.code == 'GROSS':
        #                 gross += pr.amount
        #             if pr.code == 'BASIC':
        #                 bs += pr.amount
        #             if pr.code == 'LWOP':
        #                 lwop += pr.amount
        #             if pr.code == 'PTD':
        #                 ptd += pr.amount
        #             if pr.code == 'TDS':
        #                 tds += pr.amount
        #             if pr.code == 'HRAMN':
        #                 house_rent += pr.amount
        #             if pr.code == 'EEPF':
        #                 epf += pr.amount
        #             # if pr.code == 'CMT':
        #             #     self_insurance += pr.amount
        #         # insurance_self = self.env['hr.payslip.line'].sudo().search(
        #         #     [('slip_id.employee_id', '=', rec.employee_id.id),
        #         #      ('slip_id.date_from', '>=', rec.date_range.date_start),
        #         #      ('slip_id.date_to', '<=', rec.date_range.date_stop),
        #         #      ])
        #         # for cmt in insurance_self:
        #         #     if cmt.code == 'CMT':
        #         #         self_insurance += cmt.amount
        #
        #         # check if any variable allowance is present for the current month
        #         alw_rec_start = self.env['allowance_allocation_master'].sudo().search(
        #             [('month', 'not in', [1, 2, 3]), ('year', '=', str(rec.date_range.date_start.year)),
        #              ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
        #
        #         alw_rec_end = self.env['allowance_allocation_master'].sudo().search(
        #             [('month', 'in', [1, 2, 3]), ('year', '=', str(rec.date_range.date_stop.year)),
        #              ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
        #
        #         c = 0
        #         start_c = 0
        #         end_c = 0
        #         if alw_rec_start:
        #             for alw in alw_rec_start:
        #                 start_c += alw.amount
        #         else:
        #             start_c = 0
        #
        #         if alw_rec_end:
        #             for alw in alw_rec_end:
        #                 end_c += alw.amount
        #         else:
        #             end_c = 0
        #
        #         c = start_c + end_c
        #
        #         # calculate the forcasting gross
        #
        #         contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
        #                                                          ('state', '=', 'open')
        #                                                          ], limit=1)
        #
        #         total_basic = contrct.current_basic
        #         total_hra = contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100
        #         total_conveyance = contrct.current_basic * contrct.conveyance / 100
        #         total_pb = contrct.productivity
        #         total_cb = contrct.commitment
        #         total_bonus = contrct.bonus
        #         forcast_basic = bs + (contrct.current_basic * remaining_month)
        #         sum_prl = 0.00
        #
        #         for record in prl_id:
        #             if record.code == 'HRAMN':
        #                 sum_prl += record.amount
        #         # forcast_hra = total_hra * int(month) + house_rent if len(payslip) < month_limit else house_rent
        #
        #         forcast_hra = (sum_prl + (
        #                 contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100) * remaining_month)
        #         total_gross = (
        #                                   total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus) * remaining_month + gross + c
        #
        #         other_allowance = total_gross - (forcast_hra + forcast_basic)
        #
        #         # Total after excluding the lwop
        #
        #         total_after_lwop = 0 if (total_gross - lwop) < 0 else (total_gross - lwop)
        #
        #         # print('total after lwop==========',total_after_lwop)
        #
        #         # calculate the professional tax
        #         pt_gross = total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus
        #         # if pt_gross * 12 > 300000:
        #         #     pt = 200 * (int(month) - 1) + 300
        #         # elif 160000 < pt_gross * 12 <= 300000:
        #         #     pt = 125 * int(month)
        #         # else:
        #         #     pt = 0
        #         if pt_gross * 12 >= 300000:
        #             extra_amount = 0 if remaining_month == 0 else 100
        #             pt = ptd + (200 * remaining_month) + extra_amount
        #         elif pt_gross * 12 >= 160000 and pt_gross * 12 < 300000:
        #             pt = ptd + (125 * remaining_month)
        #         else:
        #             pt = 0
        #
        #         professional_tax = pt
        #
        #         print('professional tax=========', professional_tax)
        #
        #         # Employee Epf
        #         if contrct.enable_epf == 'yes':
        #             if contrct.pf_deduction == 'other':
        #                 if contrct.epf_percent:
        #                     employee_epf = epf + (contrct.current_basic * contrct.epf_percent / 100) * remaining_month
        #                 else:
        #                     employee_epf = epf + 0
        #             elif contrct.pf_deduction == 'avail1800' and contrct.current_basic >= 15000:
        #                 employee_epf = epf + (1800 * remaining_month)
        #             else:
        #                 # employee_epf = epf + (contrct.current_basic * 12 / 100) * remaining_month
        #                 # if contrct.pf_deduction == 'basicper':
        #                 employee_epf = epf + (contrct.current_basic * 12 / 100) * remaining_month
        #         else:
        #             employee_epf = 0
        #         print('employee_epf===========', employee_epf)
        #         # employee_epf = epf + (contrct.current_basic * 12 / 100) * int(month) if len(
        #         #     payslip) < month_limit else epf
        #
        #         # Insurance Dependent
        #         health_dependant = self.env['health_insurance_dependant'].sudo().search(
        #             [('employee_id', '=', rec.employee_id.id),
        #              ('date_range.date_start', '<=', rec.date_range.date_start),
        #              ('date_range.date_stop', '>=', rec.date_range.date_stop), ('state', '=', 'approved')])
        #         hid_amount = 0
        #         if health_dependant:
        #             hid_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
        #         # for record in health_dependant:
        #         #     if record:
        #         #         for res in record.family_details_ids:
        #         #             hid_amount += res.insurance_amount
        #
        #         # Total after excluding professional tax and standard deduction 50,000
        #         total_deduction = employee_epf + hid_amount
        #         total_after_pt_sd = 0 if ((total_after_lwop - (professional_tax)) - 50000) < 0 else (
        #                 (total_after_lwop - (professional_tax)) - 50000)
        #         a = total_after_pt_sd - total_deduction
        #         print('a==========', a)
        #         if (a % 10) >= 5:
        #             z = 10 - (a % 10)
        #             print(a + z)
        #             tax_amount = a + z
        #         else:
        #             print(a - (a % 10))
        #             tax_amount = a - (a % 10)
        #
        #         taxable_income = tax_amount
        #         # calculate tax based on formula
        #         temp_tax_payable = 0.00
        #         if taxable_income > 250000 and taxable_income <= 500000:
        #             tds_amount = taxable_income - 250000
        #             tax_slab = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '<=', taxable_income),
        #                  ('salary_to', '>=', taxable_income), ('tax_regime', '=', 'old_regime')], limit=1)
        #             temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
        #         elif taxable_income > 500000 and taxable_income <= 1000000:
        #             tds_above5 = taxable_income - 500000
        #             tax_slab = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '<=', taxable_income),
        #                  ('salary_to', '>=', taxable_income), ('tax_regime', '=', 'old_regime')], limit=1)
        #             tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
        #             tax_slab_1 = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 250001),
        #                  ('salary_to', '<=', 5000000), ('tax_regime', '=', 'old_regime')], limit=1)
        #             tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
        #             temp_tax_payable = tds_above5percentage + tds_below5percentage
        #         elif taxable_income > 1000000:
        #             tds_above10 = taxable_income - 1000000
        #             tax_slab = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '<=', taxable_income),
        #                  ('salary_to', '>=', taxable_income), ('tax_regime', '=', 'old_regime')], limit=1)
        #             tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
        #             tax_slab_1 = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 500001),
        #                  ('salary_to', '<=', 1000000), ('tax_regime', '=', 'old_regime')], limit=1)
        #             tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
        #             tax_slab_2 = self.env['tax_slab'].sudo().search(
        #                 [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 250001),
        #                  ('salary_to', '<=', 5000000), ('tax_regime', '=', 'old_regime')], limit=1)
        #             tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
        #             temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage
        #
        #         tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0
        #
        #         rebate = tax_payable if taxable_income < 500000 and tax_payable > 0 else 0
        #         temp_net_tax_payable = tax_payable - rebate
        #         net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
        #         tax_slab_rec = self.env['tax_slab'].sudo().search(
        #             [('date_range', '=', rec.date_range.id), ('salary_from', '<=', taxable_income),
        #              ('salary_to', '>=', taxable_income), ('tax_regime', '=', 'old_regime')], limit=1)
        #         additional_sub_chrg = net_tax_payable * tax_slab_rec.surcharge / 100
        #         additional_edu_cess = net_tax_payable * tax_slab_rec.cess / 100 if net_tax_payable > 0 else 0
        #         var_tax_payable = round(net_tax_payable + additional_sub_chrg + additional_edu_cess)
        #         if (var_tax_payable % 10) >= 5:
        #             remaining = 10 - (var_tax_payable % 10)
        #             tax_to_be_paid = var_tax_payable + remaining
        #         else:
        #             tax_to_be_paid = var_tax_payable - (var_tax_payable % 10)
        #         total_tax_payable = tax_to_be_paid
        #         tax_recovered = tds
        #         temp_balance_tax_payable = total_tax_payable - tax_recovered
        #         balance_tax_payable = temp_balance_tax_payable
        #
        #         return {
        #             'name': 'IT Declaration',
        #             'view_type': 'form',
        #             'view_mode': 'form',
        #             'res_model': 'yearly_notsubmitted_declaration',
        #             'view_id': self.env.ref('tds.yearly_notsubmitted_declaration_view_form').id,
        #             # 'res_id': rec.id,
        #             'type': 'ir.actions.act_window',
        #             'target': 'self',
        #             'context': {'employee_id': rec.employee_id.id, 'basic': forcast_basic, 'hra': forcast_hra,
        #                         'gross': total_gross, 'oalw': other_allowance, 'lwop': lwop,
        #                         'afterlwop': total_after_lwop, 'professional_tax': professional_tax,
        #                         'total_after_pt_sd': total_after_pt_sd,
        #                         'tax_payable': tax_payable, 'rebate': rebate, 'net_tax_payable': net_tax_payable,
        #                         'additional_sub_chrg': additional_sub_chrg,
        #                         'additional_edu_cess': additional_edu_cess, 'total_tax_payable': total_tax_payable,
        #                         'tax_recovered': tax_recovered, 'balance_tax_payable': balance_tax_payable,
        #                         'employee_epf': employee_epf, 'self_insurance': 0,
        #                         'hid_amount': hid_amount, 'total_deduction': total_deduction,
        #                         'taxable_income': taxable_income},
        #         }
        #
        #         # month_dict = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
        #         # # month_dict={3:2}
        #         # currentMonth = datetime.now().month
        #         # currentyear = datetime.now().year
        #         # month = month_dict.get(currentMonth)
        #         # c = 0
        #
        #         # financial_year = rec.date_range
        #
        #         # gross = 0.00
        #         # total_gross = 0.00
        #         # bs = 0.00
        #         # house_rent = 0.00
        #         # total_basic = 0.00
        #         # total_conveyance = 0.00
        #         # total_hra = 0.00
        #         # total_pb = 0.00
        #         # total_cb = 0.00
        #         # lwop = 0.00
        #         # ptd = 0.00
        #         # tds = 0.00
        #         # total_after_lwop = 0.00
        #         # professional_tax = 0.00
        #         # total_after_pt_sd = 0.00
        #         # forcast_basic = 0.00
        #         # forcast_hra = 0.00
        #         # other_allowance = 0.00
        #         # tax_payable = 0.00
        #         # epf = 0.00
        #
        #         # # Fetch all the payslips of the current financial year
        #         # payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),
        #         #                                                 ('state', '=', 'done'),
        #         #                                                 ('date_from', '>=', financial_year.date_start),
        #         #                                                 ('date_to', '<=', financial_year.date_stop),
        #         #                                                 ])
        #         # prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
        #         #                                                     ('slip_id.state', '=', 'done'),
        #         #                                                     ('slip_id.date_from', '>=',
        #         #                                                      financial_year.date_start),
        #         #                                                     ('slip_id.date_to', '<=', financial_year.date_stop),
        #         #                                                     ])
        #
        #         # # Dynamically set remaining month till end of financial year
        #         # j_date = rec.employee_id.date_of_joining
        #         # if financial_year.date_start <= j_date <= financial_year.date_stop:
        #         #     remain_months = (financial_year.date_stop.year - j_date.year) * 12 + (
        #         #             financial_year.date_stop.month - j_date.month)
        #         #     month_limit = int(remain_months) + 1
        #         # else:
        #         #     month_limit = 12
        #         # # print('month is ===============',int(month))
        #         # remaining_month = month_limit - len(payslip)
        #
        #         # # calculate the gross salary of the employee
        #         # for pr in prl_id:
        #         #     if pr.code == 'GROSS':
        #         #         gross += pr.amount
        #         #     if pr.code == 'BASIC':
        #         #         bs += pr.amount
        #         #     if pr.code == 'LWOP':
        #         #         lwop += pr.amount
        #         #     # if pr.code == 'PTD':
        #         #     #     ptd += pr.amount
        #         #     if pr.code == 'TDS':
        #         #         tds += pr.amount
        #         #     if pr.code == 'HRAMN':
        #         #         house_rent += pr.amount
        #         #     # if pr.code == 'EEPF':
        #         #     #     epf += pr.amount
        #         #     # if pr.code == 'CMT':
        #         #     #     self_insurance += pr.amount
        #         # # insurance_self = self.env['hr.payslip.line'].sudo().search(
        #         # #     [('slip_id.employee_id', '=', rec.employee_id.id),
        #         # #      ('slip_id.date_from', '>=', rec.date_range.date_start),
        #         # #      ('slip_id.date_to', '<=', rec.date_range.date_stop),
        #         # #      ])
        #         # # for cmt in insurance_self:
        #         # #     if cmt.code == 'CMT':
        #         # #         self_insurance += cmt.amount
        #
        #         # # check if any variable allowance is present for the current month
        #         # # alw_rec = self.env['allowance_allocation_master'].sudo().search(
        #         # #     [('month', '=', str(currentMonth)), ('year', '=', str(currentyear)),
        #         # #      ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
        #
        #         # # Calculate the total of all the variable allowance
        #         # # if alw_rec:
        #         # #     for alw in alw_rec:
        #         # #         c += alw.amount
        #         # # else:
        #         # #     c = 0
        #         # alw_rec_start = self.env['allowance_allocation_master'].sudo().search(
        #         #     [('month', 'not in', [1,2,3]), ('year', '=', str(rec.date_range.date_start.year)),
        #         #     ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
        #
        #         # alw_rec_end = self.env['allowance_allocation_master'].sudo().search(
        #         #     [('month', 'in', [1,2,3]), ('year', '=', str(rec.date_range.date_stop.year)),
        #         #     ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
        #
        #         # c = 0
        #         # start_c = 0
        #         # end_c = 0
        #         # if alw_rec_start:
        #         #     for alw in alw_rec_start:
        #         #         start_c += alw.amount
        #         # else:
        #         #     start_c = 0
        #
        #         # if alw_rec_end:
        #         #     for alw in alw_rec_end:
        #         #         end_c += alw.amount
        #         # else:
        #         #     end_c = 0
        #
        #         # c = start_c + end_c
        #
        #         # # print('length of prl id is=========',len(payslip))
        #         # # print('month limit of prl id is=========',int(month_limit))
        #
        #         # # calculate the forcasting gross
        #
        #         # contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
        #         #                                                  ('state', '=', 'open')
        #         #                                                  ], limit=1)
        #
        #         # total_basic = contrct.current_basic
        #         # total_hra = contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100
        #         # total_conveyance = contrct.current_basic * contrct.conveyance / 100
        #         # total_pb = contrct.productivity
        #         # total_cb = contrct.commitment
        #         # total_bonus = contrct.bonus
        #         # # forcast_basic = total_basic * int(month) + bs if len(payslip) < month_limit else bs
        #
        #         # forcast_basic = bs + (contrct.current_basic * remaining_month)
        #         # sum_prl = 0.00
        #
        #         # for record in prl_id:
        #         #     if record.code == 'HRAMN':
        #         #         sum_prl += record.amount
        #         # # forcast_hra = total_hra * int(month) + house_rent if len(payslip) < month_limit else house_rent
        #
        #         # forcast_hra = (sum_prl + (
        #         #         contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100) * remaining_month)
        #
        #         # total_gross = (total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus) * remaining_month + gross + c
        #         # other_allowance = total_gross - (forcast_hra + forcast_basic)
        #
        #         # # Total after excluding the lwop
        #
        #         # total_after_lwop = 0 if (total_gross - lwop) < 0 else (total_gross - lwop)
        #         # # total_after_lwop = total_gross
        #
        #         # # print('total after lwop==========',total_after_lwop)
        #
        #         # # calculate the professional tax
        #         # # pt_gross = total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus
        #         # # if pt_gross * 12 > 300000:
        #         # #     pt = 200 * (int(month) - 1) + 300
        #         # # elif 160000 < pt_gross * 12 <= 300000:
        #         # #     pt = 125 * int(month)
        #         # # else:
        #         # #     pt = 0
        #
        #         # professional_tax = 0
        #         # employee_epf = 0
        #
        #         # # Employee Epf
        #         # # employee_epf = epf + (contrct.current_basic * 12 / 100) * int(month) if len(
        #         # #     payslip) < month_limit else epf
        #
        #         # # Insurance Dependent
        #         # # health_dependant = self.env['health_insurance_dependant'].sudo().search(
        #         # #     [('employee_id', '=', rec.employee_id.id),
        #         # #      ('date_range.date_start', '<=', rec.date_range.date_start),
        #         # #      ('date_range.date_stop', '>=', rec.date_range.date_stop),('state', '=', 'approved')])
        #         # hid_amount = 0
        #         # # for record in health_dependant:
        #         # #     if record:
        #         # #         for res in record.family_details_ids:
        #         # #             hid_amount += res.insurance_amount
        #
        #         # # Total after excluding professional tax and standard deduction 50,000
        #         # total_deduction = employee_epf +  hid_amount
        #         # # total_after_pt_sd = 0 if ((total_after_lwop - (professional_tax)) - 50000) < 0 else (
        #         # #         (total_after_lwop - (professional_tax)) - 50000)
        #         # total_after_pt_sd = total_after_lwop
        #         # a = total_after_pt_sd - total_deduction
        #         # print('a==========', a)
        #         # if (a % 10) >= 5:
        #         #     z = 10 - (a % 10)
        #         #     print(a + z)
        #         #     tax_amount = a + z
        #         # else:
        #         #     print(a - (a % 10))
        #         #     tax_amount = a - (a % 10)
        #
        #         # taxable_income = tax_amount
        #         # # calculate tax based on formula
        #         # temp_tax_payable = 0.00
        #         # # if taxable_income > 250000 and taxable_income <= 500000:
        #         # #     tds_amount = taxable_income - 250000
        #         # #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income)],limit=1)
        #         # #     temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
        #         # # elif taxable_income > 500000 and taxable_income <= 1000000:
        #         # #     tds_above5 = taxable_income - 500000
        #         # #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income)],limit=1)
        #         # #     tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
        #         # #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000)],limit=1)
        #         # #     tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
        #         # #     temp_tax_payable = tds_above5percentage + tds_below5percentage
        #         # # elif taxable_income > 1000000:
        #         # #     tds_above10 = taxable_income - 1000000
        #         # #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income)],limit=1)
        #         # #     tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
        #         # #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',500001),('salary_to','<=',1000000)],limit=1)
        #         # #     tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
        #         # #     tax_slab_2 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000)],limit=1)
        #         # #     tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
        #         # #     temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage
        #         # if taxable_income > 250000 and taxable_income <= 500000:
        #         #     tds_amount = taxable_income - 250000
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
        #         # elif taxable_income > 500000 and taxable_income <= 750000:
        #
        #         #     tds_above5 = taxable_income - 500000
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
        #         #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
        #         #     temp_tax_payable = tds_above5percentage + tds_below5percentage
        #         # elif taxable_income > 750000 and taxable_income <= 1000000:
        #
        #         #     tds_above75 = taxable_income - 750000
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above75percentage = tds_above75 * tax_slab.tax_rate / 100
        #         #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',500001),('salary_to','<=',750000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above5percentage = 250000 * tax_slab_1.tax_rate / 100
        #         #     tax_slab_2 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
        #         #     temp_tax_payable = tds_above75percentage + tds_above5percentage + tds_below5percentage
        #
        #         # elif taxable_income > 1000000 and taxable_income <= 1250000:
        #         #     tds_above10 = taxable_income - 1000000
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
        #
        #         #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',750001),('salary_to','<=',1000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above75percentage = 250000 * tax_slab_1.tax_rate / 100
        #
        #         #     tax_slab_2 = self.env['tax_slab'].sudo().search([('salary_from','>=',500001),('salary_to','<=',750000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above5percentage = 250000 * tax_slab_2.tax_rate / 100
        #
        #         #     tax_slab_3 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_below5percentage = 250000 * tax_slab_3.tax_rate / 100
        #
        #         #     temp_tax_payable = tds_above10percentage + tds_above75percentage +tds_above5percentage + tds_below5percentage
        #
        #         # elif taxable_income > 1250000 and taxable_income <= 1500000:
        #         #     tds_above12 = taxable_income - 1250000
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above12percentage = tds_above12 * tax_slab.tax_rate / 100
        #         #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',1000001),('salary_to','<=',1250000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above10percentage = 250000 * tax_slab_1.tax_rate / 100
        #         #     tax_slab_2 = self.env['tax_slab'].sudo().search([('salary_from','>=',750001),('salary_to','<=',1000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above75percentage = 250000 * tax_slab_2.tax_rate / 100
        #         #     tax_slab_3 = self.env['tax_slab'].sudo().search([('salary_from','>=',500001),('salary_to','<=',750000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above5percentage = 250000 * tax_slab_3.tax_rate / 100
        #         #     tax_slab_4 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',500001),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_below5percentage = 250000 * tax_slab_4.tax_rate / 100
        #         #     temp_tax_payable = tds_above12percentage + tds_above10percentage + tds_above75percentage +tds_above5percentage + tds_below5percentage
        #
        #         # elif taxable_income > 1500000:
        #         #     tds_above15 = rec.taxable_income - 1500000
        #         #     tax_slab_15 = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above15percentage = tds_above15 * tax_slab_15.tax_rate / 100
        #
        #         #     tax_slab_12 = self.env['tax_slab'].sudo().search([('salary_from','<=',1250001),('salary_to','>=',1500000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above12percentage = 250000 * tax_slab_12.tax_rate / 100
        #
        #         #     tax_slab = self.env['tax_slab'].sudo().search([('salary_from','<=',1000001),('salary_to','>=',1250000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above10percentage = 250000 * tax_slab.tax_rate / 100
        #
        #         #     tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',750001),('salary_to','<=',1000000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above75percentage = 250000 * tax_slab_1.tax_rate / 100
        #
        #         #     tax_slab_2 = self.env['tax_slab'].sudo().search([('salary_from','>=',500001),('salary_to','<=',750000),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_above5percentage = 250000 * tax_slab_2.tax_rate / 100
        #
        #         #     tax_slab_3 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',500001),('tax_regime','=','new_regime')],limit=1)
        #         #     tds_below5percentage = 250000 * tax_slab_3.tax_rate / 100
        #
        #         #     temp_tax_payable = tds_above15percentage + tds_above12percentage + tds_above10percentage + tds_above75percentage +tds_above5percentage + tds_below5percentage
        #
        #         # tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0
        #
        #         # # rebate = tax_payable if taxable_income < 500000 and tax_payable > 0 else 0
        #         # rebate = tax_payable if taxable_income < 500000 and tax_payable > 0 else 0
        #
        #         # temp_net_tax_payable = tax_payable - rebate
        #         # net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
        #         # tax_slab_rec = self.env['tax_slab'].sudo().search([('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','new_regime')],limit=1)
        #         # additional_sub_chrg = net_tax_payable * tax_slab_rec.surcharge / 100
        #         # additional_edu_cess = net_tax_payable * tax_slab_rec.cess / 100 if net_tax_payable > 0 else 0
        #         # var_tax_payable = round(net_tax_payable + additional_sub_chrg + additional_edu_cess)
        #         # if (var_tax_payable % 10) >= 5:
        #         #     remaining = 10 - (var_tax_payable % 10)
        #         #     tax_to_be_paid = var_tax_payable + remaining
        #         # else:
        #         #     tax_to_be_paid = var_tax_payable - (var_tax_payable % 10)
        #         # total_tax_payable = tax_to_be_paid
        #         # tax_recovered = tds
        #         # temp_balance_tax_payable = total_tax_payable - tax_recovered
        #         # balance_tax_payable = temp_balance_tax_payable
        #
        #         # return {
        #         #     'name': 'IT Declaration',
        #         #     'view_type': 'form',
        #         #     'view_mode': 'form',
        #         #     'res_model': 'yearly_notsubmitted_declaration',
        #         #     'view_id': self.env.ref('tds.yearly_notsubmitted_declaration_view_form').id,
        #         #     # 'res_id': rec.id,
        #         #     'type': 'ir.actions.act_window',
        #         #     'target': 'self',
        #         #     'context': {'employee_id': rec.employee_id.id, 'basic': forcast_basic, 'hra': forcast_hra,
        #         #                 'gross': total_gross, 'oalw': other_allowance, 'lwop': lwop,
        #         #                 'afterlwop': total_after_lwop, 'professional_tax': professional_tax,
        #         #                 'total_after_pt_sd': total_after_pt_sd,
        #         #                 'tax_payable': tax_payable, 'rebate': rebate, 'net_tax_payable': net_tax_payable,
        #         #                 'additional_sub_chrg': additional_sub_chrg,
        #         #                 'additional_edu_cess': additional_edu_cess, 'total_tax_payable': total_tax_payable,
        #         #                 'tax_recovered': tax_recovered, 'balance_tax_payable': balance_tax_payable,
        #         #                 'employee_epf': employee_epf,
        #         #                 'hid_amount': hid_amount, 'total_deduction': total_deduction,
        #         #                 'taxable_income': taxable_income},
        #         # }


class monthlyDeclarationreport(models.Model):
    _name = "monthly_declaration_report"
    _description = "Monthly Declaration Report"

    def _default_financial_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    april = fields.Float(string="April")
    may = fields.Float(string="May")
    june = fields.Float(string="June")
    july = fields.Float(string="July")
    august = fields.Float(string="August")
    september = fields.Float(string="September")
    october = fields.Float(string="October")
    november = fields.Float(string="November")
    december = fields.Float(string="December")
    january = fields.Float(string="January")
    february = fields.Float(string="February")
    march = fields.Float(string="March")
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    tds_amount = fields.Float(string='TDS')
