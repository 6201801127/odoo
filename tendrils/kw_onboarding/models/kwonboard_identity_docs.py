# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

import datetime
from datetime import date, datetime
# from lxml import etree
import os, base64

# import mimetypes
# from odoo.tools.mimetypes import guess_mimetype

from kw_utility_tools import kw_validations


class kwonboard_identity_docs(models.Model):
    _name = 'kwonboard_identity_docs'
    _description = "A model to store different identity documents of on-boarding."
    _rec_name = 'name'

    name = fields.Selection(string="Identification Type",
                            selection=[('1', 'PAN'), ('2', 'Passport'), ('3', 'Driving Licence'), ('4', 'Voter ID'),
                                       ('5', 'AADHAAR')], required=True)
    doc_number = fields.Char(string="Document Number", required=True, size=100)
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    renewal_sts = fields.Boolean("Renewal Applied", default=False)
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True,inverse="_inverse_field")
    filename = fields.Char('File Name')
    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID", )
    document_attachment_id = fields.Char(compute='_compute_identification_document_id')

    def _compute_identification_document_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_identity_docs'), ('res_field', '=', 'uploaded_doc')])
            attachment_data.write({'public': True})
            record.document_attachment_id = attachment_data.id

    @api.model
    def _inverse_field(self):
        for record in self:
            if record.uploaded_doc:
                bin_value = base64.b64decode(record.uploaded_doc)
                if not os.path.exists('onboarding_docs/' + str(record.enrole_id.id)):
                    os.makedirs('onboarding_docs/' + str(record.enrole_id.id))
                full_path = os.path.join(os.getcwd() + '/onboarding_docs/' + str(record.enrole_id.id), record.filename)
                # if os.path.exists(full_path):
                #     raise ValidationError("The file name "+self.filename+" exists.Please change your file name.")
                try:
                    with open(os.path.expanduser(full_path), 'wb') as fp:
                        fp.write(bin_value)
                        fp.close()
                except Exception as e:
                    # print(e)
                    pass

    @api.multi
    def write(self, vals):
        if 'uploaded_doc' in vals:
            for data in self:
                try:
                    os.remove('onboarding_docs/' + str(data.enrole_id.id) + '/' + data.filename)
                except Exception as e:
                    # print(e)
                    pass
        super(kwonboard_identity_docs, self).write(vals)
        return True

    @api.multi
    def unlink(self):
        for data in self:
            try:
                os.remove('onboarding_docs/' + str(data.enrole_id.id) + '/' + data.filename)
            except Exception as e:
                # print(e)
                pass
        return super(kwonboard_identity_docs, self).unlink()

    _sql_constraints = [('identity_uniq', 'unique(enrole_id,name)', 'Duplicate identification documents not allowed.. !')]

    # Date of issue validation added
    @api.constrains('date_of_issue', 'name')
    def validate_data(self):
        current_date = str(datetime.now().date())
        for record in self:
            if record.date_of_issue:
                if str(record.date_of_issue) >= current_date:
                    raise ValidationError("The date of issue of " + record.name + "document must be less than current date.")

    @api.constrains('uploaded_doc')
    def _check_filename(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for record in self:
            if record.uploaded_doc:
                # print(((len(self.uploaded_doc)*3/4)/1024)/1024)
                # mimetype = guess_mimetype(base64.b64decode(record.uploaded_doc))
                # if str(mimetype) not in allowed_file_list:
                #     raise ValidationError(_("Unsupported file format ! allowed file formats are .jpg , .jpeg , .png and .pdf "))
                # elif  ((len(record.uploaded_doc)*3/4)/1024)/1024 > 4.0:
                #     raise ValidationError(_("Maximum file size should be less than 4 mb."))

                kw_validations.validate_file_mimetype(record.uploaded_doc, allowed_file_list)
                kw_validations.validate_file_size(record.uploaded_doc, 4)

                # @api.constrains('date_of_issue', 'date_of_expiry')

    # def validate_identity_data(self):
    #     for record in self:
    #        if record.date_of_issue:
    #            if str(record.date_of_expiry) < str(record.date_of_issue):
    #                 raise ValidationError("Document expiry Date will not be less than Document Issue Date.")
    #             elif not record.date_of_expiry:
    #                 raise ValidationError("Please enter Document Expiry Date.")

    @api.constrains('date_of_issue', 'date_of_expiry')
    def validate_Identity_date(self):
        for record in self:
            if record.date_of_issue:
                if str(record.date_of_expiry) < str(record.date_of_issue):
                    raise ValidationError("Document expiry date should not be less than Issue date.")
                # elif not record.date_of_expiry:
                #     raise ValidationError("Please enter Document expiry date.")
