from odoo import api, fields, models, tools , _
from odoo.exceptions import UserError
from math import ceil

class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin', 'base.exception']  
    
    allow_download = fields.Boolean(string='Allow Download')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('close', 'Verified'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
#     branch_id = fields.Many2one('res.branch',string="Branch",default=lambda self: self.env['res.users']._get_default_branch())
    
    def get_details(self, slip_id):
        data = {}
        contract_id = self.env['hr.contract'].sudo().search([('employee_id', '=', slip_id.employee_id.id), 
                                                            ('state', '=', 'open')])
        data['level'] = contract_id.pay_level_id.name if contract_id else 0
        loan_number = slip_id.get_loan_installment_no(get_loan_number=True)
        loan_amount = sum(slip_id.line_ids.filtered(lambda x: x.code == 'LO').mapped('total'))
        data['loan_emi_no'] = f'{loan_amount}/{loan_number}' if loan_number and loan_amount else 0
        data['rent_recovery'] = sum(slip_id.line_ids.filtered(lambda x: x.code == 'NOHRA').mapped('total'))
        return data

    def get_total(self, code=None):
        total = 0
        for slip in self.slip_ids:
            amount = sum(slip.line_ids.filtered(lambda x: x.code == code).mapped('total'))
            diff = amount - int(amount)
            if diff < 0.6 and diff >= 0.5:
                total += ceil(amount)
            else:
                total += round(amount)
        return total

    @api.multi
    def compute_payslips(self):
        self.slip_ids.filtered(lambda x: x.state == 'draft').compute_sheet()
        return True
    
    @api.multi
    def forward_payslip_run(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            if not self.slip_ids.filtered(lambda x: x.state == 'draft'):
                raise UserError(_('You must compute the payslips before you can forward them.'))
            else:
                self.write({'state': 'to_approve'})
            return True

    @api.multi
    def cancel_payslip_run(self):
        self.slip_ids.filtered(lambda x: x.state == 'draft').compute_sheet()
        self.slip_ids.filtered(lambda x: x.state == 'draft').action_payslip_done()
        return self.write({'state': 'close'})
                
    @api.multi
    def show_payroll_register_report(self):
        for payslip in self:
            val = {
                'name': 'Payroll Register',
                'view_type': 'pivot',
                'view_mode': 'pivot',
                'res_model': 'hr.payslip.line',
                'view_id':self.env.ref('payslip_report.hr_payslip_line_pivot_view').id,
                'domain': [
                            ('slip_id', 'in', payslip.slip_ids.ids),
                            ],
                'type': 'ir.actions.act_window',
                'target':'new',
                }
            return val
