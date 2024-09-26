# *******************************************************************************************************************
#  File Name             :   kw_sync_hr_employee.py
#  Description           :   This model is used to store log data for Employee and sync all the Employee related data to Kwantify.
#  Created by            :   Abhijit Swain
#  Created On            :   02-08-2020
#  Modified by           :   Abhijit Swain
#  Modified On           :   --
#  Modification History  :   Added Work Experience Sync data
# *******************************************************************************************************************

from odoo import models, fields, api
import requests, json
from datetime import date, datetime
import datetime
from dateutil.tz import tzutc
from odoo.exceptions import ValidationError
from odoo.http import request
import ast

cur_dtime = datetime.datetime.now()
cur_dt = datetime.date(year=cur_dtime.year, month=cur_dtime.month, day=cur_dtime.day)
gender_dict = {"male": "M", "female": "F"}
religion_dict = {"Hindu": "Hindu", "Muslim": "Muslim", "Sikhism": "Sikh"}
maritalSet = {'M', 'U'}


# Code Description
# Code 1 - Add user data will be sent to the Kwantify side
# Code 2 - Identification data will be sent to the Kwantify side
# Code 3 - Personal Info data will be sent to the Kwantify side
# Code 4 - Educational data will be sent to the Kwantify Side
# Code 5 - Work Experience data will be sent to the Kwantify side


