from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from calendar import monthrange
from dateutil import relativedelta


class KwEncashmentPeriod(models.Model):
    _name = 'kw_set_encashment_period'
    _description = "Encashment Period Set"
    _rec_name = "financial_year_id"

    # @api.model
    # def _get_year_list(self):
    #     current_year = date.today().year
    #     return [(str(i),i) for i in range(current_year, 2019, -1)]

    # financial_year_id = fields.Selection(string='Financial Year',selection='_get_year_list', required=True,default=str(date.today().year))
    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', required=True)
    code = fields.Char('Code', related='financial_year_id.code')
    excluded_employees = fields.Many2many('hr.employee','kw_set_encashment_period_employee_rel', 'encashment_period_id',
                                    'employee_id', string='Excluded Employee')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    first_year_service = fields.Boolean(string='Applicable To First year Service')
    notice_period = fields.Boolean(string='Applicable To Notice Period')

    applicable_for = fields.Many2many('kwemp_employment_type', string="Applicable For")
    is_expired_date = fields.Boolean(compute='_compute_is_expired_date')

    _sql_constraints = [('financial_year_uniq', 'unique (financial_year_id)',
                         'Record with this financial year already exist.. !')]

    @api.multi
    def _compute_is_expired_date(self):
        for record in self:
            record.is_expired_date = True if record.end_date and record.end_date < date.today() else False

    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        for record in self:
            if record.start_date and record.end_date:
                current_year = int(record.code)
                next_year = current_year + 1

                if record.start_date > record.end_date:
                    raise ValidationError(
                        f'Start date should not greater than End date : {record.start_date} > {record.end_date}.')

                if record.start_date.year not in [current_year, next_year] or record.end_date.year not in [current_year,
                                                                                                           next_year]:
                    raise ValidationError(
                        f'Start date and end date must be in between the FY.')

    @api.multi
    def action_compute_encashment_carry_forward(self):
        """method to compute the cary forward ,  and encashment days for the selected fiscal year"""
        self.ensure_one()

        if datetime.now().date() <= self.end_date:
            employee_records = self.env['hr.employee'].search([])

            carryforward_encashment_report = self.env['kw_carryforward_encashment_report'].search(
                [('cycle_period', '=', int(self.financial_year_id.date_start.year))])
            kw_compute_cf_encashment = self.env['kw_compute_cf_encashment'].sudo().search(
                [('fisc_year', '=', int(self.financial_year_id.date_start.year))])

            if self.excluded_employees:
                employee_records = employee_records.filtered(lambda emp: emp.id not in self.excluded_employees.ids)
            # if self.applicable_for:
            #     employee_records = employee_records.filtered(lambda emp: emp.employement_type.id in self.applicable_for.ids and emp.in_noticeperiod == False)

            if self.applicable_for:
                notice_period_employees = self.env['hr.employee']
                applicable_employees = employee_records.filtered(lambda emp: emp.employement_type.id in self.applicable_for.ids and emp.in_noticeperiod == False)
                if self.notice_period == True:
                    notice_period_employees = employee_records.filtered(lambda emp: emp.in_noticeperiod == True)
                employee_records = applicable_employees + notice_period_employees

            if not self.applicable_for and self.notice_period:
                employee_records = employee_records.filtered(lambda emp: emp.in_noticeperiod == True)
            
            # print(self.financial_year_id)

            process_emp_records = carryforward_encashment_report.filtered(
                lambda emp: emp.employee_id.id in employee_records.ids)
            retirement_emp_records = carryforward_encashment_report.filtered(
                lambda emp: emp.retirement == True and emp.employee_id.last_working_day >= self.financial_year_id.date_start and emp.employee_id.last_working_day <= self.financial_year_id.date_stop if emp.employee_id.last_working_day else None)
            process_emp_records += retirement_emp_records
            for emp_record in process_emp_records:
                emp_years = relativedelta.relativedelta(self.financial_year_id.date_stop, emp_record.employee_id.date_of_joining).years if emp_record.employee_id.date_of_joining else False
                emp_months = relativedelta.relativedelta(self.financial_year_id.date_stop, emp_record.employee_id.date_of_joining).months if emp_record.employee_id.date_of_joining else False
                total_exp = emp_years * 12 + emp_months 
                resignation = self.env['kw_resignation'].sudo().search(
                    [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', emp_record.employee_id.id)], limit=1)
                
                if total_exp >= 6:
                    branch_id = emp_record.employee_id.resource_calendar_id.branch_id.id 
                    shift_id = emp_record.employee_id.resource_calendar_id.id
                    personal_calendar = 1
                    employee_id = emp_record.employee_id.id
                    holiday = []
                    holidays_list = self.env['resource.calendar.leaves'].get_calendar_global_leaves(branch_id,shift_id,personal_calendar,employee_id)
                    start_date, end_date = self.env['kw_late_attendance_summary_report']._get_month_range(date.today().year,3)
                    if holidays_list:
                        for rec in holidays_list['holiday_calendar']:
                            if rec['date_from'] >= start_date and rec['date_from'] <= end_date:
                                holiday.append(rec)
                    final_holiday_list = list({v['date_from']:v for v in holiday}.values())
                    total_working_days = monthrange(date.today().year,3)[1] - len(final_holiday_list)
                    # total_days = total_working_days if total_working_days > 0 else 23
                    total_days = 31

                    contract_id = self.env['hr.contract'].sudo().search([('employee_id','=',emp_record.employee_id.id),('state','=','open')],limit=1)
                    
                    basic = contract_id.current_basic
                    basic_encash = (basic / total_days) * emp_record.encashment_days if total_days > 0 else 0
                    gross = basic + ((basic * contract_id.house_rent_allowance_metro_nonmetro) / 100) + ((basic * contract_id.conveyance) / 100)
                    gross_encash = (gross / total_days) * emp_record.encashment_days if total_days > 0 else 0
                    final_gross = gross + contract_id.productivity + contract_id.commitment
                    final_gross_encash = (final_gross / total_days) * emp_record.encashment_days if total_days > 0 else 0
                    ctc = contract_id.wage
                    ctc_encash = (ctc / total_days) * emp_record.encashment_days if total_days > 0 else 0
                    
                    cf_encashment_data = {
                                        'employee_id': emp_record.employee_id.id,
                                        'fisc_year_id': self.financial_year_id.id, 
                                        'fisc_year': emp_record.cycle_period,
                                        'leave_type_id': emp_record.leave_type_id.id,
                                        'entitled': emp_record.tot_entitlement, 
                                        'leave_taken': emp_record.tot_leave_taken,
                                        'lapse_days': emp_record.tot_lapse_days,
                                        'leave_balance': emp_record.remaining_days,
                                        'carry_forward': emp_record.carry_forward_days,
                                        'encashment': emp_record.encashment_days,
                                        'total_working_days': total_days,
                                        'basic': round(basic),
                                        'basic_encash': round(basic_encash),
                                        'gross': round(gross),
                                        'gross_encash': round(gross_encash),
                                        'final_gross': round(final_gross),
                                        'final_gross_encash': round(final_gross_encash),
                                        'ctc': round(ctc),
                                        'ctc_encash': round(ctc_encash),
                                        'encashment_eligible': True if total_exp >= 12 else False,
                                        'applied_eos' : 'Yes' if resignation else 'No',
                                        }
                    # print(cf_encashment_data)
                    emp_compute_cf_rec = kw_compute_cf_encashment.filtered(lambda rec: rec.employee_id.id == emp_record.employee_id.id and rec.leave_type_id.id == emp_record.leave_type_id.id)
                    if emp_compute_cf_rec:
                        
                        emp_compute_cf_rec.write(cf_encashment_data)
                    else:
                        emp_compute_cf_rec.create(cf_encashment_data)

        return True

    @api.multi
    def action_process_carry_forward(self):
        """method to process the cary forward and allocate for the next fiscal year"""
        self.ensure_one()

        fisc_year = int(self.financial_year_id.code)

        # #create next year leave cycle
        cur_yr_leave_cycle = self.env['kw_leave_cycle_master'].with_context(active_test=False).search(
            [('cycle_period', '=', fisc_year), ('cycle_id', '!=', False)])
        # print('--------------', cur_yr_leave_cycle)
        for leave_cycle in cur_yr_leave_cycle:
            leave_cycle.cycle_id.create_leave_cycle_period(fisc_year + 1)

        next_yr_leave_cycle = self.env['kw_leave_cycle_master'].with_context(active_test=False).search(
            [('cycle_period', '=', fisc_year + 1), ('cycle_id', '!=', False)])
        if not next_yr_leave_cycle:
            raise UserError(('Next year leave cycle does not exist in system.'))

        # print(next_yr_leave_cycle)
        if next_yr_leave_cycle:
            # #get next year allocations of leave type having carry forward option
            next_yr_cf_allocations = self.env['hr.leave.allocation'].sudo().search(
                [('leave_cycle_id.id', 'in', next_yr_leave_cycle.ids), ('holiday_status_id.carry_forward', '=', True)])
            emp_allocated_record = self.env['hr.leave.allocation']
            compute_cf_encashment_records = self.env['kw_compute_cf_encashment'].sudo().search(
                [('fisc_year', '=', fisc_year)])

            for cf_record in compute_cf_encashment_records:
                accumulation_days = cf_record.leave_type_id.carry_forward_lapsed
                employee_leave_cycle = next_yr_leave_cycle.filtered(
                    lambda rec: rec.branch_id.id == cf_record.employee_id.job_branch_id.id)
                if employee_leave_cycle and accumulation_days:
                    leave_validity_start_date = employee_leave_cycle.from_date
                    leave_validity_end_date = leave_validity_start_date + timedelta(days=accumulation_days)
                    emp_allocated_record = next_yr_cf_allocations.filtered(lambda
                                                                               rec: rec.employee_id.id == cf_record.employee_id.id and rec.holiday_status_id.id == cf_record.leave_type_id.id and rec.validity_start_date == leave_validity_start_date and rec.validity_end_date == leave_validity_end_date and rec.is_carried_forward == False)
                    exist_emp_allocated_record = next_yr_cf_allocations.filtered(lambda
                                                                               rec: rec.employee_id.id == cf_record.employee_id.id and rec.holiday_status_id.id == cf_record.leave_type_id.id and rec.validity_start_date == leave_validity_start_date and rec.validity_end_date == leave_validity_end_date and rec.is_carried_forward == True)
                    allocation_data = {'employee_id': cf_record.employee_id.id,
                                       'holiday_status_id': cf_record.leave_type_id.id,
                                       'name': cf_record.leave_type_id.name + ' carry forward by system as per leave policy',
                                       'state': 'validate', 'holiday_type': 'employee',
                                       'validity_start_date': leave_validity_start_date,
                                       'validity_end_date': leave_validity_end_date,
                                       'leave_cycle_id': employee_leave_cycle.id,
                                       'number_of_days': cf_record.carry_forward,
                                       'cycle_period': employee_leave_cycle.cycle_period,
                                       'notes': cf_record.leave_type_id.name + ' carry forward by system as per leave policy',
                                       'is_carried_forward': True}
                    # print(allocation_data)
                    if exist_emp_allocated_record:
                        if cf_record.carry_forward > 0:
                            exist_emp_allocated_record.sudo().write(allocation_data)
                            cf_record.cf_status = '2'
                    elif emp_allocated_record:
                        if cf_record.carry_forward > 0:
                            emp_allocated_record.sudo().create(allocation_data)
                        # else:
                        #     print(emp_allocated_record)
                        #     emp_allocated_record.sudo().unlink()

                        cf_record.cf_status = '2'
                    elif cf_record.carry_forward > 0:
                        emp_allocated_record.sudo().create(allocation_data)
                        cf_record.cf_status = '1'
                else:
                    # raise UserError(('Leave cycle does not exist for %s branch .') % (cf_record.employee_id.job_branch_id.name))
                    cf_record.cf_status = '5'

        return True

    def auto_compute_encashment_carry_forward(self):
        """method to auto compute carry forward and encashment"""

        encashment_periods = self.env['kw_set_encashment_period'].search([])
        error_log, update_record_log = [], []
        for record in encashment_periods:
            if encashment_periods:
                try:
                    record.action_process_carry_forward()
                    update_record_log.append(
                        "## start_rec ## auto-compute of fiscal year : %s " % (record.financial_year_id.code))
                except Exception as e:
                    # print(str(e))
                    error_log.append("%s, %s: %s" % (record.financial_year_id.code, record.id, str(e)))
                    continue

        # #insert into log table -- and if error log exists send mail to configured email-id
        if error_log or update_record_log:
            try:
                self.env['kw_kwantify_integration_log'].sudo().create(
                    {'name': 'Leave Carry Forward & Encashment Computation',
                     'error_log': str(error_log) if error_log else '',
                     'update_record_log': str(update_record_log),
                     'request_params': "",
                     'response_result': ""
                     })
            except Exception as e:
                # print(str(e))
                pass

        return True

    def action_kw_compute_cf_encashment_window_server_action(self):
        encashment_period_id = self.search([],order='id desc', limit=1)
        encashment_period_id.action_compute_encashment_carry_forward()
        view_id = self.env.ref('kw_hr_leaves.kw_approval_encashment_period_list').id
        return {
            'name': 'Carry Forward & Encashment',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_compute_cf_encashment',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'context': {'create': False,'edit': False,'import': False,'toolbar':False,'search_default_current_financial_year':1},
            'domain': [('employee_id.active','=',True),('encashment_eligible','=',True),('employee_id.user_id.company_id','=',self.env.user.company_id.id)],
            'target': 'self',
        }