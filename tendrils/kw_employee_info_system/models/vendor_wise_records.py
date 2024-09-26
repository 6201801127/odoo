from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VendorwiseRecords(models.Model):
    _name = "hr.mis.vendorwise.records"
    _description = "Vendor Wise Records"
    _rec_name = "vendor_id"

    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)])
    financial_year_id = fields.Many2one('account.fiscalyear', 'Fiscal Year')
    april_employee_count = fields.Integer("Apr.No")
    april_ctc = fields.Float("Apr.CTC")
    may_employee_count = fields.Integer("May.No")
    may_ctc = fields.Float("May.CTC")
    june_employee_count = fields.Integer("Jun.No")
    june_ctc = fields.Float("Jun.CTC")
    july_employee_count = fields.Integer("Jul.No")
    july_ctc = fields.Float("Jul.CTC")
    aug_employee_count = fields.Integer("Aug.No")
    aug_ctc = fields.Float("Aug.CTC")
    sept_employee_count = fields.Integer("Sep.No")
    sept_ctc = fields.Float("Sep.CTC")
    oct_employee_count = fields.Integer("Oct.No")
    oct_ctc = fields.Float("Oct.CTC")
    nov_employee_count = fields.Integer("Nov.No")
    nov_ctc = fields.Float("Nov.CTC")
    dec_employee_count = fields.Integer("Dec.No")
    dec_ctc = fields.Float("Dec.CTC")
    jan_employee_count = fields.Integer("Jan.No")
    jan_ctc = fields.Float("Jan.CTC")
    feb_employee_count = fields.Integer("Feb.No")
    feb_ctc = fields.Float("Feb.CTC")
    march_employee_count = fields.Integer("Mar.No")
    march_ctc = fields.Float("Mar.CTC")

    total_employee_count = fields.Integer("Total Number", compute="_compute_total_employee")
    total_ctc = fields.Float("Total CTC", compute="_compute_total_ctc")

    @api.depends('april_employee_count', 'may_employee_count', 'june_employee_count', 'july_employee_count',
                 'aug_employee_count', 'sept_employee_count', 'oct_employee_count', 'nov_employee_count',
                 'dec_employee_count',
                 'jan_employee_count', 'feb_employee_count', 'march_employee_count')
    def _compute_total_employee(self):
        for vendor in self:
            sum = vendor.april_employee_count + vendor.may_employee_count + vendor.june_employee_count + vendor.july_employee_count + vendor.aug_employee_count + vendor.sept_employee_count + vendor.oct_employee_count + vendor.nov_employee_count + vendor.dec_employee_count + vendor.jan_employee_count + vendor.feb_employee_count + vendor.march_employee_count
            vendor.total_employee_count = sum

    @api.depends('april_ctc', 'may_ctc', 'june_ctc', 'july_ctc', 'aug_ctc', 'sept_ctc', 'oct_ctc', 'nov_ctc', 'dec_ctc',
                 'jan_ctc', 'feb_ctc', 'march_ctc')
    def _compute_total_ctc(self):
        for vendor in self:
            total = vendor.april_ctc + vendor.may_ctc + vendor.june_ctc + vendor.july_ctc + vendor.aug_ctc + vendor.sept_ctc + vendor.oct_ctc + vendor.nov_ctc + vendor.dec_ctc + vendor.jan_ctc + vendor.feb_ctc + vendor.march_ctc
            vendor.total_ctc = total

    @api.model
    def create(self, vals):
        res = super(VendorwiseRecords, self).create(vals)
        record = self.env['hr.mis.vendorwise.records'].sudo().search([]) - res
        for rec in record:
            if rec.vendor_id.id == res.vendor_id.id and rec.financial_year_id.id == res.financial_year_id.id:
                raise ValidationError("Vendor can't be duplicated")
        return res
