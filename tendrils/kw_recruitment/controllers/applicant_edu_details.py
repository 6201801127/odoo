# -*- coding: utf-8 -*-
import base64, re

from odoo import http
from odoo.exceptions import ValidationError


class ApplicantEducationalInfo:
    # #get specilization master data
    def getSpecializationMaster(self):
        specialization_rec = http.request.env['kwmaster_specializations'].sudo().search([])
        specialization_data = {}

        for record in specialization_rec:
            # print(record.stream_id.course_id.id)
            if record.stream_id.course_id.id not in specialization_data:
                # course_index = course_index+str(record.stream_id.course_id.id)     
                specialization_data[record.stream_id.course_id.id] = []

            specialization_data[record.stream_id.course_id.id].append(
                dict(id=record.id,
                     stream_id=record.stream_id.id,
                     name=record.name,
                     course_id=record.stream_id.course_id.id
                     )
            )
        return specialization_data

    # #read educational information data from DB
    def getEducationaldatafromDB(self, enroll_data):
        education_data = enroll_data.edu_data_ids  
        edudict = {'applicant_name': enroll_data.partner_name, 'professionalcourse': [], 'trainingcourse': []}
        finaltrainingcourse = []
        finalprofessionalcourse = []

        for record in education_data:
            for data in record:
                str_course_id = str(data.course_id.id)
                if data.course_type == '1':
                    edudict['ddlStream' + str_course_id] = data.stream_id.id
                    edudict['ddlBoard' + str_course_id] = data.university_name.id
                    edudict['ddlYear' + str_course_id] = data.passing_year
                    edudict['txtGrade' + str_course_id] = data.division
                    edudict['txtPercent' + str_course_id] = data.marks_obtained
                    # edudict['flFilename' + str_course_id] = data.filename

                    for passing_data in data.passing_details:
                        edudict['specialization_' + str(data.stream_id.id) + '_' + str(passing_data.id)] = passing_data.id

                elif record.course_type == '2':
                    temp = {'ddlprofStream': data.stream_id.id,
                            'ddlprofBoard': data.university_name.id,
                            'ddlprofYear': data.passing_year,
                            'txtprofGrade': data.division,
                            'txtprofPercent': data.marks_obtained,
                            # 'proffilename': data.filename
                            }
                    finalprofessionalcourse.append(temp)

                else:
                    temp = {'ddltrainingStream': data.stream_id.id,
                            'ddltrainingBoard': data.university_name.id,
                            'ddltrainingYear': data.passing_year,
                            'txttrainingGrade': data.division,
                            'txttrainingPercent': data.marks_obtained,
                            # 'trainfilename': data.filename
                            }
                    finaltrainingcourse.append(temp)

        edudict['edu'] = edudict
        edudict['professionalcourse'] = finalprofessionalcourse
        edudict['trainingcourse'] = finaltrainingcourse
        edudict['specialization_master'] = self.getSpecializationMaster()
        return edudict

    def saveEducationalinfo(self, enrollment_data, **kw):
        # print(kw)
        try:
            courses = http.request.env['kwmaster_course_name'].sudo().search([])
            specialization_data = self.getSpecializationMaster()

            professional_course_id = training_course_id = 0
            educational_form_data = {}

            kw['trainingcourse'] = kw['professionalcourse'] = []
            employee_data = {'edu_data_ids': []}

            # fetch existing data from education table
            education_data = enrollment_data.edu_data_ids  # http.request.env['kwonboard_edu_qualification'].sudo().search([('enrole_id', '=', enrolment_id)])

            edited_education_data = []
            posted_education_info = []
            # saving basic education details
            for course in courses:
                course_id = course.id
                str_course_id = str(course_id)

                if course.course_type == '2':
                    professional_course_id = course_id
                elif course.course_type == '3':
                    training_course_id = course_id

                # if course.course_type == '1' and kw['ddlStream' + str_course_id] and int(kw['ddlStream' + str_course_id]) != '':
                if course.course_type == '1' and kw['ddlStream' + str_course_id] and kw['ddlStream' + str_course_id].isdigit():

                    temp_data = dict()

                    # uploaddoc = base64.encodestring(kw['ddlFile' + str_course_id].read())
                    stream_id = int(kw['ddlStream' + str_course_id], 10) if int(kw['ddlStream' + str_course_id], 10) > 0 else False
                    university_name = int(kw['ddlBoard' + str_course_id], 10) if int(kw['ddlBoard' + str_course_id], 10) > 0 else None
                    passing_year = kw['ddlPYear' + str_course_id] if int(kw['ddlPYear' + str_course_id], 10) > 0 else None
                    division = kw['txtGrade' + str_course_id].strip() if kw['txtGrade' + str_course_id] else None
                    marks_obtained = kw['txtPercent' + str_course_id].strip() if kw['txtPercent' + str_course_id] else None
                    # file_name = kw['hidDllFile' + str_course_id]

                    temp_data = {'course_type': course.course_type,
                                 'course_id': course_id,
                                 'stream_id': stream_id,
                                 'university_name': university_name,
                                 'passing_year': passing_year,
                                 'division': division,
                                 'marks_obtained': marks_obtained,
                                 'passing_details': []
                                 }

                    #  'uploaded_doc': uploaddoc,
                    #  'filename': file_name,

                    if course_id in specialization_data:
                        for specilizations_rec in specialization_data[course_id]:
                            specialization_id = int(kw['specialization_' + str(stream_id) + '_' + str(specilizations_rec['id'])], 10) \
                                if 'specialization_' + str(stream_id) + '_' + str(specilizations_rec['id']) in kw else False

                            if specialization_id:
                                temp_data['passing_details'].append(specilizations_rec['id'])
                                # #form data
                                educational_form_data['specialization_' + str(stream_id) + '_' + str(specilizations_rec['id'])] = specilizations_rec['id']

                    posted_education_info.append(temp_data)

                    # #submitted data format
                    educational_form_data['ddlStream' + str_course_id] = stream_id
                    educational_form_data['ddlBoard' + str_course_id] = university_name
                    educational_form_data['ddlYear' + str_course_id] = passing_year
                    educational_form_data['txtGrade' + str_course_id] = division
                    educational_form_data['txtPercent' + str_course_id] = marks_obtained
                    # educational_form_data['flFilename' + str_course_id] = file_name

            kw['edu'] = educational_form_data

            digit = lambda x: re.search(r'\d+', x).group(0)

            temp_prof_id = []
            temp_cert_id = []
            for key, value in kw.items():
                temp_key = str(key)
                temp_data = dict()

                # print("Print profesional details...")
                # Professional course details save
                if temp_key[0:5] == 'prof_':
                    temp_seq = digit(temp_key)

                    if temp_seq not in temp_prof_id and kw['prof_stream_' + temp_seq] and int(kw['prof_stream_' + temp_seq]) > 0:
                        temp_prof_id.append(temp_seq)

                        stream_id = int(kw['prof_stream_' + temp_seq]) if int(kw['prof_stream_' + temp_seq]) > 0 else None
                        university_name = int(kw['prof_board_' + temp_seq]) if int(kw['prof_board_' + temp_seq]) > 0 else None
                        passing_year = kw['prof_year_' + temp_seq] if int(kw['prof_year_' + temp_seq]) > 0 else None
                        division = kw['prof_grade_' + temp_seq].strip() if kw['prof_grade_' + temp_seq] else None
                        marks_obtained = kw['prof_percent_' + temp_seq].strip() if kw['prof_percent_' + temp_seq] else None
                        # prof_filename = kw['prof_filename_' + temp_seq] if kw['prof_filename_' + temp_seq] else None

                        temp_data = {'course_type': '2',
                                     'course_id': professional_course_id,
                                     'stream_id': stream_id,
                                     'university_name': university_name,
                                     'passing_year': passing_year,
                                     'division': division,
                                     'marks_obtained': marks_obtained,
                                     }
                        # 'uploaded_doc': base64.encodestring(kw['prof_file_' + temp_seq].read()) if kw['prof_file_' + temp_seq] else '',
                        # 'filename': prof_filename

                        posted_education_info.append(temp_data)

                        # #form data save to kw to reload the page with data after error
                        frmtemp = {'ddlprofStream': stream_id,
                                   'ddlprofBoard': university_name,
                                   'ddlprofYear': passing_year,
                                   'txtprofGrade': division,
                                   'txtprofPercent': marks_obtained
                                   }
                        # 'proffilename': prof_filename
                        kw['professionalcourse'].append(frmtemp)

                #     # certification course details save
                elif temp_key[0:5] == 'cert_':
                    temp_seq = digit(temp_key)
                    if temp_seq not in temp_cert_id and kw['cert_stream_' + temp_seq] and int(kw['cert_stream_' + temp_seq]) > 0:
                        temp_cert_id.append(temp_seq)

                        stream_id = int(kw['cert_stream_' + temp_seq]) if int(kw['cert_stream_' + temp_seq]) > 0 else None
                        university_name = int(kw['cert_board_' + temp_seq]) if int(kw['cert_board_' + temp_seq]) > 0 else None
                        passing_year = kw['cert_year_' + temp_seq] if int(kw['cert_year_' + temp_seq]) > 0 else None
                        division = kw['cert_grade_' + temp_seq].strip() if kw['cert_grade_' + temp_seq] else None
                        marks_obtained = kw['cert_percent_' + temp_seq].strip() if kw['cert_percent_' + temp_seq] else None
                        # cert_filename = kw['cert_filename_' + temp_seq] if kw['cert_filename_' + temp_seq] else None
                        temp_data = {'course_type': '3',
                                     'course_id': training_course_id,
                                     'stream_id': stream_id,
                                     'university_name': university_name,
                                     'passing_year': passing_year,
                                     'division': division,
                                     'marks_obtained': marks_obtained,
                                     }
                        # 'uploaded_doc': base64.encodestring(kw['cert_file_' + temp_seq].read()) if kw['cert_file_' + temp_seq] else '',
                        # 'filename': cert_filename
                        posted_education_info.append(temp_data)

                        # #form data save to kw to reload the page with data after error
                        frmtemp = {'ddltrainingStream': stream_id,
                                   'ddltrainingBoard': university_name,
                                   'ddltrainingYear': passing_year,
                                   'txttrainingGrade': division,
                                   'txttrainingPercent': marks_obtained,
                                   }
                        # 'trainfilename': cert_filename
                        kw['trainingcourse'].append(frmtemp)

            if len(posted_education_info) > 0:
                for post_info in posted_education_info:

                    # if post_info['uploaded_doc'] == b'':
                    #     del post_info['uploaded_doc']
                    #     del post_info['filename']

                    if post_info['course_type'] == '1':
                        filtered_edit_data = education_data.filtered(lambda r: r.course_id.id == int(post_info['course_id']) and r.course_type == post_info['course_type'])

                        if len(post_info['passing_details']):
                            post_info['passing_details'] = [[6, 'false', post_info['passing_details']]]

                    else:
                        filtered_edit_data = education_data.filtered(lambda r: r.course_id.id == int(post_info['course_id']) and r.course_type == post_info['course_type'] and r.stream_id.id == int(post_info['stream_id']))

                    if filtered_edit_data:
                        employee_data['edu_data_ids'].append([1, filtered_edit_data.id, post_info])
                        edited_education_data.append(filtered_edit_data.id)
                    else:
                        employee_data['edu_data_ids'].append([0, 0, post_info])

            # #for the records to be deleted
            if edited_education_data:
                filtered_del_data = education_data.filtered(lambda r: r.id not in edited_education_data)

                if filtered_del_data:
                    for del_data in filtered_del_data:
                        employee_data['edu_data_ids'].append([2, del_data.id, False])

            # print(employee_data)

            # #update the onboarding record
            enrollment_data.sudo().write(employee_data)

            # #after saving into db, return data frm db
            resdata = self.getEducationaldatafromDB(enrollment_data)
            resdata['success_msg'] = 'Educational details saved successfully'

            if 'draft' in kw:
                resdata['draft'] = kw['draft']
            return resdata

        except Exception as e:
            http.request._cr.rollback()
            kw['err_msg'] = str(e)

            return kw
