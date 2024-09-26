# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime

from kw_utility_tools import kw_validations


# class for identity documents
class kw_emp_profile_identity_docs(models.Model):
    _name = 'kw_emp_profile_identity_docs'
    _description = "A model to store the identification documents of employees."

    name = fields.Selection(string="Identification Type",
                            selection=[('1', 'PAN'), ('2', 'Passport'), ('3', 'Driving Licence'), ('4', 'Voter ID'),
                                       ('5', 'AADHAAR'), ('6', 'Yellow Fever')], required=True)
    doc_number = fields.Char(string="Document Number", size=100, required=True)
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    renewal_sts = fields.Boolean("Renewal Applied", default=False)

    uploaded_doc = fields.Binary(string="Document Upload", attachment=True)  # , required=True
    doc_file_name = fields.Char(string="Document Name")

    emp_id = fields.Many2one('kw_emp_profile', string="Employee ID")
    emp_document_id = fields.Many2one('kwemp_identity_docs', string='Document Id')

    _sql_constraints = [('identity_uniq', 'unique(emp_id,name)',
                         'Duplicate Identification documents not allowed.. !')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = dict(self._fields['name'].selection).get(self.name)
            result.append((record.id, record_name))
        return result

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
                    raise ValidationError("Identification Document Date of Expiry Cannot be less then Date Of Issue")

    @api.constrains('uploaded_doc')
    def validate_identity_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for rec in self:
            kw_validations.validate_file_mimetype(rec.uploaded_doc, allowed_file_list)
            kw_validations.validate_file_size(rec.uploaded_doc, 4)
            
    @api.multi
    def action_download_identity_file(self):
        record = self.env['kw_emp_profile'].sudo().search([('id','=',self.emp_id.id)])
        # print("self context==========================",self,record)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download_emp_identity_update_doc/{record.emp_id.id}/{self.id}',
            'target': 'self',
        }
