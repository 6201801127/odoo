# -*- coding: utf-8 -*-

import requests
import json

BGV_AUTH_URL = 'https://accounts.zoho.com/oauth/v2'
BGV_API_URL = 'https://accounts.zoho.com/oauth/v2/veecheck/bgv-management/form'
BGV_REFRESH_TOKEN = '1000.ff0e00f0b83a73c7ee74cc2e2ed9bfc3.d7ac51c656dd74030921a2e7237eebd9'
BGV_CLIENT_ID = '1000.XYFDRCEZZZLJ3GV9JQCB1RN1U9T0OG'
BGV_CLIENT_SECRET = '3558746cd93e0a0561cf5116b1ea0d5f45b3e7bb43'
BGV_GRANT_TYPE = 'refresh_token'


def refresh_access_token():
    url = f"{BGV_AUTH_URL}/token?refresh_token={BGV_REFRESH_TOKEN}&client_id={BGV_CLIENT_ID}&client_secret={BGV_CLIENT_SECRET}&grant_type={BGV_GRANT_TYPE}"

    payload = {}
    files = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    # print("response.text >> ", response.text)
    # {
    #     "access_token": "1000.e658e6c2582d90c64747357bfcf1dc32.bbb9091f2d789d657d7fbdbd2e32bb9a",
    #     "scope": "ZohoCreator.form.CREATE ZohoCreator.report.READ",
    #     "api_domain": "https://www.zohoapis.com",
    #     "token_type": "Bearer",
    #     "expires_in": 3600
    # }
    rec = json.loads(response.text)
    return rec.get("access_token", False)


def add_bgv_request(access_token, data):
    url = f"{BGV_API_URL}/Add_BGV_Request"

    payload = json.dumps({
        "data": {
            "Date_field": data.get("apply_date"),
            "Company_recid": "992147000003037007",
            "Company_Entities_recid": "992147000003037011",
            "Select_Contacts": "992147000003037003",
            "Contact_Email": data.get("contact_email", "pratima.mahapatra@csm.tech"),
            "Candidates_Joining_Date": data.get("joining_date"),
            "Verification_Checks": ["992147000002718071"],
            "Approval_required_before_BGV_processing": False
        }
    })
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response.text", response.text)

    rec = json.loads(response.text)
    # if rec.get('code', False) == 3000:
    #     return rec.get('data', False).get('ID', False)
    return rec


def add_candidate(access_token, data):
    url = f"{BGV_API_URL}/Candidate_Bulk_Data_Processing"

    payload = json.dumps({
        "data": {
            "Date_field": data.get("date_field"),  # "20-03-2023",
            "bgvrecid": data.get("bgv_rec_id"),  # "992147000028162046",
            "Employee_Code_or__oferid": data.get("employee_code", "NA"),
            "Candidate_Name": data.get("candidate_name"),
            "Father_s_Name": data.get("fathers_name"),
            "Phone": data.get("phone"),
            "Email": data.get("email"),
            "Date_of_Birth": data.get("date_of_birth"),  # "30-03-2003",
            "Send_Invitation_Email": True
        }
    })
    headers = {
        'Authorization': f"Zoho-oauthtoken {access_token}",
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response.text", response.text)

    rec = json.loads(response.text)
    return rec


def add_company(access_token, data):
    url = f"{BGV_API_URL}/Company"

    payload = json.dumps({
        "data": {
            "Company_Name": data.get("company_name"),
            "Confirm_Company_Details": True
        }
    })
    headers = {
        'Authorization': f"Zoho-oauthtoken {access_token}",
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response.text", response.text)

    rec = json.loads(response.text)
    if rec.get('code', False) == 3000:
        return rec.get('data', False).get('ID', 0)
    return rec


def add_experience(access_token, data):
    url = f"{BGV_API_URL}/Candidate_Employment_Records"

    payload = json.dumps({
        "data": {
            "Candidate_Type": "Experienced",
            "Employment_Type": "Past",
            "companyrecid": data.get("company_rec_id"),  # "992147000028566003",
            "Employee_Code": data.get("employee_code"),  # "01-2003",
            "Date_of_Joining": data.get("date_of_joining"),  # "20-04-2023",
            "Date_of_Relieving": data.get("date_of_leaving"),  # "10-04-2023",
            "Salary_as_per": "CTC PM",
            "Salary_per_Month": data.get("salary"),  # "25000",
            "Designation": data.get("designation"),  # "Developer",
            "Reason_for_Leaving": data.get("reason_for_leaving"),  # "Better opportunity",
            "Reporting_Manager_Name": data.get("rm_name"),  # "Bhargav",
            "Reporting_Manager_Contact_Number": data.get("rm_phone"),  # "9876543210",
            "Reporting_Manager_Email": data.get("rm_email"),  # "rm@email.com",
            "Reporting_Manager_Designation": data.get("rm_designation"),  # "rm@email.com",
            "HR_Name": data.get("hr_name"),  # "HR Maya",
            "HR_Phone": data.get("hr_phone"),  # "8790654321",
            "HR_Email": data.get("hr_email"),  # "hr@email.com",
            "Exit_Formalities_Completed": data.get("exit_formalities_completed"),  # "Yes",
            "Reason_for_not_Completing_Exit_Formalities": data.get("reason_for_not_completing_exit_formalities", ""),
            "Do_you_have_Past_Employment": "Yes",
            "Pay_Slip_available": data.get("payslip_available"),  # "Yes",
            "Reason_for_not_having_PaySlip": data.get("reason_for_not_having_payslip", ""),
            "Releiving_Letter_available": data.get("relieving_letter_available"),  # "Yes",
            "Reason_for_not_having_Relieving_Letter": data.get("reason_for_not_having_relieving_letter")
        }
    })
    headers = {
        'Authorization': f"Zoho-oauthtoken {access_token}",
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response.text", response.text)

    rec = json.loads(response.text)
    return rec
