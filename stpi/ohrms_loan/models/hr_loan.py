# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.addons import decimal_precision as dp


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
            result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        result['type_id'] = self.env['loan.type'].sudo().search([('type_emp', '=', 'Short Term Loan')], limit=1).id
        return result

    @api.multi
    @api.depends('loan_lines.paid')
    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    # total_paid += line.amount
                    total_paid += line.actual_paid
                    # print("-----------",total_paid)
                loan.total_interest += line.monthly_interest_amount
                loan.total_paid_amount = total_paid
                loan.total_amount = loan.loan_amount
                balance_amount = (loan.total_interest + loan.total_amount) - loan.total_paid_amount
                loan.balance_amount = balance_amount
            if round(loan.balance_amount) <= 0.00:
                loan.balance_amount = 0.00
                loan.sudo().write({'is_fully_paid': True})
            else:
                loan.balance_amount = round(loan.balance_amount)
                loan.sudo().write({'is_fully_paid': False})

    @api.multi
    def _compute_paid_status(self):
        granted_recs = self.filtered(lambda x: x.state == 'grant')
        for rec in granted_recs:
            paid_stats = rec.loan_lines.mapped('paid')
            if all(paid_stats):
                rec.sudo().write({'state': 'paid'})
            else:
                rec.sudo().write({'state': 'grant'})
                
