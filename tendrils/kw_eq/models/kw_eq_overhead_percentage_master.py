from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class companyProductionHeadConfig(models.Model):
    _name = 'kw_eq_overhead_percentage_master'
    _description = 'Company head and Production head configuration'

    overhead_type = fields.Selection(string="Overhead Type",selection=[('company', 'Company Overhead'), ('production','Production Overhead')])
    percentage = fields.Float(string='OverHead Percentage')
    effective_date = fields.Date()
    company_ovhead_percentage = fields.Float(string='Company Percentage')
    effective_date = fields.Date(string="Effective Date")



    @api.constrains('overhead_type', 'percentage','effective_date')
    def unique_combination(self):
        for record in self:
            duplicate_records = self.search([
                ('overhead_type', '=', record.overhead_type),('effective_date','=',record.effective_date),('id', '!=', record.id)
            ])
            if duplicate_records:
                raise ValidationError("Duplicate combination detected!")
    
    # @api.depends('write_date')
    # def compute_effective_date(self):
    #     for rec in self:
    #         rec.effective_date = rec.write_date.date()