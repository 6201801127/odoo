# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
from odoo import tools, _

from kw_utility_tools import kw_validations


# class for Membership association
class kwemp_membership_assc(models.Model):
    _name = 'kwemp_membership_assc'
    _description = "A model to store the membership of employees in different associations."

    kw_id = fields.Integer(string='Tendrils ID')
    name = fields.Char(string="Association Name", required=True, size=100)
    date_of_issue = fields.Date(string="Date of Issue", required=True)
    date_of_expiry = fields.Date(string="Date of Expiry")
    renewal_sts = fields.Boolean("Renewal Applied", default=False)
    uploaded_doc = fields.Binary(string="Document Upload")  # , required=True
    doc_file_name = fields.Char(string="Document Name")

    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID")

    # employee_id = fields.Many2one('kwemp_all',ondelete='cascade', string="Employee ID")
    @api.constrains('date_of_issue')
    def validate_data(self):
        current_date = str(datetime.now().date())
        for record in self:
            if record.date_of_issue:
                if str(record.date_of_issue) >= current_date:
                    raise ValidationError(
                        "The date of issue of membership association should be less than current date.")

    _sql_constraints = [('membership_uniq', 'unique (emp_id,name)',
                         'Duplicate membership association details not allowed.. !')]

    @api.constrains('date_of_issue', 'date_of_expiry')
    def validate_membership_date(self):

        for record in self:
            if record.date_of_issue and record.date_of_expiry:
                if str(record.date_of_expiry) < str(record.date_of_issue):
                    raise ValidationError(
                        " The date of Expiry of membership association should not be less than Date Of Issue")

    @api.constrains('uploaded_doc')
    def validate_membership_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for rec in self:
            kw_validations.validate_file_mimetype(rec.uploaded_doc, allowed_file_list)
            kw_validations.validate_file_size(rec.uploaded_doc, 4)
