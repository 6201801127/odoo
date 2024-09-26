# Commit HIstory
# epf_limit added for maximum withdraw limit 7 June 2021(Gouranga kala)
# 
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class PfType(models.Model):

    _name="pf.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PF Withdrawal Type"


    name = fields.Char(string="PF Withdrawal Type",track_visibility='always')
    purpose = fields.Text(string="Purpose",track_visibility='always')
    months = fields.Integer(string='Month (Basic+DA)')

    voluntarily_contri = fields.Boolean('Volunteerly')

    cepf_vcpf = fields.Boolean('MPF + VPF')
    cpf = fields.Boolean('EPF')

    employee_contri = fields.Boolean('Employee')
    employer_contri = fields.Boolean('Employer')

    min_years = fields.Integer(string='Minimum Years of Service')
    attachment_document = fields.Text(string="Required Document",track_visibility='always')

    basic_da_percentage = fields.Integer('Basic + DA (%)')
    cepf_vcpf_percentage = fields.Integer('MPF + VPF (%)')
    cpf_percentage  = fields.Integer('EPF (%)')

    min_age         = fields.Integer("Minimum Age Required")
    
    # Start : added on  7 June 2021(Gouranga kala)
    epf_limit = fields.Integer('Maximum Withdraw Limit')
    min_limit = fields.Integer('Minimum Limit')
    avail_once = fields.Boolean('Avail Once', default=False, help='If checked, it can be availed once in a lifetime.')

    @api.constrains("basic_da_percentage", "cepf_vcpf_percentage","cpf_percentage","epf_limit")
    def validate_percentage(self):
        for pf_type in self:
            if pf_type.basic_da_percentage and not (1 <= pf_type.basic_da_percentage <= 100):
                raise ValidationError(_("Basic + DA Percentage must be between 1 to 100."))

            if pf_type.cepf_vcpf_percentage and not (1 <= pf_type.cepf_vcpf_percentage <= 100):
                raise ValidationError(_("CEPF + VCPF Percentage must be between 1 to 100."))
            
            if pf_type.cpf_percentage and not (1 <= pf_type.cpf_percentage <= 100):
                raise ValidationError(_("CPF Percentage must be between 1 to 100."))

            if pf_type.epf_limit and pf_type.epf_limit < 0:
                raise ValidationError(_("Maximum Withdraw Limit can't have negative value."))
   # End : added on  7 June 2021(Gouranga kala)             