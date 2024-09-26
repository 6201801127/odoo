# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime

from kw_utility_tools import kw_validations


# class for identity documets
class kwemp_identity_docs(models.Model):
    _name = 'kwemp_identity_docs'
    _description = "A model to store the identification documents of employees."

    kw_id = fields.Integer(string='Tendrils ID')
    name = fields.Selection(string="Identification Type",
                            selection=[('1', 'PAN'), ('2', 'Passport'), ('3', 'Driving Licence'), ('4', 'Voter ID'),
                                       ('5', 'AADHAAR'), ('6', 'Yellow Fever')], required=True)
    doc_number = fields.Char(string="Document Number", required=True, size=100)
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    renewal_sts = fields.Boolean("Renewal Applied", default=False)

    uploaded_doc = fields.Binary(string="Document Upload", attachment=True)  # , required=True
    doc_file_name = fields.Char(string="Document Name")

    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID")
    # onboard_id = fields.Many2one('kwonboard_all', ondelete='cascade', string="Onboard ID")

    _sql_constraints = [('identity_uniq', 'unique(emp_id,name)',
                         'Duplicate Identification documents not allowed.. !')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = dict(record._fields['name'].selection).get(record.name)
            result.append((record.id, record_name))
        return result

    # Date of issue validation added
    @api.constrains('date_of_issue')
    def validate_identity(self):
        current_date = str(datetime.now().date())
        for record in self:
            if record.date_of_issue:
                if str(record.date_of_issue) >= current_date:
                    raise ValidationError("Identification Document Date of Issue must be less than the current Date.")

    @api.constrains('date_of_issue', 'date_of_expiry')
    def validate_identity_data(self):
        for record in self:
            if record.date_of_issue and record.date_of_expiry:
                if str(record.date_of_expiry) < str(record.date_of_issue):
                    raise ValidationError(" Identification Document Date of Expiry Cannot be less then Date Of Issue")
                # elif not record.date_of_expiry:
                #     raise ValidationError("Please enter Identification Document Date Of Expiry.")

    @api.constrains('uploaded_doc')
    def validate_identity_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
       
        for rec in self:
            kw_validations.validate_file_mimetype(rec.uploaded_doc,allowed_file_list)
            kw_validations.validate_file_size(rec.uploaded_doc,4) 
