# -*- coding: utf-8 -*-

import requests, json, base64
import mimetypes
from urllib.request import urlopen
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


def is_url_image(url):
    mimetype, encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))


def check_url(url):
    try:
        image_formats = ("image/png", "image/jpeg", "image/gif")
        site = urlopen(url)
        meta = site.info()  # get header of the http request
        if meta["content-type"] in image_formats:
            return True
        else:
            return False
    except Exception:
        return False


def is_image_and_ready(url):
    return is_url_image(url) and check_url(url)


class kw_odoo_kwantify_resource_sync(models.Model):
    _name = 'kw_kwantify_integration_log'
    _description = 'Kwantify Resource Sync Scheduler'

    new_record_log = fields.Text()
    update_record_log = fields.Text()
    error_log = fields.Text()
    request_params = fields.Text()
    response_result = fields.Text()

    name = fields.Char(string='Request For', )

    # def _getResponsefromKwantify(self, from_date=False, to_date=False, page_no=False, page_size=False):
    def _getResponsefromKwantify(self, kw_id=False):
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param('kw_sync.emp_web_service_url', False)
        if not url:
            return {'status': 404, 'error_log': 'API service URL not configured', }
        if kw_id is False:
            return {'status': 404, 'error_log': 'Please set employee id', }
        json_data = False
        if kw_id:
            # print("kw==================", kw_id, url)
            json_data = {
                "UserID": kw_id,
            }
            
        # if from_date and to_date and page_size and page_no:
        #     json_data = {
        #         "FromDate": from_date.strftime('%Y-%m-%d'),
        #         "ToDate": to_date.strftime('%Y-%m-%d'),
        #         "PageNo": page_no,
        #         "PageSize": page_size,
        #     }
        # else:
        #     # print(params.get_param('kw_sync.kw_sync_service_diff_days'))
        #     if params.get_param('kw_sync.kw_sync_service_diff_days', 1):
        #         day_diff = int(params.get_param('kw_sync.kw_sync_service_diff_days', 1))
        #     else:
        #         day_diff = 1
        #     # print(day_diff)

        #     json_data = {
        #         "FromDate": (datetime.now() - relativedelta(days=+day_diff)).strftime('%Y-%m-%d'),
        #         "ToDate": datetime.now().strftime('%Y-%m-%d'),
        #         "PageNo": 1,
        #         "PageSize": 500,
        #     }

        header = {'Content-type': 'application/json', }  # , 'Accept': 'text/plain'
        data = json.dumps(json_data)

        request_params = " Service Url : " + url + " " + str(data)
        #########################################################################################
        try:
            response_result = requests.post(url, data=data, headers=header, timeout=30)
            resp = json.loads(response_result.text)
            # print("========================== resp", resp)
            return {'status': 200, 'result': resp, 'request_params': request_params}
        except Exception as e:
            # print(e)
            return {'status': 500, 'error_log': str(e), 'request_params': request_params}

    def _getAllMasterData(self, resp_result):
        blood_grp_master = []
        marital_sts_master = []
        designation_master = []
        grade_master = []
        department_master = []
        user_master = []
        # employee_role_master = []
        employment_type_master = []
        reference_mode_master = []
        # print(resp_result)

        for jsn_record in resp_result:
            # if jsn_record['EmployeeRole']:
            #     emp_role_data = {'kw_id': int(jsn_record['EmployeeRole']),
            #                      'emp_role': 0,
            #                      'emp_cat_kw_id': int(jsn_record['EmployeeCategory']),
            #                      'emp_category': 0}
            #     if emp_role_data not in employee_role_master:
            #         employee_role_master.append(emp_role_data)

            if jsn_record['EmploymentType'] and jsn_record['EmploymentType'] != '':
                emp_type_data = {'code': jsn_record['EmploymentType'].strip(), 'employement_type': 0}
                if emp_type_data not in employment_type_master:
                    employment_type_master.append(emp_type_data)

            if jsn_record['ReferenceMode'] and jsn_record['ReferenceMode'] != '' and jsn_record['ReferenceMode'] != '0':
                ref_mode_data = {'kw_id': int(jsn_record['ReferenceMode']), 'emp_refered_from': 0}
                if ref_mode_data not in reference_mode_master:
                    reference_mode_master.append(ref_mode_data)

            if jsn_record['BloodGroup'] and jsn_record['BloodGroup'] != '':
                blood_grp_data = {'name': jsn_record['BloodGroup'], 'blood_group': 0}
                if blood_grp_data not in blood_grp_master:
                    blood_grp_master.append(blood_grp_data)

            if jsn_record['MaritalStatus'] and jsn_record['MaritalStatus'] != '':
                marital_status = 'Other'
                if jsn_record['MaritalStatus'] == 'M':
                    marital_status = 'Married'
                if jsn_record['MaritalStatus'] == 'U':
                    marital_status = 'Single'

                marital_data = {'name': marital_status,
                                'marital': 0,
                                'marital_code': jsn_record['MaritalStatus']}

                if marital_data not in marital_sts_master:
                    marital_sts_master.append(marital_data)

            if jsn_record['Designation']:
                designation_data = {'kw_id': int(jsn_record['intDesgId']),
                                    'name': jsn_record['Designation'],
                                    'job_id': 0}
                if designation_data not in designation_master:
                    designation_master.append(designation_data)

            if jsn_record['intGradeId']:
                grade_data = {'kw_id': int(jsn_record['intGradeId']),
                              'name': jsn_record['Grade'],
                              'emp_grade': 0}
                if grade_data not in grade_master:
                    grade_master.append(grade_data)

            if jsn_record['Department']:
                department_data = {'kw_id': int(jsn_record['DepartmentId']),
                                   'parent_kw_id': int(jsn_record['Department'][0]['parentDeptId']),
                                   'name': jsn_record['Department'][0]['DepartmentName'],
                                   'department_id': 0,
                                   'parent_id': 0}

                if department_data not in department_master:
                    department_master.append(department_data)

            if jsn_record['Username']:
                # print(jsn_record['Photo'])
                emp_img = base64.b64encode(requests.get(jsn_record['Photo']).content) if jsn_record['Photo'] != '' and is_image_and_ready(jsn_record['Photo']) else False

                user_data = {'login': jsn_record['Username'],
                             'user_id': 0,
                             'active': int(jsn_record['Active']),
                             'name': jsn_record['Fullname'],
                             'email': jsn_record['Email'],
                             'mobile': jsn_record['MobNo'],
                             'image': emp_img,
                             'branch_id': int(jsn_record['vchOfcId'] if jsn_record['vchOfcId'] else 0)}

                if user_data not in user_master:
                    user_master.append(user_data)

        # if len(employee_role_master) > 0:
        #     employee_role_master = self.createUpdateEmpRoleMaster(employee_role_master)
        if len(employment_type_master) > 0:
            employment_type_master = self.createUpdateEmptypeMaster(employment_type_master)
        if len(reference_mode_master) > 0:
            reference_mode_master = self.createUpdateReferencemodeMaster(reference_mode_master)

        if len(marital_sts_master) > 0:
            marital_sts_master = self.createUpdateMaritalstsMaster(marital_sts_master)

        if len(designation_master) > 0:
            designation_master = self.createUpdateDesignationMaster(designation_master)

        if len(grade_master) > 0:
            grade_master = self.createUpdateGradeMaster(grade_master)

        if len(department_master) > 0:
            department_master = self.createUpdateDepartmentMaster(department_master)

        # print(user_master)
        # if len(user_master) > 0:
        #     user_master = self.createUpdateUserMaster(user_master)

        # print("----After update")
        # print(reference_mode_master)

        return {
                # 'employee_role_master': employee_role_master,
                'employment_type_master': employment_type_master,
                'reference_mode_master': reference_mode_master,
                'blood_grp_master': blood_grp_master,
                'marital_sts_master': marital_sts_master,
                'designation_master': designation_master,
                'grade_master': grade_master,
                'department_master': department_master,
                }
    # 'user_master': user_master

    # #main function called by scheduler
    # def syncKwantifyData(self, from_date=False, to_date=False, page_no=False, page_size=False):
    #     result = self._getResponsefromKwantify(from_date, to_date, page_no, page_size)
    def syncKwantifyData(self, kw_id=False):
        result = self._getResponsefromKwantify(kw_id)
        record_log = result['error_log'] if 'error_log' in result else ''
        new_record_log = ''
        update_record_log = ''
        # print('result >>>>>>>> ', result, result['status'], type(result['status']))
        if result['status'] == 200:
            result_data = result['result']
            emp_updated_list = {}
            all_master_data = {}

            # try:
            # print(" >>>>>>>>>>>>>>>>>>>>>> ")
            all_master_data = self._getAllMasterData(result_data)
            # print("all_master_data >>>>>>>> ", all_master_data)

            emp_updated_list = self._prepareEmployeeData(result_data, all_master_data)
            # print("emp_updated_list >>>> ", emp_updated_list)
            # except Exception as e:
            #     print(e)
            #     record_log += str(e)
            #     pass

            # print(" ============= ")
            hr_employee = self.env['hr.employee'].sudo()
            for emp_data in emp_updated_list:
                if emp_data['parent_id']:
                    existing_parent_emp_rec = hr_employee.search([('kw_id', '=', emp_data['parent_id']), '|', ('active', '=', True), ('active', '=', False)])
                    if existing_parent_emp_rec:
                        emp_data['parent_id'] = existing_parent_emp_rec.id
                    else:
                        emp_data['parent_id'] = False

                existing_emp_rec = hr_employee.search(
                    [('kw_id', '=', emp_data['kw_id']), '|', ('active', '=', True), ('active', '=', False)])

                if emp_data['biometric_id'] and existing_emp_rec:
                    if emp_data['biometric_id'] == '0':
                        pass
                    elif existing_emp_rec.biometric_id == '0':
                        emp_data['biometric_id'] = existing_emp_rec.biometric_id
                    else:
                        pass
                if 'user_id' in emp_data.keys():
                    if emp_data['user_id'] \
                            and ((existing_emp_rec
                                  and existing_emp_rec.user_id.id != emp_data['user_id']) or not existing_emp_rec):
                        pass
                    else:
                        del emp_data['user_id']

                try:
                    if existing_emp_rec:
                        # print('------Start: Existing Record-----')

                        """remove shift info, if it is same as previous one"""
                        # if 'resource_calendar_id' in emp_data and existing_emp_rec.resource_calendar_id.id == emp_data['resource_calendar_id']:
                        #     del emp_data['resource_calendar_id']
                        """updating existing employee"""
                        existing_emp_rec.sudo().write(emp_data)
                        emp_data['image'] = ''
                        emp_data['image_medium'] = ''
                        emp_data['image_small'] = ''
                        # print(emp_data)
                        update_record_log += ' ### start_rec### ' + str(emp_data['kw_id']) + ' ' + \
                                             str(emp_data['name']) + ' ### ' + str(existing_emp_rec.id) + \
                                             ' ###' + str(emp_data) + ' ###end_rec### '

                        # print('------End :Existing Record-----')
                    else:

                        # print('------Start: New Record-----')
                        # print(emp_data)
                        """create new employee"""
                        new_record_log += ' ### start_rec### ' + str(emp_data['kw_id']) + ' ' + str(emp_data['name'])
                        # created_recs = hr_employee.create(emp_data)

                        # emp_data['image'] = ''
                        # emp_data['image_medium'] = ''
                        # emp_data['image_small'] = ''
                        # new_record_log += '### ' + str(created_recs.id) + ' ###' + str(emp_data) + ' ###end_rec### '
                        # print(created_recs)
                except Exception as e:
                    emp_data['image'] = ''
                    emp_data['image_medium'] = ''
                    emp_data['image_small'] = ''

                    record_log += '### Error block ' + str(e) + ' ###' + str(emp_data) + ' ###end_rec### '
                    pass

        # #enter data into log model
        synch_log = self.env['kw_kwantify_integration_log'].sudo()
        synch_log.create({'name': 'Kwantify Employee Data',
                          'new_record_log': new_record_log,
                          'update_record_log': update_record_log,
                          'error_log': record_log,
                          'request_params': result['request_params'],
                          'response_result': result['result'] if 'result' in result else ''
                          })

        # #if any record.   delete last 15 days log record
        # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()

    # #prepare the employee data , update the master ids
    def _prepareEmployeeData(self, employee_data, all_master_data):
        emp_update_list = []
        # print("employee_data >>> ", employee_data, " ?? all_master_data >>>> ", all_master_data)
        # res_partner_records = self.env['res.partner'].sudo().search([("is_company", "=", True)])
        shift_records = self.env['resource.calendar'].search([('employee_id', '=', False)])

        dept_records = self.env['hr.department'].search(['|', ('active', '=', True), ('active', '=', False)])
        branch_records = self.env['kw_res_branch'].search(['|', ('active', '=', True), ('active', '=', False)])
        grade_band_records = self.env['kwemp_grade'].search(['|', ('active', '=', True), ('active', '=', False)])
       
        # print(res_partner_records)  
        for jsn_record in employee_data:
            emp_data = {
                'parent_id': int(jsn_record['RptAuthority']),
                'kw_id': int(jsn_record['UserId']),
                'name': jsn_record['Fullname'],
                'birthday': jsn_record['DOB'] if jsn_record['DOB'] else False,
                'date_of_joining': jsn_record['DOJ'],
                'epbx_no': jsn_record['EPBX'],
                'work_email': jsn_record['Email'],
                'emp_code': jsn_record['EmpCode'],
                'gender': jsn_record['Gender'].lower() if jsn_record['Gender'] else False,
                'mobile_phone': jsn_record['MobNo'],
                'personal_email': jsn_record['HomemailID'],
                'active': True if jsn_record['Active'] == '1' else False
            }
            if jsn_record['MobNo']:
                emp_data['mobile_phone'] = jsn_record['MobNo']

            emp_img = base64.b64encode(requests.get(jsn_record['Photo']).content) if jsn_record['Photo'] != '' and is_image_and_ready(jsn_record['Photo']) else False
            if emp_img:
                emp_data['image'] = emp_img

            # #start :added on 26th Dec , By : T Ketaki Debadarshini
            emp_data['biometric_id'] = jsn_record['BioId']
            if jsn_record['WhatsappNo']:
                emp_data['whatsapp_no'] = jsn_record['WhatsappNo']

            # #start :added on 29th Oct , By : T Ketaki Debadarshini
            emp_data['last_working_day'] = jsn_record['DateofLeaving'] if 'DateofLeaving' in jsn_record and jsn_record['DateofLeaving'] != '' and emp_data['active'] == False else None

            # if jsn_record['EmployeeRole']:
            #     for employee_role_master_data in all_master_data['employee_role_master']:
            #         if employee_role_master_data['kw_id'] == int(jsn_record['EmployeeRole']) and \
            #                 employee_role_master_data['emp_role'] > 0:
            #             emp_data['emp_role'] = employee_role_master_data['emp_role']

            #         if employee_role_master_data['emp_cat_kw_id'] == int(jsn_record['EmployeeCategory']) and \
            #                 employee_role_master_data['kw_id'] == int(jsn_record['EmployeeRole']) and \
            #                 employee_role_master_data['emp_category'] > 0:
            #             emp_data['emp_category'] = employee_role_master_data['emp_category']

            if jsn_record['EmploymentType']:
                for employment_type_master_data in all_master_data['employment_type_master']:
                    if jsn_record['EmploymentType'] \
                            and employment_type_master_data['code'] == jsn_record['EmploymentType'].strip() \
                            and employment_type_master_data['employement_type'] > 0:
                        emp_data['employement_type'] = employment_type_master_data['employement_type']

            if jsn_record['ReferenceMode']:
                for reference_mode_master_data in all_master_data['reference_mode_master']:
                    if reference_mode_master_data['kw_id'] == int(jsn_record['ReferenceMode']) and \
                            reference_mode_master_data['emp_refered_from'] > 0:
                        emp_data['emp_refered_from'] = reference_mode_master_data['emp_refered_from']

            # #end :added on 26th dec ,

            # #attendnace mode,shift id ,branch info :added on 24th Aug  2020, By : T Ketaki Debadarshini
            if 'EnableAttendance' in jsn_record and jsn_record['EnableAttendance'] == 'YES':
                if 'AttendanceMode' in jsn_record and jsn_record['AttendanceMode'] != '':
                    bio_attendance_mode = self.env.ref('kw_hr_attendance.kw_attendance_mode_bio').alias if self.env.ref(
                        'kw_hr_attendance.kw_attendance_mode_bio').exists() else 'bio_metric'
                    portal_attendance_mode = self.env.ref(
                        'kw_hr_attendance.kw_attendance_mode_portal').alias if self.env.ref(
                        'kw_hr_attendance.kw_attendance_mode_portal').exists() else 'portal'
                    manual_attendance_mode = self.env.ref(
                        'kw_hr_attendance.kw_attendance_mode_manual').alias if self.env.ref(
                        'kw_hr_attendance.kw_attendance_mode_manual').exists() else 'manual'
                    kw_attendance_modes = [[portal_attendance_mode], [bio_attendance_mode],
                                           [portal_attendance_mode, bio_attendance_mode], [manual_attendance_mode]]
                    attendance_modes_kw = kw_attendance_modes[int(jsn_record['AttendanceMode'])]
                    attendance_mode_ids = self.env['kw_attendance_mode_master'].sudo().search(
                        [('alias', 'in', attendance_modes_kw)])
                    if attendance_modes_kw and attendance_mode_ids:
                        emp_data['attendance_mode_ids'] = [(6, False, attendance_mode_ids.ids)]
                        emp_data['no_attendance'] = False
            else:
                emp_data['attendance_mode_ids'] = False
                emp_data['no_attendance'] = True

            # shift info

            if jsn_record['ShiftId']:
                shift_info = shift_records.filtered(lambda r: r.kw_id == int(jsn_record['ShiftId']))
                if shift_info and int(jsn_record['ShiftId']) > 0:
                    emp_data['resource_calendar_id'] = shift_info.id
            
            # ###End of attendance info##
                
            if jsn_record['BloodGroup'] and jsn_record['BloodGroup'] != '':
                for blood_grp_data in all_master_data['blood_grp_master']:
                    if blood_grp_data['name'] == jsn_record['BloodGroup'] and blood_grp_data['blood_group'] > 0:
                        emp_data['blood_group'] = blood_grp_data['blood_group']

            if jsn_record['MaritalStatus'] and jsn_record['MaritalStatus'] != '':
                for marital_sts_data in all_master_data['marital_sts_master']:
                    if marital_sts_data['marital_code'] == jsn_record['MaritalStatus']:
                        emp_data['marital_sts'] = marital_sts_data['marital']
                        emp_data['marital_code'] = marital_sts_data['marital_code']
                        emp_data['wedding_anniversary'] = jsn_record['DOA'] if jsn_record['DOA'] != '' else False

            if jsn_record['Designation']:
                for designation_master_data in all_master_data['designation_master']:
                    if designation_master_data['kw_id'] == int(jsn_record['intDesgId']):
                        emp_data['job_id'] = designation_master_data['job_id']

            if jsn_record['intGradeId']:
                for grade_master_data in all_master_data['grade_master']:
                    if grade_master_data['kw_id'] == int(jsn_record['intGradeId']):
                        # emp_data['emp_grade'] = grade_master_data['emp_grade']
                        # #modification as per the new fields grade,emp_band
                        if grade_master_data['emp_grade'] > 0:
                            existing_emp_grade_band = grade_band_records.filtered(lambda rec: rec.kw_id == int(jsn_record['intGradeId']))
                            if existing_emp_grade_band:
                                emp_data['emp_band'] = existing_emp_grade_band.band_id.id if existing_emp_grade_band.band_id else False
                                emp_data['grade'] = existing_emp_grade_band.grade_id.id if existing_emp_grade_band.grade_id else False

            if jsn_record['Department']:
                for department_master_data in all_master_data['department_master']:
                    if department_master_data['kw_id'] == int(jsn_record['DepartmentId']):
                        emp_data['department_id'] = department_master_data['department_id']

            # update department,division,section,practice info
            if 'DepartmentNew' in jsn_record and jsn_record['DepartmentNew']:
                dept_rec = dept_records.filtered(lambda rec: rec.kw_id == int(jsn_record['DepartmentNew']))
                dept = dept_rec.filtered(lambda x: x.active is True) if len(dept_rec) > 1 else dept_rec
                dept = dept if len(dept) > 0 else dept_rec[0]
                if dept:
                    emp_data['department_id'] = dept[0].id
            if 'Division' in jsn_record and jsn_record['Division']:
                division_rec = dept_records.filtered(lambda rec: rec.kw_id == int(jsn_record['Division']))
                division = division_rec.filtered(lambda x: x.active is True) if len(division_rec) > 1 else division_rec
                division = division if len(division) > 0 else division_rec[0]
                if division:
                    emp_data['division'] = division[0].id
            if 'Section' in jsn_record and jsn_record['Section']:
                section_rec = dept_records.filtered(lambda rec: rec.kw_id == int(jsn_record['Section']))
                sect = section_rec.filtered(lambda x: x.active is True) if len(section_rec) > 1 else section_rec
                sect = sect if len(sect) > 0 else section_rec[0]
                if sect:
                    emp_data['section'] = sect[0].id
            if 'Practice' in jsn_record and jsn_record['Practice']:
                practise_rec = dept_records.filtered(lambda rec: rec.kw_id == int(jsn_record['Practice']))
                practise = practise_rec.filtered(lambda x: x.active is True) if len(practise_rec) > 1 else practise_rec
                practise = practise if len(practise) > 0 else practise_rec[0]
                if practise:
                    emp_data['practise'] = practise[0].id
                
            """# #check whether new record or existing employee record"""
            if 'vchOfcId' in jsn_record and jsn_record['vchOfcId']: #or jsn_record['Location']
                # existing_office_rec = res_partner_records.filtered(lambda r: r.kw_office_id == int(jsn_record['vchOfcId']))
                # job_branch_id base_branch_id
                existing_branch_rec = branch_records.filtered(lambda r: r.kw_id == int(jsn_record['vchOfcId']))
                if existing_branch_rec:
                    emp_data['job_branch_id'] = existing_branch_rec.id
                    emp_data['base_branch_id'] = existing_branch_rec.id

            # if jsn_record['Location']:
            #     existing_location_rec = res_partner_records.filtered(lambda r: r.kw_location_id == int(jsn_record['Location']) and r.kw_office_id == int(jsn_record['vchOfcId']))
            #
            #     if existing_location_rec:
            #         emp_data['work_location_id'] = existing_location_rec.id

            # if jsn_record['Username']:
            #     for user_master_data in all_master_data['user_master']:
            #         if user_master_data['login'] == jsn_record['Username']:
            #             emp_data['user_id'] = user_master_data['user_id']

            emp_update_list.append(emp_data)
        return emp_update_list

    # #create or update emp role master
    # def createUpdateEmpRoleMaster(self, employee_role_master):
    #     emp_role_records = self.env['kwmaster_role_name'].sudo().search([])
    #     emp_cat_records = self.env['kwmaster_category_name'].sudo().search([])

    #     for emp_role in employee_role_master:
    #         existing_role_rec = emp_role_records.filtered(lambda r: r.kw_id == emp_role['kw_id'])
    #         if existing_role_rec:
    #             emp_role['emp_role'] = existing_role_rec.id
    #             existing_cat_rec = emp_cat_records.filtered(lambda r: r.kw_id == emp_role['emp_cat_kw_id'] and r.role_ids.id == existing_role_rec.id)
    #             if existing_cat_rec:
    #                 emp_role['emp_category'] = existing_cat_rec.id

    #     return employee_role_master

    # #create or update emp type master
    def createUpdateEmptypeMaster(self, employment_type_master):
        emp_type_records = self.env['kwemp_employment_type'].sudo().search(['|', ('active', '=', True), ('active', '=', False)])

        for emp_type in employment_type_master:
            existing_type_rec = emp_type_records.filtered(lambda r: r.code == emp_type['code'].strip())
            if existing_type_rec:
                emp_type['employement_type'] = existing_type_rec.id

        return employment_type_master

    # #create or update emp reference mode master
    def createUpdateReferencemodeMaster(self, reference_mode_master):
        ref_mode_records = self.env['kwemp_reference_mode_master'].sudo().search(['|', ('active', '=', True), ('active', '=', False)])

        for ref_mode in reference_mode_master:
            existing_mode_rec = ref_mode_records.filtered(lambda r: r.kw_id == ref_mode['kw_id'])
            if existing_mode_rec:
                ref_mode['emp_refered_from'] = existing_mode_rec.id

        return reference_mode_master

    # # ##create or update master data blood group
    # def createUpdateBloodgrpMaster(self, blood_grp_master):
    #     blood_grp_model = self.env['kwemp_blood_group_master'].sudo()
    #     blood_grp_records = blood_grp_model.search([])
    #
    #     for blood_grp in blood_grp_master:
    #         existing_blood_grp_rec = blood_grp_records.filtered(lambda r: r.name == blood_grp['name'])  # blood_grp_model.search([('name','=',blood_grp['name'])])
    #
    #         if not existing_blood_grp_rec:
    #             existing_blood_grp_rec = blood_grp_model.create({'name': blood_grp['name']})
    #
    #         blood_grp['blood_group'] = existing_blood_grp_rec.id
    #     return blood_grp_master

    # ##create or update master data marital status
    def createUpdateMaritalstsMaster(self, marital_sts_master):
        marital_master_model = self.env['kwemp_maritial_master'].sudo()
        marital_master_records = marital_master_model.search(['|', ('active', '=', True), ('active', '=', False)])

        for marital_data in marital_sts_master:
            existing_marital_rec = marital_master_records.filtered(lambda r: r.code == marital_data['marital_code'])  # marital_master_model.search([('code','=',marital_data['marital_code'])])

            if not existing_marital_rec:
                existing_marital_rec = marital_master_model.create({'name': marital_data['name'],
                                                                    'code': marital_data['marital_code']})
            marital_data['marital'] = existing_marital_rec.id
        return marital_sts_master

    # #create update designation master
    def createUpdateDesignationMaster(self, designation_master):
        hr_job_model = self.env['hr.job'].sudo()
        hr_job_records = hr_job_model.search([])

        for desination_data in designation_master:
            existing_hr_job_rec = hr_job_records.filtered(lambda r: r.kw_id == desination_data['kw_id'])  # hr_job_model.search([('kw_id','=',desination_data['kw_id'])])
            if existing_hr_job_rec:
                pass
                # if existing_hr_job_rec.name != desination_data['name']:
                #     existing_hr_job_rec.write({'name': desination_data['name']})
            else:
                existing_hr_job_rec = hr_job_records.filtered(lambda r: r.kw_id == False and r.name == desination_data['name'])
                if existing_hr_job_rec:
                    existing_hr_job_rec.write({'kw_id': desination_data['kw_id']})
                else:
                    existing_hr_job_rec = hr_job_model.create({'name': desination_data['name'],
                                                               'no_of_recruitment': 0,
                                                               'kw_id': desination_data['kw_id']})

            desination_data['job_id'] = existing_hr_job_rec[0].id
        return designation_master

    # #create update grade master
    def createUpdateGradeMaster(self, grade_master):
        kwemp_grade_model = self.env['kwemp_grade'].sudo()
        kwemp_grade_records = kwemp_grade_model.search(['|', ('active', '=', True), ('active', '=', False)])

        for grade_data in grade_master:
            existing_grade_rec = kwemp_grade_records.filtered(lambda r: r.kw_id == grade_data['kw_id'])
            if existing_grade_rec:
                pass
                # if existing_grade_rec.name != grade_data['name']:
                #     existing_grade_rec.write({'name': grade_data['name']})
            else:
                existing_grade_rec = kwemp_grade_records.filtered(lambda r: r.kw_id == False and r.name == grade_data['name'])
                if existing_grade_rec:
                    existing_grade_rec.write({'kw_id': grade_data['kw_id']})
                # else:
                #     existing_grade_rec = kwemp_grade_model.create({'name': grade_data['name'],
                #                                                    'kw_id': grade_data['kw_id']})

            grade_data['emp_grade'] = existing_grade_rec.id
        return grade_master

    # #create /update department master
    def createUpdateDepartmentMaster(self, department_master):
        hr_department = self.env['hr.department'].sudo()
        hr_department_records = hr_department.search(['|', ('active', '=', True), ('active', '=', False)])
       
        for department_data in department_master:
            existing_hr_department_rec = hr_department_records.filtered(lambda r: r.kw_id == department_data['kw_id'])
            parent_hr_department_rec = hr_department_records.filtered(lambda r: department_data['parent_kw_id'] and r.kw_id == department_data['parent_kw_id'])

            if existing_hr_department_rec:
                pass
                # if existing_hr_department_rec.name != department_data['name'] or existing_hr_department_rec.parent_id.id != parent_hr_department_rec.id:
                #     existing_hr_department_rec.write({'name': department_data['name'],
                #                                       'parent_id': parent_hr_department_rec.id if parent_hr_department_rec else False})
            else:
                existing_hr_department_rec = hr_department_records.filtered(lambda r: r.kw_id == False and r.name == department_data['name'])
                if existing_hr_department_rec:
                    existing_hr_department_rec.write({'kw_id': department_data['kw_id']})
                    # , 'parent_id': parent_hr_department_rec.id if parent_hr_department_rec else False
                # else:
                #     existing_hr_department_rec = hr_department.create(
                #         {'parent_id': parent_hr_department_rec.id if parent_hr_department_rec else False,
                #          'name': department_data['name'],
                #          'kw_id': department_data['kw_id']})
            dept = existing_hr_department_rec.filtered(lambda x: x.active is True) if len(existing_hr_department_rec) > 1 else existing_hr_department_rec
            dept = dept if len(dept) > 0 else existing_hr_department_rec[0]
            department_data['department_id'] = dept[0].id
        return department_master

    """# #create/update user master"""
    def createUpdateUserMaster(self, user_master):
        res_users = self.env['res.users'].sudo()
        res_users_records = res_users.search([('login', 'in', [u.get('login') for u in user_master]), '|', ('active', '=', True), ('active', '=', False)])
        branch_records = self.env['kw_res_branch'].sudo().search(['|', ('active', '=', True), ('active', '=', False)])
        for user_data in user_master:
            existing_res_user_rec = res_users_records.filtered(lambda r: r.login == user_data['login'])
            existing_branch_rec = branch_records.filtered(lambda r: r.kw_id == user_data['branch_id'])

            action_id = False
            try:
                action_id = int(self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action').id) or False
                # action_id = self.env.ref('kw_hr_attendance.action_my_office_time').id
            except Exception:
                pass
            
            if not existing_res_user_rec:  # and user_data['active'] == 1
                create_user_data = {'tz': 'Asia/Kolkata',
                                    'name': user_data['name'],
                                    'email': user_data['email'],
                                    'login': user_data['login'],
                                    'image': user_data['image'],
                                    'mobile': user_data['mobile'],
                                    'active': user_data['active'],
                                    }
                # print(action_id)
                if action_id:
                    create_user_data.update({'action_id': action_id})
                """create new user if not exist"""
                # existing_res_user_rec = res_users.create(create_user_data)

            user_data['user_id'] = existing_res_user_rec.id
            """update branch id of user"""
            if existing_branch_rec and existing_res_user_rec:
                existing_res_user_rec.sudo().write({'branch_id': existing_branch_rec.id})
            """update status of user / archive the user"""
            if user_data['active'] == 0 and existing_res_user_rec.active:
                existing_res_user_rec.sudo().write({'active': False})
        return user_master

    def get_config_email_to(self):
        params = self.env['ir.config_parameter'].sudo()
        send_mail_id = params.get_param('kw_sync.kw_sync_error_log_mail_id', False)
        # print(send_mail_id)
        return send_mail_id

    @api.model
    def create(self, vals):
        log_rec = super(kw_odoo_kwantify_resource_sync, self).create(vals)
        # print(log_rec)
        # print(vals)
        # #if error , send error log to the configured email id
        if 'error_log' in vals and vals['error_log'] != '':
            try:
                template = self.env.ref('kw_kwantify_integration.kw_odoo_sync_email_template')
                self.env['mail.template'].browse(template.id).send_mail(log_rec.id)
            except Exception as e:
                pass
        return log_rec