#     @api.multi
#     @api.depends('loan_lines.paid')
#     def _compute_loan_amount(self):
#         total_paid = 0.0
#         for loan in self:
#             for line in loan.loan_lines:
#                 if line.paid:
#                     total_paid += line.amount
#             balance_amount = loan.loan_amount - total_paid
#             self.total_amount = loan.loan_amount
#             self.balance_amount = balance_amount
#             print("_____________-------------------",self.balance_amount)
#             self.total_paid_amount = total_paid


    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.branch_id = rec.employee_id.branch_id.id
            if self.env.user.has_group('ohrms_loan.group_loan_finance_approver'):
                rec.check_finance = True
            if self.env.user.has_group('ohrms_loan.group_loan_employee_change'):
                rec.employee_change = True



    name = fields.Char(string="Loan Name", default="Loan Request", readonly=True)
    date = fields.Date(string="Requested Date", default=fields.Date.today(), readonly=False)
    employee_id = fields.Many2one('hr.employee', string="Requested By")
    # employee_id_related = fields.Many2one('hr.employee', related="employee_id", string="Requested By")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", store=True)
    branch_id= fields.Many2one('res.branch', string="Branch", compute='compute_des_dep', store=True)
    type_id =fields.Many2one('loan.type',string="Type")
    installment = fields.Integer(string="No Of Installments", default= 0)
    approve_date = fields.Date(string="Approve Date")
    payment_date = fields.Date(string="Payment Start Date", default=fields.Date.today())
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)

    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
    loan_amount = fields.Float(string="Loan Amount", digits=dp.get_precision('Loan'), track_visibility='onchange')
    interest= fields.Float(related='type_id.interest',string="Interest Rate%")
    total_amount = fields.Float(string="Total Amount", compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount')
    payslip_id = fields.Many2one('hr.payslip')
    paid = fields.Boolean(string="Paid")
    total_interest = fields.Float(string="Total Interest", compute='_compute_loan_amount')
    total_loan_taken = fields.Float('Total Loan Taken')
    total_amount_paid = fields.Float('Total Amount Paid')
    total_principal_remaining = fields.Float('Total Principal Remaining')
    total_interest_as_today = fields.Float('Total Interest as on today')
    foreclosure_amount = fields.Float('Foreclosure Amount')
    dis_date = fields.Date()
    dis_date_related = fields.Date(related='dis_date')
    pro_ins = fields.Float(string='Prorated Installment')
    calculate_bool = fields.Boolean(string='Check Bool', default=False)
    # treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    # emp_account_id = fields.Many2one('account.account', string="Loan Account")
    # journal_id = fields.Many2one('account.journal', string="Journal")
    max_emi = fields.Integer(string="Max No.EMI")
    action_app = fields.Boolean('Action Approve bool', invisible=1)
    action_clos = fields.Boolean('Action Loan Close bool', invisible=1)
    is_fully_paid = fields.Boolean('Fully Paid', invisible=1, default=False)
    check_finance = fields.Boolean('Check Finance', compute='compute_des_dep', default=False)
    employee_change = fields.Boolean('Employee Change', compute='compute_des_dep', default=False)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('grant','Granted'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
        ('paid', 'Paid'),
    ], string="Status", default='draft', track_visibility='onchange', copy=False)
    payment_advice = fields.Boolean('Payment Advice', track_visibility='onchange')

    @api.multi
    def create_payment_advices(self):
        line_ids, emp_lis = [], []
        for rec in self.filtered(lambda x: x.payment_advice == False):
            if any(tuple(filter(lambda x: x.state != 'grant', self))):
                raise ValidationError('You can create payment advice for granted loans.')
            if rec.employee_id.id not in emp_lis:
                line_ids.append((0, 0, {
                    'employee_id': rec.employee_id.id,
                    'bank_name': rec.employee_id.bank_account_id.bank_id.name,
                    'account_no': rec.employee_id.bank_account_id.acc_number,
                    'ifsc_code': rec.employee_id.bank_account_id.bank_id.bic or '',
                    'amount': rec.loan_amount,
                }))
                emp_lis.append(rec.employee_id.id)
            else:
                # filter(lambda x: x[2]['employee_id'] == rec.employee_id.id, line_ids).amount += rec.loan_amount
                for line in line_ids:
                    if line[2]['employee_id'] == rec.employee_id.id:
                        line[2]['amount'] += rec.loan_amount
            rec.payment_advice = True
        self.env['loan.payment.advice'].create({
            'date': fields.Date.today(),
            'name': 'Loan: Payment Advice',
            'line_ids': line_ids
        })
        self.env.user.notify_info('Payment advice has been created successfully.')
        return True


    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count([('employee_id', '=', values['employee_id']),
                                                        ('state', 'not in', ('paid', 'refuse', 'cancel'))])
        if loan_count:
            raise ValidationError(_("You are not allowed to save this loan, as you already have pending Loan"))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        res = super(HrLoan, self).create(values)
        res.onchange_loan_state()
        return res

    def onchange_loan_state(self):
        group_id = self.env.ref('ohrms_loan.group_loan_approver')
        resUsers = self.env['res.users'].sudo().search([]).filtered(lambda r: group_id.id in r.groups_id.ids and self.branch_id.id in r.branch_ids.ids).mapped('partner_id')
        if resUsers:
            employee_partner = self.employee_id.user_id.partner_id
            if employee_partner:
                resUsers += employee_partner
            message = "Loan %s is move to %s"%(self.name, dict(self._fields['state'].selection).get(self.state))
            self.env['mail.message'].create({'message_type':"notification",
                "subtype_id": self.env.ref("mail.mt_comment").id,
                'body': message,
                'subject': "Loan request",
                'needaction_partner_ids': [(4, p.id, None) for p in resUsers],
                'model': self._name,
                'res_id': self.id,
                })
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=[(4, p.id, None) for p in resUsers],
                subtype='mail.mt_comment',
                notif_layout='mail.mail_notification_light',
            )

    @api.constrains('dis_date')
    def onchange_dis_rate(self):
        for rec in self:
            if rec.calculate_bool == True:
                raise ValidationError(_("You are not allowed to change the date"))
            # else:
            #     if rec.approve_date > rec.dis_date and rec.state == 'approve':
            #         raise ValidationError(_("Disbursement date should not be less than Approve date"))
            # rec.calculate_bool = False

    @api.constrains('type_id')
    @api.onchange('type_id')
    def onchange_type_id_get_emi(self):
        for record in self:
            if record.type_id:
                if record.type_id.max_emi:
                    record.max_emi = record.type_id.max_emi


    @api.constrains('installment')
    def check_installment(self):
        if self.installment > 0:
            if self.installment > self.type_id.max_emi:
                raise UserError(_('Please enter valid no. of installments %d') %self.type_id.max_emi)


    @api.constrains('loan_amount','type_id')
    def check_loan_amount(self):
        if self.loan_amount > 0.00:
            max_all = self.env['allowed.loan.amount'].search([('pay_level_id', '=', self.employee_id.job_id.pay_level_id.id),('loan_type', '=', self.type_id.id)], limit=1)
            if max_all.amount and self.loan_amount > max_all.amount:
                raise UserError(_('You are not allowed to take loan more than Rs. %s/-') %max_all.amount)
    #

    @api.multi
    def action_reset_to_draft(self):
        for loan in self:
            loan.loan_lines.unlink()
            loan.write({'state': 'draft'})
            loan.onchange_loan_state()

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})
        return True

    @api.multi
    def action_submit(self):
        for line in self:
            line.sudo().compute_installment()
        self.write({'state': 'waiting_approval_1'})
        self.onchange_loan_state()
        return True
    
    @api.multi
    def action_finance_approve(self):
        for rec in self:
            start_dt = rec.dis_date
            apply_day_threshold = rec.type_id.apply_day_threshold
            if not apply_day_threshold:
                raise ValidationError(_("Please set the Apply Day Threshold for this loan type"))
            start = 0 if rec.dis_date.day <= apply_day_threshold else 1
            rec.payment_date = start_dt.replace(day=1) + relativedelta(months=start)
            for i, line in enumerate(sorted(rec.loan_lines, key=lambda x: x.date),start=start):
                line.date = start_dt.replace(day=1) + relativedelta(months=i)
            rec.write({'state': 'grant'})
        return True

    @api.multi
    def action_cancel(self):
        rc = {
            'name': 'Reason for Revert',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('ohrms_loan.view_reason_revert_loan_wizard').id,
            'res_model': 'revert.loan.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            }
        }
        return rc


    @api.multi
    def action_calculate_dis(self):
        for rec in self:
            if rec.calculate_bool == True:
                raise ValidationError(_("Your are not allowed to calculate it now"))
            else:
                if rec.dis_date and rec.payment_date:
                    count = 0
                    days = (rec.payment_date - rec.dis_date).days
                    interest = (rec.loan_amount*rec.installment)/100
                    interest2 = (interest*days)/365
                    if interest2 <= 0.00:
                        rec.pro_ins = 0.00
                    else:
                        rec.pro_ins = interest2
                    for lines in rec.loan_lines:
                        if round(lines.principle_recovery_installment) == 0:
                            count += 1
                    for lines in rec.loan_lines:
                        if lines.principle_recovery_installment == 0.00:
                            if count > 0.00:
                                lines.monthly_interest_amount = rec.pro_ins / count
                                lines.amount += rec.pro_ins / count
                    rec.calculate_bool = True



    #
    #
    # @api.multi
    # def action_approve(self):
    #     for data in self:
    #         if not data.loan_lines:
    #             raise ValidationError(_("Please Compute installment"))
    #         else:
    #             self.write({'state': 'approve'})

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()

    def restructure_emi_ledger(self, payslip, loanObj, loan_paid):
        """This method is used to restructure EMI ledger in case an employee wish to
        pay more than it's regular EMI amount.

        Args:
            payslip (obj): Current employee payslip object
            loanObj (obj): Current employee loan object
            loan_paid (int): The amount which employee paid

        Returns:
            boolean: It restructures Loan EMI ledger so it only returns True upon
            sucessfull execution.
        """
        loan_lines = []
        for rec in loanObj:
            principal_tenure = rec.installment
            interest_tenure = rec.type_id.threshold_below_emi if rec.installment <= (rec.type_id.threshold_emi - 1) \
                                    else rec.type_id.threshold_above_emi
            # principal_tenure, interest_tenure = (rec.installment - rec.type_id.threshold_below_emi, rec.type_id.threshold_below_emi)\
            #                         if rec.installment <= rec.type_id.threshold_emi\
            #                         else (rec.installment - rec.type_id.threshold_above_emi, rec.type_id.threshold_above_emi)
            paid_emi_count = len(rec.loan_lines.filtered(lambda x: x.paid))
            current_month_loan_line = rec.loan_lines.filtered(lambda x: payslip.date_from <= x.date <= payslip.date_to)
            previous_month_loan_line = rec.loan_lines.filtered(lambda x: payslip.date_from + relativedelta(months=-1) <= x.date \
                                                                            <= payslip.date_to + relativedelta(months=-1))
            current_month_loan_line.amount = loan_paid
            current_month_loan_line.actual_paid = loan_paid
            if previous_month_loan_line:
                current_month_loan_line.closing_blance_principle = previous_month_loan_line.closing_blance_principle - loan_paid
            else:
                current_month_loan_line.closing_blance_principle = rec.loan_amount - loan_paid
            last_paid_closing_balance, last_paid_cb_intr = current_month_loan_line.closing_blance_principle, current_month_loan_line.cb_interest
            closing_balance_principle, closing_cb_intr = last_paid_closing_balance, last_paid_cb_intr
            rec.loan_lines.filtered(lambda x: not x.paid).sudo().unlink()
            for r in range(principal_tenure-paid_emi_count):
                principle_recovery_installment = last_paid_closing_balance / (principal_tenure - paid_emi_count)
                amount = principle_recovery_installment
                yearly_interest = closing_balance_principle * (rec.interest / 100)
                closing_balance_principle -= amount
                loan_line_date = current_month_loan_line.date + relativedelta(months=r+1)
                closing_cb_intr += (yearly_interest / 12)
                loan_lines.append([0, 0, {
                    'date': loan_line_date,
                    'principle_recovery_installment': principle_recovery_installment,
                    'closing_blance_principle': closing_balance_principle if closing_balance_principle > 0 else 0,
                    'yearly_interest_amount': yearly_interest,
                    'monthly_interest_amount': yearly_interest / 12,
                    'cb_interest': closing_cb_intr,
                    'employee_id': rec.employee_id.id,
                    'amount': amount
                }])
                if closing_balance_principle <= 0:
                    for i in range(1, interest_tenure + 1):
                        loan_lines.append([0, 0, {
                            'date': loan_line_date + relativedelta(months=i),
                            'principle_recovery_installment': 0.00,
                            'closing_blance_principle': 0.00,
                            'yearly_interest_amount': 0.00,
                            'monthly_interest_amount': 0.00,
                            'cb_interest': 0.00,
                            'employee_id': rec.employee_id.id,
                            'amount': closing_cb_intr / interest_tenure}])
            rec.sudo().write({'loan_lines': loan_lines})
        return True


    @api.multi
    def compute_installment(self):
        """This method generates installment for recovering loan amount within defined
        tenure. The insterest will be recovered during last period of loan closure.


        Returns:
            boolean: This method generates installment for recovering loan amount within defined
                    tenure so it only returns True upon sucessfull execution.
        """
        loan_lines = []
        for rec in self:
            cur_ins = rec.installment
            new_ins = rec.type_id.threshold_below_emi if rec.installment <= (rec.type_id.threshold_emi - 1)\
                        else rec.type_id.threshold_above_emi
            # cur_ins, new_ins = (rec.installment - rec.type_id.threshold_below_emi, rec.type_id.threshold_below_emi)\
            #                     if rec.installment <= rec.type_id.threshold_emi\
            #                     else (rec.installment - rec.type_id.threshold_above_emi, rec.type_id.threshold_above_emi)
            principle_emi_amount = rec.loan_amount / cur_ins if cur_ins > 0 else rec.loan_amount

            if rec.installment <= 0:
                raise UserError('Please enter Number of Installment grater than Zero')
            if rec.loan_amount <= 0:
                raise UserError('Please enter Loan Amount grater than Zero')

            for r in range(1, cur_ins + 1):
                cb_interest = sum((lambda rec, x: ((rec.loan_amount - (principle_emi_amount * x)) * (rec.interest/100)) / 12) \
                                (rec, x) for x in range(r))
                closing_balance = rec.loan_amount - principle_emi_amount * r
                yearly_interest = (rec.loan_amount - (principle_emi_amount * (r - 1))) * (self.interest / 100)
                date_start = rec.payment_date + relativedelta(months=0) if r == 1 \
                                        else date_start + relativedelta(months=1)
                loan_lines.append([0, 0, {
                    'date': date_start,
                    'principle_recovery_installment': principle_emi_amount,
                    'closing_blance_principle': closing_balance,
                    'yearly_interest_amount': yearly_interest,
                    'monthly_interest_amount': yearly_interest / 12,
                    'cb_interest': cb_interest,
                    'employee_id': rec.employee_id.id,
                    'amount': principle_emi_amount}])
                if round(closing_balance, 2) == 0:
                    for i in range(1, new_ins+1):
                        loan_lines.append([0, 0, {
                            'date': date_start + relativedelta(months=i),
                            'principle_recovery_installment': 0.00,
                            'closing_blance_principle': 0.00,
                            'yearly_interest_amount': 0.00,
                            'monthly_interest_amount': 0.00,
                            'cb_interest': 0.00,
                            'employee_id': rec.employee_id.id,
                            'amount': cb_interest / new_ins}])

            rec.loan_lines.unlink()
            rec.write({'loan_lines': loan_lines})

            return True




    # if type_id and installment and loan_amount:
    # @api.multi
    # def compute_installment(self):
    #     """This automatically create the installment the employee need to pay to
    #     company based on payment start date and the no of installments.
    #         """
    #     for loan in self:
    #         fcb_in = 0.00
    #         new_ins = 0.00
    #         closing_balance = 0.00
    #         loan.loan_lines.unlink()
    #         date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
    #         if loan.installment <= loan.type_id.threshold_emi:
    #             cur_ins = loan.installment - loan.type_id.threshold_below_emi
    #             new_ins = loan.type_id.threshold_below_emi
    #         elif loan.installment > loan.type_id.threshold_emi:
    #             cur_ins = loan.installment - loan.type_id.threshold_above_emi # cur_ins = 20
    #             new_ins = loan.type_id.threshold_above_emi # new_ins = 2
    #         else:
    #             cur_ins = loan.installment

    #         if loan.installment <= 0:
    #             raise UserError(_('Please enter Number of Installment grater than Zero'))
    #         if loan.loan_amount <= 0:
    #             raise UserError(_('Please enter Loan Amount grater than Zero'))

    #         if cur_ins > 0:
    #             amount = loan.loan_amount / cur_ins
    #         else:
    #             amount = loan.loan_amount

    #         for i in range(1, cur_ins + 1):
    #             cb_interest = 0.0
    #             for j in range(0, i):
    #                 # print('-----j',j)
    #                 cb_interest += ((loan.loan_amount - (amount * (j))) * (self.interest / 100)) / 12
    #                 fcb_in = cb_interest

    #             closing_balance = loan.loan_amount - amount * i
    #             year_interest = (loan.loan_amount - (amount * (i - 1))) * (self.interest / 100)
    #             monthly_interest = year_interest / 12
    #             self.env['hr.loan.line'].create({
    #                 'date': date_start,
    #                 'principle_recovery_installment': amount,
    #                 'closing_blance_principle': closing_balance,
    #                 'yearly_interest_amount': year_interest,
    #                 'monthly_interest_amount': monthly_interest,
    #                 'cb_interest': cb_interest,
    #                 'pending_amount': closing_balance + cb_interest,
    #                 'amount': amount,
    #                 'employee_id': loan.employee_id.id,
    #                 'loan_id': loan.id})
    #             date_start = date_start + relativedelta(months=1)
    #         if closing_balance == 0.00:
    #             for k in range(1, new_ins + 1):
    #                 cb_int = fcb_in / new_ins
    #                 self.env['hr.loan.line'].create({
    #                     'date': date_start,
    #                     'principle_recovery_installment': 0.00,
    #                     'closing_blance_principle': 0.00,
    #                     'yearly_interest_amount': 0.00,
    #                     'monthly_interest_amount': 0.00,
    #                     'cb_interest': 0.00,
    #                     'pending_amount': cb_int,
    #                     'amount': cb_int,
    #                     'employee_id': loan.employee_id.id,
    #                     'loan_id': loan.id})
    #                 date_start = date_start + relativedelta(months=1)
    #     return True

    @api.multi
    def action_approve(self):
        self.approve_date = date.today()
        if self.approve_date.day <= 10:
            self.payment_date = self.approve_date.replace(day=1)
        else:
            self.payment_date = self.approve_date.replace(day=1) + relativedelta(months=1)
        payment_date = self.payment_date
        for id in sorted(self.loan_lines.ids):
            i = self.env["hr.loan.line"].browse(id)
            i.approval_d = payment_date
            i.date = payment_date
            payment_date = payment_date + relativedelta(months=1)
        # loan_approve = self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),('state', '=', 'open')])
        if not contract_obj:
            raise UserError('You must Define a running contract for employee')
        if not self.loan_lines:
            raise UserError('You must compute installment before Approved')
        # if loan_approve:
        #     self.write({'state': 'waiting_approval_2'})
        # else:
        self.write({'state': 'approve'})
        self.onchange_loan_state()
        return True

    def get_loan_details_onch(self):
        search_id = self.env['hr.loan'].search(
            [('state', '!=', 'rejected'),('is_fully_paid', '=', False)])
        for rec in search_id:
            cb = 0
            amount = 0
            rec.total_loan_taken = rec.total_amount
            rec.total_amount_paid = rec.total_paid_amount
            for i in rec.loan_lines:
                if i.paid == True:
                    cb+=i.cb_interest
                    amount+=i.amount
            rec.total_principal_remaining = rec.total_loan_taken - amount
            days = int((date.today() - date.today().replace(day=1)).days)
            rem_in = ((rec.total_principal_remaining * rec.interest)/100)/365 * int(days)
            rec.total_interest_as_today = cb + rem_in
            rec.foreclosure_amount = rec.total_principal_remaining + cb + rem_in


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"


    date = fields.Date(string="Installment Date")

    # Added this field by RGupta @Dexciss
    approval_d = fields.Date('EMI Date')
    # installment_month = fields.Char('Installment Month')

    principle_recovery_installment=fields.Float(string="Principle Recovery Installment", digits=dp.get_precision('Loan'))
    closing_blance_principle=fields.Float(string="Closing Balance Principle", digits=dp.get_precision('Loan'))
    yearly_interest_amount=fields.Float(string="Yearly Interest Amount", digits=dp.get_precision('Loan'))
    monthly_interest_amount = fields.Float(string="Monthly Interest Amount", digits=dp.get_precision('Loan'))
    cb_interest=fields.Float(string="C/B Interest", digits=dp.get_precision('Loan'))

    employee_id = fields.Many2one('hr.employee', string="Requested By")
    pending_amount = fields.Float(string="Total Pending Recovery")
    amount = fields.Float(string="EMI", digits=dp.get_precision('Loan'))
    paid = fields.Boolean(string="Paid", digits=dp.get_precision('Loan'))
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    loan_payslip_id = fields.Many2one('hr.loan')
    payslip_id = fields.Many2one('hr.payslip')
    loan_payslip_ref_id = fields.Many2one('hr.payslip')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", related='loan_id.state')
    actual_paid = fields.Float('Paid Amount', digits=dp.get_precision('Loan'))







class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.one
    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
