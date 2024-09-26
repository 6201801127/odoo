from odoo import api, fields, models #, tools, _
from odoo.exceptions import ValidationError,UserError
# import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


def calculate_days(joining_date: date, leave_date: date, start_date: date, end_date: date) -> int:
    days = 0
    if all((joining_date, leave_date, start_date, end_date)):
        if (start_date <= joining_date <= end_date) and (start_date <= leave_date <= end_date):
            days = (leave_date - joining_date).days
        elif (start_date <= joining_date <= end_date):
            days = (end_date - joining_date).days
        elif (start_date <= leave_date <= end_date):
            days = (leave_date - start_date).days
        else:
            days = (end_date - start_date).days
        return days + 1

class Reimbursement(models.Model):

    _name = "reimbursement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Reimbursement"
    _order = 'create_date desc'

    @api.model
    def default_get(self, field_list):
        result = super(Reimbursement, self).default_get(field_list)
        ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result



    # @api.constrains('name')
    @api.onchange('reimbursement_type_id')
    def _onchange_name(self):
        for rec in self:
            rec.date_range = False
            if rec.reimbursement_type_id:
                gr_id = self.env['reimbursement.configuration'].search(
                                    [('reimbursement_type_id', '=', rec.reimbursement_type_id.id), ('pay_level_ids', 'in', rec.employee_id.job_id.pay_level_id.id), 
                                    ('job_ids', 'in', rec.employee_id.job_id.id), # ('branch_id', '=', rec.branch_id.id),
                                    ('employee_type', '=', rec.employee_id.employee_type)], order='reimbursement_type_id desc', limit=1)
                # print('==========================reimb=================================', gr_id)
                # if not gr_id:
                #     gr_id = self.env['reimbursement.configuration'].search(
                #                         [('name', '=', rec.name), ('pay_level_ids', 'in', rec.employee_id.job_id.pay_level_id.id), 
                #                         ('branch_id', '=', rec.branch_id.id)], order='name desc', limit=1)
                # print('==========================reimb=================================', gr_id.id)
                if gr_id.reimbursement_type_id.code =='el_encashment':
                    domain = {'domain': {'date_range': [('type_id', '=', gr_id.date_range_type.id),('date_end', '>=', datetime.now().date()),('date_start', '<=', datetime.now().date())]}}

                elif gr_id.reimbursement_type_id.code not in ['tuition_fee','hostel']:
                    domain = {'domain': {'date_range': [('type_id', '=', gr_id.date_range_type.id),('date_end', '<=', datetime.now().date())]}}
                else:
                    domain = {'domain': {'date_range': [('type_id', '=', gr_id.date_range_type.id),('date_start', '<=', datetime.now().date())]}}
                return domain
    @api.multi
    def compute_attendance_days(self):
        for rec in self:
            end_date = rec.date_range.date_end
            attendance = self.env['reimbursement.attendence'].sudo()\
                                    .search([('employee_id','=',rec.employee_id.id),
                                            ('month', '=', end_date.strftime('%m')),
                                            ('year', '=', str(end_date.year))], limit=1)
            rec.attendance_days = attendance.present_days if attendance else 0
        return True


    # name = fields.Selection([
    #     ('lunch', 'Lunch Subsidy'),
    #     ('telephone', 'Telephone Reimbursement'),
    #     ('broadband', 'Broadband Reimbursement'),
    #     ('mobile', 'Mobile Reimbursement'),
    #     ('medical', 'Medical Reimbursement'),
    #     ('tuition_fee', 'Tuition Fee claim'),
    #     ('hostel', 'Hostel claim'),
    #     ('briefcase', 'Briefcase Reimbursement'),
    #     ('quarterly', 'Newspaper Reimbursements'),
    #     ('el_encashment', 'EL Encashment'),
    # ], string='Reimbursement Type', store=True, track_visibility='always')

    reimbursement_type_id = fields.Many2one('reimbursement.type','Reimbursement Type',required=True,track_visibility='always')
    name = fields.Char("Reimbursement Name",related="reimbursement_type_id.code",track_visibility='always',store=True)

    reimbursement_sequence = fields.Char('Reimbursement number', track_visibility='always')
    employee_id = fields.Many2one('hr.employee', store=True, track_visibility='always', string='Requested By')
    job_id = fields.Many2one('hr.job', string='Post', store=True, track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Center', store=True, track_visibility='always')
    department_id = fields.Many2one('hr.department', string='Department', store=True, track_visibility='always')

    el_in_account = fields.Float('Maximum EL')
    el_taking = fields.Float('EL Taking')

    claimed_amount = fields.Float(string='Claimed Amount', track_visibility='always')
    approved_amount = fields.Float(string='Approved Amount', track_visibility='always')
    net_amount = fields.Float(string='Eligible Amount', store=True, compute='compute_net_amount', track_visibility='always')
    date_range_type = fields.Many2one('date.range.type', string='Applicable Period', track_visibility='always')
    date_range = fields.Many2one('date.range', string='Date Range', track_visibility='always')

    amount_lunch = fields.Float(string='Daily Eligible Amount', track_visibility='always')
    maximum_eligible_amount = fields.Char(string='Maximum Eligible Amount', compute='compute_net_amount')
    lunch_tds_amt = fields.Float('Amount for TDS', track_visibility='always')
    working_days = fields.Char(string='Number of Days', track_visibility='always')
    tution_document = fields.Binary(string='Document', track_visibility='always')

    # amount_tel = fields.Float(string='Claimed Amount')
    # amount_mob = fields.Float(string='Claimed Amount')
    service_provider = fields.Many2one('reimbursement.service.provider',string='Service Provider', track_visibility='always')
    phone = fields.Binary(string='Attachment', track_visibility='always')
    bill_no = fields.Char(string='Bill number', track_visibility='always')
    bill_due_date = fields.Date(string='Bill Due Date', track_visibility='always')
    mobile_no = fields.Char(string='Telephone or Landline number')

    invoice_number = fields.Char('Invoice Number')
    invoice_date = fields.Date('Invoice Date')
    last_brief_date = fields.Date('Previous Claim Date')
    billing_from = fields.Date('Billing From')
    billing_to = fields.Date('Billing To')

    brief_date = fields.Date(string='Date')
    no_of_months = fields.Integer(string='No of months', default=12)
    attach_news = fields.Binary()
    remarks = fields.Text(string='Remarks: ', track_visibility='always')

    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Submitted'), ('forwarded', 'Forwarded'),
                              ('approved', 'Approved'), ('rejected', 'Rejected')
                              ], required=True, default='draft', track_visibility='always', string='Status')
    attendance_days = fields.Integer(compute='compute_attendance_days')
    hostel_exempt_amount = fields.Float(string='Hostel Exempt Amount')
    tuition_exempt_amount = fields.Float(string='Tuition Exempt Amount')
    check_manager = fields.Boolean('Manager', compute='compute_net_amount')
    check_admin = fields.Boolean('Admin', compute='compute_net_amount')
    working_days_approver = fields.Integer('Number of days as per Approver', track_visibility='onchange')
    approve_amount_approver = fields.Float()
    payment_advice = fields.Boolean('Payment Advice', track_visibility='onchange')
    dependent_ids = fields.One2many('employee.relative.reimbursement', 'reimbursement_id', 'Dependents')

    @api.multi
    def create_payment_advices(self):
        if self.env.user.has_group('reimbursement_stpi.group_finance_authority'):
            line_ids, emp_lis = [], []
            for rec in self.filtered(lambda x: x.payment_advice == False):
                if any(tuple(filter(lambda x: x.state != 'approved', self))):
                    raise ValidationError('You can create payment advice for approved reimbursements.')
                if rec.employee_id.id not in emp_lis:
                    line_ids.append((0, 0, {
                        'employee_id': rec.employee_id.id,
                        'bank_name': rec.employee_id.bank_account_id.bank_id.name,
                        'account_no': rec.employee_id.bank_account_id.acc_number,
                        'ifsc_code': rec.employee_id.bank_account_id.bank_id.bic or '',
                        'amount': rec.approved_amount,
                    }))
                    emp_lis.append(rec.employee_id.id)
                else:
                    # filter(lambda x: x[2]['employee_id'] == rec.employee_id.id, line_ids).amount += rec.approved_amount
                    for line in line_ids:
                        if line[2]['employee_id'] == rec.employee_id.id:
                            line[2]['amount'] += rec.approved_amount
                rec.payment_advice = True
            self.env['reimbursement.payment.advice'].create({
                'date': fields.Date.today(),
                'name': 'Reimbursement: Payment Advice',
                'line_ids': line_ids
            })
            self.env.user.notify_info('Payment advice has been created successfully.')
            return True
        else:
            raise ValidationError('You are not authorized to create payment advice.')

    # @api.onchange('claimed_amount','net_amount')
    # def set_approved_amount(self):
    #     if self.claimed_amount > 0:
    #         self.approved_amount = self.claimed_amount
    #     else:
    #         self.approved_amount = self.net_amount

    # @api.constrains('employee_id')
    @api.onchange('employee_id')
    def onchange_emp_get_base(self):
        # for rec in self:
        reimbursement_type_domain = [('code','=','lunch')]
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.branch_id = self.employee_id.branch_id

            if self.employee_id.employee_type == 'regular':
                reimbursement_type_domain = []
        else:
            self.job_id = False
            self.department_id = False
            self.branch_id = False

        return {
            'domain':{'reimbursement_type_id':reimbursement_type_domain}
        }
    
    @api.multi
    def add_dependents(self):
        for rec in self:
            if rec.reimbursement_type_id.code in ('tuition_fee', 'hostel'):
                depend_ids = rec.env['employee.relative'].search([('employee_id', '=', rec.employee_id.id),
                                                                    ('relate_type.name', 'in', ('Son', 'Daughter'))])
                rec.dependent_ids.unlink()

            if rec.reimbursement_type_id.code == 'tuition_fee':
                tuition_depend_ids = [[0, 0, {
                    'name': r.name,
                    'dob': r.birthday,
                    'reimbursement_id': rec.id}] for r in depend_ids.filtered(lambda x: x.tuition)]
                rec.sudo().write({'dependent_ids': tuition_depend_ids})

            if rec.reimbursement_type_id.code == 'hostel':
                hostel_depend_ids = [[0, 0, {
                    'name': r.name,
                    'dob': r.birthday,
                    'reimbursement_id': rec.id}] for r in depend_ids.filtered(lambda x: x.hostel)]
                rec.sudo().write({'dependent_ids': hostel_depend_ids})
        return True

    # @api.onchange('name','working_days')
    @api.constrains('reimbursement_type_id','working_days','employee_id')
    def _validate_name(self):
        for rec in self:
            rec.working_days_approver = rec.working_days
            relative_ids = self.env['employee.relative'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                        ('relate_type.name', 'in', ['Son', 'Daughter'])])
            # if rec.reimbursement_type_id.code == 'el_encashment':
            #     el_count = self.env['reimbursement'].sudo().search([('employee_id', '=', rec.employee_id.id),('reimbursement_type_id','=',rec.reimbursement_type_id.id)]) - rec
            #     if len(el_count) >= 6:
            #         raise ValidationError("You can take 6 EL Encashment in a service period.")
            if rec.reimbursement_type_id.code == 'lunch':
                end_date = rec.date_range.date_end
                reimbursement = self.env['reimbursement.configuration'].sudo().search([('reimbursement_type_id', '=', rec.reimbursement_type_id.id), # ('branch_id', '=', rec.branch_id.id),
                                                                    ('pay_level_ids', 'in', rec.job_id.pay_level_id.id),
                                                                    ('job_ids', 'in', rec.job_id.id),
                                                                    ('employee_type', '=', rec.employee_id.employee_type)],
                                                                    order='reimbursement_type_id desc', limit=1)
                if reimbursement.attendance_required:
                    attendance = self.env['reimbursement.attendence'].sudo()\
                                    .search([('employee_id','=',rec.employee_id.id),
                                            ('month', '=', end_date.strftime('%m')),
                                            ('year', '=', str(end_date.year))], limit=1)
                    # if attendance:
                    #     if rec.working_days and int(rec.working_days) > attendance.present_days:
                    #         raise ValidationError("No. of days should be less than your attendance working days.")

            if rec.reimbursement_type_id.code == 'hostel':
                if len(relative_ids.filtered(lambda x: x.hostel)) == 0:
                    raise ValidationError("You are not eligible to apply hostel reimbursement.")
            if rec.reimbursement_type_id.code == 'tuition_fee':
                if len(relative_ids.filtered(lambda x: x.tuition)) == 0:
                    raise ValidationError("You are not eligible to apply tuition reimbursement.")
            if rec.reimbursement_type_id.code == 'el_encashment' and rec.employee_id.employee_type == 'regular' and rec.employee_id.state == 'test_period':
                raise ValidationError("You are not allowed to apply for EL Encashment during probation.")

    @api.onchange('reimbursement_type_id','employee_id','date_range')
    def only_onchange_name_employee_date(self):
        for rec in self:
            rec.claimed_amount = 0
            rec.net_amount = 0
            attendance_ids = self.env['reimbursement.attendence'].search(
                [('employee_id', '=', rec.employee_id.id), ('date_related_month', '>=', rec.date_range.date_start),
                 ('date_related_month', '<=', rec.date_range.date_end)])
            days_present= sum(attendance_ids.mapped('present_days'))
            if rec.employee_id and rec.reimbursement_type_id.code == 'lunch':
                lunch_conf = self.env['reimbursement.configuration'].sudo()\
                                    .search([('reimbursement_type_id.code', '=', 'lunch'),
                                            ('pay_level_ids', 'in', rec.employee_id.job_id.pay_level_id.id), 
                                            ('job_ids', 'in', rec.employee_id.job_id.id),
                                            ('employee_type', '=', rec.employee_id.employee_type)], limit=1)
                rec.amount_lunch = lunch_conf.per_day_amount
                rec.taxable_per_day = lunch_conf.taxable_per_day_amount
                rec.working_days = days_present if days_present else rec.working_days
                rec.claimed_amount = float(int(rec.working_days) * rec.amount_lunch)
                rec.lunch_tds_amt = float(int(rec.working_days) * rec.taxable_per_day)
            previous = self.env['reimbursement'].search([('employee_id', '=', rec.employee_id.id),
                                                            ('state', '!=', 'rejected'),
                                                            ('reimbursement_type_id.code', '=', 'briefcase')],
                                                        limit=1,order="brief_date desc")
            if previous:
                if previous.brief_date:
                    rec.last_brief_date = previous.brief_date

    # @api.constrains('reimbursement_type_id','employee_id','date_range')
    @api.onchange('reimbursement_type_id','employee_id','date_range')
    def onchng_name_emp_date(self):
        for rec in self:
            # if rec.employee_id and rec.name == 'lunch':
            #     pass
                # count = 0
                # serch_id = self.env['reimbursement.attendence'].search([('employee_id', '=', rec.employee_id.id),('date_related_month', '>=', rec.date_range.date_start),('date_related_month', '<', rec.date_range.date_end)])
                # for i in serch_id:
                #     count += i.present_days
                # rec.amount_lunch = 75
                # rec.working_days = count
                # rec.claimed_amount = float(rec.working_days * 75)
                # rec.lunch_tds_amt = float(rec.working_days * 50)
            if rec.employee_id:
                if rec.reimbursement_type_id.code == 'telephone' or rec.reimbursement_type_id.code == 'mobile':
                    rec.mobile_no = rec.employee_id.mobile_phone
                if rec.reimbursement_type_id.code == 'el_encashment':
                    sum = 0
                    serch_id = self.env['hr.leave.report'].search([('employee_id', '=', rec.employee_id.id),('holiday_status_id.name', '=', 'Earned Leave')])
                    for lv in serch_id:
                        sum += lv.number_of_days
                    rec.el_in_account = sum


    def get_late_coming_report(self):
        lst = []
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        print('===========ids===============', active_ids)
        for employee in self.env['reimbursement'].browse(active_ids):
            print('===========id===============', employee.id)
            lst.append(employee.id)
        print('===========lst===============',lst)
        return self.env['reimbursement'].search([('id', 'in', lst)])

    @api.constrains('working_days')
    @api.onchange('working_days', 'working_days_approver')
    def onchange_working_days(self):
        for rec in self:
            if rec.employee_id and rec.reimbursement_type_id.code == 'lunch' and rec.working_days and rec.date_range:
                working_day_count = rec.working_days_approver
                lunch_conf = self.env['reimbursement.configuration'].sudo()\
                                    .search([('reimbursement_type_id.code', '=', 'lunch'),
                                            ('pay_level_ids', 'in', rec.employee_id.job_id.pay_level_id.id), 
                                            ('job_ids', 'in', rec.employee_id.job_id.id),
                                            ('employee_type', '=', rec.employee_id.employee_type)], limit=1)
                rec.amount_lunch = lunch_conf.per_day_amount
                rec.taxable_per_day = lunch_conf.taxable_per_day_amount
                rec.claimed_amount = float(working_day_count * rec.amount_lunch)
                rec.lunch_tds_amt = float(working_day_count * rec.taxable_per_day)
                y, m = rec.date_range.date_end.year, rec.date_range.date_end.month
                days = calendar.monthrange(y, m)[1]
                if float(working_day_count) > float(days):
                    raise ValidationError(
                        "You can claim for %s" % rec.reimbursement_type_id.name + ", maximum of  %s" % (days) + " days")

    @api.constrains('reimbursement_type_id','employee_id','date_range','el_taking')
    def validate_el_encashment(self):
        for reimbursement in self:
            if reimbursement.reimbursement_type_id.code == 'el_encashment':
                last_approved_el_reimbursement = self.search([('state','=','approved'),
                                                            ('employee_id','=',reimbursement.employee_id.id),
                                                            ('reimbursement_type_id.code','=','el_encashment')]) - reimbursement
                if last_approved_el_reimbursement and \
                    reimbursement.date_range.date_start < last_approved_el_reimbursement.date_range.date_start + relativedelta(years=2):
                    raise ValidationError(f"""You can't apply EL encashment before {(last_approved_el_reimbursement.date_range.date_start + relativedelta(years=2)).year}""")

    @api.depends('claimed_amount','el_taking','reimbursement_type_id','date_range')
    def compute_net_amount(self):
        for rec in self:
            if self.env.user.has_group('reimbursement_stpi.group_approving_authority'):
                rec.check_manager = True
            if self.env.uid == 2:
                rec.check_admin = True
            gr_id = self.env['reimbursement.configuration'].search([('reimbursement_type_id', '=', rec.reimbursement_type_id.id), ('job_ids', 'in', rec.employee_id.job_id.id),
                                                                    # ('branch_id', '=', rec.employee_id.branch_id.id),
                                                                    ('pay_level_ids', 'in', rec.employee_id.job_id.pay_level_id.id),
                                                                    ('employee_type', '=', rec.employee_id.employee_type)],
                                                                    order='reimbursement_type_id desc', limit=1)

            child_ids = self.env['employee.relative'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                        ('relate_type.name', 'in', ['Son', 'Daughter'])])
            contract = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                    ('state', '=', 'open')], limit=1)
            if gr_id:
                if not gr_id.full:
                    rec.maximum_eligible_amount = str(gr_id.allowed)
                    if rec.employee_id and rec.reimbursement_type_id.code == 'tuition_fee':
                        divyang_child_ids = child_ids.filtered(lambda x: x.divyang)
                        twins_child_ids = child_ids.filtered(lambda x: x.twins and x.tuition).sorted(key=lambda x: x.id)
                        twin_child_pos = child_ids.mapped('id').index(twins_child_ids.mapped('id')[0])\
                                                if len(twins_child_ids) > 0 else None
                        total_child = min(len(child_ids.filtered(lambda x: x.tuition)), 2) if len(twins_child_ids) == 0\
                                        else (2 if twin_child_pos == 0 else 3)

                        # Usecase - 1 (If all children are normal)
                        if not any(child_ids.mapped('divyang')) and not any(child_ids.mapped('twins')):
                            allowed_amount = (int(gr_id.allowed) * total_child) * int(rec.no_of_months)
                            exempt_amount = (100 * total_child) * int(rec.no_of_months)
                        
                        # Usecase - 2 (If out of two one child is divyang)
                        # Usecase - 3 (If all children are divyang)
                        elif any(child_ids.mapped('divyang')) and not any(child_ids.mapped('twins')):
                            allowed_amount = ( (int(gr_id.allowed) * (len(divyang_child_ids) * 2) ) * int(rec.no_of_months) +\
                                                (int(gr_id.allowed) * (total_child - len(divyang_child_ids))) * int(rec.no_of_months) )
                            exempt_amount = (100 * total_child) *  int(rec.no_of_months)
                        
                        # Usecase - 4 (If first child is twins)
                        # Usecase - 5 (If second child is twins)
                        elif not any(child_ids.mapped('divyang')) and any(child_ids.mapped('twins')):
                            allowed_amount = (int(gr_id.allowed) * total_child) * int(rec.no_of_months)
                            exempt_amount = (100 * total_child) *  int(rec.no_of_months)
                        
                        # Usecase - 6 (If first child is twins and one of them is divyang)
                        # Usecase - 7 (If first child is twins and both of them is divyang)
                        elif any(child_ids.mapped('divyang')) and twin_child_pos == 0:
                            allowed_amount = ( (int(gr_id.allowed) * (len(divyang_child_ids) * 2)) * int(rec.no_of_months) +\
                                                int(gr_id.allowed) * (total_child - len(divyang_child_ids)) * int(rec.no_of_months) )
                            exempt_amount = (100 * total_child) *  int(rec.no_of_months)

                        # Usecase - 8 (If second child is twins and one of them is divyang)
                        elif any(child_ids.mapped('divyang')) and twin_child_pos > 0:
                            allowed_amount = ( ((int(gr_id.allowed) * (len(divyang_child_ids) * 2)) * int(rec.no_of_months)) +\
                                                (int(gr_id.allowed) * (total_child - len(divyang_child_ids)) * int(rec.no_of_months)) )
                            exempt_amount = (100 * total_child) *  int(rec.no_of_months)

                        rec.net_amount = min(rec.claimed_amount, allowed_amount)
                        rec.tuition_exempt_amount = exempt_amount
                    elif rec.employee_id and rec.reimbursement_type_id.code == 'hostel':
                        twins_child_ids = child_ids.filtered(lambda x: x.twins and x.hostel).sorted(key=lambda x: x.id)
                        twin_child_pos = child_ids.mapped('id').index(twins_child_ids.mapped('id')[0])\
                                                if len(twins_child_ids) > 0 else None
                        total_child = min(len(child_ids.filtered(lambda x: x.hostel)), 2) if len(twins_child_ids) == 0\
                                        else (2 if twin_child_pos == 0 else 3)

                        # Usecase - 1 (If all children are normal)
                        if not any(child_ids.mapped('twins')):
                            allowed_amount = (int(gr_id.allowed) * total_child) * int(rec.no_of_months)
                            exempt_amount = (300 * total_child) * int(rec.no_of_months)
                        # Usecase - 2 (If first child is twins)
                        # Usecase - 3 (If second child is twins)
                        if any(child_ids.mapped('twins')):
                            allowed_amount = (int(gr_id.allowed) * total_child) * int(rec.no_of_months)
                            exempt_amount = (300 * total_child) * int(rec.no_of_months)

                        rec.net_amount = min(rec.claimed_amount, allowed_amount)
                        rec.hostel_exempt_amount = exempt_amount
                    else:
                        rec.net_amount = min(int(rec.claimed_amount), int(gr_id.allowed))
                else:
                    rec.maximum_eligible_amount = 'No Limit'
                    rec.net_amount = int(rec.claimed_amount)
            else:
                rec.maximum_eligible_amount = 'No Limit'
                rec.net_amount = int(rec.claimed_amount)

            if rec.employee_id and rec.reimbursement_type_id.code == 'medical':
                joining_date = rec.employee_id.date_of_join
                exit_date = rec.employee_id.exit_history.sorted(key=lambda x: x.exit_date)[-1].exit_date if rec.employee_id.exit_history else rec.date_range.date_end
                present_days = calculate_days(joining_date, exit_date, rec.date_range.date_start, rec.date_range.date_end)
                calc_basic = 0
                if contract:
                    if contract.change_log_ids:
                        if rec.date_range:
                            start_year = rec.date_range.date_start.year
                            january_data = contract.change_log_ids\
                                            .filtered(lambda r: r.date.strftime('%B')=='January' and r.date.year == start_year)\
                                            .sorted(key = lambda r:r.date,reverse=True)
                            if january_data:
                                calc_basic = int(january_data[0].basic_da)/4
                            else:
                                calc_basic = int(contract.updated_basic)/4
                    else:
                        calc_basic = int(contract.updated_basic)/4
                # else:
                total_days = (rec.date_range.date_end - rec.date_range.date_start).days + 1 if rec.date_range else 1
                per_day_amount = calc_basic / total_days
                eligible_amount = (per_day_amount * present_days) if present_days else calc_basic
                rec.net_amount = min(int(rec.claimed_amount), eligible_amount)
            
            if rec.employee_id and rec.reimbursement_type_id.code == 'el_encashment':
                now = datetime.now()
                day = int(calendar.monthrange(now.year, now.month)[1])
                if contract:
                    rec.net_amount = int((contract.updated_basic)/day) * int(rec.el_taking)
        return True



    @api.multi
    def unlink(self):
        for data in self:
            if data.state not in ('draft', 'rejected'):
                raise UserError(
                    'You cannot delete a Reimbursement which is not in draft or Rejected state')
        return super(Reimbursement, self).unlink()



    @api.multi
    def button_submit(self):
        for rec in self:
            # search_id = self.env['reimbursement'].search([('employee_id', '=', rec.employee_id.id), ('name', '=', rec.name), ('date_range', '=', rec.date_range.id), ('state', '!=', 'rejected')])
            search_id = self.env['reimbursement'].search(
                [('employee_id', '=', rec.employee_id.id), ('reimbursement_type_id', '=', rec.reimbursement_type_id.id),
                 ('date_range', '=', rec.date_range.id),
                 ('state', '!=', 'rejected'), ('id', '!=', rec.id)])
            index = False
            for emp in search_id:
                if rec.reimbursement_type_id.code not in ('briefcase', 'medical'):
                    if emp:
                        raise ValidationError("This reimbursement is already applied for this duration, please correct the dates")
            else:
                index = True
            if index == True:
                if int(rec.net_amount) <= 0:
                    raise ValidationError(
                        "Amount must be greater than zero")
                else:
                    if rec.reimbursement_type_id.code == 'el_encashment':
                        if rec.el_in_account < rec.el_taking:
                            raise ValidationError(
                                "Net Earned leave must be greater than Earned leave Taking")
                        if rec.el_in_account < 60:
                            raise ValidationError(
                                "Net Earned leave must be greater than 60")
                        if rec.el_taking > 30:
                            raise ValidationError(
                                "Earned leave Taking must be less than 30")
                        if int(rec.el_in_account - rec.el_taking) < 30:
                            raise ValidationError(
                                "After deduction, Earned leave must be greater than 30")
                        search_id = self.env['reimbursement'].search(
                            [('employee_id', '=', rec.employee_id.id), ('reimbursement_type_id', '=', rec.reimbursement_type_id.id),
                             ('state', 'not in', ['draft', 'rejected'])])
                        count = 0
                        for record in search_id:
                            count+=1
                        if count > 6:
                            raise ValidationError(
                                "Total must be less than 6")
                    gr_id = self.env['reimbursement.configuration'].search(
                        [('reimbursement_type_id', '=', rec.reimbursement_type_id.id), # ('branch_id', '=', rec.branch_id.id), 
                        ('pay_level_ids', '=', rec.employee_id.job_id.pay_level_id.id),
                        ('job_ids', '=', rec.employee_id.job_id.id),('employee_type', '=', rec.employee_id.employee_type)],
                        order='reimbursement_type_id desc',
                        limit=1)
                    if not gr_id:
                        gr_id = self.env['reimbursement.configuration'].search(
                        [('reimbursement_type_id', '=', rec.reimbursement_type_id.id), # ('branch_id', '=', rec.branch_id.id), 
                        ('pay_level_ids', '=', rec.employee_id.job_id.pay_level_id.id)],
                        order='reimbursement_type_id desc',
                        limit=1)
                    print("gr id is",gr_id)
                    if gr_id.open == False:
                        if rec.reimbursement_type_id.code != 'briefcase':
                            # submit_min = rec.date_range.date_end + relativedelta(days=1)
                            # submit_max = rec.date_range.date_end + relativedelta(days=gr_id.max_submit)
                            # today = datetime.now().date()
                            # if not(submit_min < today <= submit_max):
                            #     raise ValidationError(
                            #         "You can claim for %s" % rec.name + " between  %s" % submit_min + " and %s" % submit_max)
                            if date.today().day > gr_id.max_submit:
                                print(gr_id)
                                # raise ValidationError(f"You can claim for {dict(self._fields['name'].selection).get(rec.name)}\
                                raise ValidationError(f"You can claim for {rec.reimbursement_type_id.name}\
                                                                 within {gr_id.max_submit}th of the month.")
                            else:
                                rec.write({'state': 'waiting_for_approval'})
                        # else:
                        #     search_id = self.env['reimbursement'].search(
                        #         [('employee_id', '=', rec.employee_id.id), ('reimbursement_type_id', '=', rec.reimbursement_type_id.id),
                        #          ('state', 'not in', ['draft', 'rejected'])])
                        #     for record in search_id:
                        #         min_date = record.brief_date + relativedelta(year=2)
                        #         if min_date > rec.brief_date:
                        #             raise ValidationError(
                        #                 "You are allowed to claim for breifcase reimbursement after %s" % min_date)
                        else:
                            rec.write({'state': 'waiting_for_approval'})

                    else:
                        rec.write({'state': 'waiting_for_approval'})


    @api.model
    def create(self, vals):
        res = super(Reimbursement, self).create(vals)
        # empObj = self.env['hr.employee'].sudo().browse(res.employee_id.id)
        # dateRangeObj = self.env['date.range'].sudo().browse(res.date_range.id)
        if res.reimbursement_type_id.code != 'briefcase':
            if res.employee_id.date_of_join > res.date_range.date_end:
                raise ValidationError(f"You can not apply for {res.reimbursement_type_id.name}\
                                            prior to your joining date.")
                                    # {dict(self._fields['name'].selection).get(vals.get('name'))} prior to your joining date.")
        else:
            if res.employee_id.date_of_join > res.brief_date:
                raise ValidationError(f"You can not apply for {res.reimbursement_type_id.name}\
                                            prior to your joining date.")
            last_brief_reimburse = self.env['reimbursement'].search([('employee_id', '=', res.employee_id.id), 
                                                            ('reimbursement_type_id.code', '=', 'briefcase'),
                                                            ('state', 'not in', ('draft', 'rejected')),
                                                            ('id', '!=', res.id)], order='id desc', limit=1)
            # import pdb;pdb.set_trace()
            min_date = last_brief_reimburse.brief_date + relativedelta(years=2)\
                            if last_brief_reimburse else None
            if min_date:
                if min_date > res.brief_date:
                    raise ValidationError(
                        "You are allowed to claim for breifcase reimbursement after %s" % min_date)
        if res.reimbursement_type_id.code not in ('briefcase', 'medical'):
            search_id = self.search(
            [('employee_id', '=', res.employee_id.id), ('reimbursement_type_id', '=', res.reimbursement_type_id.id), ('date_range', '=', res.date_range.id),
             ('state', '!=', 'rejected'),('id', '!=', res.id)])
            if search_id:
                raise ValidationError("This reimbursement is already applied for this duration, please correct the dates")
             
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('reimbursement')
        sequence = 'REIMBURSEMENT - ' + str(seq)
        res.reimbursement_sequence = sequence
            # for emp in search_id:
            #     if emp:
        return res

    @api.multi
    @api.depends('reimbursement_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.reimbursement_sequence:
                name = record.reimbursement_sequence
            else:
                name = 'REIMBURSEMENT'
            res.append((record.id, name))
        return res

    @api.multi
    def button_approved(self):
        for rec in self:
            end_date = rec.date_range.date_end
            reimbursement = self.env['reimbursement.configuration'].sudo()\
                                .search([('reimbursement_type_id', '=', rec.reimbursement_type_id.id), # ('branch_id', '=', rec.branch_id.id),
                                        ('pay_level_ids', 'in', rec.job_id.pay_level_id.id),
                                        ('job_ids', 'in', rec.job_id.id),
                                        ('employee_type', '=', rec.employee_id.employee_type)],
                                        order='reimbursement_type_id desc', limit=1)
            if rec.reimbursement_type_id.code == 'lunch':
                # if reimbursement.attendance_required:
                #     attendance = self.env['reimbursement.attendence'].sudo()\
                #                         .search([('employee_id','=',rec.employee_id.id),
                #                                 ('month', '=', end_date.strftime('%m')),
                #                                 ('year','=', str(end_date.year))], limit=1)
                #     if not attendance:
                #         raise ValidationError('Attendance is not set for current month !')
                    # else:
                    #     rec.working_days = attendance.present_days
                # rec.claimed_amount = float(int(rec.working_days) * 75)
                
                rec.lunch_tds_amt = float(int(rec.working_days_approver) * 50)
            if rec.reimbursement_type_id.code == 'el_encashment':
                   leave_id = self.env['hr.leave.type'].search([('name','=','Earned Leave')],limit=1).id
                   employee_id = rec.employee_id.id
                   branch_id = rec.branch_id.id
                   no_of_days = rec.el_taking
                   self.env['hr.leave.type'].sudo().encashment_leave_from_reimbursement(employee_id,branch_id,leave_id,no_of_days)

            rec.approved_date = datetime.now().date()
            rec.approved_amount = self.approve_amount_approver or self.net_amount
            rec.write({'state': 'approved'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})


    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            self.ensure_one()
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
            ctx = dict(
                default_composition_mode='comment',
                default_res_id=self.id,

                default_model='reimbursement',
                default_is_log='True',
                custom_layout='mail.mail_notification_light'
            )
            mw = {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
            self.rejected_date = datetime.now().date()
            self.write({'state': 'draft'})
            return mw

    @api.multi
    def open_approve_wizard(self):
        reimbursement = self.env['reimbursement.configuration'].sudo()\
                                .search([('reimbursement_type_id', '=', self.reimbursement_type_id.id),# ('branch_id', '=', self.branch_id.id),
                                        ('pay_level_ids', 'in', self.job_id.pay_level_id.id),
                                        ('job_ids', 'in', self.job_id.id),
                                        ('employee_type', '=', self.employee_id.employee_type)],
                                        order='reimbursement_type_id desc', limit=1)
        paylevel_id = self.env['hr.contract'].sudo()\
                            .search([('employee_id', '=', self.employee_id.id),
                                        ('state', '=', 'open')]).pay_level_id
        group_code = paylevel_id.group_id.code
        form_view_id = self.env.ref("reimbursement_stpi.view_reimbursement_attendance_compare_form").id 
        action= {
            'name':'Please verify and submit',
            'type': 'ir.actions.act_window',
            'res_model': 'reimbursement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'context': {'hidden': self.working_days_approver == self.working_days, 
                            'attendance_required': reimbursement.attendance_required and (group_code.lower() != 'a'),
                            'as_per_employee': reimbursement.attendance_required}
        }
        if self.reimbursement_type_id.code not in ['lunch','el_encashment']:
            form_view_id = self.env.ref("reimbursement_stpi.view_claim_amount_eligible_amount_form").id
            action['view_id'] = form_view_id
            action['context']['hidden'] = self.claimed_amount == self.approve_amount_approver
        if self.reimbursement_type_id.code != 'lunch' and self.approve_amount_approver <= 0:
            raise ValidationError('Approved amount should be greater than zero !')
        return action


class ReimbursementServiceProvider(models.Model):

    _name = "reimbursement.service.provider"
    _description = "Reimbursement Service Provider"

    name = fields.Char('Name')

class EmployeeRelative(models.Model):
    _name = 'employee.relative.reimbursement'
    _description = 'Reimbursement Employee Relative'

    name = fields.Char('Name')
    dob = fields.Date('Birthday')
    school_inst_name = fields.Char('School/Institution')
    class_name = fields.Char('Class')
    reimbursement_id = fields.Many2one('reimbursement', 'Reimbursement')
