# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
from odoo import tools, _
import re

from kw_utility_tools import kw_validations

"""# educational details"""


class kwemp_educational_details(models.Model):
    _name = 'kwemp_educational_qualification'
    _description = "Educational details of employees."
    _rec_name = "course_id"

    kw_id = fields.Integer(string='Tendrils ID')
    course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
                                                             ('3', 'Training And Certification')], required=True)
    course_id = fields.Many2one('kwmaster_course_name', string="Course Name", required=True)
    stream_id = fields.Many2one('kwmaster_stream_name', string="Stream", required=True)
    university_name = fields.Many2one('kwmaster_institute_name', string="University", required=True)
    passing_details = fields.Many2many('kwmaster_specializations', string="Passing Details (Specialization)")
    # employee_id = fields.Many2one('kwemp_all',ondelete='cascade', string="Employee ID")
    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID")
    expiry_date = fields.Date(string="Expiry Date")

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]

    passing_year = fields.Selection(string="Passing Year", selection='_get_year_list', required=True)  #
    division = fields.Char(string="Division / Grade", required=True, size=6)
    marks_obtained = fields.Float(string="% of marks obtained", required=True)
    uploaded_doc = fields.Binary(string="Document Upload")  # , required=True
    doc_file_name = fields.Char(string="Document Name")

    @api.onchange('course_type')
    def change_stream_course_institute(self):
        course_type = self.course_type
        self.course_id = False
        self.stream_id = False
        self.university_name = False
        return {'domain': {'course_id': ([('course_type', '=', course_type)]), }}

    @api.onchange('course_id')
    def change_stream_university(self):
        course_id = self.course_id.id
        self.stream_id = False
        self.university_name = False
        return {'domain': {'stream_id': ([('course_id', '=', course_id)]),
                           'university_name': ([('inst_course_ids', 'in', course_id)])}}

    @api.onchange('stream_id')
    def _change_specilization(self):
        stream_id = self.stream_id.id
        self.passing_details = False
        return {'domain': {'passing_details': ([('stream_id', '=', stream_id)]), }}

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

    @api.constrains('passing_year')
    def validate_passing_year(self):
        getcourse_setting = self.env['kw_course_setting'].sudo().search([])
        for record in self:
            if record.course_type == '1':
                filteredrec = getcourse_setting.filtered(lambda r: r.course_id == record.course_id)

                if filteredrec.child_id:
                    """##get parent id course records and compare the passing year and age """
                    getcourse_recds = self.env['kwemp_educational_qualification'].sudo().search(
                        [('emp_id', '=', record.emp_id.id), ('course_id', '=', filteredrec.child_id.id)])

                    if getcourse_recds and len(getcourse_recds) == 1:
                        if int(getcourse_recds.passing_year) >= int(record.passing_year):
                            # print('sssss')
                            raise ValidationError(
                                "Passing year of " + record.course_id.name + " should be greater than " + filteredrec.child_id.name)
                        elif int(record.passing_year) < (int(getcourse_recds.passing_year) + filteredrec.diff_year):
                            raise ValidationError(
                                "Passing year difference between " + record.course_id.name + " and " + filteredrec.child_id.name + " should be at least " + str(
                                    filteredrec.diff_year) + " year(s)")
