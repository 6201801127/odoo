# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime

# from odoo import tools, _
# import re
# from lxml import etree
# from dateutil import relativedelta


"""# class to store the family info details"""


class kwemp_family_info(models.Model):
    _name = 'kwemp_family_info'
    _description = "Family information of the employees."

    kw_id = fields.Integer(string='Tendrils ID')
    relationship_id = fields.Many2one('kwmaster_relationship_name', string="Relationship Type", required=True)
    name = fields.Char(string="Full Name", required=True, size=100)
    gender = fields.Selection(string="Gender", selection=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], )
    date_of_birth = fields.Date(string="Date of Birth")
    dependent = fields.Selection(string="Dependent", selection=[('1', 'Yes'), ('2', 'No'), ('3', 'Yes and Employed')], )

    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID")
    # employee_id = fields.Many2one('kwemp_all',ondelete='cascade', string="Employee ID")
    is_insured = fields.Boolean(string="Need Insurance")
    is_insure_allowed = fields.Boolean(related='relationship_id.is_insure_covered')
    phone_no = fields.Char(string = "Phone No")

    @api.onchange('relationship_id')
    def onchange_gender(self):
        for rec in self:
            if rec.relationship_id.gender:
                rec.gender = rec.relationship_id.gender

    @api.constrains('date_of_birth')
    def validate_data(self):
        current_date = str(datetime.now().date())
        for record in self:
            if record.date_of_birth:
                if str(record.date_of_birth) >= current_date:
                    raise ValidationError("The date of birth should be less than current date.")

    @api.constrains('gender', 'dependent', )
    def validate_language_status(self):
        for record in self:
            if not (record.gender):
                raise ValidationError("Please choose gender of family member.")
            elif not (record.dependent):
                raise ValidationError("Please choose dependency of family member.")
