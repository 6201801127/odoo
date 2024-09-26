from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class LoanClose(models.Model):
    _name = 'hr.loan.close'
    _description = "Installment Payment Close"

    @api.depends('unpaid_loan_lines','unpaid_loan_lines.paid')
    def get_loan_close_lines(self):
        for rec in self:
                temp = 0.0
                for line in rec.unpaid_loan_lines:
                    if line.paid:
                        temp += line.amount
                rec.loan_amount = temp



    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string="Loan Name", default="Loan Request")
    date = fields.Date(string="Requested Date", default=fields.Date.today())
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    employee_id = fields.Many2one('hr.employee', string="Requested By", default=_default_employee)
    designation = fields.Many2one('hr.job', string="Designation", compute='compute_des_dep', track_visibility='always')
    branch_id = fields.Many2one('res.branch', 'Branch', compute='compute_des_dep', track_visibility='always')
    department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep', store=True,
                                 track_visibility='always')
    # credit_account_id = fields.Many2one('account.account', string="Credit Account")
    loan_amount = fields.Float(string="Loan Amount",compute='get_loan_close_lines', store=True)
    # payment_account_id = fields.Many2one('account.account', string="Payment Account")
    unpaid_loan_lines = fields.One2many('hr.loan.line.unpaid','un_loan_id', string="Loan Line", index=True)
    remarks = fields.Char(string='Remarks')
    document_proof = fields.Binary('Document')
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('paid', 'Paid')
         ], required=True, default='draft', string='Status', track_visibility='always')



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
        loan_count = self.env['hr.loan.close'].search_count([('employee_id', '=', res.employee_id.id),('loan_id', '=', res.loan_id.id),('id', '!=', res.id)
                                                       ])
        if loan_count:
            raise ValidationError(_("You are not allowed to save this loan Close Application"))
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



    @api.onchange('loan_id')
    @api.constrains('loan_id')
    def get_loan_details_close(self,working_list=None):
        for rec in self:
            unpaid_loan_lines = []
            for i in rec.loan_id.loan_lines:
                if i.paid == False:
                    unpaid_loan_lines.append((0, 0, {
                        'un_loan_id': rec.id,
                        'employee_id': rec.employee_id.id,
                        'loan_line_id': i.id,
                        'amount': i.amount,
                        'paid': True,
                        'date': i.date,
                    }))
            else:
                rec.unpaid_loan_lines = working_list
            rec.unpaid_loan_lines = unpaid_loan_lines




    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id

    #
    # @api.multi
    # def confirm_loan_payment(self):
    #     for lines in self.unpaid_loan_lines:
    #         if lines.paid:
    #             lines.loan_line_id.paid = True


    @api.multi
    def button_approved(self):
        for rec in self:
            for lines in rec.unpaid_loan_lines:
                if lines.paid:
                    lines.loan_line_id.paid = True
            rec.write({'state': 'approved'})




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
