from odoo import models, fields, api
from calendar import monthrange
from math import floor
from dateutil.relativedelta import relativedelta


class Arrear(models.Model):
    _name = 'arrear.arrear'
    _description = 'Arrear'
    _rec_name = 'employee_id' or 'New'


    employee_id = fields.Many2one('hr.employee', 'Employee')
    centre_id = fields.Many2one('res.branch', 'Centre')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    # payslip_id = fields.Many2one('hr.payslip', 'Payslip')
    arrear_type = fields.Selection([('dr', 'DR'), ('promotion', 'Promotion'),
                                    ('basic_inc', 'Basic Increment'), ('da_inc', 'DA Increment')], 
                                    'Arrear Type')
    arrear_due_ids = fields.One2many('arrear.due', 'arrear_id', 'Due', ondelete='cascade')
    arrear_drawn_ids = fields.One2many('arrear.drawn', 'arrear_id', 'Drawn', ondelete='cascade')
    arrear_payable_ids = fields.One2many('arrear.payable', 'arrear_id', 'Payable', ondelete='cascade')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State', default='draft')
    confirm_date = fields.Date('Credit Date')
    batch_id = fields.Many2one('arrear.batch', 'Batch')

    def get_filtered_contract(self):
        contract_ids = self.env['hr.contract'].search([('state', 'in', ('open','close'))])
        filtered_contract_ids = contract_ids\
                                        .filtered(lambda x: (x.state=='open' and (self.date_to >= x.date_start >= self.date_from)) 
                                                    or (x.state=='close' and (self.date_to >= x.date_end >= self.date_from)))

        return filtered_contract_ids

    
    @api.onchange('arrear_type')
    def onchange_date_from_to(self):
        if self.date_from and self.date_to and self.arrear_type:
            
            technical_resig_emp_ids = []
            filtered_contract_ids = self.get_filtered_contract()
            filtered_emp_ids = filtered_contract_ids.mapped('employee_id.id')
            for emp in self.env['hr.employee'].search([('id', 'in', filtered_emp_ids)]):
                technical_resig = emp.exit_history.filtered(lambda x: (self.date_from <= x.exit_date <= self.date_to)
                                                        and (x.exit_type == 'technical resignation'))
                if technical_resig:
                    technical_resig_emp_ids.append(emp.id)
            if self.arrear_type == 'dr':
                return {'domain': {'employee_id': [('id', 'in', technical_resig_emp_ids)]}}
            elif self.arrear_type == 'promotion':
                emp_ids = filtered_contract_ids.mapped('employee_id.id')
                promotion_emp_ids = [x for x in emp_ids if x not in technical_resig_emp_ids]
                return {'domain': {'employee_id': [('id', 'in', promotion_emp_ids)]}}
            else:
                return {'domain': {'employee_id': [('id', '!=', False)]}}
        else:
            return {'domain': {'employee_id': [('id', '=', False)]}}

    def calculate_month_days(self, date):
        y, m = date.year, date.month
        return monthrange(y, m)[1]

    def calculate_employee_age(self,employee):
        dob = employee.birthday
        current_date = fields.Date.today()
        age = floor((abs(current_date - dob).days) / 365)
        return age
    
    def check_fresher(self,employee):
        pfObj = self.env['pf.employee'].sudo().search([('employee_id', '=', employee.id)])
        return False if pfObj.eps_deduct else True

    def check_mid_month_eps_factor(self, empObj,  payslip=None, **kwargs):
        employee_age_58 = empObj.birthday + relativedelta(years=58)
        if payslip:
            mid_month_join = payslip.date_from >= empObj.date_of_join <= payslip.date_to
            mid_month_age = payslip.date_from >= employee_age_58 <= payslip.date_to
            mid_month_leave = payslip.date_from >= empObj.last_working_date <= payslip.date_to\
                                        if empObj.last_working_date else False
            if mid_month_age:
                no_of_days = (payslip.date_from - employee_age_58).days
            if mid_month_join:
                no_of_days = (payslip.date_to - empObj.date_of_join).days
            if mid_month_leave:
                no_of_days = (empObj.last_working_date - payslip.date_from).days
            if mid_month_join and mid_month_leave:
                no_of_days = (empObj.last_working_date - empObj.date_of_join).days
        else:
            date_from, date_to = kwargs.get('date_from'), kwargs.get('date_to')
            mid_month_join = date_from >= empObj.date_of_join <= date_to
            mid_month_age = date_from >= employee_age_58 <= date_to
            mid_month_leave = date_from >= empObj.last_working_date <= date_to\
                                    if empObj.last_working_date else False
            if mid_month_age:
                no_of_days = (date_from - employee_age_58).days
            if mid_month_join:
                no_of_days = (date_to - empObj.date_of_join).days
            if mid_month_leave:
                no_of_days = (empObj.last_working_date - date_from).days
            if mid_month_join and mid_month_leave:
                no_of_days = (empObj.last_working_date - empObj.date_of_join).days
        return no_of_days + 1

    def default_eps_calculation(self, empObj, BASIC, DA, payslip=None, **kwargs):
        if payslip:
            eps_per_day = (0.0833 * (BASIC+DA)) / self.calculate_month_days(payslip.date_to)
            no_of_days = self.check_mid_month_eps_factor(empObj, payslip=payslip)
            if not no_of_days:
                result = min((eps_per_day * no_of_days), 1250)
            else:
                result = min((0.0833 * (BASIC+DA)), 1250)
        else:
            eps_per_day = (0.0833 * (BASIC+DA)) / self.calculate_month_days(kwargs.get('date_to'))
            no_of_days = self.check_mid_month_eps_factor(empObj, date_from=kwargs.get('date_from'), 
                                                            date_to=kwargs.get('date_to'))
            if not no_of_days:
                result = min((eps_per_day * no_of_days), 1250)
            else:
                result = min((0.0833 * (BASIC+DA)), 1250)
        return result 

    def calculate_eps(self, employee_id, BASIC, DA, payslip=None, **kwargs):
        empObj = self.env['hr.employee'].browse(employee_id)
        age = self.calculate_employee_age(empObj)
        is_fresher = self.check_fresher(empObj)
        if payslip:
            if age > 58 or is_fresher:
                result = 0
            else:
                result = self.default_eps_calculation(empObj, BASIC, DA, payslip=payslip)
        else:
            if age > 58 or is_fresher:
                result = 0
            else:
                result = self.default_eps_calculation(empObj, BASIC, DA, date_from=kwargs.get('date_from'), 
                                                            date_to=kwargs.get('date_to'))
        return result

    def calculate_hra(self, contract_id, basic_da=None):
        result = 0
        for rec in self:
            if not basic_da:
                if contract_id.employee_hra_cat == 'x':
                    if contract_id.da > 50:
                        result = 0.3 * rec.basic_amount
                    elif contract_id.da > 25:
                        result = 0.27 * rec.basic_amount
                    else:
                        result = 0.24 * rec.basic_amount
                elif contract_id.employee_hra_cat == 'y':
                    if contract_id.da > 50:
                        result = 0.2 * rec.basic_amount
                    elif contract_id.da > 25:
                        result = 0.18 * rec.basic_amount
                    else:
                        result = 0.16 * rec.basic_amount
                elif contract_id.employee_hra_cat == 'z':
                    if contract_id.da > 50:
                        result = 0.1 * rec.basic_amount
                    elif contract_id.da > 25:
                        result = 0.09 * rec.basic_amount
                    else:
                        result = 0.08 * rec.basic_amount
                else:
                    result = 0
            else:
                if contract_id.employee_hra_cat == 'x':
                    if contract_id.da > 50:
                        result = 0.3 * contract_id.wage
                    elif contract_id.da > 25:
                        result = 0.27 * contract_id.wage
                    else:
                        result = 0.24 * contract_id.wage
                elif contract_id.employee_hra_cat == 'y':
                    if contract_id.da > 50:
                        result = 0.2 * contract_id.wage
                    elif contract_id.da > 25:
                        result = 0.18 * contract_id.wage
                    else:
                        result = 0.16 * contract_id.wage
                elif contract_id.employee_hra_cat == 'z':
                    if contract_id.da > 50:
                        result = 0.1 * contract_id.wage
                    elif contract_id.da > 25:
                        result = 0.09 * contract_id.wage
                    else:
                        result = 0.08 * contract_id.wage
                else:
                    result = 0
        return result

    def calculate_ta(self, contract_id):
        result = 0
        if ((contract_id.city_tier != 'other') and (contract_id.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                    'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                    'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                    'Pay Level 17','Pay Level 18'])):
            result = 7200 + (7200 * (contract_id.da / 100))
        elif ((contract_id.city_tier != 'other') and (contract_id.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                    'Pay Level 6','Pay Level 7','Pay Level 8'])):
            result = 3600 + (3600 * (contract_id.da / 100))
        elif ((contract_id.city_tier != 'other') and (contract_id.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
            if contract_id.wage >= 24200:
                result = 3600 + (3600 * (contract_id.da / 100))
            else:
                result = 1350 + (1350*(contract_id.da/100))
        elif ((contract_id.city_tier == 'other') and (contract_id.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                    'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                    'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                    'Pay Level 17','Pay Level 18'])):
            result = 3600 + (3600 * (contract_id.da / 100))
        elif ((contract_id.city_tier == 'other') and (contract_id.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                    'Pay Level 6','Pay Level 7','Pay Level 8'])):
            result = 1800 + (1800 * (contract_id.da / 100))
        elif ((contract_id.city_tier == 'other') and (contract_id.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
            if contract_id.wage >= 24200:
                result = 1800 + (1800 * (contract_id.da / 100))
            else:
                result = 900 + (900 * (contract_id.da / 100))
        else:
            result = 101
        return result

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        arrear_due_ids = []
        self.arrear_due_ids = False
        if self.employee_id:
            self.centre_id = self.employee_id.branch_id.id
            if self.arrear_type in ('dr', 'promotion'):
                filtered_contract_ids = self.get_filtered_contract()
                emp_contracts = filtered_contract_ids.filtered(lambda x: x.employee_id == self.employee_id)
                for contract in emp_contracts:
                    self.start_dt, self.end_dt = (self.date_from, contract.date_end) if contract.state == 'close'\
                                                        else (contract.date_start, self.date_to)
                
                    num_days = (self.end_dt - self.start_dt).days + 1
                    month_days = self.calculate_month_days(self.date_to)

                    # Basic Calculation
                    basic_per_day = contract.wage / month_days
                    self.basic_amount = basic_per_day * num_days

                    # DA Calculation
                    self.da_amount = self.basic_amount * (contract.da / 100)

                    # TA Calculation
                    ta_per_day = self.calculate_ta(contract) / month_days
                    self.ta_amount = ta_per_day * num_days

                    # HRA Calculation
                    self.hra_amount = self.calculate_hra(contract)

                    # Gross Calculation
                    self.gross_amount = self.basic_amount + self.da_amount + self.hra_amount + self.ta_amount

                    # MPF Calculation
                    self.mpf_amount = 0.12 * (self.basic_amount + self.da_amount)

                    # EPS Calculation
                    self.eps_amount = self.calculate_eps(self.employee_id.id, self.basic_amount, 
                                                            self.da_amount, date_from=self.start_dt, 
                                                            date_to=self.end_dt)
                    
                    # EPF Calculation
                    self.epf_amount = self.mpf_amount - self.eps_amount

                    arrear_due_ids.append([0, 0, {
                                'date_from': self.start_dt,
                                'date_to': self.end_dt,
                                'contract_id': contract.id,
                                'basic_amount': self.basic_amount,
                                'da_amount': self.da_amount,
                                'ta_amount': self.ta_amount,
                                'hra_amount': self.hra_amount,
                                'gross_amount': self.gross_amount,
                                'mpf_amount': self.mpf_amount,
                                'eps_amount': self.eps_amount,
                                'epf_amount': self.epf_amount
                            }])
                self.arrear_due_ids = arrear_due_ids

    @api.multi
    def compute_arrear(self):
        for rec in self:
            arrear_due_ids, arrear_drawn_ids, arrear_payable_ids = [], [], []
            rec.arrear_due_ids.unlink()
            rec.arrear_drawn_ids.unlink()
            rec.arrear_payable_ids.unlink()
            start_dt = rec.date_from
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])

            if self.arrear_type in ('basic_inc', 'da_inc'):

                # Due
                rdelta = relativedelta(rec.date_to, start_dt)
                month_num = (rdelta.years * 12) + rdelta.months
                payslip_list = []

                for r in range(month_num + 1):
                    start_dt += relativedelta(months=r)
                    end_dt = (start_dt + relativedelta(months=1)) - relativedelta(days=1)

                    num_days = (end_dt - start_dt).days + 1
                    month_days = self.calculate_month_days(start_dt)

                    # Basic Calculation
                    basic_per_day = contract.wage / month_days
                    rec.basic_amount = basic_per_day * num_days

                    # DA Calculation
                    rec.da_amount = rec.basic_amount * (contract.da / 100)

                    # TA Calculation
                    ta_per_day = self.calculate_ta(contract) / month_days
                    rec.ta_amount = ta_per_day * num_days

                    # HRA Calculation
                    rec.hra_amount = self.calculate_hra(contract, basic_da=True)

                    # Gross Calculation
                    rec.gross_amount = rec.basic_amount + rec.da_amount + rec.hra_amount + rec.ta_amount

                    # MPF Calculation
                    rec.mpf_amount = 0.12 * (rec.basic_amount + rec.da_amount)

                    # EPS Calculation
                    rec.eps_amount = self.calculate_eps(rec.employee_id.id, rec.basic_amount, 
                                                            rec.da_amount, date_from=start_dt, 
                                                            date_to=end_dt)
                    
                    # EPF Calculation
                    rec.epf_amount = rec.mpf_amount - rec.eps_amount

                    arrear_due_ids.append([0, 0, {
                        'date_from': start_dt,
                        'date_to': end_dt,
                        'basic_amount': rec.basic_amount,
                        'da_amount': rec.da_amount,
                        'ta_amount': rec.ta_amount,
                        'hra_amount': rec.hra_amount,
                        'gross_amount': rec.gross_amount,
                        'mpf_amount': rec.mpf_amount,
                        'eps_amount': rec.eps_amount,
                        'epf_amount': rec.epf_amount
                    }])

                    payslip_list.append(self.env['hr.payslip'].search([('date_from', '>=', start_dt),
                                                                        ('date_to', '<=', end_dt),
                                                                        ('state', '=', 'done'),
                                                                        ('employee_id', '=', self.employee_id.id)]))

                rec.arrear_due_ids = arrear_due_ids
                
                # Drawn
                for payslip in payslip_list:
                    arrear_drawn_ids.append([0, 0, {
                        'payslip_id': payslip.id,
                        'date_from': payslip.date_from,
                        'date_to': payslip.date_to,
                        'basic_amount': payslip.line_ids.filtered(lambda x: x.code == 'BASIC').total,
                        'da_amount': payslip.line_ids.filtered(lambda x: x.code == 'DA').total,
                        'ta_amount': payslip.line_ids.filtered(lambda x: x.code == 'TA').total,
                        'hra_amount': payslip.line_ids.filtered(lambda x: x.code == 'HRA').total,
                        'gross_amount': payslip.line_ids.filtered(lambda x: x.code == 'GROSS').total,
                        'mpf_amount': payslip.line_ids.filtered(lambda x: x.code == 'MPF').total,
                        'epf_amount': payslip.line_ids.filtered(lambda x: x.code == 'EPF').total
                    }])
                
                rec.arrear_drawn_ids = arrear_drawn_ids

                # Arrear Payable
                total_basic_due = sum(rec.arrear_due_ids.mapped('basic_amount'))
                total_da_due = sum(rec.arrear_due_ids.mapped('da_amount'))
                total_hra_due = sum(rec.arrear_due_ids.mapped('hra_amount'))
                total_ta_due = sum(rec.arrear_due_ids.mapped('ta_amount'))
                total_mpf_due = sum(rec.arrear_due_ids.mapped('mpf_amount'))
                total_epf_due = sum(rec.arrear_due_ids.mapped('epf_amount'))
                total_basic_drawn = sum(rec.arrear_drawn_ids.mapped('basic_amount'))
                total_da_drawn = sum(rec.arrear_drawn_ids.mapped('da_amount'))
                total_hra_drawn = sum(rec.arrear_drawn_ids.mapped('hra_amount'))
                total_ta_drawn = sum(rec.arrear_drawn_ids.mapped('ta_amount'))
                total_mpf_drawn = sum(rec.arrear_drawn_ids.mapped('mpf_amount'))
                total_epf_drawn = sum(rec.arrear_drawn_ids.mapped('epf_amount'))

                diff_basic_amount = total_basic_due - total_basic_drawn
                diff_da_amount = total_da_due - total_da_drawn
                diff_hra_amount = total_hra_due - total_hra_drawn
                diff_ta_amount = total_ta_due - total_ta_drawn

                arrear_payable_ids.append([0, 0, {
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'diff_basic_amount': diff_basic_amount,
                    'diff_da_amount': diff_da_amount,
                    'diff_hra_amount': diff_hra_amount,
                    'diff_ta_amount': diff_ta_amount,
                    'diff_total_arrear_amount': diff_basic_amount + diff_da_amount +\
                                                diff_hra_amount + diff_ta_amount,
                    'diff_mpf_amount': total_mpf_due - total_mpf_drawn,
                    'diff_epf_amount': total_epf_due - total_epf_drawn,
                }])

                rec.arrear_payable_ids = arrear_payable_ids

        return True

    @api.multi
    def confirm_arrear(self):
        for rec in self:
            rec.write({'state': 'confirm', 'confirm_date': fields.Date.today()})
        return True


