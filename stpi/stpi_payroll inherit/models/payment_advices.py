from odoo import models, fields, api,_
from odoo.exceptions import UserError


class HrPayrollAdvices(models.Model):
    _inherit='hr.payroll.advice'


    @api.depends('name')
    def compute_note(self):
        for rec in self:
            if rec.cheque_date and rec.chaque_nos:
                rec.note = f"You are requested to transfer the amount through NEFT/RTGS as per details from SB A/C - {rec.company_id.partner_id.bank_ids[0].acc_number} against {rec.chaque_nos} and {rec.cheque_date.strftime('%d/%b/%Y')}"
            if self.env.user.has_group('stpi_payroll inherit.group_hr_payment_advice_user'):
                rec.payment_advice_user = True

    cheque_date = fields.Date('Cheque Date')
    note = fields.Text('Description', compute='compute_note')
    payment_advice_user = fields.Boolean('Payment Advice User', default=False, compute='compute_note')


    @api.multi
    def compute_advice(self):
        """
        Advice - Create Advice lines in Payment Advice and
        compute Advice lines.
        """
        for advice in self:
            old_lines = self.env['hr.payroll.advice.line'].search([('advice_id', '=', advice.id)])
            if old_lines:
                old_lines.unlink()
            payslips = self.env['hr.payslip'].search([('date_from', '<=', advice.date), ('date_to', '>=', advice.date), ('state', '=', 'done')])
            for slip in payslips:
                if not slip.employee_id.bank_account_id:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name,))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_id.bank_id.name,
                        'bank_name': slip.employee_id.bank_account_id.bank_id.name,
                        'ifsc_code': slip.employee_id.bank_account_id.bank_id.bic or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
                slip.advice_id = advice.id



class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'



    @api.multi
    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(_("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
            company = self.env.user.company_id
            advice = self.env['hr.payroll.advice'].create({
                        'batch_id': run.id,
                        'company_id': company.id,
                        'name': run.name,
                        'date': run.date_end,
                        'bank_id': company.partner_id.bank_ids and company.partner_id.bank_ids[0].bank_id.id or False
                    })
            for slip in run.slip_ids:
                # TODO is it necessary to interleave the calls ?
                # slip.action_payslip_done()
                if not slip.employee_id.bank_account_id:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_id.bank_id.name,
                        'bank_name': slip.employee_id.bank_account_id.bank_id.name,
                        'ifsc_code': slip.employee_id.bank_account_id.bank_id.bic or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
        self.write({'available_advice': True})
        return True



class HrPayrollAdviceLine(models.Model):
    '''
    Bank Advice Lines
    '''
    _inherit = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    bank_name = fields.Char('Bank Name')
