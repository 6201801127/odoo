from odoo import api, fields, models, tools, _

class IncomeTaxSlab(models.Model):
    _name = "income.tax.slab"
    _description = "Income Tax Slab"

    salary_from = fields.Float(string='Salary From')
    salary_to = fields.Float(string='Salary To')
    tax_rate = fields.Float(string='Tax Rate(%)')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('both', 'Transgender'),
    ], string='Gender')
    age_from = fields.Integer(string='Age From')
    age_to = fields.Integer(string='Age To')
    surcharge = fields.Float(string='Surcharge (%)')
    cess = fields.Float(string='Cess (%)')


class SalaryRules_inh(models.Model):
    _inherit = "hr.salary.rule"
    _description = "Salary Rule"

    taxable_percentage = fields.Float(string='Taxable Percentage')
    pf_register = fields.Boolean(string='Register PF?')
