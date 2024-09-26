import json
import requests
from odoo import fields, models, api
import base64
import urllib.request
from datetime import datetime


class IdentificationDataSync(models.TransientModel):
    _name = "identification_sync_data_v5"
    _description = "Fetch Identification data from v5"

    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='identification_sync_employee_rel',
                                   column1='rec_id', column2='emp_id', string="Employees")
    page_no = fields.Integer(string="Page No", default=1)
    page_size = fields.Integer(string="Page Size", default=1)

    @api.multi
    def button_get_identification_data(self):
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_identification_data_url')
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            for emp in self.employee_ids:
                user_id = emp.kw_id if emp and emp.kw_id else 0
                employee_id = emp.id if emp else 0
                old_identification_list = emp.identification_ids.mapped('name')
                education_data_dict = {
                    "UserID": user_id,
                    "PageNo": self.page_no,
                    "PageSize": self.page_size,
                }
                resp = requests.post(parameter_url, headers=header, data=json.dumps(education_data_dict))
                json_data = resp.json()
                for identification in json_data:
                    emp_kw_id = int(identification.get('Int_UserID', '0'))
                    emp_code = identification.get('vchEmpCode', '')
                    name = identification.get('vchEmpName', '')
                    for details in identification.get('IdentificationDtls', []):
                        renewal_sts = int(details.get('A_Status', '0'))
                        date_of_issue = details.get('DTM_ISSUE')
                        date_of_expiry = details.get('DTM_EXPIRY')
                        doc_id = details.get('DocType_ID', '0')
                        doc_type = details.get('DocType', '')
                        doc_kw_id = details.get('UserID', '0')
                        doc_no = details.get('Identification_No', '')
                        uploaded_data_url = details.get('Doc_Url', '')
                        #     response = urllib.request.urlopen(uploaded_data_url).read()
                        try:
                            data_bytes = base64.b64encode(requests.get(uploaded_data_url).content)
                            # data_bytes = base64.b64encode(response)
                        except:
                            data_bytes = ""
                        identification_data_dict = {
                                                'emp_id': employee_id,
                                                'kw_id': int(doc_kw_id) if doc_kw_id else False,
                                                'name': doc_id,
                                                'date_of_issue': datetime.strptime(date_of_issue, "%d-%b-%Y") if date_of_issue else False,
                                                'date_of_expiry': datetime.strptime(date_of_expiry, "%d-%b-%Y") if date_of_expiry else False,
                                                'doc_number': doc_no,
                                                'uploaded_doc': data_bytes
                                            }
                        if doc_id and int(doc_id) in [1, 2, 3, 4, 5, 6]:
                            if doc_id in old_identification_list:
                                    record = self.env['kwemp_identity_docs'].sudo().search([('name', '=', doc_id), ('emp_id', '=', int(employee_id))], limit=1).write(identification_data_dict)
                            else:
                                record = self.env['kwemp_identity_docs'].create(identification_data_dict)
            self.env.user.notify_success("Employee data updated successfully")
