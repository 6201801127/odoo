# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
from odoo import tools, _
import re

from kw_utility_tools import kw_validations


class kw_emp_profile_qualification(models.Model):
    """ educational details"""
    _name = 'kw_emp_profile_qualification'
    _description = "Educational details of employees."
    _rec_name = "course_id"

    emp_id = fields.Many2one('kw_emp_profile', string="Employee ID")
    course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
                                                             ('3', 'Training And Certification')], required=True)
    course_id = fields.Many2one('kwmaster_course_name', string="Course Name", required=True)
    stream_id = fields.Many2one('kwmaster_stream_name', string="Stream", required=True)
    university_name = fields.Many2one('kwmaster_institute_name', string="University", required=True)
    division = fields.Char(string="Division / Grade", required=True, size=6)
    marks_obtained = fields.Float(string="% of marks obtained", required=True)
    uploaded_doc = fields.Binary(string="Document Upload")  # , required=True
    doc_file_name = fields.Char(string="Document Name")
    emp_educational_id = fields.Many2one('kwemp_educational_qualification', string='Educational Id')
    passing_details = fields.Many2many('kwmaster_specializations', string="Passing Details (Specialization)")
    expiry_date = fields.Date(string='Expiry Date')


    @api.model
    def _get_year_list(self):
        current_year = date.today().year

        return [(str(i), i) for i in range(current_year, 1953, -1)]

    passing_year = fields.Selection(string="Passing Year", selection='_get_year_list', required=True)

    @api.onchange('course_type')
    def change_stream_course_institute(self):
        course_type = self.course_type
        self.course_id = False
        self.stream_id = False
        self.university_name = False
        return {'domain': {'course_id': ([('course_type', '=', course_type)])}}

    @api.onchange('course_id')
    def change_stream_university(self):
        course_id = self.course_id.id
        self.stream_id = False
        self.university_name = False
        return {'domain': {'stream_id': ([('course_id', '=', course_id)]),
                           'university_name': ([('inst_course_ids', '=', course_id)])}}

    @api.onchange('stream_id')
    def _change_specilization(self):
        stream_id = self.stream_id.id
        self.passing_details = False
        return {'domain': {'passing_details': ([('stream_id', '=', stream_id)])}}

    @api.constrains('course_type', 'course_id')
    def validate_educational_course(self):
        for data in self:
            if data.course_type == '1':
                domain = [('id', '!=', data.id), ('emp_id', '=', data.emp_id.id), ('course_id', '=', data.course_id.id),
                          ('course_type', '=', data.course_type)]
                if self.search_count(domain) > 0:
                    raise ValidationError(_('Duplicate educational details are not allowed.'))

    # _sql_constraints = [('education_uniq', 'unique (emp_id,course_id)',
    #              'Duplicate educational details are  not allowed.. !')]
    @api.constrains('marks_obtained')
    def validate_marks_obtained(self):
        for record in self:
            if (record.marks_obtained > 100) or (record.marks_obtained < 0):
                raise ValidationError("Obtained mark should be greater than 0 and less than 100")

    @api.constrains('uploaded_doc')
    def validate_educational_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.uploaded_doc, allowed_file_list)
            kw_validations.validate_file_size(record.uploaded_doc, 4)
            
    @api.multi
    def action_download_edu_file(self):
        record = self.env['kw_emp_profile'].sudo().search([('id','=',self.emp_id.id)])
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download_emp_all_update_doc/{record.emp_id.id}/{self.id}',
            'target': 'self',
        }
            
