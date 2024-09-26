# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date, datetime

import os, base64

# from odoo.tools.mimetypes import guess_mimetype

from kw_utility_tools import kw_validations


# a model for Education details : opening
class kwonboard_edu_qualification(models.Model):
    _name = 'kwonboard_edu_qualification'
    _description = "A  model to store different educational qualifications of on-boarding."

    course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
                                                             ('3', 'Training And Certification')], required=True)
    course_id = fields.Many2one('kwmaster_course_name', string="Course Name", required=True)
    stream_id = fields.Many2one('kwmaster_stream_name', string="Stream", required=True)
    university_name = fields.Many2one('kwmaster_institute_name', string="University", required=True)
    passing_details = fields.Many2many('kwmaster_specializations', string="Passing Details (Specialization)")
    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID")
    passing_year = fields.Selection(string="Passing Year", selection='_get_year_list', required=True)
    division = fields.Char(string="Division / Grade", required=True, size=6)
    marks_obtained = fields.Float(string="% of marks obtained", required=True)
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True)  # ,inverse="_inverse_field"
    filename = fields.Char('filename')
    emp_id = fields.Many2one('hr.employee')
    document_attachment_id = fields.Char(compute='_compute_education_document_id')

    def _compute_education_document_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_edu_qualification'), ('res_field', '=', 'uploaded_doc')])
            attachment_data.write({'public': True})
            record.document_attachment_id = attachment_data.id

    # @api.model
    # def _inverse_field(self):
    #         if self.uploaded_doc:
    #             bin_value=base64.b64decode(self.uploaded_doc)
    #             if not os.path.exists('onboarding_docs/'+str(self.enrole_id.id)):
    #                 os.makedirs('onboarding_docs/'+str(self.enrole_id.id))
    #             full_path=os.path.join(os.getcwd()+'/onboarding_docs/'+str(self.enrole_id.id),self.filename)
    #             # if os.path.exists(full_path):
    #             #     raise ValidationError("The file name "+self.filename+" exists.Please change your file name.")
    #             try:
    #                 with open(os.path.expanduser(full_path), 'wb') as fp:
    #                     fp.write(bin_value)
    #                     fp.close()
    #             except Exception as e:
    #                 print(e)

    @api.multi
    def write(self, vals):
        if 'uploaded_doc' in vals:
            for data in self:
                try:
                    os.remove('onboarding_docs/' + str(data.enrole_id.id) + '/' + data.filename)
                except Exception as e:
                    # print(e)
                    pass
        edu_record = super(kwonboard_edu_qualification, self).write(vals)
        # if edu_record:
        #     self.env.user.notify_success(message='Education qualification updated successfully')
        # else:
        #     self.env.user.notify_danger(message='Education qualification updation failed')
        return True

    @api.multi
    def unlink(self):
        for data in self:
            try:
                os.remove('onboarding_docs/' + str(data.enrole_id.id) + '/' + data.filename)
            except Exception as e:
                # print(e)
                pass
        return super(kwonboard_edu_qualification, self).unlink()

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]

    @api.model
    def get_year_options(self):
        return self._get_year_list()

    @api.onchange('course_type')
    def _change_stream_course_institute(self):
        course_type = self.course_type
        self.course_id = False
        self.stream_id = False
        self.university_name = False
        return {'domain': {'course_id': ([('course_type', '=', course_type)]), }}

    @api.onchange('course_id')
    def _change_stream(self):
        if self.course_id:
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

    @api.constrains('uploaded_doc')
    def _check_filename(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            if record.uploaded_doc:
                kw_validations.validate_file_mimetype(record.uploaded_doc, allowed_file_list)
                kw_validations.validate_file_size(record.uploaded_doc, 4)

    @api.constrains('marks_obtained')
    def validate_marks_obtained(self):
        for record in self:
            if (record.marks_obtained > 100) or (record.marks_obtained < 0):
                raise ValidationError("Obtained mark should be greater than 0 and less than 100")

    @api.constrains('passing_year')
    def validate_passing_year(self):
        getcourse_setting = self.env['kw_course_setting'].sudo().search([])
        for record in self:
            if record.course_type == '1':
                filteredrec = getcourse_setting.filtered(lambda r: r.course_id == record.course_id)
                if filteredrec.child_id:
                    # get parent id course records and compare the passing year and age
                    getcourse_recds = self.env['kwonboard_edu_qualification'].sudo().search(
                        [('enrole_id', '=', record.enrole_id.id), ('course_id', '=', filteredrec.child_id.id)])
                    if getcourse_recds and len(getcourse_recds) == 1:
                        if int(getcourse_recds.passing_year) >= int(record.passing_year):
                            raise ValidationError(
                                "Passing year of " + record.course_id.name + " should be greater than " + filteredrec.child_id.name)
                        elif int(record.passing_year) < (int(getcourse_recds.passing_year) + filteredrec.diff_year):
                            raise ValidationError(
                                "Passing year difference between " + record.course_id.name + " and " + filteredrec.child_id.name + " should be at least " + str(
                                    filteredrec.diff_year) + " year(s)")

    # _sql_constraints = [('education_uniq', 'unique (enrole_id,course_id)',
    #              'Duplicate educational details are not allowed.. !')]

    # @api.constrains('course_type', 'course_id')
    # def validate_educational_course(self):
    #     for data in self:
    #         if data.course_type == '1':
    #             domain = [('id', '!=', data.id),('emp_id','=',data.emp_id.id),('course_id','=',data.course_id.id),('course_type','=',data.course_type)]               
    #             if self.search_count(domain) > 0:
    #                 raise ValidationError(_('Duplicate educational details are not allowed.'))
