from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PfRefund(models.Model):
    _name = 'pf.refund'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PF Refund"
    _rec_name = "employee_id"


    @api.multi
    def _compute_check_approver(self):
        if self.env.user.has_group('pf_withdrawl.group_pf_withdraw_approver'):
            self.check_approver = True


    employee_id = fields.Many2one('hr.employee', "Employee", required=True, track_visibility='onchange',
                                    default=lambda self: self.env['hr.employee'].sudo()\
                                                        .search([('user_id', '=', self.env.uid)], limit=1))
    date = fields.Date("Date", required=True, default=fields.Date.today(), track_visibility='onchange')
    amount = fields.Float("Amount", required=True, track_visibility='onchange')
    pf_id = fields.Many2one('pf.widthdrawl', "PF", required=True, track_visibility='onchange',
                                domain="[('employee_id', '=', employee_id),('state', '=', 'approved'),\
                                            ('applied_refund', '=', False)]")
    designation_id = fields.Many2one('hr.job', "Designation", related='employee_id.job_id', 
                                            track_visibility='onchange')
    branch_id = fields.Many2one('res.branch', "Center", related='employee_id.branch_id', 
                                            track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), 
                                ('approve', 'Approved'), ('reject', 'Rejected'),
                                ('paid', 'Paid')], 'State', default='draft', 
                                track_visibility='onchange')
    emp_mpf_vpf_bal = fields.Float('Employee Contribution')
    emp_epf_bal = fields.Float('Employer Contribution')
    check_approver = fields.Boolean('Check Approver', compute='_compute_check_approver')
    description = fields.Char('Description')
    cheque_detail = fields.Binary('Attachment', attachment=True)
    payment_detail = fields.Char('Payment Details')
    paid_date = fields.Date('Paid Date')
    remark = fields.Text('Remarks')


    @api.onchange('pf_id')
    def onchange_pf(self):
        self.amount, self.emp_mpf_vpf_bal, self.emp_epf_bal = False, False, False
    
    @api.onchange('amount', 'pf_id')
    def allocate_mpf_vpf_epf(self):
        for rec in self:
            if rec.amount:
                if rec.amount > rec.pf_id.advance_amount:
                    raise ValidationError(_("Refund amount should be less than Withdrawl amount."))
                mpf_vpf_ratio = rec.pf_id.emp_cepf_vcpf_bal / rec.pf_id.advance_amount
                epf_ratio = 1 - mpf_vpf_ratio
                rec.emp_mpf_vpf_bal = rec.amount * mpf_vpf_ratio
                rec.emp_epf_bal = rec.amount * epf_ratio

    @api.constrains('amount', 'date', 'emp_mpf_vpf_bal', 'emp_epf_bal','paid_date')
    def check_constrains(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Amount should be greater than zero."))
            if rec.date < rec.pf_id.date:
                raise ValidationError(_("Refund date should be greater than Withdrawl date."))
            if rec.emp_mpf_vpf_bal or rec.emp_epf_bal:
                if (rec.emp_mpf_vpf_bal + rec.emp_epf_bal) != rec.amount:
                    raise ValidationError(_("Refund amount should be equal Employee\
                                                    and Employer Contribution."))
            if rec.paid_date:
                if rec.paid_date > fields.Date.today():
                    raise ValidationError(_("Paid date can not be future date."))
        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.pf_id.write({'applied_refund': True})
        return res
    
    @api.multi
    def button_forward(self):
        for rec in self:
            rec.write({'state': 'to_approve'})
        return True

    @api.multi
    def button_approve(self):
        for rec in self:
            rec.write({'state': 'approve'})
        return True

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'reject'})
        return True

    @api.multi
    def button_paid(self):
        for rec in self:
            pf_details_ids = []
            pf_employee = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)])
            pf_details_ids.append([0, 0, {
                    'employee_id': rec.employee_id.id,
                    'type': 'Deposit',
                    'pf_code': 'CEPF + VCPF',
                    'description': f'PF Refund against {rec.pf_id.name}',
                    'date': rec.paid_date,
                    'amount': rec.emp_mpf_vpf_bal,
                    'reference': f'PF Refund against {rec.pf_id.name}',
                }])
            pf_details_ids.append([0, 0, {
                    'employee_id': rec.employee_id.id,
                    'type': 'Deposit',
                    'pf_code': 'CPF',
                    'description': f'PF Refund against {rec.pf_id.name}',
                    'date': rec.paid_date,
                    'amount': rec.emp_epf_bal,
                    'reference': f'PF Refund against {rec.pf_id.name}',
                }])
            pf_employee.write({'pf_details_ids': pf_details_ids})
            rec.write({'state': 'paid'})
        return True