from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
import re

class FormIo(models.Model):
    _inherit='formio.form'

    @api.model
    def create(self, vals):
        res = super(FormIo, self).create(vals)
        dict = self.submission_data
        res = json.loads(dict)
        advertisement_id = 0
        job_id = 0
        name = ''
        for i in res:
            if i == 'advertisementNo':
                advertisement_id = res[i]['id']
            if i == 'category_id':
                category_id = res[i]['id']
            if i == 'religion_id':
                religion_id = res[i]['id']
            if i == 'title':
                title = res[i]['id']
            if i == 'job_id':
                job_id = res[i]['id']
            if i == 'aadhar_no':
                aadhar_no = res[i]
            if i == 'pan_no':
                pan_no = res[i]
            if i == 'personal_email':
                personal_email = res[i]
            if i == 'modeOfrecruitment':
                recruitment_type = res[i]
            if i == 'employee_type':
                employee_type = res[i]
            if i == 'blood_group':
                blood_group = res[i]
            # if i == 'uploadImage':
            #     upload_image = res[i]
            if i == 'applicantName':
                name = res[i]
            # if i == 'applicantName1':
            #     fnmae = res[i]
            # if i == 'applicantName2':
            #     mname = res[i]
            if i == 'dob':
                dob = res[i]
            if i == 'gender':
                gende = res[i]
        stage_id = self.env['hr.recruitment.stage'].search([('sequence', '=', 1)], limit=1)
        branch_id = self.env['res.branch'].search([('id', '=', 1)], limit=1)
        struct_id = self.env['hr.payroll.structure'].search([('id', '=', 1)], limit=1)
        pay_level_id = self.env['hr.payslip.paylevel'].search([], limit=1)
        print("==========Stage==============", stage_id.id)
        print("==========branch_id==============", branch_id.id)
        print("==========struct_id==============", struct_id.id)
        print("==========pay_level_id==============", pay_level_id.id)
        print("==========Advertisement==============", advertisement_id)
        print("==========Job ID==============", job_id)
        print("==========Name==============", name)
        print("==========category_id ID==============", category_id)
        print("==========religion_id ID==============", religion_id)
        print("==========title ID==============", title)
        print("==========aadhar_no ID==============", aadhar_no)
        print("==========pan_no==============", pan_no)
        print("==========personal_email==============", personal_email)
        print("==========employee_type==============", employee_type)
        print("==========recruitment_type==============", recruitment_type)
        print("==========blood_group==============", blood_group)
        print("==========dob==============", dob)
        print("==========gende==============", gende)
        create_applicant = self.env['hr.applicant'].sudo().create(
            {
                'stage_id': stage_id.id,
                'branch_id': branch_id.id,
                'struct_id': struct_id.id,
                'pay_level_id': pay_level_id.id,
                'title': title,
                'name': name,
                'employee_type': employee_type,
                'recruitment_type': recruitment_type,
                'religion_id': religion_id,
                'category_id': category_id,
                'aadhar_no': aadhar_no,
                'pan_no': pan_no,
                'blood_group': blood_group,
                'personal_email': personal_email,
                'advertisement_id': advertisement_id,
                'job_id': job_id,
                # 'dob': dob,
            }
        )
        print("==========================Applicant===============================", create_applicant.id)
        return res

    #
    # @api.onchange('state')
    # @api.constrains('state')
    # def create_applicant_from_form(self):
    #     if self.state == 'COMPLETE':
    #         dict = self.submission_data
    #         res = json.loads(dict)
    #         advertisement_id = 0
    #         job_id = 0
    #         name = ''
    #         for i in res:
    #             if i == 'advertisementNo':
    #                 advertisement_id = res[i]['id']
    #             if i == 'category_id':
    #                 category_id = res[i]['id']
    #             if i == 'religion_id':
    #                 religion_id = res[i]['id']
    #             if i == 'title':
    #                 title = res[i]['id']
    #             if i == 'job_id':
    #                 job_id = res[i]['id']
    #             if i == 'aadhar_no':
    #                 aadhar_no = res[i]
    #             if i == 'pan_no':
    #                 pan_no = res[i]
    #             if i == 'personal_email':
    #                 personal_email = res[i]
    #             if i == 'modeOfrecruitment':
    #                 recruitment_type = res[i]
    #             if i == 'employee_type':
    #                 employee_type = res[i]
    #             if i == 'blood_group':
    #                 blood_group = res[i]
    #             # if i == 'uploadImage':
    #             #     upload_image = res[i]
    #             if i == 'applicantName':
    #                 name = res[i]
    #             # if i == 'applicantName1':
    #             #     fnmae = res[i]
    #             # if i == 'applicantName2':
    #             #     mname = res[i]
    #             if i == 'dob':
    #                 dob = res[i]
    #             if i == 'gender':
    #                 gende = res[i]
    #         stage_id= self.env['hr.recruitment.stage'].search([('sequence','=',1)], limit=1)
    #         branch_id= self.env['res.branch'].search([('id','=',1)], limit=1)
    #         struct_id= self.env['hr.payroll.structure'].search([('id','=',1)], limit=1)
    #         pay_level_id= self.env['hr.payslip.paylevel'].search([],limit=1)
    #         print("==========Stage==============", stage_id.id)
    #         print("==========branch_id==============", branch_id.id)
    #         print("==========struct_id==============", struct_id.id)
    #         print("==========pay_level_id==============", pay_level_id.id)
    #         print("==========Advertisement==============", advertisement_id)
    #         print("==========Job ID==============", job_id)
    #         print("==========Name==============", name)
    #         print("==========category_id ID==============", category_id)
    #         print("==========religion_id ID==============", religion_id)
    #         print("==========title ID==============", title)
    #         print("==========aadhar_no ID==============", aadhar_no)
    #         print("==========pan_no==============", pan_no)
    #         print("==========personal_email==============", personal_email)
    #         print("==========employee_type==============", employee_type)
    #         print("==========recruitment_type==============", recruitment_type)
    #         print("==========blood_group==============", blood_group)
    #         print("==========dob==============", dob)
    #         print("==========gende==============", gende)
    #         create_applicant = self.env['hr.applicant'].sudo().create(
    #             {
    #                 'stage_id': stage_id.id,
    #                 'branch_id': branch_id.id,
    #                 'struct_id': struct_id.id,
    #                 'pay_level_id': pay_level_id.id,
    #                 'title': title,
    #                 'name': name,
    #                 'employee_type': employee_type,
    #                 'recruitment_type': recruitment_type,
    #                 'religion_id': religion_id,
    #                 'category_id': category_id,
    #                 'aadhar_no': aadhar_no,
    #                 'pan_no': pan_no,
    #                 'blood_group': blood_group,
    #                 'personal_email': personal_email,
    #                 'advertisement_id': advertisement_id,
    #                 'job_id': job_id,
    #                 # 'dob': dob,
    #             }
    #         )
    #         print("==========================Applicant===============================", create_applicant.id)