class DRArrearDue(models.Model):
    _name = 'arrear.due'
    _description = 'Arrear due'

    contract_id = fields.Many2one('hr.contract', 'Contract')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    basic_amount = fields.Float('Basic')
    da_amount = fields.Float('DA')
    hra_amount = fields.Float('HRA')
    ta_amount = fields.Float('TA')
    gross_amount = fields.Float('Gross')
    mpf_amount = fields.Float('Employee PF')
    eps_amount = fields.Float('Employer PS')
    epf_amount = fields.Float('Employer PF')
    arrear_id = fields.Many2one('arrear.arrear', 'Arrear')

class DRArrearDrawn(models.Model):
    _name = 'arrear.drawn'
    _description = 'Arrear drawn'

    contract_id = fields.Many2one('hr.contract', 'Contract')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    basic_amount = fields.Float('Basic')
    da_amount = fields.Float('DA')
    hra_amount = fields.Float('HRA')
    ta_amount = fields.Float('TA')
    gross_amount = fields.Float('Gross')
    mpf_amount = fields.Float('Employee PF')
    epf_amount = fields.Float('Employer PF')
    payslip_id = fields.Many2one('hr.payslip')
    arrear_id = fields.Many2one('arrear.arrear', 'Arrear')

    @api.onchange('payslip_id')
    def onchange_payslip(self):
        if self.payslip_id:
            self.date_from, self.date_to = self.payslip_id.date_from, self.payslip_id.date_to
            self.basic_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'BASIC').mapped('total'))
            self.da_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'DA').mapped('total'))
            self.hra_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'HRA').mapped('total'))
            self.ta_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'TA').mapped('total'))
            self.gross_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'GROSS').mapped('total'))
            self.mpf_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'MPF').mapped('total'))
            self.epf_amount = sum(self.payslip_id.line_ids.filtered(lambda r: r.code == 'EPF').mapped('total'))

