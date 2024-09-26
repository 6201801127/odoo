# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
import datetime
from datetime import date, datetime

import re
import time

import os, base64
# import mimetypes
# from odoo.tools.mimetypes import guess_mimetype

from kw_utility_tools import kw_validations


class kwonboard_work_experience(models.Model):
    _name = 'kwonboard_work_experience'
    _description = "Work experience of on-boardings."

    country_id = fields.Many2one('res.country', string="Country Name", required=True)
    name = fields.Char(string="Previous Organization Name", required=True, size=100)
    designation_name = fields.Char(string="Job Profile ", required=True, size=100)
    organization_type = fields.Many2one('kwemp_organization', string="Organization Type", required=True)
    industry_type = fields.Many2one('kwemp_industry', string="Industry Type", )

    effective_from = fields.Date(string="Effective From", required=True)
    effective_to = fields.Date(string="Effective To", required=True)
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True, inverse="_inverse_field")
    filename = fields.Char("file name", )

    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID", )
    document_attachment_id = fields.Char(compute='_compute_work_experience_document_id')

    def _compute_work_experience_document_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_work_experience'), ('res_field', '=', 'uploaded_doc')])
            attachment_data.write({'public': True})
            record.document_attachment_id = attachment_data.id

    @api.model
    def _inverse_field(self):
        for rec in self:
            if rec.uploaded_doc:
                bin_value = base64.b64decode(rec.uploaded_doc)
                path = 'onboarding_docs/' + str(rec.enrole_id.id)
                if not os.path.exists(path):
                    os.makedirs(path)
                full_path = os.path.join(os.getcwd() + '/' + path, rec.filename)
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
        super(kwonboard_work_experience, self).write(vals)
        return True

    @api.multi
    def unlink(self):
        for data in self:
            try:
                os.remove('onboarding_docs/' + str(data.enrole_id.id) + '/' + data.filename)
            except Exception as e:
                # print(e)
                pass
        return super(kwonboard_work_experience, self).unlink()

    @api.constrains('effective_from', 'effective_to')
    def validate_data(self):
        current_date = str(datetime.now().date())
        date_list = []
        for record in self:
            if str(record.effective_from) >= current_date:
                raise ValidationError("Effective From work experience Date should be less than current date.")
            # if str(record.effective_to) >= current_date:
            #     raise ValidationError("Effective to work experience should be less than current date.")
            if datetime.strptime(str(record.effective_to), '%Y-%m-%d') <= datetime.strptime(str(record.effective_from), '%Y-%m-%d'):
                raise ValidationError("Experience To Date should not be less or equal to Experience From Date.")

    @api.constrains('uploaded_doc')
    def _check_filename(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for rec in self:
            if rec.uploaded_doc:
                # mimetype = guess_mimetype(base64.b64decode(rec.uploaded_doc))
                # if str(mimetype) not in allowed_file_list:
                #     raise ValidationError(_("Unsupported file format ! allowed file formats are .jpg , .jpeg , .png and .pdf "))
                # elif  ((len(rec.uploaded_doc)*3/4)/1024)/1024 > 4.0:
                #     raise ValidationError(_("Maximum file size should be less than 4 mb."))

                kw_validations.validate_file_mimetype(rec.uploaded_doc, allowed_file_list)
                kw_validations.validate_file_size(rec.uploaded_doc, 4)