class kw_sync_hr_employee(models.Model):
    _inherit = 'hr.employee'

    need_sync = fields.Boolean(string="Create in Tendrils?")
    # display_name = fields.Char(compute='display_name')

    # @api.constrains('new_ra_id')
    # def _check_parent_id(self):
    #     for employee in self:
    #         if not employee._check_recursion():
    #             raise ValidationError('Recurrsive RA can not be created')

    # def display_name(self):
    #     for record in self:
    #         record.display_name = f"{name}({emp_code})"

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'hr.employee'), ('rec_id', '=', record.id)])
            if log_record:
                status = log_record.mapped('status')
                if 0 in status:
                    record.sync_status = '1'
                else:
                    record.sync_status = '2'
            else:
                record.sync_status = '0'

    # @api.model
    # @api.onchange('new_ra_id')
    # def _check_new_ra(self):
    #     if self.new_ra_id.id == self.parent_id.id :
    #         raise ValidationError('New RA Must Not Be Same With Current RA')
    #     if self.new_ra_id.name == self.name :
    #         raise ValidationError('New RA Must Not Be Same With Employee Name.')

    @api.model
    def action_sync_employee(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')
        employee_rec = self.env['kw_emp_sync_log'].sudo().search([('model_id', '=', 'hr.employee'), ('status', '=', 0)],
                                                                 limit=25)
        addUserDict = {}
        employee_update_url = self.env['ir.config_parameter'].sudo().get_param('kw_employee_update_sync')
        employee_user_update_url = employee_update_url + 'Update_User_Details'

        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        employeeurl = parameterurl + 'AddNewUserDetails'
        personalinfourl = parameterurl + 'AddPersonalInfoDetails'
        identificationurl = parameterurl + 'AddIdentification'
        expurl = parameterurl + 'AddWorkExp'
        educationalurl = parameterurl + 'AddEducationTrainingDetails'

        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        # cur_k=self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        # x = cur_kw_id.kw_id
        emp_search = self.env['hr.employee'].sudo()
        kw_integration_log = self.env['kw_kwantify_integration_log'].sudo()
        attTypDic = {'portal': '0', 'bio_metric': '1', 'manual': '3'}

        # # for add update user sync data
        for rec in employee_rec:
            employee_record = emp_search.sudo().browse(rec.rec_id)
            emp_kw_id = employee_record.kw_id  # "0" if employee_record.kw_id == 0 else
            # if rec.code == 1 and rec.updated_status == True:
            if rec.code == 1 and emp_kw_id > 0:
                employee_update_sync = {}
                # print('update employee call from button', employee_update_sync)
                # emp_search = self.env['hr.employee']

                if employee_record.no_attendance is False:
                    attTypDic = {'portal': '0', 'bio_metric': '1', 'manual': '3'}
                    attendance_rec = employee_record.attendance_mode_ids.mapped('alias')
                    bothLis = ['portal', 'bio_metric']
                    if len(attendance_rec) == 2:
                        if all(item in attendance_rec for item in bothLis):
                            employee_update_sync['AttendanceMode'] = "2"
                    else:
                        employee_update_sync['AttendanceMode'] = attTypDic.get(str(attendance_rec[0]))
                else:
                    employee_update_sync['AttendanceMode'] = "0"

                employee_update_sync['Fullname'] = employee_record.name
                employee_update_sync['Email'] = employee_record.work_email
                if employee_record.practise:
                    employee_update_sync['DepartmentId'] = str(employee_record.practise.kw_id)
                elif employee_record.section:
                    employee_update_sync['DepartmentId'] = str(employee_record.section.kw_id)
                elif employee_record.division:
                    employee_update_sync['DepartmentId'] = str(employee_record.division.kw_id)
                else:
                    employee_update_sync['DepartmentId'] = str(employee_record.department_id.kw_id)

                employee_update_sync['DesgId'] = str(employee_record.job_id.kw_id)
                employee_update_sync['GradeId'] = str(self.env['kwemp_grade'].sudo().search(
                    ['&', ('grade_id', '=', employee_record.grade.id),
                        ('band_id', '=', employee_record.emp_band.id)]).kw_id)
                employee_update_sync['Location'] = str(employee_record.base_branch_id.location.kw_id)
                employee_update_sync['DOJ'] = employee_record.date_of_joining.strftime('%d-%b-%y')
                employee_update_sync['ProbetionComplitionDate'] = employee_record.date_of_completed_probation.strftime(
                    '%d-%b-%y') if employee_record.on_probation else employee_record.date_of_joining.strftime(
                    '%d-%b-%y')
                employee_update_sync['ConfirmationStatus'] = "1" if employee_record.on_probation else "0"
                employee_update_sync['DateofLeaving'] = employee_record.last_working_day.strftime('%d-%b-%y') if employee_record.last_working_day  else ''

                employee_update_sync['Religion'] = religion_dict[employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"

                employee_update_sync['Gender'] = gender_dict[employee_record.gender] if employee_record.gender in gender_dict else ""
                employee_update_sync['IsAdmin'] = "no" 
                employee_update_sync['Attendance'] = "No" if employee_record.no_attendance == True else "Yes"

                employee_update_sync['OfcId'] = str(employee_record.base_branch_id.kw_id)
                employee_update_sync['RptDept'] = str(employee_record.parent_id.department_id.kw_id)
                employee_update_sync['RptAuthority'] = str(employee_record.parent_id.kw_id)
                employee_update_sync['DOB'] = employee_record.birthday.strftime('%d-%b-%y') if employee_record.birthday else ""
                employee_update_sync['ActiveStatus'] = "Yes" if employee_record.active == True else "No"
                employee_update_sync['UserId'] = "0" if employee_record.kw_id == 0 else employee_record.kw_id
                employee_update_sync['EmploymentType'] = employee_record.employement_type.code
                employee_update_sync['ShiftId'] = str(employee_record.resource_calendar_id.kw_id)
                employee_update_sync['EmployeeRole'] = str(employee_record.emp_role.kw_id)
                employee_update_sync['EmployeeCategory'] = str(employee_record.emp_category.kw_id)
                employee_update_sync['EmpCode'] = employee_record.emp_code
                # employee_update_sync['HierarchyID'] = '--'
                # employee_update_sync['LevelID'] = '--'
                employee_update_sync['Int_SbuID'] = employee_record.sbu_master_id.kw_id if employee_record.sbu_master_id and employee_record.sbu_master_id.kw_id else ''
                employee_update_sync['PhotoFile'] = employee_record.image_url
                # print("employee_update_sync >>> ", employee_update_sync)
                resp = requests.post(employee_user_update_url, headers=header, data=json.dumps(employee_update_sync))
                json_data = json.dumps(resp.json())
                json_record = json.loads(json_data)

                # print('json record>>>>>>', json_record, type(json_record))

                if resp.status_code == 200 or json_record[0]['Status'] == '2':
                    if json_record[0]['Status'] == '2':
                        rec.write({'json_data': employee_update_sync,
                                   'status': 1,
                                   'response_result': resp.json()})
                        kw_integration_log.create(
                            {'name': 'Employee Update User Sync Data',
                                'new_record_log': employee_update_sync,
                                'request_params': employee_user_update_url,
                                'response_result': resp.json()})
                    else:
                        rec.write({'json_data': employee_update_sync,
                                   'status': 0,
                                   'response_result': resp.json()})
                        kw_integration_log.create(
                            {'name': 'Employee Update User Sync Data',
                                'new_record_log': employee_update_sync,
                                'request_params': employee_user_update_url,
                                'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({'json_data': employee_update_sync,
                               'status': 0,
                               'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create(
                        {'name': 'Employee Update User Sync Data',
                         'new_record_log': employee_update_sync,
                         'request_params': employee_user_update_url,
                         'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

            if rec.code == 1 and emp_kw_id == 0:
                # employee_record = emp_search.search([('id', '=', rec.rec_id)])
                if employee_record.no_attendance == False:
                    attendance_rec = employee_record.attendance_mode_ids.mapped('alias')
                    bothLis = ['portal', 'bio_metric']
                    if len(attendance_rec) == 2:
                        if all(item in attendance_rec for item in bothLis):
                            addUserDict['AttendanceType'] = "2"
                    else:
                        addUserDict['AttendanceType'] = attTypDic.get(str(attendance_rec[0]))
                else:
                    addUserDict['AttendanceType'] = "0"

                if employee_record.practise:
                    addUserDict['UserDept'] = str(employee_record.practise.kw_id)
                elif employee_record.section:
                    addUserDict['UserDept'] = str(employee_record.section.kw_id)
                elif employee_record.division:
                    addUserDict['UserDept'] = str(employee_record.division.kw_id)
                else:
                    addUserDict['UserDept'] = str(employee_record.department_id.kw_id)

                addUserDict['Attendance'] = "No" if employee_record.no_attendance == True else "Yes"
                addUserDict['ConfStatus'] = "1" if employee_record.on_probation else "0"
                addUserDict['CreatedBy'] = "224"  # To be sent static as created by is odoo bot
                addUserDict['DateOfBirth'] = employee_record.birthday.strftime('%d-%b-%y')
                addUserDict['dateOfjoin'] = employee_record.date_of_joining.strftime('%d-%b-%y')
                addUserDict['Designation'] = str(employee_record.job_id.kw_id)
                addUserDict['DomainName'] = employee_record.domain_login_id if employee_record.domain_login_id else ''
                addUserDict['IsAdmin'] = 'no'  # To be sent static value 0
                addUserDict['EmailId'] = employee_record.work_email
                addUserDict['EmployeeCategory'] = str(employee_record.emp_category.kw_id)
                addUserDict['EmployeeType'] = str(employee_record.emp_role.kw_id)
                addUserDict['EmpType'] = employee_record.employement_type.code
                addUserDict['Fullname'] = employee_record.name
                addUserDict['Gender'] = gender_dict[employee_record.gender] if employee_record.gender in gender_dict else ""
                addUserDict['Grade'] = str(self.env['kwemp_grade'].sudo().search(
                    ['&', ('grade_id', '=', employee_record.grade.id),
                     ('band_id', '=', employee_record.emp_band.id)]).kw_id)

                addUserDict['MDate'] = employee_record.wedding_anniversary.strftime('%d-%b-%y') if employee_record.wedding_anniversary else "1-Jan-00"
                addUserDict['ModuleId'] = "0"  # To be sent static value 0
                addUserDict['OfficeType'] = str(employee_record.base_branch_id.kw_id)
                addUserDict['Password'] = "5F4DCC3B5AA765D61D8327DEB882CF99"  # employee_record.conv_pwd Password to be sent static
                addUserDict['PhotoFileName'] = employee_record.image_url
                addUserDict['PositionId'] = str(employee_record.job_id.kw_id)
                addUserDict['ProbComplDate'] = employee_record.date_of_completed_probation.strftime('%d-%b-%y') if employee_record.on_probation else employee_record.date_of_joining.strftime('%d-%b-%y')
                addUserDict['Religion'] = religion_dict[employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"
                addUserDict['repoauthority2'] = str(employee_record.coach_id.kw_id)
                addUserDict['ReportingAuthority'] = str(employee_record.parent_id.kw_id)
                addUserDict['Shift'] = str(employee_record.resource_calendar_id.kw_id)
                addUserDict['UserId'] = "0" if employee_record.kw_id == 0 else str(employee_record.kw_id)
                addUserDict['UserLocation'] = str(employee_record.base_branch_id.location.kw_id)
                addUserDict['UserName'] = employee_record.user_id.login
                addUserDict['EmpCode'] = employee_record.emp_code

                addUserDict['Payroll'] = 'Yes' if employee_record.enable_payroll == 'yes' else 'No'
                addUserDict['Gratuity'] = 'Yes' if employee_record.enable_gratuity == 'yes' else 'No'
                addUserDict['Bankname'] = ''
                addUserDict['AccountNo'] = ''
                addUserDict['EPF'] = '0'
                addUserDict['CTC'] = '0'
                addUserDict['LatestCTC'] = '0'
                addUserDict['HRA'] = '0'
                addUserDict['Conveyance'] = '0'
                addUserDict['MedicalReum'] = '0'
                addUserDict['Transport'] = '0'
                addUserDict['ProdBonous'] = '0'
                addUserDict['ComBonous'] = '0'
                addUserDict['BasicSal'] = '0'
                addUserDict['BillingAmt'] = '0'
                # addUserDict['FunctionArea'] = "3"
                # addUserDict['groupid'] = "18"
                # if employee_record.emp_refered.kw_id > 0:
                #     addUserDict['RefMode'] = employee_record.emp_refered.kw_id
                # if employee_record.emp_refered.code == 'employee':
                #     addUserDict['RefferedBy'] = str(employee_record.emp_employee_referred.name)
                addUserDict['Int_SbuID'] = employee_record.sbu_master_id.kw_id if employee_record.sbu_master_id and employee_record.sbu_master_id.kw_id else ''

                addUserDict['RefMode'] = employee_record.emp_refered.kw_id if employee_record.emp_refered.kw_id > 0 else ''
                # addUserDict['RefferedBy'] = str(employee_record.emp_employee_referred.name) if employee_record.emp_refered.code == 'employee' else ''
                if employee_record.emp_refered.code == 'employee':
                    addUserDict['RefferedBy'] = str(employee_record.emp_employee_referred.kw_id)
                elif employee_record.emp_refered.code == 'job':
                    addUserDict['RefferedBy'] = 1
                elif employee_record.emp_refered.code == 'exemployee':
                    emp_data = emp_search.sudo().search([('active', '=', False), ('id', '=', rec.rec_id)])
                    addUserDict['RefferedBy'] = str(emp_data.kw_id)
                elif employee_record.emp_refered.code == 'client':
                    addUserDict['RefferedBy'] = str(employee_record.emp_reference)
                elif employee_record.emp_refered.code == 'website':
                    addUserDict['RefferedBy'] = 'CSM Career'
                elif employee_record.emp_refered.code == 'career':
                    addUserDict['RefferedBy'] = 'career@csm.co.in'
                elif employee_record.emp_refered.code == 'walkindrive':
                    addUserDict['RefferedBy'] = str(employee_record.emp_reference_walkindrive)
                elif employee_record.emp_refered.code == 'institute':
                    addUserDict['RefferedBy'] = str(employee_record.emp_institute_id.name)
                elif employee_record.emp_refered.code == 'social':
                    addUserDict['RefferedBy'] = str(employee_record.emp_media_id.name)
                elif employee_record.emp_refered.code == 'csmdatabase':
                    addUserDict['RefferedBy'] = str(employee_record.emp_reference)
                elif employee_record.emp_refered.code == 'jobfair':
                    addUserDict['RefferedBy'] = str(employee_record.emp_reference_job_fair)
                elif employee_record.emp_refered.code == 'printmedia':
                    addUserDict['RefferedBy'] = str(employee_record.emp_reference_print_media)
                elif employee_record.emp_refered.code == 'consultancy':
                    addUserDict['RefferedBy'] = str(employee_record.emp_consultancy_id.name)
                elif employee_record.emp_refered.code == 'partners':
                    addUserDict['RefferedBy'] = str(employee_record.emp_service_partner_id.name)
                else:
                    addUserDict['RefferedBy'] = ''

                resp = requests.post(employeeurl, headers=header, data=json.dumps(addUserDict))
                j_data = json.dumps(resp.json())
                json_record = json.loads(j_data)

                if addUserDict['UserId'] == "0":
                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            employee_record.write({'kw_id': json_record['id']})
                            rec.write({'json_data': addUserDict, 'status': 1, 'response_result': resp.json()})
                            kw_integration_log.create(
                                {'name': 'Employee Add User Sync Data',
                                 'new_record_log': addUserDict,
                                 'request_params': employeeurl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': addUserDict, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Add User Sync Data',
                                 'new_record_log': addUserDict,
                                 'request_params': employeeurl,
                                 'response_result': resp.json()})

                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                     response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': addUserDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Add User Sync Data',
                                                                               'new_record_log': addUserDict,
                                                                               'request_params': employeeurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            rec.write({'json_data': addUserDict, 'status': 1, 'response_result': resp.json()})
                            kw_integration_log.create(
                                {'name': 'Employee Add User Sync Data',
                                 'new_record_log': addUserDict,
                                 'request_params': employeeurl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': addUserDict, 'status': 0, 'response_result': resp.json()})
                            kw_integration_log.create(
                                {'name': 'Employee Add User Sync Data',
                                 'new_record_log': addUserDict,
                                 'request_params': employeeurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                     response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': addUserDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Add User Sync Data',
                                                                               'new_record_log': addUserDict,
                                                                               'request_params': employeeurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

            if rec.code == 3:
                personalDict = {}

                employee_record = self.env['hr.employee'].sudo().search([('id', '=', rec.rec_id)])
                # print(f"employee record {employee_record.kw_id}")
                if employee_record.kw_id != 0:
                    personalDict['ActionType'] = 'DPI'
                    personalDict['CreatedBy'] = str(employee_record.kw_id)
                    personalDict['Directory'] = '122555625'
                    personalDict['EmailId'] = employee_record.personal_email
                    personalDict['EmgrAddress'] = '--'
                    personalDict['EmgrCity'] = '--'
                    personalDict['EmgrState'] = '--'
                    personalDict['EmgrTelNo'] = '--'
                    personalDict['EmgrContactPerson'] = employee_record.emergency_contact
                    personalDict['EmgrCountry'] = '1'  # passed static as error is displaying without country id
                    personalDict['EmgrMobile'] = employee_record.emergency_phone
                    personalDict['MaritalSts'] = employee_record.marital_sts.code if employee_record.marital_sts.code in maritalSet else "O"
                    personalDict['MobileNumber'] = employee_record.mobile_phone
                    personalDict['Nationality'] = "Indian" if employee_record.country_id.id == 104 else "Other"
                    personalDict['OfficeExetension'] = employee_record.epbx_no if employee_record.epbx_no else ''
                    personalDict['OffPreTelephoneNo'] = '--'
                    personalDict['PermanentAddress'] = employee_record.permanent_addr_street
                    personalDict['PermanentCity'] = employee_record.permanent_addr_city
                    personalDict['PermanentCountry'] = str(employee_record.permanent_addr_country_id.kw_id)
                    personalDict['PermanentState'] = str(employee_record.permanent_addr_state_id.name)
                    personalDict['PerTelephoneNo'] = '--'
                    personalDict['PresentAddress'] = employee_record.present_addr_street
                    personalDict['PresentCity'] = employee_record.present_addr_city
                    personalDict['PresentCountry'] = str(employee_record.present_addr_country_id.kw_id)
                    personalDict['PresentState'] = str(employee_record.present_addr_state_id.name)
                    personalDict['Religion'] = religion_dict[employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"
                    personalDict['ResPreTelephoneNo1'] = '--'
                    personalDict['UserId'] = str(employee_record.kw_id)
                    personalDict['LinkedInURL'] = str(employee_record.linkedin_url)
                    personalDict['Ldata'] = []
                    statDict = {'good': "1", "fair": "2", "slight": "3"}
                    if employee_record.known_language_ids:
                        for r in employee_record.known_language_ids:
                            val = {'LNID': str(r.language_id.kw_id),
                                   'RNID': statDict[r.reading_status],
                                   'WNID': statDict[r.writing_status],
                                   'SPID': statDict[r.speaking_status],
                                   'UNID': statDict[r.understanding_status]
                                   }
                            personalDict['Ldata'].append(val)

                    resp = requests.post(personalinfourl, headers=header, data=json.dumps(personalDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)
                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            rec.write({'json_data': personalDict, 'status': 1, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Personal information Sync Data',
                                 'new_record_log': personalDict,
                                 'request_params': personalinfourl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': personalDict, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Personal information Sync Data',
                                 'new_record_log': personalDict,
                                 'request_params': personalinfourl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id, response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': personalDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Employee Personal information Sync Data',
                             'new_record_log': personalDict,
                             'request_params': personalinfourl,
                             'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

            if rec.code == 2:
                identificationDict = {}
                employee_record = self.env['hr.employee'].sudo().search([('id', '=', rec.rec_id)])
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                if employee_record.kw_id != 0:
                    identificationDict['ActionCode'] = 'AID'
                    identificationDict['BloodGroup'] = employee_record.blood_group.name
                    identificationDict['NoofRecord'] = str(len(employee_record.identification_ids)) if len(employee_record.identification_ids) > 0 else '0'
                    identificationDict['CreatedBy'] = str(employee_record.kw_id)
                    identificationDict['UserId'] = str(employee_record.kw_id)
                    identificationDict['MSADet'] = []
                    if employee_record.identification_ids:
                        for r in employee_record.identification_ids:
                            attachment_data = self.env['ir.attachment'].sudo().search(
                                [('res_id', '=', r.id),
                                 ('res_model', '=', 'kwemp_identity_docs'),
                                 ('res_field', '=', 'uploaded_doc')])
                            if attachment_data:
                                attachment_data.write({'public': True})
                            val = {
                                'IDTYPEID': r.name,
                                'DOCNO': r.doc_number,
                                'DTISSUE': r.date_of_issue.strftime('%d-%b-%y') if r.date_of_issue else "1-Jan-00",
                                'DTEXP': r.date_of_expiry.strftime('%d-%b-%y') if r.date_of_expiry else "1-Jan-00",
                                'URL': f"{base_url}/web/content/{attachment_data.id}" if attachment_data else '',
                                'DOCUMENTNAME': r.doc_file_name if r.doc_file_name else 'Demo.png',
                                'RENAPPLIED': 'Y' if r.renewal_sts else 'N'
                            }
                            identificationDict['MSADet'].append(val)

                    # print(identificationDict)

                    resp = requests.post(identificationurl, headers=header, data=json.dumps(identificationDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            rec.write({'json_data': identificationDict, 'status': 1, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Identification information Sync Data',
                                 'new_record_log': identificationDict,
                                 'request_params': identificationurl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': identificationDict, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Identification information Sync Data',
                                 'new_record_log': identificationDict,
                                 'request_params': identificationurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                     response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': identificationDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Employee Identification information Sync Data',
                             'new_record_log': identificationDict,
                             'request_params': identificationurl,
                             'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

            if rec.code == 5:
                workExpDict = {}
                profDict = {'1': 'Excellent', '2': 'Good', '3': 'Average'}
                employee_record = self.env['hr.employee'].sudo().search([('id', '=', rec.rec_id)])
                if employee_record.kw_id != 0:
                    workExpDict['CreatedBy'] = str(employee_record.kw_id)
                    workExpDict['UserId'] = str(employee_record.kw_id)
                    workExpDict['ActionCode'] = 'AWTD'
                    workExpDict['LWkEData'] = []
                    workExpDict['NoofRecord'] = str(len(employee_record.technical_skill_ids)) if len(
                        employee_record.technical_skill_ids) > 0 else '0'
                    if employee_record.work_experience_ids:
                        experience_country_rec = employee_record.work_experience_ids.mapped('country_id.kw_id')
                        experience_country = ",".join(str(x) for x in experience_country_rec)

                        for r in employee_record.work_experience_ids:
                            val = {
                                'COUNTRYNAME': r.country_id.name,
                                'COUNTRYID': str(r.country_id.kw_id),
                                'WORKEXPID': '0',
                                'ORGNAME': r.name,
                                'JOBPROFILE': r.designation_name,
                                'ORGTYPENAME': r.organization_type.name,
                                'ORGTYPEID': str(r.organization_type.kw_id),
                                'INDTYPENAME': r.industry_type.name,
                                'INDTYPEID': str(r.industry_type.kw_id),
                                'EFFROM': r.effective_from.strftime('%d-%b-%Y'),
                                'EFTO': r.effective_to.strftime('%d-%b-%Y'),
                                'DOC': r.doc_file_name if r.doc_file_name else 'Demo.png'
                            }
                            workExpDict['LWkEData'].append(val)

                    workExpDict['PermanentCountry'] = experience_country

                    workExpDict['LTsQData'] = []
                    if employee_record.technical_skill_ids:
                        for r in employee_record.technical_skill_ids:
                            val = {
                                'TECID': '0',
                                'CATNAME': r.category_id.name,
                                'CATID': str(r.category_id.kw_id),
                                'SKILLNAME': r.skill_id.name,
                                'SKILLID': str(r.skill_id.kw_id),
                                'PROFILVLNAME': profDict.get(r.proficiency),
                                'PROFILVL': r.proficiency
                            }
                            workExpDict['LTsQData'].append(val)

                    resp = requests.post(expurl, headers=header, data=json.dumps(workExpDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            rec.write({'json_data': workExpDict, 'status': 1, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Work Experience Information Sync Data',
                                 'new_record_log': workExpDict,
                                 'request_params': expurl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': workExpDict, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Work Experience Information Sync Data',
                                 'new_record_log': workExpDict,
                                 'request_params': expurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                     response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': workExpDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Employee Work Experience Information Sync Data',
                             'new_record_log': workExpDict,
                             'request_params': expurl,
                             'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

            if rec.code == 4:
                educationTrainingDict = {}
                employee_record = self.env['hr.employee'].sudo().search([('id', '=', rec.rec_id)])
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                if employee_record.kw_id != 0:
                    educationTrainingDict['UserId'] = str(employee_record.kw_id)
                    educationTrainingDict['LEddata'] = [
                        {"SID": "0", "PID": "0", "DID": "0", "QID": "0", "PRID": "0", "AID": "0", "RID": "0",
                         "TID": "0"}]  # To be sent static
                    educationTrainingDict['LQudata'] = []
                    rcount = 1
                    edu_length = 0
                    if employee_record.educational_details_ids:
                        str_passing_details = ""
                        for r in employee_record.educational_details_ids:
                            if r.course_type == '1':
                                edu_length += 1
                            if r.passing_details:
                                for p_detail in r.passing_details:
                                    str_passing_details += str(p_detail.kw_id) + ','
                            attachment_data = self.env['ir.attachment'].sudo().search(
                                [('res_id', '=', r.id),
                                 ('res_model', '=', 'kwemp_educational_qualification'),
                                 ('res_field', '=', 'uploaded_doc')])
                            if attachment_data:
                                attachment_data.write({'public': True})
                            val = {
                                'INT_QUALIF_ID': '0',
                                'INT_STREAM_ID': str(r.stream_id.kw_id),
                                'VCH_BOARD_NAME': r.university_name.name,
                                'VCH_PASSING_DTLS': str_passing_details if r.passing_details else 'NA',
                                'INT_PASSING_YEAR': r.passing_year,
                                'VCH_DIVISION_GRADE': r.division,
                                'DEC_PERCENTAGE': str(r.marks_obtained),
                                'INT_PQSTREAM_ID': '0',
                                'INT_CERTTYPE_ID': '0',
                                'INT_POSITION': str(rcount),
                                'FILE_NAME': r.doc_file_name if r.doc_file_name else 'Demo.png',
                                'URL': f"{base_url}/web/content/{attachment_data.id}" if attachment_data else '',
                                'VCH_INNERACTION': 'Y'
                            }
                            rcount += 1
                            educationTrainingDict['LQudata'].append(val)

                    educationTrainingDict['strMetricStatus'] = 'yes' if edu_length >= 1 else 'no'
                    educationTrainingDict['strPlus2Status'] = 'yes' if edu_length >= 2 else 'no'
                    educationTrainingDict['strPlus3Status'] = 'yes' if edu_length >= 3 else 'no'

                    resp = requests.post(educationalurl, headers=header, data=json.dumps(educationTrainingDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)
                    if resp.status_code == 200:
                        if json_record['status'] == 1:
                            rec.write({'json_data': educationTrainingDict, 'status': 1, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Educational information Sync Data',
                                 'new_record_log': educationTrainingDict,
                                 'request_params': educationalurl,
                                 'response_result': resp.json()})
                        else:
                            rec.write({'json_data': educationTrainingDict, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Employee Educational information Sync Data',
                                 'new_record_log': educationTrainingDict,
                                 'request_params': educationalurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                     response_result=resp.json()).send_mail(rec.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        rec.write({'json_data': educationTrainingDict, 'status': 0, 'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Employee Educational information Sync Data',
                             'new_record_log': educationTrainingDict,
                             'request_params': educationalurl,
                             'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

    """#Check Employee Group"""

    @api.model
    def check_employee_group(self, args):
        menu_id = args.get("menu_id", False)
        employee_menu_id = self.env['ir.ui.menu'].sudo().search([('name', '=', 'Employees')],limit=1)
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        # print("menu_id==",menu_id)
        # print("employee_menu_id.id===",employee_menu_id.id)
        if u_id.has_group('hr.group_hr_manager') and int(menu_id) == int(employee_menu_id.id):
            return '1'
        else:
            return '0'

    """#Override Create method for employee"""
    @api.model
    def create(self, vals):
        employee_record = super(kw_sync_hr_employee, self).create(vals)
        # Create 4 records in log model with code,1-Add User,2-Identification Info,3-Personal Info,4-Educational Info.
        # Data will be synced to Kwantify from the Log model based on code.
        if employee_record.need_sync != False and employee_record.user_id:
            for r in range(1, 5):
                if r == 4:
                    if len(employee_record.educational_details_ids) > 0:
                        self.env['kw_emp_sync_log'].create(
                            {'model_id': 'hr.employee', 'rec_id': employee_record.id, 'code': 4, 'status': 0})
                else:
                    self.env['kw_emp_sync_log'].create(
                        {'model_id': 'hr.employee', 'rec_id': employee_record.id, 'code': r, 'status': 0})

            # Check if experience type is not fresher then create a record in log with code 5
            if employee_record.experience_sts == "2" and len(employee_record.work_experience_ids) > 0:
                self.env['kw_emp_sync_log'].create(
                    {'model_id': 'hr.employee', 'rec_id': employee_record.id, 'code': 5, 'status': 0})

        return employee_record

    # write method for employee
    @api.multi
    def write(self, vals):
        # print("Write for sync", vals)
        employee_record = super(kw_sync_hr_employee, self).write(vals)
        for rec in self:
            # print(f"if {rec.need_sync} != False and {rec.user_id} != False and {rec.kw_id} > 0:")
            if rec.need_sync != False and rec.user_id != False and rec.kw_id > 0:
                w_id = rec
                # w_id = self.env['hr.employee'].sudo().search([('id', '=', rec.id)])
                if w_id.write_uid.id != 1 and w_id.need_sync != False:
                    # d1 = {'bankaccount_id', 'bank', 'basic_at_join_time', 'proj_bill_amnt',
                    #       'date_of_completed_probation', 'at_join_time_ctc', 'birthday', 'date_of_joining', 'job_id',
                    #       'domain_login_id',
                    #       'work_email', 'emp_category', 'emp_role', 'employement_type', 'enable_payroll', 'name',
                    #       'gender', 'enable_gratuity', 'current_ctc', 'wedding_anniversary', 'base_branch_id',
                    #       'conv_pwd',
                    #       'enable_payroll', 'image_url', 'date_of_completed_probation', 'emp_religion', 'coach_id',
                    #       'parent_id', 'department_id', 'base_branch_id', 'login', 'medical_reimb', 'transport',
                    #       'productivity', 'commitment', 'emp_code', 'attendance_mode_ids', 'image', 'no_attendance'}
                    d1 = {'name', 'work_email', 'department_id', 'job_id', 'grade', 'base_branch_id', 'date_of_joining',
                          'date_of_completed_probation', 'last_working_day', 'gender', 'emp_religion', 'parent_id',
                          'birthday',
                          'active', 'kw_id', 'employement_type', 'resource_calendar_id', 'emp_code', 'emp_role',
                          'emp_category', 'image', 'no_attendance', 'on_probation', 'image_url'}

                    pDict = {'personal_email', 'emergency_contact', 'emergency_phone', 'marital', 'mobile_phone',
                             'country_id', 'epbx_no', 'permanent_addr_street', 'permanent_addr_city',
                             'permanent_addr_country_id',
                             'present_addr_state_id', 'present_addr_street', 'present_addr_city',
                             'present_addr_country_id', 'present_addr_state_id', 'emp_religion', 'known_language_ids'}
                    iDict = {'blood_group', 'identification_ids'}
                    expDict = {'technical_skill_ids', 'work_experience_ids'}

                    # Check if any Add user Api data is Updated in Employee,If updated then create a record
                    # in Log model to sync data to Kwantify
                    for key in d1:
                        # print("KEY IN D!")
                        if key in vals:
                            log_rec = self.env['kw_emp_sync_log'].sudo().search(
                                [('model_id', '=', 'hr.employee'), ('rec_id', '=', w_id.id), ('status', '=', 0),
                                 ('code', '=', 1), ('updated_status', '=', True)])
                            if not log_rec.exists():
                                # print("not log record")
                                log_rec.create({'model_id': 'hr.employee', 'rec_id': w_id.id,
                                                'code': 1, 'status': 0,
                                                'updated_status': True})

                    # Check if any Identification info Api data is Updated in Employee,If updated then create a record
                    # in Log model to sync data to Kwantify
                    for key in iDict:
                        if key in vals:
                            log_rec = self.env['kw_emp_sync_log'].sudo().search(
                                [('model_id', '=', 'hr.employee'), ('rec_id', '=', w_id.id),
                                 ('status', '=', 0), ('code', '=', 2)])
                            if not log_rec.exists():
                                sync_data = self.env['kw_emp_sync_log'].create(
                                    {'model_id': 'hr.employee', 'rec_id': w_id.id, 'code': 2, 'status': 0})

                    # Check if any Personal Info Api data is Updated in Employee,If updated then create a record
                    # in Log model to sync data to Kwantify
                    for key in pDict:
                        if key in vals:
                            log_rec = self.env['kw_emp_sync_log'].sudo().search(
                                ['&', '&', '&', ('model_id', '=', 'hr.employee'),
                                 ('rec_id', '=', w_id.id), ('status', '=', 0), ('code', '=', 3)])
                            if not log_rec.exists():
                                sync_data = self.env['kw_emp_sync_log'].create(
                                    {'model_id': 'hr.employee', 'rec_id': w_id.id, 'code': 3, 'status': 0})

                    #  Check if any Work Info Api data is Updated in Employee,If updated then create a record
                    #  in Log model to sync data to Kwantify
                    for key in expDict:
                        if key in vals:
                            log_rec = self.env['kw_emp_sync_log'].sudo().search(
                                [('model_id', '=', 'hr.employee'), ('rec_id', '=', w_id.id),
                                 ('status', '=', 0), ('code', '=', 5)])

                            if not log_rec.exists():
                                sync_data = self.env['kw_emp_sync_log'].create(
                                    {'model_id': 'hr.employee', 'rec_id': w_id.id, 'code': 5, 'status': 0})

                    if 'educational_details_ids' in vals:
                        log_rec = self.env['kw_emp_sync_log'].sudo().search(
                            [('model_id', '=', 'hr.employee'), ('rec_id', '=', w_id.id),
                             ('status', '=', 0), ('code', '=', 4)])

                        if not log_rec.exists():
                            sync_data = self.env['kw_emp_sync_log'].create(
                                {'model_id': 'hr.employee', 'rec_id': w_id.id, 'code': 4, 'status': 0})

        return employee_record
