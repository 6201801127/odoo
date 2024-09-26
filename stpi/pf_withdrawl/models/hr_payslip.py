from odoo import models, fields, api, _
from datetime import date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = "Payslip"

    @api.multi
    def action_payslip_done(self):
        code_dict = {'MPF': 'CEPF', 'VPF': 'VCPF', 'EPF': 'CPF'}
        for rec in self:
            if rec.state == 'draft':
                pf_balance = self.env['pf.employee'].search([('employee_id', '=', rec.employee_id.id)], limit=1)
                if pf_balance:
                    for record in pf_balance:
                        if rec.line_ids:
                            for i in rec.line_ids:
                                if i.salary_rule_id.pf_register == True:
                                    self.env['pf.employee.details'].create({
                                            'pf_details_id': record.id,
                                            'employee_id': record.employee_id.id,
                                            'type': 'Deposit',
                                            'pf_code': code_dict.get(i.code),
                                            'description': i.name,
                                            'date': date.today(),
                                            'amount': i.total,
                                            'reference': f"{rec.number} ({rec.date_to.strftime('%m')}-{rec.date_to.strftime('%Y')})"})
        res = super(HrPayslip, self).action_payslip_done()
        return res
