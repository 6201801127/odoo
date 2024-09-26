from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class TaxMaster(models.Model):
    _name = 'tax_master'
    _description = 'TAx Master'
    
    
    payslipid = fields.Many2one('hr.payslip',ondelete='cascade')
    year = fields.Char()
    month = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    personal_relief = fields.Float("")
    nhif = fields.Float("NHIF Employee")
    nhif_relief = fields.Float("Insurance/NHIF Relief")
    tax = fields.Float("PAYE")
    taxable_income = fields.Float("")
    gross_amt = fields.Float("GROSS")
    nssf = fields.Float("NSSF Employee")
    name = fields.Char(related='employee_id.name',string='Name of the Employee')
    code = fields.Char(related='employee_id.emp_code')
    gross_nssf =  fields.Float("Taxable Income",compute='_calculate_amt')
    compute_personal_relief = fields.Float("Personal Relief",compute='_calculate_amt')
    compute_nhif_relief = fields.Float("Insurance/NHIF Relief",compute='_calculate_amt')
    pin_no = fields.Char(compute='_compute_pan_num',string='KRA PIN')
    tax_payble = fields.Float("Tax Before Relief",compute='_calculate_amt')
    
    
    def _compute_pan_num(self):
        for rec in self:
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pin_no = record.doc_number
    
    @api.depends('gross_amt','nssf')
    def _calculate_amt(self):
        for rec in self:
            rec.gross_nssf = rec.gross_amt - rec.nssf
            rec.compute_personal_relief = 0 if rec.gross_nssf < 24000 else rec.personal_relief
            rec.compute_nhif_relief = 0 if rec.gross_nssf < 24000 else rec.nhif_relief
            rec.tax_payble = 0  if rec.gross_nssf < 24000 else rec.taxable_income