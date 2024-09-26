import json
import requests
import calendar
import datetime
# from datetime import datetime, date
from dateutil import relativedelta
from odoo import fields, models, api
import base64 
import urllib.request


class EducationData(models.TransientModel):
    _name = "education_sync_data_v5"
    _description = "Fetch Education data from v5"

    # employee_id = fields.Many2one('hr.employee', string="User Id")

    employee_id = fields.Many2many(comodel_name='hr.employee', relation='education_sync_employee_rel',
                                   column1='rec_id', column2='emp_id', string="Employees")
    page_no = fields.Integer(string="Page No", default=1)
    page_size = fields.Integer(string="Page Size", default=1)

    @api.multi
    def button_get_education_data(self):
        # Fetch the url
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_education_data_url')
        course_type = course_id = stream_id = university_id = specialization_ids = passing_year = division = marks_obtained = False
        # print("parameter_url----->>>", parameter_url)
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            for emp in self.employee_id:
                user_id = emp.kw_id if emp and emp.kw_id else 0
                employee_id = emp.id if emp else 0
                # parameters for url
                education_data_dict = {
                    "UserID": user_id,
                    "PageNo": self.page_no,
                    "PageSize": self.page_size,
                }
                # print("parameter_url >> ", parameter_url, education_data_dict)
                resp = requests.post(parameter_url, headers=header, data=json.dumps(education_data_dict))
                json_data = resp.json()
                # print('All Data From Api---------------------->>>>', json_data)
                for education in json_data:
                    # print("Every education Data is---------->", education, '\n')
                    stream_kw_id = int(education.get('StreamID', '0'))
                    board_name = education.get('BoardName', '')
                    stream_name = education.get('StreamName', '')
                    course_ids = int(education.get('Course_ID', '0'))
                    course_name = education.get('Course_Name', '')
                    qualification_kw_id = int(education.get('INTQUALIF_ID', '0'))
                    upload_url = education.get('URL', '')
                    # print('&&&&&&', upload_url)
                    response = urllib.request.urlopen(upload_url.replace(" ", "%20"))
                    data_bytes = base64.b64encode(response.read())
                    stream_id = self.env['kwmaster_stream_name'].search([('kw_id', '=', stream_kw_id)], limit=1)
                    qualification_rec = self.env['kwemp_educational_qualification'].search(
                        [('kw_id', '=', qualification_kw_id)], limit=1)

                    # ## search course ###
                    if not stream_id:
                        created_stream = stream_id.create({'name': stream_name,
                                                           'course_id': course_ids,
                                                           'kw_id': stream_kw_id
                                                           })
                        # print("created_stream is--->", created_stream)
                    course_id = stream_id.course_id if stream_id else created_stream.course_id

                    # print("Stream is--->", stream_id)
                    # print("course_id is ---> >>>>>>>>> ------ ", course_ids, course_id)
                    # course_type = course_id.course_type if course_id else False
                    # print('course_type--------------->', course_type)
                    if course_ids in [1, 2, 3, 4]:
                        course_type = "1"
                    elif course_ids == 5:
                        course_type = "2"
                    else:
                        course_type = "3"

                    specialization_ids = []

                    university_obj = self.env['kwmaster_institute_name']
                    university_id = university_obj.search([('name', '=ilike', board_name)], limit=1)
                    # print("board id is--->", university_id)
                    if not university_id and course_id:
                        university_id = university_obj.create({'name': board_name,
                                                               'inst_course_ids': [[6, 0, [course_id.id]]]})

                    for stream in education.get('Specialization', []):
                        if stream.get('SpecializationName', False) and stream.get('SpecializationID', 'False').isnumeric():
                            specialization_kw_id = int(stream.get('SpecializationID'))
                            if specialization_kw_id:
                                specialization_id = self.env['kwmaster_specializations'].search(
                                    [('kw_id', '=', specialization_kw_id)], limit=1)
                                if specialization_id:
                                    specialization_ids.append(specialization_id.id)
                                else:
                                    created_specialization = specialization_id.create({
                                        'name': stream.get('SpecializationName'),
                                        'stream_id': stream_id.id if stream_id else created_stream.id,
                                        'kw_id': specialization_kw_id
                                    })
                                    specialization_ids.append(created_specialization.id)

                    passing_year = education.get('PassingYear', '')
                    division = education.get('Division', '')
                    marks_obtained = float(education.get('Percentage', '0.0')) if education.get('Percentage', '0.0') != '' else 0

                    # data = {'educational_details_ids': [[0, 0, {
                    #     'course_type': course_type,
                    #     'course_id': course_id if course_id else False,
                    #     'stream_id': stream_id.id if stream_id else False,
                    #     'university_name': university_id.id,
                    #     'passing_details': [[4, id] for id in specialization_ids] if specialization_ids else [],
                    #     'passing_year': passing_year,
                    #     'division': division,
                    #     'marks_obtained': marks_obtained,
                    #     'uploaded_doc': False
                    # }]]}

                    # print("data prepared is--------------->", data)
                    # emp.write(data)

                    education_data_dict = {
                        'emp_id': employee_id,
                        'course_type': course_type,
                        'course_id': course_id.id if course_id else False,
                        'stream_id': stream_id.id if stream_id else created_stream.id,
                        'university_name': university_id.id,
                        'passing_details': [[4, id] for id in specialization_ids] if specialization_ids else [],
                        'passing_year': passing_year,
                        'division': division,
                        'marks_obtained': marks_obtained,
                        'kw_id': qualification_kw_id,
                        'uploaded_doc': data_bytes
                    }
                    if course_ids in [1, 2, 3, 4]:
                        qualification_rec_x = self.env['kwemp_educational_qualification'].search(
                            [('course_id', '=', course_id.id), ('emp_id', '=', employee_id),
                             ('course_type', '=', course_type)],
                            limit=1)
                    else:
                        qualification_rec_x = self.env['kwemp_educational_qualification'].search(
                            [('course_id', '=', course_id.id), ('emp_id', '=', employee_id),
                             ('stream_id', '=', stream_id.id if stream_id else created_stream.id)],
                            limit=1)

                    # print("qualification_rec_x   >> ", qualification_rec, qualification_rec_x, education_data_dict)

                    if not qualification_rec and not qualification_rec_x:
                        data = self.env['kwemp_educational_qualification'].create(education_data_dict)
                        # print("create data prepared is ------------>", data)
                    else:
                        if qualification_rec:
                            data = qualification_rec.write(education_data_dict)
                            # print("update 1 qualification_rec data prepared is -------------> ", data)
                        else:
                            data = qualification_rec_x.write(education_data_dict)
                            # print("update 2 qualification_rec_x data prepared is ------------> ", data)

            self.env.user.notify_success("Employee data updated successfully")
