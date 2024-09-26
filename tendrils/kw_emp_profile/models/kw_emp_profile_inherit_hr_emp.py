from odoo import models, fields, api


class hr_employee_in(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def write(self, vals):
        for emp_record in self:
            list_1 = []
            list_2 = []
            list_3 = []
            list_4 = []
            list_5 = []
            list_6 = []
            list_7 = []
            list_8 = []
            list_9 = []

            for rec in emp_record.family_details_ids:
                list_1.append(rec.id)
            for language in emp_record.known_language_ids:
                list_3.append(language.id)
            for work in emp_record.work_experience_ids:
                list_4.append(work.id)
            for identification in emp_record.identification_ids:
                list_5.append(identification.id)
            for education in emp_record.educational_details_ids:
                list_6.append(education.id)
            for skill in emp_record.technical_skill_ids:
                list_7.append(skill.id)
            for membership in emp_record.membership_assc_ids:
                list_8.append(membership.id)
            for cv_id in emp_record.cv_info_details_ids:
                list_9.append(cv_id.id)

            emp_prpf_rec = self.env['kw_emp_profile'].sudo().search([('emp_id', '=', emp_record.id)])
            val = {}
            if 'cv_info_details_ids' in vals:
                for record in vals['cv_info_details_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_cv_info'].search(
                            [('emp_cv_info_id', '=', record[1])]).unlink()
            if 'family_details_ids' in vals:
                for record in vals['family_details_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_family_info'].search(
                            [('family_id', '=', record[1])]).unlink()

            if 'known_language_ids' in vals:
                for record in vals['known_language_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_language_known'].search(
                            [('emp_language_id', '=', record[1])]).unlink()

            if 'membership_assc_ids' in vals:
                for record in vals['membership_assc_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_membership_assc'].search(
                            [('emp_membership_id', '=', record[1])]).unlink()

            if 'educational_details_ids' in vals:
                for record in vals['educational_details_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_qualification'].search(
                            [('emp_educational_id', '=', record[1])]).unlink()
            if 'identification_ids' in vals:
                for record in vals['identification_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_identity_docs'].search(
                            [('emp_document_id', '=', record[1])]).unlink()
            if 'technical_skill_ids' in vals:
                for record in vals['technical_skill_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_technical_skills'].search(
                            [('emp_technical_id', '=', record[1])]).unlink()
            if 'work_experience_ids' in vals:
                for record in vals['work_experience_ids']:
                    if record[0] == 2:
                        profile_data = self.env['kw_emp_profile_work_experience'].search(
                            [('emp_work_id', '=', record[1])]).unlink()

            emp_rec = super(hr_employee_in, self).write(vals)
            if 'cv_info_details_ids' in vals:
                for rec in emp_record.cv_info_details_ids:
                    list_2.append(rec.id)

                for res in list_9:
                    if res in list_2:
                        list_2.remove(res)

                for record in vals['cv_info_details_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_cv_info'].sudo().search(
                            [('emp_cv_info_id', '=', record[1])])
                        if 'project_name' in record[2]:
                            values.update({'project_name': record[2]['project_name']})
                        if 'project_of' in record[2]:
                            values.update({'project_of': record[2]['project_of']})
                        if 'location' in record[2]:
                            values.update({'location': record[2]['location']})
                        # if 'project_id' in record[2]:
                        #     values.update({'project_id':record[2]['project_id']})
                        if 'start_month_year' in record[2]:
                            values.update({'start_month_year': record[2]['start_month_year']})
                        if 'project_feature' in record[2]:
                            values.update({'project_feature': record[2]['project_feature']})
                        if 'role' in record[2]:
                            values.update({'role': record[2]['role']})
                        if 'responsibility_activity' in record[2]:
                            values.update({'responsibility_activity': record[2]['responsibility_activity']})
                        if 'client_name' in record[2]:
                            values.update({'client_name': record[2]['client_name']})
                        if 'activity' in record[2]:
                            values.update({'activity': record[2]['activity']})
                        if 'other_activity' in record[2]:
                            values.update({'other_activity': record[2]['other_activity']})
                        if 'organization_id' in record[2]:
                            values.update({'organization_id': record[2]['organization_id']})
                        if 'emp_project_id' in record[2]:
                            values.update({'emp_project_id': record[2]['emp_project_id']})
                        profile_data.update(values)
                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_cv_info'].sudo()  # .search([])
                        values = {
                            'activity': record[2]['activity'] if record[2]['activity'] else False,
                            'other_activity': record[2]['other_activity'] if record[2]['other_activity'] else False,
                            'project_of': record[2]['project_of'] if record[2]['project_of'] else False,
                            'project_name': record[2]['project_name'] if record[2]['project_name'] else False,
                            # 'project_id':record[2]['project_id'] if record[2]['project_id'] else False,
                            'location': record[2]['location'] if record[2]['location'] else False,
                            'start_month_year': record[2]['start_month_year'] if record[2]['start_month_year'] else False,
                            'end_month_year': record[2]['end_month_year'] if record[2]['end_month_year'] else False,
                            'project_feature': record[2]['project_feature'] if record[2]['project_feature'] else False,
                            'role': record[2]['role'] if record[2]['role'] else False,
                            'responsibility_activity': record[2]['responsibility_activity'] if record[2]['responsibility_activity'] else False,
                            'client_name': record[2]['client_name'] if record[2]['client_name'] else False,
                            'emp_project_id': record[2]['emp_project_id'] if record[2]['emp_project_id'] else False,
                            'organization_id': record[2]['organization_id'] if record[2]['organization_id'] else False,
                            'emp_cv_info_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'membership_assc_ids' in vals:
                for rec in emp_record.membership_assc_ids:
                    list_2.append(rec.id)

                for res in list_8:
                    if res in list_2:
                        list_2.remove(res)

                for record in vals['membership_assc_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_membership_assc'].sudo().search(
                            [('emp_membership_id', '=', record[1])])
                        if 'name' in record[2]:
                            values.update({'name': record[2]['name']})
                        if 'date_of_issue' in record[2]:
                            values.update({'date_of_issue': record[2]['date_of_issue']})
                        if 'date_of_expiry' in record[2]:
                            values.update({'date_of_expiry': record[2]['date_of_expiry']})
                        if 'renewal_sts' in record[2]:
                            values.update({'renewal_sts': record[2]['renewal_sts']})
                        if 'uploaded_doc' in record[2]:
                            values.update({'uploaded_doc': record[2]['uploaded_doc']})
                        profile_data.update(values)
                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_membership_assc'].sudo()  # .search([])
                        values = {
                            'uploaded_doc': record[2]['uploaded_doc'] if record[2]['uploaded_doc'] else False,
                            'renewal_sts': record[2]['renewal_sts'] if record[2]['renewal_sts'] else False,
                            'date_of_expiry': record[2]['date_of_expiry'] if record[2]['date_of_expiry'] else False,
                            'name': record[2]['name'] if record[2]['name'] else False,
                            'date_of_issue': record[2]['date_of_issue'] if record[2]['date_of_issue'] else False,
                            'emp_membership_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'technical_skill_ids' in vals:
                for rec in emp_record.technical_skill_ids:
                    list_2.append(rec.id)

                for res in list_7:
                    if res in list_2:
                        list_2.remove(res)

                for record in vals['technical_skill_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_technical_skills'].sudo().search(
                            [('emp_technical_id', '=', record[1])])
                        if 'category_id' in record[2]:
                            values.update({'category_id': record[2]['category_id']})
                        if 'skill_id' in record[2]:
                            values.update({'skill_id': record[2]['skill_id']})
                        if 'proficiency' in record[2]:
                            values.update({'proficiency': record[2]['proficiency']})

                        profile_data.update(values)

                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_technical_skills'].sudo()  # .search([])
                        values = {
                            'category_id': record[2]['category_id'] if record[2]['category_id'] else False,
                            'skill_id': record[2]['skill_id'] if record[2]['skill_id'] else False,
                            'proficiency': record[2]['proficiency'] if record[2]['proficiency'] else False,
                            'emp_technical_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'educational_details_ids' in vals:
                for rec in emp_record.educational_details_ids:
                    list_2.append(rec.id)

                for res in list_6:
                    if res in list_2:
                        list_2.remove(res)

                for record in vals['educational_details_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_qualification'].sudo().search(
                            [('emp_educational_id', '=', record[1])])
                        if 'course_type' in record[2]:
                            values.update({'course_type': record[2]['course_type']})
                        if 'course_id' in record[2]:
                            values.update({'course_id': record[2]['course_id']})
                        if 'uploaded_doc' in record[2]:
                            values.update({'uploaded_doc': record[2]['uploaded_doc']})
                        if 'stream_id' in record[2]:
                            values.update({'stream_id': record[2]['stream_id']})
                        if 'university_name' in record[2]:
                            values.update({'university_name': record[2]['university_name']})
                        if 'passing_year' in record[2]:
                            values.update({'passing_year': record[2]['passing_year']})
                        if 'division' in record[2]:
                            values.update({'division': record[2]['division']})
                        if 'marks_obtained' in record[2]:
                            values.update({'marks_obtained': record[2]['marks_obtained']})
                        if 'passing_details' in record[2]:
                            values.update({'passing_details': record[2]['passing_details']})

                        profile_data.update(values)
                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_qualification'].sudo()  # .search([])
                        if 'passing_details' in record[2]:
                            values = {
                                'marks_obtained': record[2]['marks_obtained'] if record[2]['marks_obtained'] else False,
                                'division': record[2]['division'] if record[2]['division'] else False,
                                'passing_year': record[2]['passing_year'] if record[2]['passing_year'] else False,
                                'university_name': record[2]['university_name'] if record[2]['university_name'] else False,
                                'stream_id': record[2]['stream_id'] if record[2]['stream_id'] else False,
                                'course_id': record[2]['course_id'] if record[2]['course_id'] else False,
                                'course_type': record[2]['course_type'] if record[2]['course_type'] else False,
                                'uploaded_doc': record[2]['uploaded_doc'] if record[2]['uploaded_doc'] else False,
                                'passing_details': record[2]['passing_details'],
                                'emp_educational_id': list_2[0],
                                'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                            }
                        else:
                            values = {
                                'marks_obtained': record[2]['marks_obtained'] if record[2]['marks_obtained'] else False,
                                'division': record[2]['division'] if record[2]['division'] else False,
                                'passing_year': record[2]['passing_year'] if record[2]['passing_year'] else False,
                                'university_name': record[2]['university_name'] if record[2]['university_name'] else False,
                                'stream_id': record[2]['stream_id'] if record[2]['stream_id'] else False,
                                'course_id': record[2]['course_id'] if record[2]['course_id'] else False,
                                'course_type': record[2]['course_type'] if record[2]['course_type'] else False,
                                'uploaded_doc': record[2]['uploaded_doc'] if record[2]['uploaded_doc'] else False,
                                'emp_educational_id': list_2[0],
                                'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                            }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'identification_ids' in vals:
                for rec in emp_record.identification_ids:
                    list_2.append(rec.id)

                for r in list_5:
                    if r in list_2:
                        list_2.remove(r)

                for record in vals['identification_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_identity_docs'].sudo().search(
                            [('emp_document_id', '=', record[1])])
                        if 'name' in record[2]:
                            values.update({'name': record[2]['name']})
                        if 'doc_number' in record[2]:
                            values.update({'doc_number': record[2]['doc_number']})
                        if 'uploaded_doc' in record[2]:
                            values.update({'uploaded_doc': record[2]['uploaded_doc']})
                        if 'date_of_issue' in record[2]:
                            values.update({'date_of_issue': record[2]['date_of_issue']})
                        if 'date_of_expiry' in record[2]:
                            values.update({'date_of_expiry': record[2]['date_of_expiry']})
                        if 'renewal_sts' in record[2]:
                            values.update({'renewal_sts': record[2]['renewal_sts']})

                        profile_data.update(values)
                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_identity_docs'].sudo()  # .search([])
                        values = {
                            'name': record[2]['name'] if record[2]['name'] else False,
                            'doc_number': record[2]['doc_number'] if record[2]['doc_number'] else False,
                            'date_of_issue': record[2]['date_of_issue'] if record[2]['date_of_issue'] else False,
                            'date_of_expiry': record[2]['date_of_expiry'] if record[2]['date_of_expiry'] else False,
                            'renewal_sts': record[2]['renewal_sts'] if record[2]['renewal_sts'] else False,
                            'uploaded_doc': record[2]['uploaded_doc'] if record[2]['uploaded_doc'] else False,
                            'emp_document_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'work_experience_ids' in vals:
                for rec in emp_record.work_experience_ids:
                    list_2.append(rec.id)

                for r in list_4:
                    if r in list_2:
                        list_2.remove(r)
                for record in vals['work_experience_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('emp_work_id', '=', record[1])])
                        if 'country_id' in record[2]:
                            values.update({'country_id': record[2]['country_id']})
                        if 'name' in record[2]:
                            values.update({'name': record[2]['name']})
                        if 'designation_name' in record[2]:
                            values.update({'designation_name': record[2]['designation_name']})
                        if 'organization_type' in record[2]:
                            values.update({'organization_type': record[2]['organization_type']})
                        if 'industry_type' in record[2]:
                            values.update({'industry_type': record[2]['industry_type']})
                        if 'effective_from' in record[2]:
                            values.update({'effective_from': record[2]['effective_from']})
                        if 'effective_to' in record[2]:
                            values.update({'effective_to': record[2]['effective_to']})
                        if 'uploaded_doc' in record[2]:
                            values.update({'uploaded_doc': record[2]['uploaded_doc']})

                        profile_data.update(values)

                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_work_experience'].sudo()  # .search([])
                        values = {
                            'country_id': record[2]['country_id'] if record[2]['country_id'] else False,
                            'name': record[2]['name'] if record[2]['name'] else False,
                            'designation_name': record[2]['designation_name'] if record[2]['designation_name'] else False,
                            'organization_type': record[2]['organization_type'] if record[2]['organization_type'] else False,
                            'industry_type': record[2]['industry_type'] if record[2]['industry_type'] else False,
                            'effective_from': record[2]['effective_from'] if record[2]['effective_from'] else False,
                            'effective_to': record[2]['effective_to'] if record[2]['effective_to'] else False,
                            'uploaded_doc': record[2]['uploaded_doc'] if record[2]['uploaded_doc'] else False,
                            'emp_work_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'known_language_ids' in vals:
                for rec in emp_record.known_language_ids:
                    list_2.append(rec.id)

                for r in list_3:
                    if r in list_2:
                        list_2.remove(r)

                for record in vals['known_language_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_language_known'].sudo().search(
                            [('emp_language_id', '=', record[1])])
                        if 'language_id' in record[2]:
                            values.update({'language_id': record[2]['language_id']})
                        if 'reading_status' in record[2]:
                            values.update({'reading_status': record[2]['reading_status']})
                        if 'writing_status' in record[2]:
                            values.update({'writing_status': record[2]['writing_status']})
                        if 'speaking_status' in record[2]:
                            values.update({'speaking_status': record[2]['speaking_status']})
                        if 'understanding_status' in record[2]:
                            values.update({'understanding_status': record[2]['understanding_status']})
                            # linkedin_url_boolean
                        profile_data.update(values)

                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_language_known'].sudo()  # .search([])
                        values = {
                            'language_id': record[2]['language_id'] if record[2]['language_id'] else False,
                            'reading_status': record[2]['reading_status'] if record[2]['reading_status'] else False,
                            'writing_status': record[2]['writing_status'] if record[2]['writing_status'] else False,
                            'speaking_status': record[2]['speaking_status'] if record[2]['speaking_status'] else False,
                            'understanding_status': record[2]['understanding_status'] if record[2]['understanding_status'] else False,
                            'emp_language_id': list_2[0],
                            'emp_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'family_details_ids' in vals:
                for rec in emp_record.family_details_ids:
                    list_2.append(rec.id)

                for r in list_1:
                    if r in list_2:
                        list_2.remove(r)

                for record in vals['family_details_ids']:
                    if record[0] == 1:
                        values = {}

                        profile_data = self.env['kw_emp_profile_family_info'].sudo().search(
                            [('family_id', '=', record[1])])
                        if 'relationship_id' in record[2]:
                            values.update({'relationship_id': record[2]['relationship_id']})
                        if 'name' in record[2]:
                            values.update({'name': record[2]['name']})
                        if 'gender' in record[2]:
                            values.update({'gender': record[2]['gender']})
                        if 'date_of_birth' in record[2]:
                            values.update({'date_of_birth': record[2]['date_of_birth']})
                        if 'dependent' in record[2]:
                            values.update({'dependent': record[2]['dependent']})

                        profile_data.update(values)

                    if record[0] == 0:
                        profile_data = self.env['kw_emp_profile_family_info'].sudo()  # .search([])
                        values = {
                            'relationship_id': record[2]['relationship_id'] if record[2]['relationship_id'] else False,
                            'name': record[2]['name'] if record[2]['name'] else False,
                            'gender': record[2]['gender'] if record[2]['gender'] else False,
                            'date_of_birth': record[2]['date_of_birth'] if record[2]['date_of_birth'] else False,
                            'dependent': record[2]['dependent'] if record[2]['dependent'] else False,
                            'family_id': list_2[0],
                            'emp_family_id': emp_prpf_rec.id if emp_prpf_rec.id else False,
                        }
                        profile_data.create(values)
                        list_2.pop(0)

            if 'name' in vals:
                val['name'] = vals['name']
            if 'emp_code' in vals:
                val['employee_code'] = vals['emp_code']
            if 'work_email' in vals:
                val['work_email_id'] = vals['work_email']
            if 'work_phone' in vals:
                val['work_phone'] = vals['work_phone']
            if 'user_id' in vals:
                val['user_id'] = vals['user_id']
            if 'date_of_joining' in vals:
                val['date_of_joining'] = vals['date_of_joining']
            if 'gender' in vals:
                val['gender'] = vals['gender']
            if 'permanent_addr_street' in vals:
                val['permanent_addr_street'] = vals['permanent_addr_street']
            if 'blood_group' in vals:
                val['blood_group'] = vals['blood_group']
            if 'emp_religion' in vals:
                val['emp_religion'] = vals['emp_religion']
            if 'id_card_no' in vals:
                val['id_card_no'] = vals['id_card_no']
            if 'country_id' in vals:
                val['country_id'] = vals['country_id']
            if 'outlook_pwd' in vals:
                val['outlook_pwd'] = vals['outlook_pwd']
            if 'emergency_contact' in vals:
                val['emergency_contact_name'] = vals['emergency_contact']
            if 'present_addr_street' in vals:
                val['present_addr_street'] = vals['present_addr_street']
            if 'present_addr_city' in vals:
                val['present_addr_city'] = vals['present_addr_city']
            if 'present_addr_state_id' in vals:
                val['present_addr_state_id'] = vals['present_addr_state_id']
            if 'present_addr_zip' in vals:
                val['present_addr_zip'] = vals['present_addr_zip']
            if 'whatsapp_no' in vals:
                val['whatsapp_no'] = vals['whatsapp_no']
            if 'marital_sts' in vals:
                val['marital'] = vals['marital_sts']
            if 'permanent_addr_street' in vals:
                val['permanent_addr_street'] = vals['permanent_addr_street']
            if 'personal_email' in vals:
                val['personal_email'] = vals['personal_email']
            if 'permanent_addr_zip' in vals:
                val['permanent_addr_zip'] = vals['permanent_addr_zip']
            if 'permanent_addr_country_id' in vals:
                val['permanent_addr_country_id'] = vals['permanent_addr_country_id']
            if 'permanent_addr_state_id' in vals:
                val['permanent_addr_state_id'] = vals['permanent_addr_state_id']
            if 'permanent_addr_city' in vals:
                val['permanent_addr_city'] = vals['permanent_addr_city']
            if 'emergency_phone' in vals:
                val['emergency_mobile_no'] = vals['emergency_phone']
            if 'same_address' in vals:
                val['same_address'] = vals['same_address']
            if 'image' in vals:
                val['image'] = vals['image']
            if 'worked_country_ids' in vals:
                val['worked_country_ids'] = vals['worked_country_ids']
            if 'birthday' in vals:
                val['birthday'] = vals['birthday']
            if 'mobile_phone' in vals:
                val['mobile_phone'] = vals['mobile_phone']
            if 'wedding_anniversary' in vals:
                val['wedding_anniversary'] = vals['wedding_anniversary']
            if 'permanent_addr_street2' in vals:
                val['permanent_addr_street2'] = vals['permanent_addr_street2']
            if 'present_addr_street2' in vals:
                val['present_addr_street2'] = vals['present_addr_street2']
            if 'marital_code' in vals:
                val['marital_code'] = vals['marital_code']
            if 'epbx_no' in vals:
                val['extn_no'] = vals['epbx_no']
            if 'linkedin_url' in vals:
                val['linkedin_url'] = vals['linkedin_url']
            if 'job_title' in vals:
                val['job_profile'] = vals['job_title']

            res = emp_prpf_rec.write(val)
            return emp_rec

    @api.model
    def get_my_job_role(self, *args, **kwargs):
        # print("args >>> ", kwargs, kwargs.get('uid'))
        emp_data = self.search([('user_id', '=', kwargs.get('uid'))], limit=1)
        if emp_data.exists():
            children = self.search([('parent_id', '=', emp_data.id)])
            emp_role = self.env['hr.job.role'].sudo().search([('designations', '=', emp_data.job_id.id)], limit=1)
            autonomy = self.env['hr_job_autonomy'].sudo().search([('designations', '=', emp_data.job_id.id)], limit=1)
            # print("children_ids >>>>>>> ", children, children.mapped('display_name'))
            return {
                'name': emp_data.display_name,
                'designation': emp_data.job_id.name,
                'ra': emp_data.parent_id.display_name or 'NA',
                'team': '</br>'.join(children.mapped('display_name')) if children.exists() else 'NA',
                'jd': emp_role.description if emp_role.exists() else 'Not Found',
                'autonomy': autonomy.description if autonomy.exists() else 'Not Found'
            }
        return {'name': 'NA', 'designation': 'NA', 'ra': 'NA', 'team': 'NA', 'jd': 'NA', 'autonomy': 'NA'}
