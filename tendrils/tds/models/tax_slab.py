from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class TaxSlab(models.Model):
    _name = "tax_slab"
    _description = "Income Tax Slab"

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')
    salary_from = fields.Float(string='Salary From')
    salary_to = fields.Float(string='Salary To')
    tax_rate = fields.Float(string='Tax Rate(%)')
    age_from = fields.Integer(string='Age From')
    age_to = fields.Integer(string='Age To')
    tax_regime=fields.Selection([('old_regime', 'Old Regime'), ('new_regime', 'New Regime')], 
                             string='Tax Regime')

    # @api.constrains('salary_from', 'salary_to', 'tax_rate', 'gender', 'age_from', 'age_to', 'surcharge', 'cess','tax_regime')
    # def validate_tax_slab(self):
    #     for rec in self:
    #         record = self.env['tax_slab'].sudo().search(
    #             [('date_range','=',rec.date_range.id),('salary_from', '=', rec.salary_from), ('salary_to', '=', rec.salary_to),
    #              ('tax_rate', '=', rec.tax_rate), ('age_from', '=', rec.age_from),
    #              ('age_to', '=', rec.age_to), ('surcharge', '=', rec.surcharge), ('cess', '=', rec.cess), ('tax_regime', '=', rec.tax_regime)]) - self
    #         if record:
    #             raise ValidationError(f"The Record is Already Exist.")


class TaxCess(models.Model):
    _name = "tax_cess"
    _description = "Income Tax Cess"

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')
    salary_from = fields.Float(string='Salary From')
    salary_to = fields.Float(string='Salary To')
    age_from = fields.Integer(string='Age From')
    age_to = fields.Integer(string='Age To')
    cess = fields.Float(string='Cess (%)')
    tax_regime=fields.Selection([('old_regime', 'Old Regime'), ('new_regime', 'New Regime')], 
                             string='Tax Regime')
    
class TaxSurcharge(models.Model):
    _name = "tax_surcharge"
    _description = "Income Tax Cess"

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')
    salary_from = fields.Float(string='Salary From')
    salary_to = fields.Float(string='Salary To')
    surcharge = fields.Float(string='Surcharge (%)')
    tax_regime=fields.Selection([('old_regime', 'Old Regime'), ('new_regime', 'New Regime')], 
                             string='Tax Regime')