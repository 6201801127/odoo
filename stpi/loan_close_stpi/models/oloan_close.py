from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp

class LoanClose(models.Model):
    _name = 'hr.loan.close'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Installment Payment Close"

    @api.depends('unpaid_loan_lines','unpaid_loan_lines.paid')
    def get_loan_close_lines(self):
        for rec in self:
                temp = 0.0
                for line in rec.unpaid_loan_lines:
                    if line.paid:
                        temp += line.amount
                rec.loan_amount = temp


    # @api.onchange('loan_id')
    # @api.constrains('loan_id')
    # def get_loan_details_onch(self):
    #     for rec in self:
    #         cb = 0
    #         amount = 0
    #         rec.total_loan_taken = rec.loan_id.total_amount
    #         rec.total_amount_paid = rec.loan_id.total_paid_amount
    #         for i in rec.loan_id.loan_lines:
    #             if i.paid == True:
    #                 cb+=i.cb_interest
    #                 amount+=i.amount
    #         rec.total_principal_remaining = rec.total_loan_taken - amount
    #         days = int((date.today() - date.today().replace(day=1)).days)
    #         rem_in = ((rec.total_principal_remaining * rec.loan_id.interest)/100)/365 * int(days)
    #         rec.total_interest_as_today = cb + rem_in
    #         rec.foreclosure_amount = rec.total_principal_remaining + cb + rem_in

    @api.constrains('loan_id', 'loan_paid_date')
    def get_loan_details(self):
        for rec in self:
            loan_lines = rec.loan_id.loan_lines
            monthly_interest_paid = sum(loan_lines.filtered(lambda x: x.paid).mapped('monthly_interest_amount'))
            rec.total_amount_paid = sum(loan_lines.filtered(lambda x: x.paid).mapped('amount'))
            rec.total_loan_taken = rec.loan_id.total_amount
            rec.total_principal_remaining = rec.total_loan_taken - rec.total_amount_paid
            close_day_threshold = rec.loan_id.type_id.close_day_threshold
            if not close_day_threshold:
                raise ValidationError(_("Please set the Close Day Threshold for this loan type"))
            if rec.loan_paid_date:
                if rec.loan_paid_date.day > close_day_threshold:
                    current_month_interest = sum(loan_lines.filtered(lambda x: x.date.month == rec.loan_paid_date.month\
                                                    and x.date.year == rec.loan_paid_date.year).mapped('monthly_interest_amount'))
                else:
                    current_month_interest = 0
                rec.total_interest_as_today = monthly_interest_paid if rec.loan_paid_date.day <= close_day_threshold\
                                                    else monthly_interest_paid + current_month_interest
                rec.foreclosure_amount = rec.total_principal_remaining + rec.total_interest_as_today


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string="Loan Name", default="Loan Request")
    date = fields.Date(string="Requested Date", default=fields.Date.today())
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    total_loan_taken = fields.Float('Total Loan Taken', track_visibility='onchange', digits=dp.get_precision('Loan'))
    total_amount_paid = fields.Float('Total Amount Paid', track_visibility='onchange', digits=dp.get_precision('Loan'))
    total_principal_remaining = fields.Float('Total Principal Remaining', track_visibility='onchange', digits=dp.get_precision('Loan'))
    total_interest_as_today = fields.Float('Total Interest as on today', track_visibility='onchange', digits=dp.get_precision('Loan'))
    foreclosure_amount = fields.Float('Foreclosure Amount', track_visibility='onchange', digits=dp.get_precision('Loan'))

    employee_id = fields.Many2one('hr.employee', string="Requested By", default=_default_employee)
    designation = fields.Many2one('hr.job', string="Designation", compute='compute_des_dep', track_visibility='always')
    branch_id = fields.Many2one('res.branch', 'Center', compute='compute_des_dep', track_visibility='always')
    department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep', store=True,
                                 track_visibility='always')
    # credit_account_id = fields.Many2one('account.account', string="Credit Account")
    loan_amount = fields.Float(string="Loan Amount",compute='get_loan_close_lines', store=True)
    # payment_account_id = fields.Many2one('account.account', string="Payment Account")
    unpaid_loan_lines = fields.One2many('hr.loan.line.unpaid','un_loan_id', string="Loan Line", index=True)
    remarks = fields.Char(string='Remarks')
    document_proof = fields.Binary('Document')
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), 
         ('approved', 'Approved'), ('granted', 'Closed'),
         ('rejected', 'Rejected')], 
        required=True, default='draft', string='Status', track_visibility='always')
    loan_paid_date = fields.Date( track_visibility='onchange')
    loan_paid_date_rel = fields.Date(related="loan_paid_date")
    # check_admin = fields.Boolean(string="Check Admin Approver", compute='compute_des_dep', default=False)
    own_record = fields.Boolean(string="Own Record", default=False)


    @api.constrains('loan_paid_date')
    def check_paid_date(self):
        for rec in self:
            if rec.loan_paid_date and rec.loan_paid_date < rec.date:
                raise ValidationError(_('Paid Date should be greater than or equal to requested date.'))
            if rec.loan_paid_date and rec.loan_paid_date < rec.loan_id.payment_date:
                raise ValidationError(_('Paid Date should be greater than payment start date.'))
    
    @api.multi
    @api.depends('loan_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.loan_id:
                name = record.loan_id.name + ' - Loan Close Request'
            else:
                name = 'Lone Close Request'
            res.append((record.id, name))
            record.name = str(name)
        return res




    @api.model
    def create(self, values):
        res = super(LoanClose, self).create(values)
        duplicate_loan = self.env['hr.loan.close'].search([('employee_id', '=', res.employee_id.id),
                                                            ('loan_id', '=', res.loan_id.id),
                                                            ('state', '!=', 'rejected')]) - res
        if duplicate_loan:
            raise ValidationError(_(f"You have already applied for loan close of {res.loan_id.name}"))
        return res


    @api.multi
    def button_submit(self):
        for rec in self:
            rec.write({'state': 'submitted'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    @api.multi
    def unlink(self):
        for tour in self:
            if tour.state != 'draft':
                raise UserError(
                    'You cannot delete a Loan Close Request which is not in draft state')
        return super(LoanClose, self).unlink()


    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,
            default_model='hr.loan.close',
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
        self.write({'state': 'draft'})
        return mw


    #
    # @api.onchange('loan_id')
    # @api.constrains('loan_id')
    # def get_loan_details_close(self,working_list=None):
    #     for rec in self:
    #         unpaid_loan_lines = []
    #         for i in rec.loan_id.loan_lines:
    #             if i.paid == False:
    #                 i.sudo().unlink()
    #             unpaid_loan_lines.append((0, 0, {
    #                 'un_loan_id': rec.id,
    #                 'employee_id': rec.employee_id.id,
    #                 'loan_line_id': i.id,
    #                 'amount': i.amount,
    #                 'paid': True,
    #                 'date': i.date,
    #             }))
    #         else:
    #             rec.unpaid_loan_lines = working_list
    #         rec.unpaid_loan_lines = unpaid_loan_lines




    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id
        if self.env.user.has_group('ohrms_loan.group_loan_approver'):
            rec.check_admin = True
        if rec.employee_id.user_id == self.env.user:
            rec.own_record = True

    #
    # @api.multi
    # def confirm_loan_payment(self):
    #     for lines in self.unpaid_loan_lines:
    #         if lines.paid:
    #             lines.loan_line_id.paid = True

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})
        return True

    @api.multi
    def action_finance_approve(self):
        for rec in self:
            close_day_threshold = rec.loan_id.type_id.close_day_threshold
            if not close_day_threshold:
                raise ValidationError(_("Please set the Close Day Threshold for this loan type"))
            current_month_interest = sum(rec.loan_id.loan_lines\
                                                .filtered(lambda x: x.date.month == rec.loan_paid_date.month\
                                                and x.date.year == rec.loan_paid_date.year).mapped('monthly_interest_amount'))
            rec.loan_id.loan_lines.filtered(lambda x: x.paid == False).sudo().unlink()
            total_paid_intres = sum(rec.loan_id.loan_lines\
                                    .filtered(lambda x: x.paid and x.date <= rec.date)\
                                    .mapped('monthly_interest_amount'))
            self.env['hr.loan.line'].create({
                'date': date.today(),
                'principle_recovery_installment': rec.total_principal_remaining,
                'closing_blance_principle': 0.00,
                'yearly_interest_amount': 0.00,
                'monthly_interest_amount': current_month_interest if rec.loan_paid_date.day > close_day_threshold else 0,
                'cb_interest': rec.total_interest_as_today,
                'pending_amount': rec.total_interest_as_today,
                'amount': rec.foreclosure_amount,
                'employee_id': rec.loan_id.employee_id.id,
                'paid': True,
                'actual_paid': rec.foreclosure_amount,
                'loan_id': rec.loan_id.id})
            rec.loan_id.sudo()._compute_paid_status()
            rec.write({'state': 'granted'})




class UnpaidInstallmentLine(models.Model):
    _name = "hr.loan.line.unpaid"
    _description = "Installment Line"

    un_loan_id = fields.Many2one('hr.loan.close',string="Wizard ref")
    date = fields.Date(string="Payment Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount")
    paid = fields.Boolean(string="To be Paid", default=True)
    loan_line_id = fields.Many2one('hr.loan.line', string="Loan line Ref.")
    payslip_id = fields.Many2one('hr.payslip')
