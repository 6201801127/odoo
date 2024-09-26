# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
from dateutil import relativedelta
from odoo import tools, _

from kw_utility_tools import kw_validations


# class for work experience details
class kwemp_work_experience(models.Model):
    _name = 'kwemp_work_experience'
    _description = "A model to store the worked experience of employees."

    kw_id = fields.Integer(string='Tendrils ID')
    country_id = fields.Many2one('res.country', string="Country Name", required=True)
    name = fields.Char(string="Previous Organization Name", required=True, size=100)
    designation_name = fields.Char(string="Job Profile ", required=True, size=100)
    organization_type = fields.Many2one('kwemp_organization', string="Organization Type", required=True)
    industry_type = fields.Many2one('kwemp_industry', string="Industry Type", )

    effective_from = fields.Date(string="Effective From", required=True)
    effective_to = fields.Date(string="Effective To", required=True)
    uploaded_doc = fields.Binary(string="Document Upload")  # , required=True
    doc_file_name = fields.Char(string="Document Name")
    effective_experiance = fields.Char(string="Experience", compute='_compute_experience_effect')

    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID")

    # onboard_id = fields.Many2one('kwonboard_all',ondelete='cascade', string="Onboard ID")

    @api.depends('effective_from', 'effective_to')
    def _compute_experience_effect(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.effective_from and rec.effective_to:
                exp_difference = relativedelta.relativedelta(rec.effective_to, rec.effective_from)
                total_years += exp_difference.years
                total_months += exp_difference.months
                if exp_difference.days >= 30:
                    total_months += exp_difference.days // 30
                # print("effective_to is %s effective_from %s  >>> " % (rec.effective_to, rec.effective_from), exp_difference)
                # print("Difference is %s year, %s months >>> " % (total_years, total_months), exp_difference)

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:
                rec.effective_experiance = " %s.%s" % (total_years, total_months)
                # print('experience effect===========',rec.effective_experiance)
            else:
                rec.effective_experiance = ''

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
