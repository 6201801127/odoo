# -*- coding: utf-8 -*-
import base64, re
from datetime import datetime
from odoo import http, models
from odoo.exceptions import ValidationError
from odoo.http import request


class Personaldetails:

    # read personal data from DB
    def getPersonaldetailsfromDB(self, enrollment_data):
        personaldict = dict()
        # print(enrollment_data) .strftime('%d-%m-%Y') 
        if enrollment_data:
            personaldict['txtFullName'] = enrollment_data.name if enrollment_data.name else ""
            # personaldict['ddlMotherTounge'] = enrollment_data.mother_tounge_ids.id if enrollment_data.mother_tounge_ids else ""
            personaldict['txtDateOfBirth'] = enrollment_data.birthday.strftime('%d-%b-%Y') if enrollment_data.birthday else ""
            personaldict['ddlBloodGroup'] = enrollment_data.blood_group if enrollment_data.blood_group else ""
            personaldict['ddlReligion'] = enrollment_data.emp_religion.id if enrollment_data.emp_religion else ""
            # personaldict['ddlMaritalStatus'] = enrollment_data.marital.id if enrollment_data.marital else ""
            # personaldict['txtWedAniversary'] = enrollment_data.wedding_anniversary.strftime('%d-%b-%Y') if enrollment_data.wedding_anniversary else ""
            personaldict['txtMobNo1'] = enrollment_data.mobile if enrollment_data.mobile else ""
            personaldict['txtMobNo2'] = enrollment_data.whatsapp_no if enrollment_data.whatsapp_no else ""
            personaldict['txtEmail'] = enrollment_data.email if enrollment_data.email else ""
            personaldict['presentaddress1'] = str(enrollment_data.present_addr_street.strip()) if enrollment_data.present_addr_street else ""
            personaldict['presentaddress2'] = str(enrollment_data.present_addr_street2.strip()) if enrollment_data.present_addr_street2 else ""
            personaldict['ddlPresentContry'] = enrollment_data.present_addr_country_id.id if enrollment_data.present_addr_country_id else ""
            personaldict['ddlPresState'] = enrollment_data.present_addr_state_id.id if enrollment_data.present_addr_state_id else ""
            personaldict['txtPresCity'] = enrollment_data.present_addr_city if enrollment_data.present_addr_city else ""
            personaldict['txtPresPinCode'] = enrollment_data.present_addr_zip if enrollment_data.present_addr_zip else ""
            personaldict['txtPermAddressLine1'] = str(enrollment_data.permanent_addr_street.strip()) if enrollment_data.permanent_addr_street else ""
            personaldict['txtPermAddressLine2'] = str(enrollment_data.permanent_addr_street2.strip()) if enrollment_data.permanent_addr_street2 else ""
            personaldict['ddlPermCountry'] = enrollment_data.permanent_addr_country_id.id if enrollment_data.permanent_addr_country_id else ""
            personaldict['ddlPermstate'] = enrollment_data.permanent_addr_state_id.id if enrollment_data.permanent_addr_state_id else ""
            personaldict['txtPermCity'] = enrollment_data.permanent_addr_city if enrollment_data.permanent_addr_city else ""
            personaldict['txtPermPinCode'] = enrollment_data.permanent_addr_zip if enrollment_data.permanent_addr_zip else ""
            personaldict['same_address'] = enrollment_data.same_address if enrollment_data.same_address else False
            # personaldict['hiddenimage'] = enrollment_data.image_name if enrollment_data.image_name else ""
            # personaldict['hiddencertificate'] = enrollment_data.certificate_name if enrollment_data.certificate_name else ""
            # personaldict['marital_code'] = enrollment_data.marital_code if enrollment_data.marital_code else ""
            # personaldict['txtEmgrPer'] = enrollment_data.emgr_contact if enrollment_data.emgr_contact else ""
            # personaldict['txtEmgrPhn'] = enrollment_data.emgr_phone if enrollment_data.emgr_phone else ""
            # personaldict['ddlEmgrRel'] = enrollment_data.emgr_rel if enrollment_data.emgr_rel else ""
            # personaldict['willing_travel'] = enrollment_data.will_travel #'0' if enrollment_data.will_travel=='0' else '1'
            # personaldict['travel_abroad'] = enrollment_data.travel_abroad #'0' if enrollment_data.travel_abroad=='0' else '1'
            # personaldict['travel_domestic'] = enrollment_data.travel_domestic #'0' if enrollment_data.travel_domestic=='0' else '1'
            # personaldict['linkedin_url'] = enrollment_data.linkedin_url
            personaldict['emp_uan'] = enrollment_data.uan_id if enrollment_data.uan_id else ""
            personaldict['emp_esi'] = enrollment_data.esi_id if enrollment_data.esi_id else ""
            personaldict['txtBankName'] = enrollment_data.personal_bank_name if enrollment_data.personal_bank_name else ""
            personaldict['txtAccountNo'] = enrollment_data.personal_bank_account if enrollment_data.personal_bank_account else ""
            personaldict['txtIFSCcode'] = enrollment_data.personal_bank_ifsc if enrollment_data.personal_bank_ifsc else ""
            personaldict['txtFatherName'] = enrollment_data.applicant_father_name if enrollment_data.applicant_father_name else ""
            personaldict['txtFatherDob'] = enrollment_data.applicant_father_dob.strftime('%d-%b-%Y') if enrollment_data.applicant_father_dob else ""
            personaldict['txtMotherName'] = enrollment_data.applicant_mother_name if enrollment_data.applicant_mother_name else ""
            personaldict['txtMotherDob'] = enrollment_data.applicant_mother_dob.strftime('%d-%b-%Y') if enrollment_data.applicant_mother_dob else ""

        #     if enrollment_data.gender == 'male':
        #         personaldict['rbtGender'] = "male"
        #     elif enrollment_data.gender == 'female':
        #         personaldict['rbtGender'] = "female"
        #     elif enrollment_data.gender == 'others':
        #         personaldict['rbtGender'] = "others"
        #     else:
        #         personaldict['rbtGender'] = "0"
            ind_record = request.env['res.country'].search([('code','=','IN')])
            if ind_record:
                personaldict['ddlNationality'] = ind_record.id
            else:
                personaldict['ddlNationality'] = ""
		#
        #     langrecord = enrollment_data.known_language_ids
		#
        #     if langrecord:
        #         languages = []
        #         for record in langrecord:
        #             for data in record:
        #                 temp = {'id': data.id,
        #                         'langdrpdrpLanguage': data.language_id.id,
        #                         'langrdnReading': data.reading_status,
        #                         'langrdnWriting': data.writing_status,
        #                         'langrdnSpeaking': data.speaking_status,
        #                         'langrdnUnderstanding': data.understanding_status}
        #                 languages.append(temp)
        #                 # print(languages)
        #         personaldict['languages'] = languages
        #     else:
        #         personaldict['languages'] = False
        else:
            personaldict['ddlNationality'] = str(104)
        return personaldict

    # save personal information to database
    def savePersonalInfo(self, enrollment_data, **kw):
        # print("kw ++++++++++++++++++++++++++ ", kw)
        try:
            # image = base64.encodestring(kw['fupPhoto'].read()) if kw['fupPhoto'] else ''
            # medic_certificate = base64.encodestring(kw['medicPhoto'].read()) if kw['medicPhoto'] else ''

            birthday_date_string = kw['txtDateOfBirth']
            slist = birthday_date_string.split("-")
            birthday_new_string = ''

            if kw['txtFatherName']:
                # wedding_annv_string = kw['txtWedAniversary']
                # sp_list = wedding_annv_string.split("-")
                wedding_annv_new_string = ''

            personal_data = {
                'birthday': birthday_new_string,
                'applicant_father_name': kw['txtFatherName'],
                'applicant_father_dob' :  kw['txtFatherDob'] if kw['txtFatherDob'] else None,
                'applicant_mother_name': kw['txtMotherName'],
                'applicant_mother_dob': kw['txtMotherDob'] if kw['txtMotherDob'] else None,
                # 'gender': kw['rbtGender'],
                # 'mother_tounge_ids':kw['ddlMotherTounge'],
                'blood_group': kw['ddlBloodGroup'],
                'emp_religion': kw['ddlReligion'],
                # 'marital': kw['ddlMaritalStatus'],
                # 'marital_code': kw['marital_code'],
                # 'wedding_anniversary': wedding_annv_new_string if kw['txtWedAniversary'] else None, # kw['txtWedAniversary'] if kw['txtWedAniversary'] else None,
                # 'country_id': kw['ddlNationality'],
                # 'image_name': kw['hiddenimage'],
                'present_addr_street': kw['txtPresAddressLine1'].strip(),
                'present_addr_street2': kw['txtPresAddressLine2'].strip(),
                'present_addr_country_id': kw['ddlPresentContry'],
                'present_addr_state_id': kw['ddlPresState'],
                'present_addr_city': kw['txtPresCity'].strip(),
                'present_addr_zip': kw['txtPresPinCode'].strip(),
                'same_address': True if 'checksame' in kw else False,
                'permanent_addr_country_id': kw['ddlPermCountry'],
                'permanent_addr_street': kw['txtPermAddressLine1'].strip(),
                'permanent_addr_street2': kw['txtPermAddressLine2'].strip(),
                'permanent_addr_state_id': kw['ddlPermstate'],
                'permanent_addr_city': kw['txtPermCity'].strip(),
                'permanent_addr_zip': kw['txtPermPinCode'].strip(),
                'emgr_contact': kw['txtEmgrPer'].strip(),
                'emgr_phone': kw['txtEmgrPhn'].strip(),
                'whatsapp_no': kw['txtMobNo2'].strip(),
                # 'emgr_rel': kw['ddlEmgrRel'],
                # 'will_travel': '0' if kw['willing_travel']=='0' else '1',
                # 'travel_abroad': '0' if kw['travel_abroad']=='0' else '1',
                # 'travel_domestic': '0' if kw['travel_domestic']=='0' else '1',
                # 'linkedin_url': kw['linkedin_url'],
                'uan_id' : kw['emp_uan'],
                'esi_id': kw['emp_esi'],
                'personal_bank_name':kw['txtBankName'],
                'personal_bank_account':kw['txtAccountNo'],
                'personal_bank_ifsc':kw['txtIFSCcode'],
            }
            # kw['presentaddress1'] = kw['txtPresAddressLine1'].strip()
            # kw['presentaddress2'] = kw['txtPresAddressLine2'].strip()
			#
            # if image != b'':
            #     personal_data['image'] = image
            # if medic_certificate != b'':
            #     personal_data['medical_certificate'] = medic_certificate
            #     personal_data['certificate_name'] = kw['hiddencertificate']
            # personal_data['known_language_ids'] = []
			#
            # # all lang record
            # lang_record = enrollment_data.known_language_ids  # http.request.env['kwonboard_language_known'].sudo().search([('enrole_id', '=', enrolment_id)])
            # # if lang_record:
            # kw['languages'] = []
            # temp_lang_id = []
            # sel_lang_ids = []
            # temp_languages = []
            # digit = lambda x: re.search(r'\d+', x).group(0)
			#
            # for key, value in kw.items():
            #     temp_key = str(key)
            #     # print(">>>>>>>>>>>>>>>>>>> ", key, temp_key, value)
            #     if temp_key[0:5] == 'lang_':
            #         temp_seq = digit(key)
            #         if temp_seq not in temp_lang_id and kw['lang_language_' + temp_seq] and int(kw['lang_language_' + temp_seq]) > 0:
            #             temp_lang_id.append(temp_seq)
			#
            #             language = int(kw['lang_language_' + temp_seq]) if int(kw['lang_language_' + temp_seq]) > 0 else 0
            #             temp_languages.append(language)
			#
            #             edit_id = int(kw['lang_languageid_' + temp_seq]) if int(kw['lang_languageid_' + temp_seq]) > 0 else 0
            #             reading_status = kw['lang_reading_' + temp_seq] if kw['lang_reading_' + temp_seq] else None
            #             writing_status = kw['lang_writing_' + temp_seq] if kw['lang_writing_' + temp_seq] else None
            #             speaking_status = kw['lang_speaking_' + temp_seq] if kw['lang_speaking_' + temp_seq] else None
            #             understanding_status = kw['lang_understand_' + temp_seq] if kw['lang_understand_' + temp_seq] else None
			#
            #             lang_data = {
            #                 'language_id': language,
            #                 'reading_status': reading_status,
            #                 'writing_status': writing_status,
            #                 'speaking_status': speaking_status,
            #                 'understanding_status': understanding_status
            #             }
			#
            #             # if new record
            #             if edit_id == 0:
            #                 personal_data['known_language_ids'].append([0, 0, lang_data])
			#
            #             # edit the record present in the list
            #             elif lang_record.filtered(lambda r: r.id == edit_id):
            #                 personal_data['known_language_ids'].append([1, edit_id, lang_data])
            #                 sel_lang_ids.append(edit_id)
			#
            #             temp = {'id': edit_id,
            #                     'langdrpdrpLanguage': language,
            #                     'langrdnReading': reading_status,
            #                     'langrdnWriting': writing_status,
            #                     'langrdnSpeaking': speaking_status,
            #                     'langrdnUnderstanding': understanding_status}
            #             kw['languages'].append(temp)
			#
            # result = self.getRepeatedlist(temp_languages)
            # if len(result) > 0:
            #     raise ValidationError("Please remove duplicate languages from list ")
			#
            # for lang_rec in lang_record:
            #     if lang_rec.id not in sel_lang_ids:
            #         personal_data['known_language_ids'].append([2, lang_rec.id, False])
            #
            # # update the onboarding record
            enrollment_data.sudo().write(personal_data)

            # after saving into db, return data frm db
            resdata = self.getPersonaldetailsfromDB(enrollment_data)
            resdata['success_msg'] = 'Personal details saved successfully'
            if 'draft' in kw:
                resdata['draft'] = kw['draft']
            # print("resdata ======================= ", resdata)
            return resdata
        except Exception as e:
            http.request._cr.rollback()
            kw['err_msg'] = str(e)
            return kw

    def getRepeatedlist(self, x):
        _size = len(x)
        repeated = []
        for i in range(_size):
            k = i + 1
            for j in range(k, _size):
                if x[i] == x[j] and x[i] not in repeated:
                    repeated.append(x[i])
        return repeated