class DRArrearPayable(models.Model):
    _name = 'arrear.payable'
    _description = 'Arrear payable'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    diff_basic_amount = fields.Float('Diff Basic')
    diff_da_amount = fields.Float('Diff DA')
    diff_hra_amount = fields.Float('Diff HRA')
    diff_ta_amount = fields.Float('Diff TA')
    diff_total_arrear_amount = fields.Float('Total Arrear')
    diff_mpf_amount = fields.Float('Diff Employee PF')
    diff_epf_amount = fields.Float('Diff Employer PF')
    arrear_id = fields.Many2one('arrear.arrear', 'Arrear')


class ArrearBatch(models.Model):
    _name = 'arrear.batch'
    _description = 'Arrear Batch'

    name = fields.Char('Name')
    arrear_type = fields.Selection([('basic_inc', 'Basic Increment'), 
                                    ('da_inc', 'DA Increment')], 'Arrear Type')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    confirm_date = fields.Date('Credit Date')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], 'State', default='draft')
    arrear_ids = fields.One2many('arrear.arrear', 'batch_id', 'Arrear')
    center_id = fields.Many2one('res.branch', 'Center', 
                                    domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)])
    @api.multi
    def confirm_batch(self):
        for rec in self.arrear_ids:
            rec.confirm_arrear()
        self.write({"state": 'done'})
        return True
