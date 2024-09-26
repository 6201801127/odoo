from odoo import models,fields,api,_


class HrPayslipLinesIn(models.Model):
    _inherit = 'hr.payslip.line'

    taxable_amount = fields.Float('Taxable Amount', compute='_compute_taxable_amount')

    @api.depends('total')
    def _compute_taxable_amount(self):
        for record in self:
            record.taxable_amount = (record.total * record.salary_rule_id.taxable_percentage) / 100

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _check_tds_amount(self, payslip):
        tds = self.env['misc.allowance.deduct'].search([('salary_rule_id.code', '=', 'TDS'),
                                                        ('employee_id', '=', payslip.employee_id),
                                                        ('date', '>=', payslip.date_from),
                                                        ('date', '<=', payslip.date_to)])
        return tds.amount if tds else 0

    @api.multi
    def calculate_tds(self, payslip):
        tds = self._check_tds_amount(payslip)
        result = 0
        if not tds:
            financialYearObj = self.env['date.range'].sudo().search([('type_id.name', '=', 'Fiscal Year'),
                                                                    ('date_start', '<=', payslip.date_from),
                                                                    ('date_end', '>=', payslip.date_to)])

            tdsObj = self.env['hr.declaration'].sudo().search([('employee_id', '=', payslip.employee_id),
                                                                ('date_range', '=', financialYearObj.id)])

            taxPaymentObj = self.env['tax.payment'].sudo().search([('tax_payment_id', '=', tdsObj.id),
                                                                    ('date', '>=', payslip.date_from),
                                                                    ('date', '<=', payslip.date_to)], limit=1)
            
            result = round(taxPaymentObj.amount) if taxPaymentObj else 0
        else:
            result = tds
        return result

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tds_applicable = fields.Boolean('TDS Applicable')

    @api.onchange('employee_type')
    def onchange_employee_type(self):
        if self.employee_type != 'contractual_with_stpi':
            self.tds_applicable = False