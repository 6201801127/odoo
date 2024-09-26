# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
from odoo import tools, _

from kw_utility_tools import kw_validations


# class for work experience details
class kw_emp_profile_work_experience(models.Model):
    _name = 'kw_emp_profile_work_experience'
    _description = "A model to store the worked experience of employees."

    country_id = fields.Many2one('res.country', string="Country Name", required=True)
    name = fields.Char(string="Previous Organization Name", required=True, size=100)
    designation_name = fields.Char(string="Job Profile ", required=True, size=100)
    organization_type = fields.Many2one('kwemp_organization', string="Organization Type", required=True)
    industry_type = fields.Many2one('kwemp_industry', string="Industry Type", )

    effective_from = fields.Date(string="Effective From", required=True)
    effective_to = fields.Date(string="Effective To", required=True)
    uploaded_doc = fields.Binary(string="Document Upload")  # , required=True
    doc_file_name = fields.Char(string="Document Name")
    emp_id = fields.Many2one('kw_emp_profile', ondelete='cascade', string="Employee ID")
    emp_work_id = fields.Many2one('kwemp_work_experience', string='Work Id')

    @api.constrains('effective_from')
    def validate_data(self):
        current_date = str(datetime.now().date())
        for record in self:
            if str(record.effective_from) >= current_date:
                raise ValidationError("The date of issue of work experience should be less than current date.")

    @api.constrains('effective_to')
    def validate_effective_to(self):
        current_date = str(datetime.now().date())
        for record in self:
            if str(record.effective_to) >= current_date:
                raise ValidationError("The effective to date of work experience should be less than current date.")

            if str(record.effective_to) <= str(record.effective_from):
                raise ValidationError("The effective to date should be later than effective from date.")

    @api.constrains('uploaded_doc')
    def validate_uploaded_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for record in self:
            kw_validations.validate_file_mimetype(record.uploaded_doc, allowed_file_list)
            kw_validations.validate_file_size(record.uploaded_doc, 4)
            
    @api.multi
    def action_download_work_file(self):
        record = self.env['kw_emp_profile'].sudo().search([('id','=',self.emp_id.id)])
        # print("self context==========================",self,record)
      
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download_emp_work_update_doc/{record.emp_id.id}/{self.id}',
            'target': 'self',
        }
