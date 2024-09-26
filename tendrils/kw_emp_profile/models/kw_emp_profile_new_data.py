from types import FunctionType
from inspect import getmembers
from odoo import models, fields, api


class EmployeeApproval(models.Model):
    _name = 'kw_emp_profile_new_data'
    _description = "Profile Changes Request"

    emp_prfl_id = fields.Many2one('kw_emp_profile', string="Employee Profile Id")
    emp_family_id = fields.One2many(related='emp_prfl_id.emp_id.family_details_ids', string='Family Details')
    profile_family_details = fields.One2many(related='emp_prfl_id.family_details_ids', string='Family Details')
    # emp_id = fields.Many2one('kw_emp_profile',string = "Employee Id")
    emp_technical_ids = fields.One2many(related='emp_prfl_id.emp_id.technical_skill_ids', string='Technical Skills')
    profile_technical_ids = fields.One2many(related='emp_prfl_id.technical_skill_ids', string='Technical Skills')
    emp_work_experience_ids = fields.One2many(related='emp_prfl_id.emp_id.work_experience_ids', string='Work Experience Details')
    profile_work_experience_ids = fields.One2many(related='emp_prfl_id.work_experience_ids', string='Work Experience Details')
    emp_educational_ids = fields.One2many(related='emp_prfl_id.emp_id.educational_details_ids', string='Educational Details')
    profile_educational_ids = fields.One2many(related='emp_prfl_id.educational_details_ids', string='Educational Details')
    emp_identification_ids = fields.One2many(related='emp_prfl_id.emp_id.identification_ids', string='Identification Details')
    profile_identification_ids = fields.One2many(related='emp_prfl_id.identification_ids', string='Identification Details')
    emp_membership_ids = fields.One2many(related='emp_prfl_id.emp_id.membership_assc_ids', string='Membership Association Details')
    profile_membership_ids = fields.One2many(related='emp_prfl_id.membership_assc_ids', string='Membership Association Details')
    emp_language_ids = fields.One2many(related='emp_prfl_id.emp_id.known_language_ids', string='Language Known')
    profile_language_ids = fields.One2many(related='emp_prfl_id.known_language_ids', string='Language Known')
    emp_cv_info_ids = fields.One2many(related='emp_prfl_id.emp_id.cv_info_details_ids', string='CV Info')
    profile_cv_info_ids = fields.One2many(related='emp_prfl_id.cv_info_details_ids', string='CV Info')

    hr_emp_id = fields.Many2one('hr.employee')
    department = fields.Char(related='emp_prfl_id.department_name', string="Department")
    designation = fields.Char(related='emp_prfl_id.job_position', string='Designation')
    employee_code = fields.Char(related='emp_prfl_id.employee_code', string='Employee Code')
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    email_id = fields.Char(related='emp_prfl_id.work_email_id', string='Work Email')

    new_blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    name = fields.Char(string='Employee')
    user_id = fields.Char('User Id')
    work_email_id = fields.Char(string="Work Email", size=100)
    date_of_joining = fields.Date(string="Joining Date")
    birthday = fields.Date(groups="base.group_user")
    work_phone = fields.Char(string="Work Phone No",)
    whatsapp_no = fields.Char(string='WhatsApp No.', size=15)
    extn_no = fields.Char(string='Extn No.')

    new_name = fields.Char(string='Employee')
    new_user_id = fields.Char('User Id')

    new_work_email_id = fields.Char(string="Work Email", size=100)
    new_date_of_joining = fields.Date(string="Joining Date")
    new_birthday = fields.Date(groups="base.group_user")
    new_work_phone = fields.Char(string="Work Phone No",)
    new_whatsapp_no = fields.Char(string='WhatsApp No.', size=15)
    new_extn_no = fields.Char(string='Extn No.')

    user_name = fields.Char(string='User Name')
    digital_signature = fields.Binary(string="Digital Signature")
    id_card_no = fields.Char(string=u'ID Card No', size=100)
    outlook_pwd = fields.Char(string=u'Outlook Password', size=100)

    new_user_name = fields.Char(string='User Name')
    new_digital_signature = fields.Binary(string="Digital Signature")
    new_id_card_no = fields.Char(string=u'ID Card No', size=100)
    new_outlook_pwd = fields.Char(string=u'Outlook Password', size=100)

    personal_email = fields.Char(string='Personal EMail Id ',)
    country_id = fields.Many2one('res.country', string="Nationality")
    marital = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    marital_code = fields.Char(string=u'Marital Status Code ')
    wedding_anniversary = fields.Date(string=u'Wedding Anniversary')
    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    # gender = fields.Char(string='Gender')
    mobile_phone = fields.Char(string="Mobile No", size=15)
    present_addr_street = fields.Text(string="Present Address", size=500)
    present_addr_country_id = fields.Many2one('res.country', string="Present Country Address")
    present_addr_city = fields.Char(string="Present City Address", size=100)
    present_addr_state_id = fields.Many2one('res.country.state', string="Present State Address")
    present_addr_zip = fields.Char(string="Present Address ZIP", size=10)
    present_addr_street2 = fields.Text(string="Present Address(2)", size=500)
    permanent_addr_street2 = fields.Text(string="Permanent Address (2)", size=500)
    same_address = fields.Boolean(string=u'Same as Present Address', default=False)
    permanent_addr_country_id = fields.Many2one('res.country', string="Permanent Country Address")
    permanent_addr_street = fields.Text(string="Permanent Street Address", size=500)
    permanent_addr_city = fields.Char(string="Permanent City Address",  size=100)
    permanent_addr_state_id = fields.Many2one('res.country.state', string="Permanent State Address")
    permanent_addr_zip = fields.Char(string="Permanent Address ZIP", size=10)
    emergency_contact_name = fields.Char(string='Name')
    emergency_address = fields.Text(string='Address')
    emergencye_telephone = fields.Char(string='Telephone(R)')
    emergency_city = fields.Char(string='City')
    emergency_country = fields.Many2one('res.country', string='Country')
    emergency_state = fields.Many2one('res.country.state', string='State')
    emergency_mobile_no = fields.Char(string='Mobile No')
    emergency_mobile_no_2 = fields.Char(string='Mobile No 2')
   
    new_present_addr_street2 = fields.Text(string="Present Address(2)", size=500)
    new_permanent_addr_street2 = fields.Text(string="Permanent Address (2)", size=500)
    new_personal_email = fields.Char(string='Personal Email Id ',)
    new_country_id = fields.Many2one('res.country', string="Nationality")
    new_marital = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    new_marital_code = fields.Char(string=u'Marital Status Code ')
    new_wedding_anniversary = fields.Date(string=u'Wedding Anniversary')
    new_emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    # new_gender = fields.Char(string='Gender')
    new_mobile_phone = fields.Char(string="Mobile No", size=15)
    new_present_addr_street = fields.Text(string="Present Address", size=500)
    new_present_addr_country_id = fields.Many2one('res.country', string="Present Address Country")
    new_present_addr_city = fields.Char(string="Present Address City", size=100)
    new_present_addr_state_id = fields.Many2one('res.country.state', string="Present Address State")
    new_present_addr_zip = fields.Char(string="Present Address ZIP", size=10)
    new_same_address = fields.Boolean(string=u'Same as Present Address', default=False)
    new_permanent_addr_country_id = fields.Many2one('res.country', string="Permanent Address Country")
    new_permanent_addr_street = fields.Text(string="Permanent Address", size=500)
    new_permanent_addr_city = fields.Char(string="Permanent Address City",  size=100)
    new_permanent_addr_state_id = fields.Many2one('res.country.state', string="Permanent Address State")
    new_permanent_addr_zip = fields.Char(string="Permanent Address ZIP", size=10)
    new_emergency_contact_name = fields.Char(string='Name')
    new_emergency_address = fields.Text(string='Address')
    new_emergencye_telephone = fields.Char(string='Telephone(R)')
    new_emergency_city = fields.Char(string='City')
    new_emergency_country = fields.Many2one('res.country', string='Country')
    new_emergency_state = fields.Many2one('res.country.state', string='State')
    new_emergency_mobile_no = fields.Char(string='Mobile No')
    new_emergency_mobile_no_2 = fields.Char(string='Mobile No 2')
    new_experience_sts = fields.Selection(string="Work Experience Details ",
                                          selection=[('1', 'Fresher'), ('2', 'Experience')])
    linkedin_url = fields.Char(string='Linked In Profile URL')
    new_linkedin_url = fields.Char(string='New Linked In Profile URL')
    upload_medical_certificate = fields.Binary(string="Medical Certficate")

    worked_country_ids = fields.Many2many(
        string='Countries Of Work Experience',
        comodel_name='res.country',
        relation='kw_emp_profile_country_old_data_rel',
        column1='profile_id', column2='country_id'
    )
    new_worked_country_ids = fields.Many2many(
        string='Countries Of Work Experience',
        comodel_name='res.country',
        relation='kw_emp_profile_country_new_rel',
        column1='profile_id', column2='country_id'
    )

    # check_all_boolean = fields.Char(compute='_get_value')
    digital_signature_boolean = fields.Boolean(string="Check Availability", compute='_get_value')
    personal_email_boolean = fields.Boolean(string='Check Personal Email', compute='_get_value')
    country_id_boolean = fields.Boolean(string='Check Nationality', compute='_get_value')
    marital_boolean = fields.Boolean(string="Check Marital", compute='_get_value')
    wedding_anniversary_boolean = fields.Boolean(string="Check Anniversary", compute='_get_value')
    emp_religion_boolean = fields.Boolean(string="Check Religion", compute='_get_value')
    mobile_phone_boolean = fields.Boolean(string="Check Mobile", compute='_get_value')
    whatsapp_no_boolean = fields.Boolean(string="Check Whatsapp no", compute='_get_value')
    extn_no_boolean = fields.Boolean(string="Check Extn No", compute='_get_value')
    present_addr_street_boolean = fields.Boolean(string="Check Street", compute='_get_value')
    present_addr_country_id_boolean = fields.Boolean(string="Check Country", compute='_get_value')
    present_addr_city_boolean = fields.Boolean(string="Check City", compute='_get_value')
    present_addr_state_id_boolean = fields.Boolean(string="Check Present state", compute='_get_value')
    present_addr_zip_boolean = fields.Boolean(string="Check Present zip", compute='_get_value')
    permanent_addr_state_id_boolean = fields.Boolean(string="Check Permanent State", compute='_get_value')
    permanent_addr_country_id_boolean = fields.Boolean(string="Check Per Country", compute='_get_value')
    permanent_addr_city_boolean = fields.Boolean(string="Check City", compute='_get_value')
    permanent_addr_street_boolean = fields.Boolean(string="Check per street", compute='_get_value')
    permanent_addr_zip_boolean = fields.Boolean(string="Check Per Zip", compute='_get_value')
    emergency_address_boolean = fields.Boolean(string="Check Emergency Address", compute='_get_value')
    emergency_city_boolean = fields.Boolean(string="Check Emergency City", compute='_get_value')
    emergency_contact_name_boolean = fields.Boolean(string="Check Emergency Name", compute='_get_value')
    emergency_mobile_no_boolean = fields.Boolean(string="Check Emergency Mobile", compute='_get_value')
    emergency_mobile_no_boolean_2 = fields.Boolean(string="Check Emergency Mobile 2", compute='_get_value')
    emergency_state_boolean = fields.Boolean(string="Check Emergency State", compute='_get_value')
    emergencye_telephone_boolean = fields.Boolean(string="Check Emergency tel", compute='_get_value')
    emergency_country_boolean = fields.Boolean(string="Check Emergency country", compute='_get_value')
    known_language_ids_boolean = fields.Boolean(string="Check Language")
    blood_group_boolean = fields.Boolean(string="Check Blood group", compute='_get_value')
    identification_ids_boolean = fields.Boolean(string="Check Identification")
    membership_assc_ids_boolean = fields.Boolean(string="Check Membership")
    educational_details_ids_boolean = fields.Boolean(string="Check Educational Details")
    work_experience_ids_boolean = fields.Boolean(string="Check Work experience Details")
    experience_sts_boolean = fields.Boolean(string="Check Work experience Details")
    technical_skill_ids_boolean = fields.Boolean(string="Check Technical Details")
    family_details_ids_boolean = fields.Boolean(string="Check Family Details")
    cv_info_boolean = fields.Boolean(string='Check CV Info')
    worked_country_ids_boolean = fields.Boolean(string="Check Worked Countries", compute='_get_value')
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='pending')
    present_addr_street2_boolean = fields.Boolean(string="Check Pre_Street2 Add", compute='_get_value')
    permanent_addr_street2_boolean = fields.Boolean(string="Check Per_Street2 Add", compute='_get_value')
    outlook_pwd_boolean = fields.Boolean(string="Check Outlook Pwd", compute='_get_value')
    linkedin_url_boolean = fields.Boolean(string='Check Linked In Profile URL', compute='_get_value')
    upload_medical_cert_boolean = fields.Boolean(string='Check medical certificate', compute='_get_value')
    # pending_emp_details_bool = fields.Boolean(compute='_check_emp_details_info')
    # peding_check_bool = fields.Boolean(string="Pending_check")
    

    def _get_value(self):
        for record in self:
            record.linkedin_url_boolean = True if record.new_linkedin_url else False
            record.upload_medical_cert_boolean = True if record.upload_medical_certificate else False
            record.outlook_pwd_boolean = True if record.new_outlook_pwd else False
            record.permanent_addr_street2_boolean = True if record.new_permanent_addr_street2 else False
            record.present_addr_street2_boolean = True if record.new_present_addr_street2 else False
            record.worked_country_ids_boolean = True if record.new_worked_country_ids else False
            record.experience_sts_boolean = True if record.new_experience_sts else False
            record.blood_group_boolean = True if record.new_blood_group else False
            record.digital_signature_boolean = True if record.new_digital_signature else False
            record.personal_email_boolean = True if record.new_personal_email else False
            record.country_id_boolean = True if record.new_country_id else False
            record.marital_boolean = True if record.new_marital else False
            record.wedding_anniversary_boolean = True if record.new_wedding_anniversary else False
            record.emp_religion_boolean = True if record.new_emp_religion else False
            record.mobile_phone_boolean = True if record.new_mobile_phone else False
            record.whatsapp_no_boolean = True if record.new_whatsapp_no else False
            record.extn_no_boolean = True if record.new_extn_no else False
            record.present_addr_street_boolean = True if record.new_present_addr_street else False
            record.present_addr_country_id_boolean = True if record.new_present_addr_country_id else False
            record.present_addr_city_boolean = True if record.new_present_addr_city else False
            record.present_addr_state_id_boolean = True if record.new_present_addr_state_id else False
            record.present_addr_zip_boolean = True if record.new_present_addr_zip else False
            record.permanent_addr_state_id_boolean = True if record.new_permanent_addr_state_id else False
            record.permanent_addr_country_id_boolean = True if record.new_permanent_addr_country_id else False
            record.permanent_addr_city_boolean = True if record.new_permanent_addr_city else False
            record.permanent_addr_zip_boolean = True if record.new_permanent_addr_zip else False
            record.permanent_addr_street_boolean = True if record.new_permanent_addr_street else False
            record.emergency_city_boolean = True if record.new_emergency_city else False
            record.emergency_address_boolean = True if record.new_emergency_address else False
            record.emergencye_telephone_boolean = True if record.new_emergencye_telephone else False
            record.emergency_state_boolean = True if record.new_emergency_state else False
            record.emergency_mobile_no_boolean = True if record.new_emergency_mobile_no else False
            record.emergency_mobile_no_boolean_2 = True if record.new_emergency_mobile_no_2 else False
            record.emergency_contact_name_boolean = True if record.new_emergency_contact_name else False
            record.emergency_country_boolean = True if record.new_emergency_country else False

    @api.multi
    def take_action(self):
        view_id = self.env.ref(
            'kw_emp_profile.kw_emp_profile_new_data_view_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_emp_profile_new_data',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            # 'domain': [('id', '=', self.id)],
        }
        
    

    def object_attribute(self, obj):
        li = ['<lambda>', 'CONCURRENCY_CHECK_FIELD', 'clear_caches', 'ids', 'is_transient', 'is_transient', 'pool']
        return [name for name, value in getmembers(type(obj)) if name[0] != '_' and not isinstance(value, FunctionType) and name not in li]

    @api.multi
    def button_approve(self):
        for record in self:
            linkedin_url = record.emp_prfl_id.linkedin_url if record.emp_prfl_id.linkedin_url else '',
            outlook_pwd = record.emp_prfl_id.outlook_pwd if record.emp_prfl_id.outlook_pwd else '',
            permanent_addr_street2 = record.emp_prfl_id.permanent_addr_street2 if record.emp_prfl_id.permanent_addr_street2 else '',
            present_addr_street2 = record.emp_prfl_id.present_addr_street2 if record.emp_prfl_id.present_addr_street2 else '',
            personal_email = record.emp_prfl_id.personal_email if record.emp_prfl_id.personal_email else '',
            country_id = record.emp_prfl_id.country_id.id if record.emp_prfl_id.country_id else None,
            whatsapp_no = record.emp_prfl_id.whatsapp_no if record.emp_prfl_id.whatsapp_no else '',
            epbx_no = record.emp_prfl_id.extn_no if record.emp_prfl_id.extn_no else '',
            marital_sts = record.emp_prfl_id.marital.id if record.emp_prfl_id.marital else None,
            emp_religion = record.emp_prfl_id.emp_religion.id if record.emp_prfl_id.emp_religion else None,
            wedding_anniversary = record.emp_prfl_id.wedding_anniversary if record.emp_prfl_id.wedding_anniversary else None,
            mobile_phone = record.emp_prfl_id.mobile_phone if record.emp_prfl_id.mobile_phone else '',
            present_addr_street = record.emp_prfl_id.present_addr_street if record.emp_prfl_id.present_addr_street else '',
            present_addr_country_id = record.emp_prfl_id.present_addr_country_id.id if record.emp_prfl_id.present_addr_country_id else None,
            present_addr_city = record.emp_prfl_id.present_addr_city if record.emp_prfl_id.present_addr_city  else '',
            present_addr_state_id = record.emp_prfl_id.present_addr_state_id.id if record.emp_prfl_id.present_addr_state_id  else None,
            present_addr_zip = record.emp_prfl_id.present_addr_zip if record.emp_prfl_id.present_addr_zip else '',
            permanent_addr_zip = record.emp_prfl_id.permanent_addr_zip if record.emp_prfl_id.permanent_addr_zip else '',
            permanent_addr_country_id = record.emp_prfl_id.permanent_addr_country_id.id if record.emp_prfl_id.permanent_addr_country_id.id else None,
            permanent_addr_street = record.emp_prfl_id.permanent_addr_street if record.emp_prfl_id.permanent_addr_street else '',
            permanent_addr_city = record.emp_prfl_id.permanent_addr_city if record.emp_prfl_id.permanent_addr_city else '',
            permanent_addr_state_id = record.emp_prfl_id.permanent_addr_state_id.id if record.emp_prfl_id.permanent_addr_state_id else None,
            emergency_contact = record.emp_prfl_id.emergency_contact_name if record.emp_prfl_id.emergency_contact_name else '',
            emergency_phone = record.emp_prfl_id.emergency_mobile_no if record.emp_prfl_id.emergency_mobile_no  else '',
            emergency_phone_2 = record.emp_prfl_id.emergency_mobile_no_2 if record.emp_prfl_id.emergency_mobile_no_2  else '',
            blood_group = record.emp_prfl_id.blood_group.id if record.emp_prfl_id.blood_group else None,
            experience_sts = record.emp_prfl_id.experience_sts if record.emp_prfl_id.experience_sts else '',
            id = record.emp_prfl_id.emp_id.id
            self.env.cr.execute("""
                        update hr_employee set 
                                        linkedin_url = %s,
                                        outlook_pwd = %s,
                                        country_id = %s,
                                        permanent_addr_street2 = %s,
                                        present_addr_street2 = %s,
                                        personal_email = %s,
                                        whatsapp_no = %s,
                                        epbx_no = %s,
                                        marital_sts = %s,
                                        emp_religion = %s,
                                        wedding_anniversary = %s,
                                        mobile_phone = %s,
                                        present_addr_street = %s,
                                        present_addr_country_id = %s,
                                        present_addr_city = %s,
                                        present_addr_state_id = %s,
                                        present_addr_zip = %s,
                                        permanent_addr_zip = %s,
                                        permanent_addr_country_id = %s,
                                        permanent_addr_street = %s,
                                        permanent_addr_city = %s,
                                        permanent_addr_state_id = %s,
                                        emergency_contact = %s,
                                        emergency_phone = %s,
                                        emergency_phone_2 = %s,
                                        blood_group = %s,
                                        experience_sts = %s
                            
                          where id = %s 
                        """, [linkedin_url, outlook_pwd, country_id, permanent_addr_street2, present_addr_street2,
                              personal_email, whatsapp_no, epbx_no, marital_sts, emp_religion, wedding_anniversary,
                              mobile_phone, present_addr_street, present_addr_country_id, present_addr_city,
                              present_addr_state_id, present_addr_zip, permanent_addr_zip, permanent_addr_country_id,
                              permanent_addr_street, permanent_addr_city, permanent_addr_state_id, emergency_contact,
                              emergency_phone,emergency_phone_2, blood_group, experience_sts, id])

            # vals = self.object_attribute(record)
            # for rec in vals:
            #     if rec in field_dict.keys():
            #         if record[rec]:
            #             print(record[rec])
            #             print(field_dict[rec][1], '------------->', record[field_dict[rec][0]])
            #
            #             query = f"""update hr_employee set {field_dict[rec][1]} = {record[field_dict[rec][0]]}
            #                         where id = {record.emp_prfl_id.emp_id.id}
            #             """
            #             self.env.cr.execute(query)

            value = {}
            # print("if-----------==========",self,self.write_uid.id,"=========self.user_id",self.user_id)
            # print(l)
            if self.write_uid.id != 1 and self.user_id != self.env.uid:
                # print("in if other emp data changes===========================================")
                # ----------Approval For Worked Country_ids------------------

                res = self.env['hr.employee'].sudo().search([('id', '=', record.emp_prfl_id.emp_id.id)])
                if res:
                    if record.emp_prfl_id.worked_country_ids:
                        res.write({'worked_country_ids': [(6, 0, record.emp_prfl_id.worked_country_ids.ids)]})
                    else:
                        if not record.emp_prfl_id.worked_country_ids.ids:
                            res.write({'worked_country_ids': [(6, 0, [])]})

                # ----Approval for CV Info---------
                # if self.del_emp_cv_bool is not True:
                #     emp_cv_lst = []
                #     pfl_cv_lst = []
                #     pfl_new_cv_lst = []
                #     for res in record.emp_cv_info_ids:
                #         emp_cv_lst.append(res.id)
                #     for rec in record.profile_cv_info_ids:
                #         if rec.emp_cv_info_id:
                #             pfl_cv_lst.append(rec.emp_cv_info_id.id)
                #         else:
                #             pfl_new_cv_lst.append(rec.id)

                #     for items in pfl_cv_lst:
                #         if items in emp_cv_lst:
                #             profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('emp_cv_info_id', '=', int(items))])
                #             emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                #             emp_cv_rec.update({
                #                 'project_of': profile_cv_rec.project_of,
                #                 'project_name': profile_cv_rec.project_name,
                #                 # 'project_id':profile_cv_rec.project_id.id,
                #                 'location': profile_cv_rec.location,
                #                 'start_month_year': profile_cv_rec.start_month_year,
                #                 'end_month_year': profile_cv_rec.end_month_year,
                #                 'project_feature': profile_cv_rec.project_feature,
                #                 'role': profile_cv_rec.role,
                #                 'responsibility_activity': profile_cv_rec.responsibility_activity,
                #                 'client_name': profile_cv_rec.client_name,
                #                 'compute_project': profile_cv_rec.compute_project,
                #                 'organization_id': profile_cv_rec.organization_id.id,
                #                 'activity': profile_cv_rec.activity,
                #                 'other_activity': profile_cv_rec.other_activity,
                #                 'emp_project_id': profile_cv_rec.emp_project_id.id,
                #             })
                #     for items in emp_cv_lst:
                #         if items not in pfl_cv_lst:
                #             emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])
                #             emp_cv_rec.unlink()

                #     for items in pfl_new_cv_lst:
                #         profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('id', '=', int(items))])

                #         emp_cv_rec = record.emp_prfl_id.emp_id.cv_info_details_ids.create({
                #             'project_of': profile_cv_rec.project_of,
                #             'project_name': profile_cv_rec.project_name,
                #             # 'project_id':profile_cv_rec.project_id.id,
                #             'location': profile_cv_rec.location,
                #             'start_month_year': profile_cv_rec.start_month_year,
                #             'end_month_year': profile_cv_rec.end_month_year,
                #             'project_feature': profile_cv_rec.project_feature,
                #             'role': profile_cv_rec.role,
                #             'responsibility_activity': profile_cv_rec.responsibility_activity,
                #             'client_name': profile_cv_rec.client_name,
                #             'compute_project': profile_cv_rec.compute_project,
                #             'organization_id': profile_cv_rec.organization_id.id,
                #             'activity': profile_cv_rec.activity,
                #             'other_activity': profile_cv_rec.other_activity,
                #             'emp_id': record.emp_prfl_id.emp_id.id,
                #             'emp_project_id': profile_cv_rec.emp_project_id.id,

                #         })
                #         profile_cv_rec.update({'emp_cv_info_id': emp_cv_rec.id})

                # ----Approval for language known -------

                emp_lang_lst = []
                pfl_lang_lst = []
                pfl_new_lang_lst = []
                for res in record.emp_language_ids:
                    emp_lang_lst.append(res.id)
                for rec in record.profile_language_ids:
                    if rec.emp_language_id:
                        pfl_lang_lst.append(rec.emp_language_id.id)
                    else:
                        pfl_new_lang_lst.append(rec.id)

                for items in pfl_lang_lst:
                    if items in emp_lang_lst:
                        profile_lang_rec = self.env['kw_emp_profile_language_known'].sudo().search(
                            [('emp_language_id', '=', int(items))])
                        emp_lang_rec = self.env['kwemp_language_known'].sudo().search([('id', '=', int(items))])

                        emp_lang_rec.update({
                            'language_id': profile_lang_rec.language_id.id,
                            'reading_status': profile_lang_rec.reading_status,
                            'writing_status': profile_lang_rec.writing_status,
                            'speaking_status': profile_lang_rec.speaking_status,
                            'understanding_status': profile_lang_rec.understanding_status
                        })
                for items in emp_lang_lst:
                    if items not in pfl_lang_lst:
                        emp_lang_rec = self.env['kwemp_language_known'].sudo().search([('id', '=', int(items))])
                        emp_lang_rec.unlink()

                for items in pfl_new_lang_lst:
                    profile_lang_rec = self.env['kw_emp_profile_language_known'].sudo().search([('id', '=', int(items))])

                    emp_lang_rec = record.emp_prfl_id.emp_id.known_language_ids.create({
                        'language_id': profile_lang_rec.language_id.id,
                        'reading_status': profile_lang_rec.reading_status,
                        'writing_status': profile_lang_rec.writing_status,
                        'speaking_status': profile_lang_rec.speaking_status,
                        'understanding_status': profile_lang_rec.understanding_status,
                        'emp_id': record.emp_prfl_id.emp_id.id

                    })
                    profile_lang_rec.update({'emp_language_id': emp_lang_rec.id})

               
                # ---Approval for Identification Details-----
                # print("in identification-------------------------------")
                emp_identification_lst = []
                pfl_identification_lst = []
                pfl_new_identification_lst = []
                for res in record.emp_identification_ids:
                    emp_identification_lst.append(res.id)
                for rec in record.profile_identification_ids:
                    if rec.emp_document_id:
                        pfl_identification_lst.append(rec.emp_document_id.id)
                    else:
                        pfl_new_identification_lst.append(rec.id)

                for items in pfl_identification_lst:
                    if items in emp_identification_lst:
                        profile_identification_rec = self.env['kw_emp_profile_identity_docs'].sudo().search(
                            [('emp_document_id', '=', int(items))])
                        emp_identification_rec = self.env['kwemp_identity_docs'].sudo().search(
                            [('id', '=', int(items))])

                        emp_identification_rec.update({
                            'name': profile_identification_rec.name,
                            'doc_number': profile_identification_rec.doc_number,
                            'date_of_expiry': profile_identification_rec.date_of_expiry,
                            'date_of_issue': profile_identification_rec.date_of_issue,
                            'renewal_sts': profile_identification_rec.renewal_sts,
                            'uploaded_doc': profile_identification_rec.uploaded_doc,
                        })
                for items in emp_identification_lst:
                    if items not in pfl_identification_lst:
                        emp_identification_rec = self.env['kwemp_identity_docs'].sudo().search([('id', '=', int(items))])
                        emp_identification_rec.unlink()

                for items in pfl_new_identification_lst:
                    profile_identification_rec = self.env['kw_emp_profile_identity_docs'].sudo().search([('id', '=', int(items))])

                    emp_identification_rec = record.emp_prfl_id.emp_id.identification_ids.create({
                        'name': profile_identification_rec.name,
                        'doc_number': profile_identification_rec.doc_number,
                        'date_of_expiry': profile_identification_rec.date_of_expiry,
                        'date_of_issue': profile_identification_rec.date_of_issue,
                        'renewal_sts': profile_identification_rec.renewal_sts,
                        'uploaded_doc': profile_identification_rec.uploaded_doc,
                        'emp_id': record.emp_prfl_id.emp_id.id
                    })
                    profile_identification_rec.update({'emp_document_id': emp_identification_rec.id})

                # ---Approval For Educational details------

                emp_education_lst = []
                pfl_education_lst = []
                pfl_new_education_lst = []
                for res in record.emp_educational_ids:
                    emp_education_lst.append(res.id)
                for rec in record.profile_educational_ids:
                    if rec.emp_educational_id:
                        pfl_education_lst.append(rec.emp_educational_id.id)
                    else:
                        pfl_new_education_lst.append(rec.id)

                for items in pfl_education_lst:
                    if items in emp_education_lst:
                        profile_education_rec = self.env['kw_emp_profile_qualification'].sudo().search(
                            [('emp_educational_id', '=', int(items))])
                        emp_education_rec = self.env['kwemp_educational_qualification'].sudo().search(
                            [('id', '=', int(items))])

                        emp_education_rec.update({
                            'marks_obtained': profile_education_rec.marks_obtained,
                            'division': profile_education_rec.division,
                            'passing_year': profile_education_rec.passing_year,
                            'university_name': profile_education_rec.university_name.id,
                            'stream_id': profile_education_rec.stream_id.id,
                            'course_id': profile_education_rec.course_id.id,
                            'course_type': profile_education_rec.course_type,
                            'uploaded_doc': profile_education_rec.uploaded_doc,
                            'passing_details': [(6, 0, profile_education_rec.passing_details.ids)],
                            'expiry_date':profile_education_rec.expiry_date
                        })
                for items in emp_education_lst:
                    if items not in pfl_education_lst:
                        emp_education_rec = self.env['kwemp_educational_qualification'].sudo().search([('id', '=', int(items))])
                        emp_education_rec.unlink()

                for items in pfl_new_education_lst:
                    profile_education_rec = self.env['kw_emp_profile_qualification'].sudo().search(
                        [('id', '=', int(items))])

                    emp_educational_rec = record.emp_prfl_id.emp_id.educational_details_ids.create({
                        'marks_obtained': profile_education_rec.marks_obtained,
                        'division': profile_education_rec.division,
                        'passing_year': profile_education_rec.passing_year,
                        'university_name': profile_education_rec.university_name.id,
                        'stream_id': profile_education_rec.stream_id.id,
                        'course_id': profile_education_rec.course_id.id,
                        'course_type': profile_education_rec.course_type,
                        'uploaded_doc': profile_education_rec.uploaded_doc,
                        'passing_details': [(6, 0, profile_education_rec.passing_details.ids)],
                        'emp_id': record.emp_prfl_id.emp_id.id,
                        'expiry_date':profile_education_rec.expiry_date
                    })
                    profile_education_rec.update({'emp_educational_id': emp_educational_rec.id})

                # ----Approval of Work Experience-----

                emp_work_lst = []
                pfl_work_lst = []
                pfl_new_work_lst = []
                for res in record.emp_work_experience_ids:
                    emp_work_lst.append(res.id)
                for rec in record.profile_work_experience_ids:
                    if rec.emp_work_id:
                        pfl_work_lst.append(rec.emp_work_id.id)
                    else:
                        pfl_new_work_lst.append(rec.id)

                for items in pfl_work_lst:
                    if items in emp_work_lst:
                        profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('emp_work_id', '=', int(items))])
                        emp_work_rec = self.env['kwemp_work_experience'].sudo().search([('id', '=', int(items))])

                        emp_work_rec.update({
                            'country_id': profile_work_rec.country_id.id,
                            'name': profile_work_rec.name,
                            'designation_name': profile_work_rec.designation_name,
                            'organization_type': profile_work_rec.organization_type.id,
                            'industry_type': profile_work_rec.industry_type.id,
                            'effective_from': profile_work_rec.effective_from,
                            'effective_to': profile_work_rec.effective_to,
                            'uploaded_doc': profile_work_rec.uploaded_doc,
                        })
                for items in emp_work_lst:
                    if items not in pfl_work_lst:
                        emp_tech_rec = self.env['kwemp_work_experience'].sudo().search([('id', '=', int(items))])
                        emp_tech_rec.unlink()

                for items in pfl_new_work_lst:
                    profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                        [('id', '=', int(items))])

                    emp_work_rec = record.emp_prfl_id.emp_id.work_experience_ids.create({
                        'country_id': profile_work_rec.country_id.id,
                        'name': profile_work_rec.name,
                        'designation_name': profile_work_rec.designation_name,
                        'organization_type': profile_work_rec.organization_type.id,
                        'industry_type': profile_work_rec.industry_type.id,
                        'effective_from': profile_work_rec.effective_from,
                        'effective_to': profile_work_rec.effective_to,
                        'uploaded_doc': profile_work_rec.uploaded_doc,
                        'emp_id': record.emp_prfl_id.emp_id.id

                    })
                    profile_work_rec.update({'emp_work_id': emp_work_rec.id})

                # ------Approval of Technical skills------
                emp_tech_lst = []
                pfl_tech_lst = []
                new_pfl_lst = []
                for skill in record.emp_technical_ids:
                    emp_tech_lst.append(skill.id)
                for skill in record.profile_technical_ids:
                    if skill.emp_technical_id:
                        pfl_tech_lst.append(skill.emp_technical_id.id)
                    else:
                        new_pfl_lst.append(skill.id)
                for items in pfl_tech_lst:
                    if items in emp_tech_lst:
                        profile_tech_rec = self.env['kw_emp_profile_technical_skills'].sudo().search(
                            [('emp_technical_id', '=', int(items))])
                        emp_tech_rec = self.env['kwemp_technical_skills'].sudo().search([('id', '=', int(items))])

                        emp_tech_rec.update({
                            'category_id': profile_tech_rec.category_id.id,
                            'skill_id': profile_tech_rec.skill_id.id,
                            'proficiency': profile_tech_rec.proficiency
                        })
                for items in emp_tech_lst:
                    if items not in pfl_tech_lst:
                        emp_tech_rec = self.env['kwemp_technical_skills'].sudo().search([('id', '=', int(items))])
                        emp_tech_rec.unlink()
                for items in new_pfl_lst:
                    profile_tech_rec = self.env['kw_emp_profile_technical_skills'].sudo().search([
                        ('id', '=', int(items))])

                    emp_tech = record.emp_prfl_id.emp_id.technical_skill_ids.create({
                        'category_id': profile_tech_rec.category_id.id,
                        'skill_id': profile_tech_rec.skill_id.id,
                        'proficiency': profile_tech_rec.proficiency,
                        'emp_id': record.emp_prfl_id.emp_id.id
                    })
                    profile_tech_rec.update({'emp_technical_id': emp_tech.id})

                    # -------Approval of Family Details----------

                list_1 = []
                list_2 = []
                list_3 = []
                for res in record.emp_family_id:
                    list_1.append(res.id)
                for rec in record.profile_family_details:
                    if rec.family_id:
                        list_2.append(rec.family_id.id)
                    else:
                        list_3.append(rec.id)
                for items in list_2:
                    if items in list_1:
                        profile_family_rec = self.env['kw_emp_profile_family_info'].sudo().search(
                            [('family_id', '=', int(items))])
                        emp_family_rec = self.env['kwemp_family_info'].sudo().search([('id', '=', int(items))])

                        emp_family_rec.update({
                            'relationship_id': profile_family_rec.relationship_id.id,
                            'name': profile_family_rec.name,
                            'gender': profile_family_rec.gender,
                            'date_of_birth': profile_family_rec.date_of_birth,
                            'dependent': profile_family_rec.dependent
                        })
                for items in list_1:
                    if items not in list_2:
                        emp_family_rec = self.env['kwemp_family_info'].sudo().search([('id', '=', int(items))])
                        emp_family_rec.unlink()
                for items in list_3:
                    profile_family_rec = self.env['kw_emp_profile_family_info'].sudo().search([
                        ('id', '=', int(items))])

                    emp_family = record.emp_prfl_id.emp_id.family_details_ids.create({
                        'relationship_id': profile_family_rec.relationship_id.id,
                        'name': profile_family_rec.name,
                        'gender': profile_family_rec.gender,
                        'date_of_birth': profile_family_rec.date_of_birth,
                        'dependent': profile_family_rec.dependent,
                        'emp_id': record.emp_prfl_id.emp_id.id,
                        'phone_no':profile_family_rec.phone_no
                    })
                    profile_family_rec.update({'family_id': emp_family.id})

                
        #
            #  Mail Template for profile approval

            inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_approve_request_email_template')
            profile_manager_group = self.env.ref('kw_emp_profile.group_kw_emp_profile_manager')
            if profile_manager_group.users:
                # print('check manager')
                employee_manager = self.env['hr.employee'].sudo().search([('user_id', 'in', profile_manager_group.users.ids)])
                for rec in employee_manager:
                    if record.write_uid.id == rec.user_id.id:
                        hr_emails = self.env.user.employee_ids.work_email
                        action_taken_by = self.env.user.employee_ids.name
                        inform_template.with_context(email=record.work_email_id, action_taken_by=action_taken_by,
                                                     email_from=hr_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success(message='Profile record updated successfully.')
            
            if record.outlook_pwd_boolean == True or record.digital_signature_boolean == True:
                value = {'account_info_sts': False}
            if record.permanent_addr_street2_boolean == True or record.present_addr_street2_boolean == True \
                    or record.personal_email_boolean == True or record.country_id_boolean == True \
                    or record.marital_boolean == True or record.wedding_anniversary_boolean == True \
                    or record.emp_religion_boolean == True or record.mobile_phone_boolean == True \
                    or record.whatsapp_no_boolean == True or record.extn_no_boolean == True \
                    or record.present_addr_street_boolean == True or record.present_addr_country_id_boolean == True \
                    or record.present_addr_city_boolean == True or record.present_addr_state_id_boolean == True \
                    or record.present_addr_zip_boolean == True or record.permanent_addr_state_id_boolean == True \
                    or record.permanent_addr_country_id_boolean == True or record.permanent_addr_city_boolean == True \
                    or record.permanent_addr_zip_boolean == True or record.permanent_addr_street_boolean == True \
                    or record.emergency_city_boolean == True or record.emergency_address_boolean == True \
                    or record.emergencye_telephone_boolean == True or record.emergency_state_boolean == True \
                    or record.emergency_state_boolean == True or record.emergency_mobile_no_boolean == True \
                    or record.emergency_contact_name_boolean == True or record.emergency_country_boolean == True \
                    or record.known_language_ids_boolean == True or record.linkedin_url_boolean == True \
                    or record.blood_group_boolean == True:
                print("in personal-------------")
                value = {'personalinfo_sts': False}
            if record.identification_ids_boolean == True or record.membership_assc_ids_boolean == True:
                # print("in identy----------------------------------------------------------")
                value = {'identification_sts': False}
            if record.educational_details_ids_boolean == True:
                value = {'educational_sts': False}
            if record.technical_skill_ids_boolean == True or record.work_experience_ids_boolean == True \
                    or record.worked_country_ids_boolean == True:
                value = {'workinfo_sts': False}
            if record.family_details_ids_boolean == True:
                value = {'family_sts': False}
            # if record.cv_info_boolean == True:
            #     value = {'cv_sts': False}
            record.state = 'approved'
            # print(value,"==================value")
            profile = self.env['kw_emp_profile'].sudo().search([('id', '=', record.emp_prfl_id.id)])
            profile.update(value)
            menu_id = self.env['ir.ui.menu'].sudo().search([('name', '=', 'Profile Approval')]).id
            action_id = self.env.ref("kw_emp_profile.profile_new_data_approval_action").id
            # return {
            #     'type': 'ir.actions.act_url',
            #     'target': 'self',
            #     'url': f'/web#action={action_id}&model=kw_emp_profile_new_data&view_type=list&menu_id={menu_id}',
            # }
    

    def button_reject(self):
        for record in self:
            value = {}
            record.state = 'rejected'
            profile = self.env['kw_emp_profile'].sudo().search(
                [('id', '=', record.emp_prfl_id.id)])

            if record.write_uid.id != 1:
                # -----Reject of CV Info------
                # emp_cv_lst = []
                # pfl_cv_lst = []
                # pfl_new_cv_lst = []
                # for res in record.emp_cv_info_ids:
                #     emp_cv_lst.append(res.id)
                # for rec in record.profile_cv_info_ids:
                #     if rec.emp_cv_info_id:
                #         pfl_cv_lst.append(rec.emp_cv_info_id.id)
                #     else:
                #         pfl_new_cv_lst.append(rec.id)

                # for items in emp_cv_lst:
                #     if items in pfl_cv_lst:
                #         profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search(
                #             [('emp_cv_info_id', '=', int(items))])
                #         emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                #         profile_cv_rec.update({
                #             'project_of': emp_cv_rec.project_of,
                #             'project_name': emp_cv_rec.project_name,
                #             # 'project_id':emp_cv_rec.project_id.id,
                #             'location': emp_cv_rec.location,
                #             'start_month_year': emp_cv_rec.start_month_year,
                #             'end_month_year': emp_cv_rec.end_month_year,
                #             'project_feature': emp_cv_rec.project_feature,
                #             'role': emp_cv_rec.role,
                #             'responsibility_activity': emp_cv_rec.responsibility_activity,
                #             'client_name': emp_cv_rec.client_name,
                #             'compute_project': emp_cv_rec.compute_project,
                #             'organization_id': emp_cv_rec.organization_id.id,
                #             'activity': emp_cv_rec.activity,
                #             'other_activity': emp_cv_rec.other_activity,
                #             'emp_project_id': emp_cv_rec.emp_project_id.id,
                #         })
                # for items in pfl_new_cv_lst:
                #     if items not in pfl_cv_lst:
                #         profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('id', '=', int(items))])
                #         profile_cv_rec.unlink()

                # for items in emp_cv_lst:
                #     if items not in pfl_cv_lst:
                #         emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                #         profile_cv_rec = record.emp_prfl_id.cv_info_details_ids.create({
                #             'project_of': emp_cv_rec.project_of,
                #             'project_name': emp_cv_rec.project_name,
                #             # 'project_id':emp_cv_rec.project_id.id,
                #             'location': emp_cv_rec.location,
                #             'start_month_year': emp_cv_rec.start_month_year,
                #             'end_month_year': emp_cv_rec.end_month_year,
                #             'project_feature': emp_cv_rec.project_feature,
                #             'role': emp_cv_rec.role,
                #             'responsibility_activity': emp_cv_rec.responsibility_activity,
                #             'client_name': emp_cv_rec.client_name,
                #             'compute_project': emp_cv_rec.compute_project,
                #             'organization_id': emp_cv_rec.organization_id.id,
                #             'activity': emp_cv_rec.activity,
                #             'other_activity': emp_cv_rec.other_activity,
                #             'emp_cv_info_id': emp_cv_rec.id,
                #             'emp_project_id': emp_cv_rec.emp_project_id.id,
                #         })
                #         profile_cv_rec.update({'emp_id': record.emp_prfl_id.id})

                # -----Reject of Language Known-------
                emp_lang_lst = []
                pfl_lang_lst = []
                pfl_new_lang_lst = []
                for res in record.emp_language_ids:
                    emp_lang_lst.append(res.id)
                for rec in record.profile_language_ids:
                    if rec.emp_language_id:
                        pfl_lang_lst.append(rec.emp_language_id.id)
                    else:
                        pfl_new_lang_lst.append(rec.id)
                for items in emp_lang_lst:
                    if items in pfl_lang_lst:
                        profile_lang_rec = self.env['kw_emp_profile_language_known'].sudo().search(
                            [('emp_language_id', '=', int(items))])
                        emp_lang_rec = self.env['kwemp_language_known'].sudo().search([('id', '=', int(items))])

                        profile_lang_rec.update({
                            'language_id': emp_lang_rec.language_id.id,
                            'reading_status': emp_lang_rec.reading_status,
                            'writing_status': emp_lang_rec.writing_status,
                            'speaking_status': emp_lang_rec.speaking_status,
                            'understanding_status': emp_lang_rec.understanding_status
                        })
                for items in pfl_new_lang_lst:
                    if items not in pfl_lang_lst:
                        profile_lang_rec = self.env['kw_emp_profile_language_known'].sudo().search(
                            [('id', '=', int(items))])
                        profile_lang_rec.unlink()

                for items in emp_lang_lst:
                    if items not in pfl_lang_lst:
                        emp_lang_rec = self.env['kwemp_language_known'].sudo().search([('id', '=', int(items))])

                        profile_lang_rec = record.emp_prfl_id.known_language_ids.create({
                            'language_id': emp_lang_rec.language_id.id,
                            'reading_status': emp_lang_rec.reading_status,
                            'writing_status': emp_lang_rec.writing_status,
                            'speaking_status': emp_lang_rec.speaking_status,
                            'understanding_status': emp_lang_rec.understanding_status,
                            'emp_language_id': emp_lang_rec.id
                        })
                        profile_lang_rec.update({'emp_id': record.emp_prfl_id.id})

                # -----Reject of Membership Details--------
                emp_membership_lst = []
                pfl_membership_lst = []
                pfl_new_membership_lst = []
                for res in record.emp_membership_ids:
                    emp_membership_lst.append(res.id)
                for rec in record.profile_membership_ids:
                    if rec.emp_membership_id:
                        pfl_membership_lst.append(rec.emp_membership_id.id)
                    else:
                        pfl_new_membership_lst.append(rec.id)
                for items in emp_membership_lst:
                    if items in pfl_membership_lst:
                        profile_membership_rec = self.env['kw_emp_profile_membership_assc'].sudo().search(
                            [('emp_membership_id', '=', int(items))])
                        emp_membership_rec = self.env['kwemp_membership_assc'].sudo().search(
                            [('id', '=', int(items))])

                        profile_membership_rec.update({
                            'uploaded_doc': emp_membership_rec.uploaded_doc,
                            'renewal_sts': emp_membership_rec.renewal_sts,
                            'date_of_expiry': emp_membership_rec.date_of_expiry,
                            'name': emp_membership_rec.name,
                            'date_of_issue': emp_membership_rec.date_of_issue,
                        })
                for items in pfl_new_membership_lst:
                    if items not in pfl_membership_lst:
                        profile_membership_rec = self.env['kw_emp_profile_membership_assc'].sudo().search(
                            [('id', '=', int(items))])
                        profile_membership_rec.unlink()

                for items in emp_membership_lst:
                    if items not in pfl_membership_lst:
                        emp_membership_rec = self.env['kwemp_membership_assc'].sudo().search([('id', '=', int(items))])

                        profile_membership_rec = record.emp_prfl_id.membership_assc_ids.create({
                            'uploaded_doc': emp_membership_rec.uploaded_doc,
                            'renewal_sts': emp_membership_rec.renewal_sts,
                            'date_of_expiry': emp_membership_rec.date_of_expiry,
                            'name': emp_membership_rec.name,
                            'date_of_issue': emp_membership_rec.date_of_issue,
                            'emp_membership_id': emp_membership_rec.id
                        })
                        profile_membership_rec.update({'emp_id': record.emp_prfl_id.id})
                # -----Reject of Identification Details-------
                emp_identification_lst = []
                pfl_identification_lst = []
                pfl_new_identification = []
                for res in record.emp_identification_ids:
                    emp_identification_lst.append(res.id)
                for rec in record.profile_identification_ids:
                    if rec.emp_document_id:
                        pfl_identification_lst.append(rec.emp_document_id.id)
                    else:
                        pfl_new_identification.append(rec.id)
                for items in emp_identification_lst:
                    if items in pfl_identification_lst:
                        profile_identification_rec = self.env['kw_emp_profile_identity_docs'].sudo().search(
                            [('emp_document_id', '=', int(items))])
                        emp_identification_rec = self.env['kwemp_identity_docs'].sudo().search(
                            [('id', '=', int(items))])

                        profile_identification_rec.update({
                            'name': emp_identification_rec.name,
                            'doc_number': emp_identification_rec.doc_number,
                            'date_of_issue': emp_identification_rec.date_of_issue,
                            'date_of_expiry': emp_identification_rec.date_of_expiry,
                            'renewal_sts': emp_identification_rec.renewal_sts,
                            'uploaded_doc': emp_identification_rec.uploaded_doc,
                        })
                for items in pfl_new_identification:
                    if items not in pfl_identification_lst:
                        profile_identification_rec = self.env['kw_emp_profile_identity_docs'].sudo().search([
                            ('id', '=', int(items))])
                        profile_identification_rec.unlink()

                for items in emp_identification_lst:
                    if items not in pfl_identification_lst:
                        emp_identification_rec = self.env['kwemp_identity_docs'].sudo().search([('id', '=', int(items))])

                        profile_identification_rec= record.emp_prfl_id.identification_ids.create({
                            'name': emp_identification_rec.name,
                            'doc_number': emp_identification_rec.doc_number,
                            'date_of_issue': emp_identification_rec.date_of_issue,
                            'date_of_expiry': emp_identification_rec.date_of_expiry,
                            'renewal_sts': emp_identification_rec.renewal_sts,
                            'uploaded_doc': emp_identification_rec.uploaded_doc,
                            'emp_document_id': emp_identification_rec.id
                        })
                        profile_identification_rec.update({'emp_id': record.emp_prfl_id.id})
                # -----Reject of Educational Details-----------
                emp_education_lst = []
                pfl_education_lst = []
                pfl_new_education = []
                for res in record.emp_educational_ids:
                    emp_education_lst.append(res.id)
                for rec in record.profile_educational_ids:
                    if rec.emp_educational_id:
                        pfl_education_lst.append(rec.emp_educational_id.id)
                    else:
                        pfl_new_education.append(rec.id)
                for items in emp_education_lst:
                    if items in pfl_education_lst:
                        profile_educational_rec = self.env['kw_emp_profile_qualification'].sudo().search(
                            [('emp_educational_id', '=', int(items))])
                        emp_educational_rec = self.env['kwemp_educational_qualification'].sudo().search(
                            [('id', '=', int(items))])

                        profile_educational_rec.update({
                            'marks_obtained': emp_educational_rec.marks_obtained,
                            'division': emp_educational_rec.division,
                            'passing_year': emp_educational_rec.passing_year,
                            'university_name': emp_educational_rec.university_name.id,
                            'stream_id': emp_educational_rec.stream_id.id,
                            'course_id': emp_educational_rec.course_id.id,
                            'course_type': emp_educational_rec.course_type,
                            'uploaded_doc': emp_educational_rec.uploaded_doc,
                            'passing_details': [(6, 0, emp_educational_rec.passing_details.ids)]
                        })
                for items in pfl_new_education:
                    if items not in pfl_education_lst:
                        profile_education_rec = self.env['kw_emp_profile_qualification'].sudo().search(
                            [('id', '=', int(items))])
                        profile_education_rec.unlink()

                for items in emp_education_lst:
                    if items not in pfl_education_lst:
                        emp_education_rec = self.env['kwemp_educational_qualification'].sudo().search(
                            [('id', '=', int(items))])

                        profile_education_rec = record.emp_prfl_id.educational_details_ids.create({
                            'marks_obtained': emp_education_rec.marks_obtained,
                            'division': emp_education_rec.division,
                            'passing_year': emp_education_rec.passing_year,
                            'university_name': emp_education_rec.university_name.id,
                            'stream_id': emp_education_rec.stream_id.id,
                            'course_id': emp_education_rec.course_id.id,
                            'course_type': emp_education_rec.course_type,
                            'uploaded_doc': emp_education_rec.uploaded_doc,
                            'passing_details': [(6, 0, emp_education_rec.passing_details.ids)],
                            'emp_educational_id': emp_education_rec.id
                        })
                        profile_education_rec.update({'emp_id': record.emp_prfl_id.id})
                # ----Reject of Work Experience------
                emp_work_lst = []
                pfl_work_lst = []
                pfl_new_work = []
                for res in record.emp_work_experience_ids:
                    emp_work_lst.append(res.id)
                for rec in record.profile_work_experience_ids:
                    if rec.emp_work_id:
                        pfl_work_lst.append(rec.emp_work_id.id)
                    else:
                        pfl_new_work.append(rec.id)

                for items in emp_work_lst:
                    if items in pfl_work_lst:
                        profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('emp_work_id', '=', int(items))])
                        emp_work_rec = self.env['kwemp_work_experience'].sudo().search(
                            [('id', '=', int(items))])

                        profile_work_rec.update({
                            'country_id': emp_work_rec.country_id.id,
                            'name': emp_work_rec.name,
                            'designation_name': emp_work_rec.designation_name,
                            'organization_type': emp_work_rec.organization_type.id,
                            'industry_type': emp_work_rec.industry_type.id,
                            'effective_from': emp_work_rec.effective_from,
                            'effective_to': emp_work_rec.effective_to,
                            'uploaded_doc': emp_work_rec.uploaded_doc,
                        })
                for items in pfl_new_work:
                    if items not in pfl_work_lst:
                        profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('id', '=', int(items))])
                        profile_work_rec.unlink()

                for items in emp_work_lst:
                    if items not in pfl_work_lst:
                        emp_work_rec = self.env['kwemp_work_experience'].sudo().search([('id', '=', int(items))])

                        profile_tech_rec = record.emp_prfl_id.work_experience_ids.create({
                            'country_id': emp_work_rec.country_id.id,
                            'name': emp_work_rec.name,
                            'designation_name': emp_work_rec.designation_name,
                            'organization_type': emp_work_rec.organization_type.id,
                            'industry_type': emp_work_rec.industry_type.id,
                            'effective_from': emp_work_rec.effective_from,
                            'effective_to': emp_work_rec.effective_to,
                            'uploaded_doc': emp_work_rec.uploaded_doc,
                            'emp_work_id': emp_work_rec.id
                        })
                        profile_tech_rec.update({'emp_id': record.emp_prfl_id.id})

                # -----Reject of Tecnical skills--------
                emp_tech_lst = []
                pfl_tech_lst = []
                pfl_new_tech = []
                for res in record.emp_technical_ids:
                    emp_tech_lst.append(res.id)
                for rec in record.profile_technical_ids:
                    if rec.emp_technical_id:
                        pfl_tech_lst.append(rec.emp_technical_id.id)
                    else:
                        pfl_new_tech.append(rec.id)
                for items in emp_tech_lst:
                    if items in pfl_tech_lst:
                        profile_tech_rec = self.env['kw_emp_profile_technical_skills'].sudo().search(
                            [('emp_technical_id', '=', int(items))])
                        emp_tech_rec = self.env['kwemp_technical_skills'].sudo().search(
                            [('id', '=', int(items))])

                        profile_tech_rec.update({
                            'category_id': emp_tech_rec.category_id.id,
                            'skill_id': emp_tech_rec.skill_id.id,
                            'proficiency': emp_tech_rec.proficiency
                        })
                for items in pfl_new_tech:
                    if items not in pfl_tech_lst:
                        profile_tech_rec = self.env['kw_emp_profile_technical_skills'].sudo().search(
                            [('id', '=', int(items))])
                        profile_tech_rec.unlink()

                for items in emp_tech_lst:
                    if items not in pfl_tech_lst:
                        emp_tech_rec = self.env['kwemp_technical_skills'].sudo().search([('id', '=', int(items))])

                        profile_tech_rec = record.emp_prfl_id.technical_skill_ids.create({
                            'category_id': emp_tech_rec.category_id.id,
                            'skill_id': emp_tech_rec.skill_id.id,
                            'proficiency': emp_tech_rec.proficiency,
                            'emp_technical_id': emp_tech_rec.id
                        })
                        profile_tech_rec.update({'emp_id': record.emp_prfl_id.id})
                # ----Reject of Work Experience------
                emp_work_lst = []
                pfl_work_lst = []
                pfl_new_work = []
                for res in record.emp_work_experience_ids:
                    emp_work_lst.append(res.id)
                for rec in record.profile_work_experience_ids:
                    if rec.emp_work_id:
                        pfl_work_lst.append(rec.emp_work_id.id)
                    else:
                        pfl_new_work.append(rec.id)

                for items in emp_work_lst:
                    if items in pfl_work_lst:
                        profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('emp_work_id', '=', int(items))])
                        emp_work_rec = self.env['kwemp_work_experience'].sudo().search(
                            [('id', '=', int(items))])

                        profile_work_rec.update({
                            'country_id': emp_work_rec.country_id.id,
                            'name': emp_work_rec.name,
                            'designation_name': emp_work_rec.designation_name,
                            'organization_type': emp_work_rec.organization_type.id,
                            'industry_type': emp_work_rec.industry_type.id,
                            'effective_from': emp_work_rec.effective_from,
                            'effective_to': emp_work_rec.effective_to,
                            'uploaded_doc': emp_work_rec.uploaded_doc,
                        })
                for items in pfl_new_work:
                    if items not in pfl_work_lst:
                        profile_work_rec = self.env['kw_emp_profile_work_experience'].sudo().search(
                            [('id', '=', int(items))])
                        profile_work_rec.unlink()

                for items in emp_work_lst:
                    if items not in pfl_work_lst:
                        emp_work_rec = self.env['kwemp_work_experience'].sudo().search([('id', '=', int(items))])

                        profile_tech_rec = record.emp_prfl_id.work_experience_ids.create({
                            'country_id': emp_work_rec.country_id.id,
                            'name': emp_work_rec.name,
                            'designation_name': emp_work_rec.designation_name,
                            'organization_type': emp_work_rec.organization_type.id,
                            'industry_type': emp_work_rec.industry_type.id,
                            'effective_from': emp_work_rec.effective_from,
                            'effective_to': emp_work_rec.effective_to,
                            'uploaded_doc': emp_work_rec.uploaded_doc,
                            'emp_work_id': emp_work_rec.id
                        })
                        profile_tech_rec.update({'emp_id': record.emp_prfl_id.id})

                # ------Reject of Family Details--------
                list_1 = []
                list_2 = []
                list_3 = []
                for res in record.emp_family_id:
                    list_1.append(res.id)
                for rec in record.profile_family_details:
                    if rec.family_id:
                        list_2.append(rec.family_id.id)
                    else:
                        list_3.append(rec.id)
                for items in list_1:
                    if items in list_2:
                        profile_family_rec = self.env['kw_emp_profile_family_info'].sudo().search(
                            [('family_id', '=', int(items))])
                        emp_family_rec = self.env['kwemp_family_info'].sudo().search(
                            [('id', '=', int(items))])

                        profile_family_rec.update({
                            'relationship_id': emp_family_rec.relationship_id.id,
                            'name': emp_family_rec.name,
                            'gender': emp_family_rec.gender,
                            'date_of_birth': emp_family_rec.date_of_birth,
                            'dependent': emp_family_rec.dependent
                        })
                for items in list_3:
                    if items not in list_1:
                        profile_family_rec = self.env['kw_emp_profile_family_info'].sudo().search([('id','=',int(items))])
                        profile_family_rec.unlink()
                for items in list_1:
                    if items not in list_2:
                        emp_family = self.env['kwemp_family_info'].sudo().search([('id', '=', int(items))])

                        profile_family_rec = record.emp_prfl_id.family_details_ids.create({
                            'relationship_id': emp_family.relationship_id.id,
                            'name': emp_family.name,
                            'gender': emp_family.gender,
                            'date_of_birth': emp_family.date_of_birth,
                            'dependent': emp_family.dependent,
                            'family_id': emp_family.id
                        })
                        profile_family_rec.update({'emp_family_id': record.emp_prfl_id.id})

                profile.write({
                    'linkedin_url': record.linkedin_url if 'linkedin_url' in record else False,
                    'worked_country_ids': [(6, None, record.worked_country_ids.ids)] if 'worked_country_ids' in record else False,
                    'personal_email': record.personal_email if 'personal_email' in record else False,
                    'mobile_phone': record.mobile_phone if 'mobile_phone' in record else False,
                    'work_email_id': record.work_email_id if 'work_email_id' in record else False,
                    'whatsapp_no': record.whatsapp_no if 'whatsapp_no' in record else False,
                    'extn_no': record.extn_no if 'extn_no' in record else False,
                    'digital_signature': record.digital_signature if 'digital_signature' in record else False,
                    'country_id': record.country_id.id if 'country_id' in record else False,
                    'marital': record.marital.id if 'marital' in record else False,
                    'marital_code': record.marital_code if 'marital_code' in record else False,
                    'wedding_anniversary': record.wedding_anniversary if 'wedding_anniversary' in record else False,
                    'emp_religion': record.emp_religion.id if 'emp_religion' in record else False,
                    'present_addr_street': record.present_addr_street if 'present_addr_street' in record else False,
                    'present_addr_country_id': record.present_addr_country_id.id if 'present_addr_country_id' in record else False,
                    'present_addr_city': record.present_addr_city if 'present_addr_city' in record else False,
                    'present_addr_state_id': record.present_addr_state_id.id if 'present_addr_state_id' in record else False,
                    'present_addr_zip': record.present_addr_zip if 'present_addr_zip' in record else False,
                    'permanent_addr_zip': record.permanent_addr_zip if 'permanent_addr_zip' in record else False,
                    'permanent_addr_country_id': record.permanent_addr_country_id.id if 'permanent_addr_country_id' in record else False,
                    'permanent_addr_street': record.permanent_addr_street if 'permanent_addr_street' in record else False,
                    'permanent_addr_city': record.permanent_addr_city if 'permanent_addr_city' in record else False,
                    'permanent_addr_state_id': record.permanent_addr_state_id.id if 'permanent_addr_state_id' in record else False,
                    'emergency_contact_name': record.emergency_contact_name if 'emergency_contact_name' in record else False,
                    'emergency_address': record.emergency_address if 'emergency_address' in record else False,
                    'emergencye_telephone': record.emergencye_telephone if 'emergencye_telephone' in record else False,
                    'emergency_city': record.emergency_city if 'emergency_city' in record else False,
                    'emergency_country': record.emergency_country.id if 'emergency_country' in record else False,
                    'emergency_state': record.emergency_state.id if 'emergency_state' in record else False,
                    'emergency_mobile_no': record.emergency_mobile_no if 'emergency_mobile_no' in record else False,
                    'blood_group': record.blood_group.id if 'blood_group' in record else False,
                    'experience_sts': record.experience_sts if 'experience_sts' in record else False,
                    'permanent_addr_street2': record.permanent_addr_street2 if 'permanent_addr_street2' in record else False,
                    'present_addr_street2': record.present_addr_street2 if 'present_addr_street2' in record else False,
                    'outlook_pwd': record.outlook_pwd if 'outlook_pwd' in record else False,
                })
            inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_reject_request_email_template')
            profile_manager_group = self.env.ref('kw_emp_profile.group_kw_emp_profile_manager')
            if profile_manager_group.users:
                employee_manager = self.env['hr.employee'].sudo().search([('user_id', 'in', profile_manager_group.users.ids)])
                for rec in employee_manager:
                    if record.write_uid.id == rec.user_id.id:
                        hr_emails = rec.work_email
                        action_taken_by = rec.name
                        inform_template.with_context(email=record.work_email_id, action_taken_by=action_taken_by,
                                                     email_from=hr_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success(message='Profile record rejected.')
            if record.outlook_pwd_boolean == True or record.digital_signature_boolean == True:
                value = {'account_info_sts': False}
            if record.permanent_addr_street2_boolean == True or record.present_addr_street2_boolean == True \
                    or record.personal_email_boolean == True or record.country_id_boolean == True \
                    or record.marital_boolean == True or record.wedding_anniversary_boolean == True \
                    or record.emp_religion_boolean == True or record.mobile_phone_boolean == True \
                    or record.whatsapp_no_boolean == True or record.extn_no_boolean == True \
                    or record.present_addr_street_boolean == True or record.present_addr_country_id_boolean == True \
                    or record.present_addr_city_boolean == True or record.present_addr_state_id_boolean == True \
                    or record.present_addr_zip_boolean == True or record.permanent_addr_state_id_boolean == True \
                    or record.permanent_addr_country_id_boolean == True or record.permanent_addr_city_boolean == True \
                    or record.permanent_addr_zip_boolean == True or record.permanent_addr_street_boolean == True \
                    or record.emergency_city_boolean == True or record.emergency_address_boolean == True \
                    or record.emergencye_telephone_boolean == True or record.emergency_state_boolean == True \
                    or record.emergency_state_boolean == True or record.emergency_mobile_no_boolean == True \
                    or record.emergency_contact_name_boolean == True or record.emergency_country_boolean == True \
                    or record.known_language_ids_boolean == True or record.linkedin_url_boolean == True \
                    or record.blood_group_boolean == True:
                value = {'personalinfo_sts': False}
            if record.identification_ids_boolean == True or record.membership_assc_ids_boolean == True:
                value = {'identification_sts': False}
            if record.educational_details_ids_boolean == True:
                value = {'educational_sts': False}
            if record.technical_skill_ids_boolean == True or record.work_experience_ids_boolean == True \
                    or record.worked_country_ids_boolean == True:
                value = {'workinfo_sts': False}
            if record.family_details_ids_boolean == True:
                value = {'family_sts': False}
            # if record.cv_info_boolean == True:
            #     value = {'cv_sts': False}

            profile = self.env['kw_emp_profile'].sudo().search([('id', '=', record.emp_prfl_id.id)])
        profile.update(value)
        menu_id = self.env['ir.ui.menu'].sudo().search([('name', '=', 'Profile Approval')]).id
        action_id = self.env.ref("kw_emp_profile.profile_new_data_approval_action").id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'self',
        #     'url': f'/web#action={action_id}&model=kw_emp_profile_new_data&view_type=list&menu_id={menu_id}',
        # }

    @api.model
    def create(self, vals):
        emp_rec = super(EmployeeApproval, self).create(vals)
        profile = self.env['kw_emp_profile'].sudo().search([('id', '=', emp_rec.emp_prfl_id.id)])
        profile_manager_group = self.env.ref('kw_emp_profile.group_kw_emp_profile_manager')
        for rec in emp_rec:
            inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_change_request_email_template')
            #  <div style="margin-left: 0.7rem;margin-bottom:1em;font-size: 16px;color:#676767;padding-left: 8px;">
    #        <a href="/web#id=${ctx['rec_id']}&amp;active_id=${ctx['rec_id']}&amp;model=kw_emp_profile_new_data&amp;view_type=form" style="background-color: #875A7B; margin-left: 1rem; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" target="new">
            if profile_manager_group.users:
                employee_manager = self.env['hr.employee'].sudo().search(
                    [('user_id', 'in', profile_manager_group.users.ids)])
                for record in employee_manager:
                    hr_emails = record.work_email
                    action_taken_by = record.name
                    from_mail =  emp_rec.emp_prfl_id.emp_id.work_email
                    action_id = self.env.ref('kw_emp_profile.profile_new_data_approval_action').id
                    inform_template.with_context(email=hr_emails, from_mail=from_mail,view_id=action_id, rec_id=rec.id, by=action_taken_by).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            
        if emp_rec.outlook_pwd_boolean == True or emp_rec.digital_signature_boolean == True:
            profile.write({'account_info_sts': True})
        if emp_rec.permanent_addr_street2_boolean == True or emp_rec.present_addr_street2_boolean == True \
                or emp_rec.personal_email_boolean == True or emp_rec.country_id_boolean == True \
                or emp_rec.marital_boolean == True or emp_rec.wedding_anniversary_boolean == True \
                or emp_rec.emp_religion_boolean == True or emp_rec.mobile_phone_boolean == True \
                or emp_rec.whatsapp_no_boolean == True or emp_rec.extn_no_boolean == True \
                or emp_rec.present_addr_street_boolean == True or emp_rec.present_addr_country_id_boolean == True \
                or emp_rec.present_addr_city_boolean == True or emp_rec.present_addr_state_id_boolean == True \
                or emp_rec.present_addr_zip_boolean == True or emp_rec.permanent_addr_state_id_boolean == True \
                or emp_rec.permanent_addr_country_id_boolean == True or emp_rec.permanent_addr_city_boolean == True \
                or emp_rec.permanent_addr_zip_boolean == True or emp_rec.permanent_addr_street_boolean == True \
                or emp_rec.emergency_city_boolean == True or emp_rec.emergency_address_boolean == True \
                or emp_rec.emergencye_telephone_boolean == True or emp_rec.emergency_state_boolean == True \
                or emp_rec.emergency_state_boolean == True or emp_rec.emergency_mobile_no_boolean == True \
                or emp_rec.emergency_contact_name_boolean == True or emp_rec.emergency_country_boolean == True \
                or emp_rec.known_language_ids_boolean == True or emp_rec.linkedin_url_boolean == True \
                or emp_rec.blood_group_boolean == True:
            profile.write({'personalinfo_sts': True})
        if emp_rec.identification_ids_boolean == True or emp_rec.membership_assc_ids_boolean == True:
            profile.write({'identification_sts': True})
        if emp_rec.educational_details_ids_boolean == True:
            profile.write({'educational_sts': True})
        if emp_rec.technical_skill_ids_boolean == True or emp_rec.work_experience_ids_boolean == True \
                or emp_rec.worked_country_ids_boolean == True:
            profile.write({'workinfo_sts': True})
        if emp_rec.family_details_ids_boolean == True:
            profile.write({'family_sts': True})
        # if emp_rec.cv_info_boolean == True:
        #     profile.write({'cv_sts': True})
            