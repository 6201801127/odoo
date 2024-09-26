from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
import datetime
from dateutil.relativedelta import relativedelta
import sys
from odoo.addons.kw_utility_tools import kw_helpers
import calendar
from odoo.addons import decimal_precision as dp


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', res.employee_id.id),
                                                     ('date_from', '=', res.date_from),
                                                     ('date_to', '=', res.date_to),
                                                     ('id', '!=', res.id),
                                                     ])
        if payslip_ids:
            raise ValidationError(
                _(f'You are Not allowed to create multiple payslips for {res.employee_id.name} - Month combination'))
        else:
            return res

    @api.multi
    def refund_sheet(self):
        for payslip in self:
            payslip.state = 'draft'
            to_date = payslip.date_to
            from_date =  payslip.date_from
            alw_rec = self.env['allowance_allocation_master'].sudo().search(
            [('month', '=', str(to_date.month)), ('year', '=', str(to_date.year)),
             ('employee', '=', payslip.employee_id.id),
             ('boolean_readonly', '=', True)])
            alw_rec.write({'boolean_readonly': False})
            lunch_rec = self.env['lunch_expenses'].sudo().search(
            [('month', '=', str(to_date.month)), ('year', '=', str(to_date.year)),
             ('employee_id', '=', payslip.employee_id.id), ('boolean_readonly', '=', True)])
            lunch_rec.write({'boolean_readonly': False})
            ledger = self.env['kw_payslip_ledger'].sudo().search([('year', '=', str(to_date.year)),('employee_id', '=', payslip.employee_id.id), ('month', '=', str(to_date.month)), ('boolean_readonly', '=', True)])
            ledger.write({'boolean_readonly': False})
            health_ins_self = self.env['health_insurance_self'].sudo().search(
            [('year', '=', str(to_date.year)),
             ('employee_id', '=', payslip.employee_id.id), ('boolean_readonly', '=', True)])
            health_ins_self.write({'boolean_readonly': False})
            health_dependant = self.env['health_insurance_dependant'].sudo().search(
                            [('employee_id', '=', payslip.employee_id.id),
                             ('state', '=', 'approved')],order='id desc', limit=1)
            attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
                [('attendance_year', '=',to_date.year), ('attendance_month', '=', to_date.month),
                ('employee_id', '=', payslip.employee_id.id)])
            if len(health_dependant) > 0:
                if attendance_info and attendance_info.zero_payslip_boolean == True:
                    emi_rec = self.env['health_insurance_emi'].sudo()
                    max_date_rec = emi_rec.search([('emi_details_id','=',health_dependant.id)],order='emi_date desc',limit=1)
                    month_numb = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
                    max_date_rec.write({'emi_date':to_date,'year':to_date.year,'month': month_numb.get(to_date.month),'status':'unpaid'})
                elif attendance_info and attendance_info.zero_payslip_boolean == False:
                    deduction_rec = health_dependant.emi_details_ids.filtered(lambda r: r.emi_date >= from_date and r.emi_date <= to_date)
                    deduction_rec.write({'status':'unpaid'})
            salary_rec = self.env['kw_advance_apply_salary_advance'].sudo().search(
                        [('employee_id', '=', payslip.employee_id.id),('state', 'in', ['release','paid'])])
            
            if salary_rec:
                for rec in salary_rec:
                    sal_deduction_rec = rec.deduction_line_ids.filtered(lambda r: r.status == 'paid' and r.deduction_date.month == payslip.date_to.month and r.deduction_date.year == payslip.date_to.year and r.is_preclosure == False)
                    if attendance_info and attendance_info.zero_payslip_boolean == False:
                        if sal_deduction_rec:
                            sal_deduction_rec.write({'status':'draft','pay_slip':''})
                    else:
                        adv_emi_rec = self.env['kw_advance_deduction_line'].sudo().search([('skipped_by_payroll','=',True)])
                        adv_max_date_rec = adv_emi_rec.search([('deduction_id','=',rec.id)],order='deduction_date desc',limit=1)
                        adv_max_date_rec.write({'deduction_date':to_date,'status':'draft','pay_slip':'','skipped_by_payroll':False})
                    

    def compute_yearly_earnings(self):
        for record in self:
            date_range_rec = self.env['account.fiscalyear'].search(
                [('date_start', '<=', record.date_from), ('date_stop', '>=', record.date_to)])
            if date_range_rec:
                payslips = self.env['hr.payslip'].search(
                    [('state', '=', 'done'), ('employee_id', '=', record.employee_id.id),
                     ('date_from', '>=', date_range_rec.date_start), ('date_to', '<=', date_range_rec.date_stop)])
                if payslips:
                    grs = 0
                    for rec in payslips:
                        earning_rec = rec.line_ids.filtered(lambda x: x.code == 'GROSS')
                        if earning_rec:
                            grs += earning_rec.total
                    return grs
                else:
                    return 0.00
            else:
                return 0.00
            
    yearly_basic = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_lwop = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_hra = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_adv = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_conv = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_epf = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_esi = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_pbnous = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_protax = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_cbnous = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_insurance_self = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_insurance_dependant = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_incentive = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_ctn_exp = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_var = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_salw = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_eqall = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_lven = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_city = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_trng = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_erbonus = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_other_deduction = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_bnous = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_arre = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_tds = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_salary_advance_principal  = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_salary_advance_interest  = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_prof_persuit = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_ltc = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    yearly_nps = fields.Float(compute='compute_yearly_basic', digits=dp.get_precision('Payroll'))
    




    @api.depends('date_to')
    def compute_yearly_basic(self):
        for record in self:
            arre = 0.00
            basic = 0.00
            lwop = 0.00
            hra = 0.00
            adv = 0.00
            conv = 0.00
            epf = 0.00
            esi = 0.00
            pbonus = 0.00
            tax = 0.00
            cbonus = 0.00
            bonus = 0.00
            self_insurance = 0.00
            dependant_insurance = 0.00
            incentive = 0.00
            canteen = 0.00
            var = 0.00
            spcl = 0.00
            yearly_eqall = 0.00
            yearly_lven = 0.00
            city = 0.00
            yearly_trng = 0.00
            yearly_erbonus = 0.00
            yearly_other_deduction = 0.00
            tds = 0.00
            salary_principal = 0.00
            salary_interest =0.00
            prof_persuit = 0
            ltc = 0
            nps = 0
            date_range_rec = self.env['account.fiscalyear'].search(
                [('date_start', '<=', record.date_from), ('date_stop', '>=', record.date_to)])
            if date_range_rec:
                payslips = self.env['hr.payslip'].search(
                    [('state', '=', 'done'), ('employee_id', '=', record.employee_id.id),
                     ('date_from', '>=', date_range_rec.date_start), ('date_to', '<=', date_range_rec.date_stop)])
                filtered_payslips = payslips.filtered(lambda x: x.date_to <= record.date_to)
                if filtered_payslips:
                    for rec in filtered_payslips: 
                        yearly_arre = rec.line_ids.filtered(lambda x: x.code == 'ARRE')
                        yearly_bonus = rec.line_ids.filtered(lambda x: x.code == 'BONUS')
                        yearly_od = rec.line_ids.filtered(lambda x: x.code == 'OD')
                        erbonus_rec = rec.line_ids.filtered(lambda x: x.code == 'ERBONUS')
                        training_rec = rec.line_ids.filtered(lambda x: x.code == 'TINC')
                        city_all = rec.line_ids.filtered(lambda x: x.code == 'CBDA')
                        lv_rec = rec.line_ids.filtered(lambda x: x.code == 'LE')
                        eqiall_rec = rec.line_ids.filtered(lambda x: x.code == 'EALW')
                        spclall_rec = rec.line_ids.filtered(lambda x: x.code == 'SALW')
                        variable_rec = rec.line_ids.filtered(lambda x: x.code == 'VAR')
                        lunch_exp_rec = rec.line_ids.filtered(lambda x: x.code == 'FC')
                        incentive_rec = rec.line_ids.filtered(lambda x: x.code == 'INC')
                        insurance_rec = rec.line_ids.filtered(lambda x: x.code == 'CMT')
                        basic_rec = rec.line_ids.filtered(lambda x: x.code == 'BASIC')
                        lwop_rec = rec.line_ids.filtered(lambda x: x.code == 'LWOP')
                        hra_rec = rec.line_ids.filtered(lambda x: x.code == 'HRAMN')
                        adv_rec = rec.line_ids.filtered(lambda x: x.code == 'SALADV')
                        tca_rec = rec.line_ids.filtered(lambda x: x.code == 'TCA')
                        epf_rec = rec.line_ids.filtered(lambda x: x.code == 'EEPF')
                        esi_rec = rec.line_ids.filtered(lambda x: x.code == 'ESI')
                        bonus_rec = rec.line_ids.filtered(lambda x: x.code == 'PBONUS')
                        pro_tax_rec = rec.line_ids.filtered(lambda x: x.code == 'PTD')
                        cbonus_rec = rec.line_ids.filtered(lambda x: x.code == 'CBONUS')
                        dep_insurance = rec.line_ids.filtered(lambda x: x.code == 'HID')
                        yearly_tds =  rec.line_ids.filtered(lambda x: x.code == 'TDS')
                        yearly_persuit =  rec.line_ids.filtered(lambda x: x.code == 'PP')
                        yearly_ltc =  rec.line_ids.filtered(lambda x: x.code == 'LTC')
                        yearly_nps =  rec.line_ids.filtered(lambda x: x.code == 'NPS')
                        nps += yearly_nps.total
                        record.yearly_nps = nps
                        ltc += yearly_ltc.total
                        record.yearly_ltc = ltc
                        prof_persuit += yearly_persuit.total
                        record.yearly_prof_persuit = prof_persuit
                        tds += yearly_tds.total
                        record.yearly_tds = tds
                        arre += yearly_arre.total
                        record.yearly_arre = arre
                        bonus += yearly_bonus.total
                        record.yearly_bnous = bonus
                        yearly_other_deduction += yearly_od.total
                        record.yearly_other_deduction = yearly_other_deduction
                        yearly_erbonus += erbonus_rec.total
                        record.yearly_erbonus = yearly_erbonus
                        yearly_trng += training_rec.total
                        record.yearly_trng = yearly_trng
                        city += city_all.total
                        record.yearly_city = city
                        yearly_lven += lv_rec.total
                        record.yearly_lven = yearly_lven
                        yearly_eqall += eqiall_rec.total
                        record.yearly_eqall = yearly_eqall
                        spcl += spclall_rec.total
                        record.yearly_salw = spcl
                        var += variable_rec.total
                        record.yearly_var = var
                        canteen += lunch_exp_rec.total
                        record.yearly_ctn_exp = canteen
                        incentive += incentive_rec.total
                        record.yearly_incentive = incentive
                        dependant_insurance += dep_insurance.total
                        record.yearly_insurance_dependant = dependant_insurance
                        self_insurance += insurance_rec.total
                        record.yearly_insurance_self = self_insurance
                        cbonus += cbonus_rec.total
                        record.yearly_cbnous = cbonus
                        tax += pro_tax_rec.total
                        record.yearly_protax = tax
                        basic += basic_rec.total
                        record.yearly_basic = basic
                        lwop += lwop_rec.total
                        record.yearly_lwop = lwop
                        hra += hra_rec.total
                        record.yearly_hra = hra
                        adv += adv_rec.total
                        record.yearly_adv = adv
                        conv += tca_rec.total
                        record.yearly_conv = conv
                        epf += epf_rec.total
                        record.yearly_epf = epf
                        esi += esi_rec.total
                        record.yearly_esi = esi
                        pbonus += bonus_rec.total
                        record.yearly_pbnous = pbonus
                        salary_rec = self.env['kw_advance_apply_salary_advance'].sudo().search(
                                [('employee_id', '=', rec.employee_id.id),('state', 'in', ['release','paid'])])
                        final_salary_principal,final_salary_interest = 0.00,0.00
                        if salary_rec:
                            for advance in salary_rec:
                                salary_deduction_rec = advance.deduction_line_ids.filtered(lambda r: r.status == 'paid' and r.deduction_date >= date_range_rec.date_start and r.deduction_date <= date_range_rec.date_stop and r.is_preclosure == False)
                                filtered_deduction = salary_deduction_rec.filtered(lambda x: x.deduction_date <= rec.date_to)
                                if filtered_deduction:
                                    salary_principal  = filtered_deduction.mapped('principal_amt')
                                    salary_interest = filtered_deduction.mapped('monthly_interest')
                                    final_salary_principal += sum(salary_principal)
                                    final_salary_interest += sum(salary_interest)
                            
                            record.yearly_salary_advance_principal =  final_salary_principal
                            record.yearly_salary_advance_interest = final_salary_interest
                else:
                    record.yearly_nps = nps
                    record.yearly_ltc = ltc
                    record.yearly_prof_persuit = prof_persuit
                    record.yearly_tds = tds
                    record.yearly_arre = arre
                    record.yearly_erbonus = yearly_erbonus
                    record.yearly_trng = yearly_trng
                    record.yearly_city = city
                    record.yearly_lven = yearly_lven
                    record.yearly_eqall = yearly_eqall
                    record.yearly_salw = spcl
                    record.yearly_var = var
                    record.yearly_ctn_exp = canteen
                    record.yearly_incentive = incentive
                    record.yearly_insurance_dependant = dependant_insurance
                    record.yearly_insurance_self = self_insurance
                    record.yearly_cbnous = cbonus
                    record.yearly_protax = tax
                    record.yearly_basic = basic
                    record.yearly_lwop = lwop
                    record.yearly_hra = hra
                    record.yearly_adv = adv
                    record.yearly_conv = conv
                    record.yearly_epf = epf
                    record.yearly_esi = esi
                    record.yearly_pbnous = pbonus
                    record.yearly_other_deduction = yearly_other_deduction
                    record.yearly_bnous = bonus
                    record.yearly_salary_advance_principal =  salary_principal
                    record.yearly_salary_advance_interest = salary_interest
                    record.yearly_prof_persuit = prof_persuit


            else:
                record.yearly_nps = nps
                record.yearly_ltc = ltc
                record.yearly_prof_persuit = prof_persuit
                record.yearly_tds = tds
                record.yearly_arre = arre
                record.yearly_bnous = bonus
                record.yearly_erbonus = yearly_erbonus
                record.yearly_trng = yearly_trng
                record.yearly_city = city
                record.yearly_lven = yearly_lven
                record.yearly_eqall = yearly_eqall
                record.yearly_salw = spcl
                record.yearly_var = var
                record.yearly_ctn_exp = canteen
                record.yearly_incentive = incentive
                record.yearly_insurance_dependant = dependant_insurance
                record.yearly_insurance_self = self_insurance
                record.yearly_cbnous = cbonus
                record.yearly_protax = tax
                record.yearly_basic = basic
                record.yearly_lwop = lwop
                record.yearly_hra = hra
                record.yearly_adv = adv
                record.yearly_conv = conv
                record.yearly_epf = epf
                record.yearly_esi = esi
                record.yearly_pbnous = pbonus
                record.yearly_other_deduction = yearly_other_deduction
                record.yearly_salary_advance_principal =  salary_principal
                record.yearly_salary_advance_interest = salary_interest

    def _compute_pan_num(self):
        for rec in self:
            if rec.employee_id.identification_ids:
                for record in rec.employee_id.identification_ids:
                    if record.name == '1':
                        pan_num = record.doc_number
                        return pan_num
                    else:
                        return '--NA--'
            else:
                return '--NA--'
                
            

    def _compute_grade_band(self):
        for rec in self:
            org_grade = self.env['kwemp_grade'].sudo().search(
                [('grade_id', '=', rec.employee_id.grade.id), ('band_id', '=', rec.employee_id.emp_band.id)], limit=1)
            if org_grade:
                return org_grade.name

    monthly_lwop = fields.Float(compute='_compute_total_working_days', digits=dp.get_precision('Payslip Report'))

    tot_working_day = fields.Float(compute='_compute_total_working_days', digits=dp.get_precision('Payslip Report'))
    total_present_days = fields.Float(compute='_compute_total_working_days', digits=dp.get_precision('Payslip Report'))
    ckeck_calendar_days = fields.Boolean(compute='_compute_total_working_days')
    

    @api.depends('date_from')
    def _compute_total_working_days(self):
        for rec in self:
            date = rec.date_to
            attendance_rec = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('attendance_year', '=', date.year),
                 ('attendance_month', '=', date.month)])
            if attendance_rec:
                for record in attendance_rec:
                    rec.ckeck_calendar_days = record.ckeck_calendar_days
                    rec.tot_working_day = calendar.monthrange(int(rec.date_to.year), int(rec.date_to.month))[1] if record.ckeck_calendar_days == True else record.num_shift_working_days
                    rec.total_present_days = record.calculation_days if record.ckeck_calendar_days == True else record.actual_working
                    rec.monthly_lwop = record.total_pay_cut

    yearly_deduction = fields.Float(compute='compute_deduction', digits=dp.get_precision('Payroll'))
    monthly_deduction = fields.Float(compute='compute_deduction', digits=dp.get_precision('Payroll'))

    @api.depends('employee_id')
    def compute_deduction(self):
        for rec in self:
            lwop = rec.yearly_lwop
            nps = rec.yearly_nps
            sal_adv = rec.yearly_adv
            eepf = rec.yearly_epf
            esi = rec.yearly_esi
            pro_tax = rec.yearly_protax
            self_insurance = rec.yearly_insurance_self
            canteen = rec.yearly_ctn_exp
            dependant_insurance = rec.yearly_insurance_dependant
            yrly_other_deductn = rec.yearly_other_deduction
            yrly_tds =  rec.yearly_tds
            rec.yearly_deduction = nps + lwop + sal_adv + eepf + esi + pro_tax + self_insurance + canteen + dependant_insurance + yrly_other_deductn + yrly_tds
            lwop_rec = rec.line_ids.filtered(lambda x: x.code == 'LWOP')
            nps_rec = rec.line_ids.filtered(lambda x: x.code == 'NPS')
            adv_rec = rec.line_ids.filtered(lambda x: x.code == 'SALADV')
            eepf_rec = rec.line_ids.filtered(lambda x: x.code == 'EEPF')
            esi_rec = rec.line_ids.filtered(lambda x: x.code == 'ESI')
            pro_tax_rec = rec.line_ids.filtered(lambda x: x.code == 'PTD')
            insurance_rec = rec.line_ids.filtered(lambda x: x.code == 'CMT')
            lunch_exp_rec = rec.line_ids.filtered(lambda x: x.code == 'FC')
            dependant = rec.line_ids.filtered(lambda x: x.code == 'HID')
            other_deduction_rec = rec.line_ids.filtered(lambda x: x.code == 'OD')
            other_ded = other_deduction_rec.total if other_deduction_rec else 0
            lwop_yr = lwop_rec.total if lwop_rec else 0
            nps_yr = nps_rec.total if nps_rec else 0
            adv_yr = adv_rec.total if adv_rec else 0
            eepf_yr = eepf_rec.total if eepf_rec else 0
            esi_yr = esi_rec.total if esi_rec else 0
            tax_yr = pro_tax_rec.total if pro_tax_rec else 0
            self_ins_yr = insurance_rec.total if insurance_rec else 0
            lunch_yr = lunch_exp_rec.total if lunch_exp_rec else 0
            hid_yr = dependant.total if dependant else 0
            tds_rec = rec.line_ids.filtered(lambda x: x.code == 'TDS')
            tds = tds_rec.total if tds_rec else 0
            rec.monthly_deduction =nps_yr + lwop_yr + adv_yr + eepf_yr + esi_yr + tax_yr + self_ins_yr + lunch_yr + hid_yr + other_ded  + tds

    def compute_difference_two_date(self):
        s = self.date_from
        e = self.date_to
        start = s.day
        end = e.day
        date_days = end - start + 1
        return date_days

    # added by sangita
    def compute_net_pay(self):
        loan_amount = 0.0
        if self.line_ids:
            for line in self.line_ids:
                if line.code == 'LOAN':
                    loan_amount = line.amount
                if line.code == 'NET':
                    net = line.amount - loan_amount
                    return net
    total_yrly_earning = fields.Float(compute='compute_yearly_total_earing', digits=dp.get_precision('Payroll'))
    yearly_gross = fields.Float(compute='compute_yearly_total_earing', digits=dp.get_precision('Payroll'))

    @api.depends('line_ids')
    def compute_yearly_total_earing(self):
        total = 0.00
        for rec in self:
            arre = rec.yearly_arre
            basic = rec.yearly_basic
            hra = rec.yearly_hra
            conveyance = rec.yearly_conv
            pbnous = rec.yearly_pbnous
            cbnus = rec.yearly_cbnous
            bonus = rec.yearly_bnous
            trng_incentive = rec.yearly_trng
            variable = rec.yearly_var
            eqi_all = rec.yearly_eqall
            leave = rec.yearly_lven
            city_all = rec.yearly_city
            incentive = rec.yearly_incentive
            erbonus = rec.yearly_erbonus
            pp = rec.yearly_prof_persuit
            ltc = rec.yearly_ltc

            total = basic + hra + conveyance + pbnous + cbnus + trng_incentive + variable + eqi_all + leave + city_all + incentive + erbonus + bonus + arre + pp + ltc
            rec.total_yrly_earning = total
            rec.yearly_gross = basic + hra + conveyance + pbnous + cbnus + bonus + pp + ltc
    
    # def compute_gross_yearly(self):
    #     total = 0 
    #     basic=self.yearly_basic
    #     hra = self.yearly_hra
    #     conveyance = self.yearly_conv
    #     pbnous = self.yearly_pbnous
    #     cbnus = self.yearly_cbnous
    #     total = basic + hra + conveyance + pbnous + cbnus 
    #     print("total earning====",total)
    #     return total 

    monthly_earning = fields.Float(compute='compute_monthly_earnings', digits=dp.get_precision('Payroll'))

    @api.depends('contract_id')
    def compute_monthly_earnings(self):
        for record in self:
            basic_rec = record.line_ids.filtered(lambda x: x.code == 'BASIC')
            hra_rec = record.line_ids.filtered(lambda x: x.code == 'HRAMN')
            pb_rec = record.line_ids.filtered(lambda x: x.code == 'PBONUS')
            cb_rec = record.line_ids.filtered(lambda x: x.code == 'CBONUS')
            conv_rec = record.line_ids.filtered(lambda x: x.code == 'TCA')
            bonus_rec = record.line_ids.filtered(lambda x: x.code == 'BONUS')
            pp_rec = record.line_ids.filtered(lambda x: x.code == 'PP')
            ltc_rec = record.line_ids.filtered(lambda x: x.code == 'LTC')

            basic = basic_rec.total if basic_rec else 0
            hra = hra_rec.total if hra_rec else 0
            pb = pb_rec.total if pb_rec else 0
            cb = cb_rec.total if cb_rec else 0
            conv = conv_rec.total if conv_rec else 0
            bonus = bonus_rec.total if bonus_rec else 0
            pp = pp_rec.total if pp_rec else 0
            ltc = ltc_rec.total if ltc_rec else 0

            record.monthly_earning = basic + hra + pb + cb + conv + bonus + pp + ltc

    month_year = fields.Char(compute='_compute_month_year')

    @api.depends('name')
    def _compute_month_year(self):
        for rec in self:
            rec.month_year = f"Salary Slip for the month of {rec.date_from.strftime('%B')} {rec.date_to.strftime('%Y')}"

    def _compute_salary_write_date(self):
        for rec in self:
            last_modified = f"{rec.write_date.date().strftime('%d-%B-%Y')}"
            return last_modified
        
        
    gross_basic = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_hra = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_conveyance = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_pb = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_cb = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_total_earning = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_final_total_earning = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_prof_persuit = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))
    gross_ltc = fields.Float(compute='compute_gross_entitlement', digits=dp.get_precision('Payroll'))

   
    def compute_gross_entitlement(self):
        Incentive, Variable ,Equitable , SpecialAllowance , LeaveEncashment ,CityAllowance , TrainingIncentive , EmployeeReferralBonus , Arrear = 0,0,0,0,0,0,0,0,0
        for record in self:
            date = record.date_to
            attendance_emp_sts = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('attendance_year', '=', date.year),
                    ('attendance_month', '=', date.month)]).emp_status
            if attendance_emp_sts == 1:
                record.gross_basic = record.basic
                record.gross_hra = record.hra
                record.gross_conveyance = record.conveyance
                record.gross_pb = record.pb
                record.gross_cb = record.cb
                record.gross_prof_persuit = record.prof_persuit
                record.gross_ltc = record.ltc
            elif attendance_emp_sts == 2:
                next_payslip = self.search([('date_to','>',record.date_to)],order='id asc',limit=1)
                if next_payslip:
                    record.gross_basic = next_payslip.basic
                    record.gross_hra = next_payslip.hra
                    record.gross_conveyance = next_payslip.conveyance
                    record.gross_pb = next_payslip.pb
                    record.gross_cb = next_payslip.cb
                    record.gross_prof_persuit = next_payslip.contract_id.prof_persuit
                    record.gross_ltc = next_payslip.contract_id.ltc
                else:
                    record.gross_basic = record.contract_id.current_basic
                    record.gross_hra = record.contract_id.current_basic * record.contract_id.house_rent_allowance_metro_nonmetro / 100
                    record.gross_conveyance = record.contract_id.current_basic * record.contract_id.conveyance / 100
                    record.gross_pb = record.contract_id.productivity
                    record.gross_cb = record.contract_id.commitment
                    record.gross_prof_persuit = record.contract_id.prof_persuit
                    record.gross_ltc = record.contract_id.ltc
            else:
                # prvs_payslip = self.search([('date_to','<',record.date_to)],order='id desc',limit=1)
                # if prvs_payslip:
                #     record.gross_basic = prvs_payslip.basic
                #     record.gross_hra = prvs_payslip.hra
                #     record.gross_conveyance = prvs_payslip.conveyance
                #     record.gross_pb = prvs_payslip.pb
                #     record.gross_cb = prvs_payslip.cb
                #     record.gross_prof_persuit = prvs_payslip.contract_id.prof_persuit
                #     record.gross_ltc = prvs_payslip.contract_id.ltc
                # else:
                    record.gross_basic = record.contract_id.current_basic
                    record.gross_hra = record.contract_id.current_basic * record.contract_id.house_rent_allowance_metro_nonmetro / 100
                    record.gross_conveyance = record.contract_id.current_basic * record.contract_id.conveyance / 100
                    record.gross_pb = record.contract_id.productivity
                    record.gross_cb = record.contract_id.commitment
                    record.gross_prof_persuit = record.contract_id.prof_persuit
                    record.gross_ltc = record.contract_id.ltc

            record.gross_total_earning = record.gross_basic + record.gross_hra + record.gross_pb + record.gross_cb + record.gross_conveyance + record.gross_prof_persuit +  record.gross_ltc
            Incentive += sum(record.line_ids.filtered(lambda x: x.code == 'INC').mapped('total'))
            Variable += sum(record.line_ids.filtered(lambda x: x.code == 'VAR').mapped('total'))
            Equitable += sum(record.line_ids.filtered(lambda x: x.code == 'EALW').mapped('total'))
            SpecialAllowance += sum(record.line_ids.filtered(lambda x: x.code == 'SALW').mapped('total'))
            LeaveEncashment += sum(record.line_ids.filtered(lambda x: x.code == 'LE').mapped('total'))
            CityAllowance += sum(record.line_ids.filtered(lambda x: x.code == 'CBDA').mapped('total'))
            TrainingIncentive += sum(record.line_ids.filtered(lambda x: x.code == 'TINC').mapped('total'))
            EmployeeReferralBonus += sum(record.line_ids.filtered(lambda x: x.code == 'ERBONUS').mapped('total'))
            Arrear += sum(record.line_ids.filtered(lambda x: x.code == 'ARRE').mapped('total'))
            
            record.gross_final_total_earning = record.gross_total_earning + Incentive + Variable + Equitable + SpecialAllowance + LeaveEncashment + CityAllowance + TrainingIncentive + EmployeeReferralBonus + Arrear
        
        
    salary_advance_principal = fields.Float(compute='compute_salary_advance', digits=dp.get_precision('Payroll'))
    salary_advance_interest = fields.Float(compute='compute_salary_advance', digits=dp.get_precision('Payroll'))
    

    def compute_salary_advance(self):
        for record in self:
            date_to = record.date_to
            for line in record.line_ids:
                if line.code == 'SALADV' and line.amount >0:
                    salary_rec = self.env['kw_advance_apply_salary_advance'].sudo().search(
                        [('employee_id', '=', record.employee_id.id), ('state', 'in', ['release','paid'])])
                    principal_amount,interest_amount = 0,0
                    if salary_rec:
                        for rec in salary_rec:
                            deduction_rec = rec.deduction_line_ids.filtered(lambda r: r.deduction_date.month == date_to.month and r.deduction_date.year == date_to.year and r.is_preclosure == False)
                            for lines in deduction_rec:
                                principal_amount += lines.principal_amt
                                interest_amount += lines.monthly_interest
                            record.salary_advance_interest = interest_amount
                            record.salary_advance_principal = principal_amount
                # else:
                #     record.salary_advance_principal = 0
                #     record.salary_advance_interest = 0
                    
    

    @api.depends('line_ids.amount')
    def _compute_amount_total_words(self):
        for s in self:
            currency_label = s.currency_id.name
            # print("currency_label >>> ", currency_label)
            for line in s.line_ids:
                if line.code == 'NET':
                    var_amt = line.amount if line.amount > 0 else 0
                    amount_total_words = kw_helpers.num_to_words(var_amt)
                    s.amount_total_words = f"{currency_label} {amount_total_words} only"


                if line.code == 'CTC':
                    var_amt_ctc = line.amount
                    total_ctc = kw_helpers.num_to_words(var_amt_ctc)
                    s.total_ctc = f"{currency_label} {total_ctc} only"
                

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words", store=True)
    total_ctc = fields.Char("Total (In Words)", compute="_compute_amount_total_words", store=True)

    el_remaining_days = fields.Float(compute='_compute_remaining_leave_days')
    cl_remaining_days = fields.Float(compute='_compute_remaining_leave_days')
    paternity_leave_remaining_days = fields.Float(compute='_compute_remaining_leave_days')
    maternity_leave_remaining_days = fields.Float(compute='_compute_remaining_leave_days')
    medical_leave_remaining_days = fields.Float(compute='_compute_remaining_leave_days')

    def _compute_remaining_leave_days(self):
        for record in self:
            date_range_rec = self.env['account.fiscalyear'].search(
                [('date_start', '<=', record.date_from), ('date_stop', '>=', record.date_to)],limit=1)
            
            leave_allocation_rec = self.env['hr.leave.allocation'].sudo().search([('validity_start_date', '>=', date_range_rec.date_start), ('validity_end_date', '<=', date_range_rec.date_stop),('employee_id','=',record.employee_id.id)])
            lapse_leave = self.env['hr.leave.allocation'].sudo().search([('employee_id','=',record.employee_id.id),('state','=','validate'),('number_of_days','<',0)]).filtered(lambda x : x.leave_cycle_id.from_date >= date_range_rec.date_start and x.leave_cycle_id.to_date <= date_range_rec.date_stop and x.applied_on >= date_range_rec.date_start and x.applied_on <= record.date_to)

            el_lapse = sum(lapse_leave.filtered(lambda x:x.holiday_status_id.leave_code == 'EL').mapped('number_of_days'))
            cl_lapse = sum(lapse_leave.filtered(lambda x:x.holiday_status_id.leave_code == 'CL').mapped('number_of_days'))
            paternity_lapse = sum(lapse_leave.filtered(lambda x:x.holiday_status_id.leave_code == 'PT').mapped('number_of_days'))
            maternity_lapse = sum(lapse_leave.filtered(lambda x:x.holiday_status_id.leave_code == 'MT').mapped('number_of_days'))
            ml_lapse = sum(lapse_leave.filtered(lambda x:x.holiday_status_id.leave_code == 'ML').mapped('number_of_days'))
            
            
            el_remaining_days,cl_remaining_days,paternity_leave_remaining_days,maternity_leave_remaining_days,medical_leave_remaining_days = 0,0,0,0,0
            if leave_allocation_rec:
                cl_allocated = sum(leave_allocation_rec.filtered(lambda x:x.holiday_status_id.leave_code == 'CL').mapped('number_of_days'))
                el_allocated = sum(leave_allocation_rec.filtered(lambda x:x.holiday_status_id.leave_code == 'EL').mapped('number_of_days'))
                paternity_allocated = sum(leave_allocation_rec.filtered(lambda x:x.holiday_status_id.leave_code == 'PT').mapped('number_of_days'))
                maternity_allocated = sum(leave_allocation_rec.filtered(lambda x:x.holiday_status_id.leave_code == 'MT').mapped('number_of_days'))
                medical_allocated = sum(leave_allocation_rec.filtered(lambda x:x.holiday_status_id.leave_code == 'ML').mapped('number_of_days'))
                
                attendance_rec = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','>=',date_range_rec.date_start),('attendance_recorded_date','<=',datetime.date(record.date_to.year,record.date_to.month,25)),('employee_id','=',record.employee_id.id)])
                
                
                
                for rec in attendance_rec:
                    if rec.leave_code == 'EL':
                        el_remaining_days += rec.leave_day_value
                    if rec.leave_code == 'CL':
                        cl_remaining_days += rec.leave_day_value
                    if rec.leave_code == 'PT':
                        paternity_leave_remaining_days += rec.leave_day_value
                    if rec.leave_code == 'MT':
                        maternity_leave_remaining_days += rec.leave_day_value
                    if rec.leave_code == 'ML':
                        medical_leave_remaining_days += rec.leave_day_value
                
                record.paternity_leave_remaining_days = paternity_allocated - paternity_leave_remaining_days + paternity_lapse if (paternity_allocated and (paternity_allocated - paternity_leave_remaining_days + paternity_lapse) >= 0) else 0
                    
                record.maternity_leave_remaining_days = maternity_allocated - maternity_leave_remaining_days + maternity_lapse if (maternity_allocated and (maternity_allocated - maternity_leave_remaining_days + maternity_lapse) >= 0) else 0
                
                record.medical_leave_remaining_days = medical_allocated - medical_leave_remaining_days + ml_lapse if (medical_allocated and (medical_allocated - medical_leave_remaining_days + ml_lapse) >= 0) else 0
                
                record.el_remaining_days = el_allocated - el_remaining_days + el_lapse  if (el_allocated and (el_allocated - el_remaining_days + el_lapse) >= 0) else 0
                
                record.cl_remaining_days = cl_allocated - cl_remaining_days + cl_lapse if (cl_allocated  and (cl_allocated - cl_remaining_days + cl_lapse) >= 0) else  0
    def _get_report_filename(self):
        for rec in self:
            return f'{rec.employee_id.name}-{calendar.month_name[rec.date_to.month]}-{rec.date_to.year}'
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    # date_from = fields.Date(string='Date From', readonly=True)
    # date_to = fields.Date(string='Date To', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('verify', 'Waiting'),
                              ('done', 'Done'),
                              ('cancel', 'Rejected')
                              ], string="Status", related="slip_id.state")
    paid = fields.Boolean(string="Made Payment Order", related="slip_id.paid")
    date_from = fields.Date(string="Date From", related="slip_id.date_from")
    date_to = fields.Date(string="Date To", related="slip_id.date_to")
    payslip_batch = fields.Many2one(string="Payslip Batch", related="slip_id.payslip_run_id")
    is_current_month = fields.Boolean(compute="_check_current_month", store=True)
    year = fields.Char(string='Year')
    month = fields.Integer(string='Month')
    current_month = fields.Boolean()

    @api.depends('date_from')
    def _check_current_month(self):
        for rec in self:
            if rec.date_from:
                first_day = datetime.date.today().replace(day=1)
                last_day = datetime.date.today().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
                if rec.date_from:
                    if first_day <= rec.date_from <= last_day:
                        rec.is_current_month = True
                    else:
                        rec.is_current_month = False
                    
    @api.model
    def create(self, vals):
        res = super(HrPayslipLine, self).create(vals)
        if res.slip_id:
            res.year = res.slip_id.date_to.year
            res.month = int(res.slip_id.date_to.month)
        return res
    