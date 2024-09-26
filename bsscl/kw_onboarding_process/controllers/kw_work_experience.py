# -*- coding: utf-8 -*-
import base64, re

from odoo import http


class WorkExperience:

    # #read work information data from DB
    def getWorkexperiencedetailsfromDB(self, enroll_data):
        workdict = {'experience_sts': enroll_data.experience_sts}
        experience = []
        for data in enroll_data.work_experience_ids:
            # for data in record:  
            temp = {'country_id': data.country_id.id, 'name': data.name,
                    'organization_type': data.organization_type, 'effective_from': data.effective_from.strftime('%d-%b-%Y') if data.effective_from else "",
                    'designation_name': data.designation_name, 'industry_type': data.industry_type,
                    'effective_to': data.effective_to.strftime('%d-%b-%Y') if data.effective_to else "", 'filename': data.filename, 'expid': data.id}
            experience.append(temp)
        workdict['experience'] = experience
        return workdict

    # #save work information information to database
    def saveWorkinformation(self, enrollment_data, **kw):
        # print(kw)
        workexperiencelist = []
        try:
            # print("inside try block")
            employee_data = {'experience_sts': kw['experience'], 'work_experience_ids': []}

            work_exp_db_data = []
            edited_workexp_data = []

            if enrollment_data.work_experience_ids:
                work_exp_db_data = enrollment_data.work_experience_ids.mapped('id')

            if kw['experience'] == '2':
                # print(kw)
                digit = lambda x: re.search(r'\d+', x).group(0)
                temp_work_seq = []

                for key, value in kw.items():
                    temp_key = str(key)
                    temp_data = dict()
                    if temp_key[0:5] == 'work_':
                        temp_seq = digit(temp_key)

                        if temp_seq not in temp_work_seq and kw['work_country_' + temp_seq] and int(kw['work_country_' + temp_seq]) > 0:
                            temp_work_seq.append(temp_seq)
                            uploaddoc = base64.encodestring(kw['work_file_' + temp_seq].read()) if kw['work_file_' + temp_seq] else ''
                            file_name = kw['work_filename_' + temp_seq]

                            # if kw['work_dufrom_' + temp_seq]:
                            #     effec_frm_string = kw['work_dufrom_' + temp_seq]
                            #     sp_list = effec_frm_string.split("-")
                            #     effec_frm_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'
							#
                            # if kw['work_duto_' + temp_seq]:
                            #     effec_to_string = kw['work_duto_' + temp_seq]
                            #     sp_list = effec_to_string.split("-")
                            #     effec_to_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'

                            # 'effective_from': kw['work_dufrom_' + temp_seq],
                            # 'effective_to': kw['work_duto_' + temp_seq],

                            temp_data = frmtemp = {
                                'country_id': int(kw['work_country_' + temp_seq]),
                                'name': kw['work_orgname_' + temp_seq].strip(),
                                'designation_name': kw['work_desg_' + temp_seq].strip(),
                                'organization_type': kw['work_orgtype_' + temp_seq],
                                'industry_type': kw['work_indtype_' + temp_seq],
                                'effective_from':  kw['work_dufrom_' + temp_seq] if kw['work_dufrom_' + temp_seq] else None,
                                'effective_to':  kw['work_duto_' + temp_seq] if kw['work_duto_' + temp_seq] else  None,
                            }
                            # print("WORK TEMP DATA", temp_data)

                            if uploaddoc != b'':
                                temp_data['uploaded_doc'] = uploaddoc
                                temp_data['filename'] = file_name

                            # #form data save to kw to reload the page with data after error
                            frmtemp['filename'] = file_name
                            workexperiencelist.append(frmtemp)

                            edit_id = kw['work_expid_' + temp_seq] if 'work_expid_' + temp_seq in kw else 0
                            edit_id = int(edit_id) if edit_id != '' else 0

                            if edit_id in work_exp_db_data:
                                employee_data['work_experience_ids'].append([1, edit_id, temp_data])
                                edited_workexp_data.append(edit_id)
                                work_exp_db_data.remove(edit_id)
                            else:
                                employee_data['work_experience_ids'].append([0, 0, temp_data])

            # delete the remaining data
            if work_exp_db_data:
                for del_data in work_exp_db_data:
                    employee_data['work_experience_ids'].append([2, del_data, False])

            # #update the data in db
            enrollment_data.sudo().write(employee_data)

            # #after saving into db, return data frm db
            resdata = self.getWorkexperiencedetailsfromDB(enrollment_data)
            resdata['success_msg'] = 'Work experience details saved successfully'

            if 'draft' in kw:
                resdata['draft'] = kw['draft']
            return resdata

        except Exception as e:
            http.request._cr.rollback()
            kw['err_msg'] = str(e)
            kw['experience_sts'] = kw['experience']
            kw['experience'] = workexperiencelist
            return kw
