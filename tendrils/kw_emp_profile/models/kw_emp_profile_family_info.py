# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime


class kw_emp_profile_family_info(models.Model):
    _name = 'kw_emp_profile_family_info'
    _description = "Family information of the employees."

    relationship_id = fields.Many2one('kwmaster_relationship_name', string="Relationship Type", required=True)
    name = fields.Char(string="Full Name", size=100, required=True)
    gender = fields.Selection(string="Gender", selection=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
                              required=True)
    date_of_birth = fields.Date(string="Date of Birth")
    dependent = fields.Selection(string="Dependent", selection=[('1', 'Yes'), ('2', 'No'), ('3', 'Yes and Employed')],
                                 required=True)

    emp_family_id = fields.Many2one('kw_emp_profile', string="Employee's Name")
    family_id = fields.Many2one('kwemp_family_info', string='Family ID')
    phone_no = fields.Char(string="Phone No")

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
            if not record.gender:
                raise ValidationError("Please choose gender of family member.")
            elif not record.dependent:
                raise ValidationError("Please choose dependency of family member.")

    @api.constrains('phone_no')
    def check_phone_no(self):
        for record in self:
            if record.phone_no:
                if not record.phone_no.isdigit():
                    raise ValidationError("Invalid phone no: %s. Phone number must be exactly 10 digits." % record.phone_no)
