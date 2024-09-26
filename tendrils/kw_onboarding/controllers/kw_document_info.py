import base64
import re

from odoo import http
from odoo.exceptions import ValidationError


class DocumentInfo:
    def getDocumentdetailsfromDB(self, enroll_data):
        # educdict = {'educational_ids': enroll_data.educational_ids,
        #             'work_experience_ids': enroll_data.work_experience_ids,
        #             'identification_ids': enroll_data.identification_ids}
        # documentDict = {
        #     'submit_edu_work': enroll_data.applicant_id.submit_edu_work if enroll_data.applicant_id.submit_edu_work is True else False
        # }
        documentDict = {}
        education = []
        experience = []
        identification = []
        documentDict['personal_image'] = enroll_data.image_id
        documentDict['hidden_personal_image'] = enroll_data.image_name

        documentDict['medical_certificate'] = enroll_data.medical_certifcate_attachment_id
        documentDict['hidden_medical_certificate'] = enroll_data.certificate_name

        documentDict['uploaded_payslip_doc1'] = enroll_data.payslip_attachment1_id
        documentDict['hidden_payslip_doc1'] = enroll_data.payslip_filename1
        
        documentDict['uploaded_payslip_doc2'] = enroll_data.payslip_attachment2_id
        documentDict['hidden_payslip_doc2'] = enroll_data.payslip_filename2
        
        documentDict['uploaded_payslip_doc3'] = enroll_data.payslip_attachment3_id
        documentDict['hidden_payslip_doc3'] = enroll_data.payslip_filename3

        documentDict['experience_sts'] = enroll_data.experience_sts
        documentDict['previous_payslip_available'] = enroll_data.previous_payslip_available

        for edudata in enroll_data.educational_ids:
            temp = {'course_id': edudata.course_id.name,
                    'stream_id': edudata.stream_id.name,
                    'id': edudata.id,
                    'hidden_education_document': edudata.filename,
                    'education_document': edudata.document_attachment_id}
            education.append(temp)

        if enroll_data.work_experience_ids:
            for data in enroll_data.work_experience_ids:
                temp = {'name': data.name,
                        'id': data.id,
                        'hidden_experience_document': data.filename,
                        'experience_document': data.document_attachment_id}
                experience.append(temp)

        for identidata in enroll_data.identification_ids:
            # print(type(identidata.name))
            if identidata.name == '5':
                name = 'Aadhar'
            elif identidata.name == '1':
                name = 'PAN'
            elif identidata.name == '4':
                name = 'Voter'
            elif identidata.name == '3':
                name = 'DL'
            elif identidata.name == '2':
                name = 'Passport'
            temp = {'name': name,
                    'id': identidata.id,
                    'hidden_identification_document': identidata.filename,
                    'identification_document': identidata.document_attachment_id}
            identification.append(temp)
        
        # print(identification)

        documentDict['education'] = education
        documentDict['experience'] = experience
        documentDict['identification'] = identification
        print("educdict >>>>>>>>>>>>>>>>>>>>>>> {documentDict}", documentDict)
        return documentDict

    def saveDocumentOnchange(self, enrollment_data, **kw):
        # print(kw)
        data, first_key = {}, ''
        try:
            if kw and len(kw) > 0:
                update_data = {}
                first_key = next(iter(kw))
                del kw[first_key]
                if first_key == 'upload_identification_document':
                    update_data['identification_ids'] = [[1, int(kw['identification_id']), {'uploaded_doc': kw['uploaded_doc'], 'filename': kw['filename']}]]
                    enrollment_data.sudo().write(update_data)
                elif first_key == 'upload_experience_document':
                    update_data['work_experience_ids'] = [[1, int(kw['experience_id']), {'uploaded_doc': kw['uploaded_doc'], 'filename': kw['filename']}]]
                    enrollment_data.sudo().write(update_data)
                elif first_key == 'upload_educational_document':
                    update_data['educational_ids'] = [[1, int(kw['education_id']), {'uploaded_doc': kw['uploaded_doc'], 'filename': kw['filename']}]]
                    enrollment_data.sudo().write(update_data)
                else:
                    enrollment_data.sudo().write(kw)

                if first_key == 'upload_image':
                    data.update({'hidden_personal_image': enrollment_data.image_name,
                                 'personal_image': enrollment_data.image_id})
                elif first_key == 'upload_medical_certificate':
                    data.update({'hidden_medical_certificate': enrollment_data.certificate_name,
                                 'medical_certificate': enrollment_data.medical_certifcate_attachment_id})
                elif first_key == 'upload_payslip_document1':
                    # print('enrollment_data >>> ', enrollment_data.payslip_filename1, enrollment_data.payslip_attachment1_id)
                    data.update({'hidden_payslip_doc1': enrollment_data.payslip_filename1,
                                 'uploaded_payslip_doc1': enrollment_data.payslip_attachment1_id})

                elif first_key == 'upload_payslip_document2':
                    data.update({'hidden_payslip_doc2': enrollment_data.payslip_filename2,
                                 'uploaded_payslip_doc2': enrollment_data.payslip_attachment2_id})

                elif first_key == 'upload_payslip_document3':
                    data.update({'hidden_payslip_doc3': enrollment_data.payslip_filename3,
                                 'uploaded_payslip_doc3': enrollment_data.payslip_attachment3_id})

                elif first_key == 'upload_identification_document':
                    indentification_id = http.request.env['kwonboard_identity_docs'].sudo().search(
                        [('enrole_id', '=', enrollment_data.id), ('id', '=', int(kw['identification_id']))], limit=1)
                    data.update({'hidden_identification_document': indentification_id.filename,
                                 'identification_document': indentification_id.document_attachment_id})
                elif first_key == 'upload_experience_document':
                    experience_id = http.request.env['kwonboard_work_experience'].sudo().search(
                        [('enrole_id', '=', enrollment_data.id), ('id', '=', int(kw['experience_id']))], limit=1)
                    data.update({'hidden_experience_document': experience_id.filename,
                                 'experience_document': experience_id.document_attachment_id})
                elif first_key == 'upload_educational_document':
                    experience_id = http.request.env['kwonboard_edu_qualification'].sudo().search(
                        [('enrole_id', '=', enrollment_data.id), ('id', '=', int(kw['education_id']))], limit=1)
                    data.update({'hidden_education_document': experience_id.filename,
                                 'education_document': experience_id.document_attachment_id})

        except Exception as e:
            data.update({'success': False,'error':str(e)})
        return data

    # def saveDocumentdetailsInfo(self, enrollment_data, **kw):
    #     # print("enroll data is;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",enrollment_data)


    #     personal_data = {
    #         'image': kw['hiddenimage'],
    #         'medical_certificate': kw['hiddencertificate']

    #     }
    #     # print(personal_data)
    #     enrollment_data.sudo().write(personal_data)

    #     # after saving into db, return data frm db
    #     resdata = self.getDocumentdetailsfromDB(enrollment_data)
    #     # resdata['success_msg'] = 'Personal details saved successfully'
    #     if 'draft' in kw:
    #         resdata['draft'] = kw['draft']
    #     return resdata
    #     # except Exception as e:
    #     #         http.request._cr.rollback()
    #     #         kw['err_msg'] = str(e)
    #     #         return kw
