# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import models, fields, api
from odoo.addons.kw_onboarding_bgv_integration.tools import api


class kw_recruitmentHrApplicant(models.Model):
    _inherit = "kwonboard_enrollment"

    def sync_bgv_applicant_data(self):
        access_token = api.refresh_access_token()
        today = datetime.today().date().strftime("%d-%m-%Y")
        # print("access_token==========", today, access_token)
        record = False
        if access_token:
            log_data = self.env['kwonboard_enrollment_bgv_log'].sudo().search([('enrollment_id', '=', self.id)])
            if not log_data.exists():
                record = self.env['kwonboard_enrollment_bgv_log'].create({'enrollment_id': self.id,
                                                                          'access_token': access_token, })
            else:
                log_data.access_token = access_token
        # return record

        bgv_data = self.prepare_bgv_data()
        # print("bgv_data >>>> ", bgv_data)
        # bgv_req = api.add_bgv_request(access_token, bgv_data)

        candidate_data = self.prepare_candidate_data()
        # print("candidate_data >>>> ", candidate_data)
        # candidate_req = api.add_candidate(access_token, candidate_data)

        company_data = self.prepare_company_data()
        # print("company_data >>>> ", company_data)
        # company_req = api.add_company(access_token, company_data)

        experience_data = self.prepare_employment_data()
        # print("experience_data >>>> ", experience_data)
        # experience_req = api.add_experience(access_token, experience_data)
        # print(k)
        return record

    def prepare_bgv_data(self):
        today = datetime.today().date().strftime("%d-%m-%Y")
        return {
            "data": {
                "Date_field": today,
                "Company_recid": "992147000003037007",
                "Company_Entities_recid": "992147000003037011",
                "Select_Contacts": "992147000003037003",
                "Contact_Email": "pratima.mahapatra@csm.tech",
                "Candidates_Joining_Date": self.tmp_join_date.strftime("%d-%m-%Y"),
                "Verification_Checks": ["992147000002718071"],
                "Approval_required_before_BGV_processing": False
            }
        }

    def prepare_candidate_data(self):
        today = datetime.today().date().strftime("%d-%m-%Y")
        return {
            "data": {
                "Date_field": today,
                "bgvrecid": "992147000028832003",
                "Employee_Code_or__oferid": "NA",
                "Candidate_Name": self.name,
                "Father_s_Name": self.applicant_father_name,
                "Phone": self.mobile,
                "Email": self.email,
                "Date_of_Birth": self.birthday.strftime("%d-%m-%Y"),
                "Send_Invitation_Email": True
            }
        }

    def prepare_company_data(self):
        last_experience = self.env['kwonboard_work_experience'].sudo().search([('enrole_id','=', self.id)], order="effective_to DESC", limit=1)
        return {
            "data": {
                "Company_Name": last_experience.name,
                "Confirm_Company_Details": True
            }
        }

    def prepare_employment_data(self):
        last_experience = self.env['kwonboard_work_experience'].sudo().search([('enrole_id', '=', self.id)],
                                                                              order="effective_to DESC", limit=1)
        return {
            "data": {
                "Candidate_Type": "Experienced",
                "Employment_Type": "Past",
                "companyrecid": "992147000028832014",
                "Employee_Code": self.previous_emp_code,
                "Date_of_Joining": self.tmp_join_date.strftime("%d-%m-%Y"),
                "Date_of_Relieving": self.previous_date_of_relieving.strftime("%d-%m-%Y"),
                "Salary_as_per": "CTC PM",
                "Salary_per_Month": self.previous_salary_per_month,
                "Designation": last_experience.designation_name,
                "Reason_for_Leaving": self.reason_for_leaving,
                "Reporting_Manager_Name": self.previous_ra,
                "Reporting_Manager_Designation": self.previous_ra_designation,
                "Reporting_Manager_Contact_Number": self.previous_ra_phone,
                "Reporting_Manager_Email": self.previous_ra_mail,
                "HR_Name": self.previous_hr_name,
                "HR_Phone": self.previous_hr_phone,
                "HR_Email": self.previous_hr_mail,
                "Exit_Formalities_Completed": self.previous_exit_formalities_completion,
                "Reason_for_not_Completing_Exit_Formalities": self.reason_for_not_complete,
                "Do_you_have_Past_Employment": "Yes",
                "Pay_Slip_available": self.previous_payslip_available,
                "Reason_for_not_having_PaySlip": self.reason_for_not_available,
                "Releiving_Letter_available": self.previous_relieving_letter,
                "Reason_for_not_having_Relieving_Letter": self.reason_for_not_having_relieving_letter
            }
        }
