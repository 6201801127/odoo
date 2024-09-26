import requests, json
import datetime
import base64
from datetime import datetime, timedelta
import urllib.request

from odoo import models, fields, api


class SyncConsultantData(models.Model):
    _name = "sync_consultant_data"
    _description = "Independent Consultant"
    _order = "sync_link_id desc"

    sync_link_id = fields.Integer('Id')
    name = fields.Char('Name')
    email_id = fields.Char('Email')
    phone_no = fields.Char('Phone No.')
    industry_segment = fields.Char(string='Industry Segment')
    consultant_cv = fields.Binary(string='Resume', attachment=True, store=True)
    consultant_cv_name = fields.Char(string='Resume File')
    industry_id = fields.Integer(string='Industry Id')
    created_on = fields.Datetime('Date')
    deleted_flag = fields.Text('Deleted Flag')
    country_preference = fields.Char('Location')
    qualification = fields.Char(string='Qualification')
    course = fields.Char(string='Course')
    certification = fields.Char(string='Certification')
    comments = fields.Char(string='Language')
    experience = fields.Char(string='Experience')
    headline = fields.Char(string='Headline')
    active = fields.Boolean(string='Active', default=True)

    @api.multi
    def sync_consultant_data_upload(self, *args):
        sync_data_update_rec = self.env['sync_consultant_data'].search([('active', 'in', [True, False])])
        project_url = self.env.ref('kw_resource_management.sync_consultant_parameter').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        current_date = datetime.now()
        three_years_ago = current_date - timedelta(days=3 * 365)
        ten_days_ago = current_date - timedelta(days=10)
        if not sync_data_update_rec.exists():
            data_to_encode = {
                "method": "industryconsultants",
                "date": str(three_years_ago)
            }
        else:
            data_to_encode = {
                "method": "industryconsultants",
                "date": str(ten_days_ago)
            }

        data = json.dumps(data_to_encode)
        resp_result = requests.post(project_url, headers=header, data=data)
        resp = json.loads(resp_result.text)

        if 'result' in resp:
            result_data = resp['result']
            existing_records_ids = sync_data_update_rec.mapped('id')
            for rec in result_data:
                sync_link_id = rec['intId']
                if 'path' in resp:
                    cv_content = resp['path']
                cv_file = rec['vchResume']
                full_file_url = cv_content + cv_file
                response = urllib.request.urlopen(full_file_url.replace(" ", "%20"))
                encoded_data = base64.b64encode(response.read())

                # existing_record = sync_data_update_rec.filtered(lambda r: r.sync_link_id == sync_link_id)
                resource_data = {
                    'name': rec['vchName'],
                    'email_id': rec['vchEmailId'],
                    'phone_no': rec['vchPhoneNo'],
                    'industry_segment': rec['vchIndustrySegment'],
                    'consultant_cv': encoded_data,
                    'industry_id': rec['intIndustryId'],
                    'created_on': rec['dtmCreatedOn'],
                    'deleted_flag': rec['bitDeletedFlag'],
                    'country_preference': rec['vchCountryPreference'],
                    'qualification': rec['vchQualification'],
                    'course': rec['vchCourse'],
                    'certification': rec['vchCertification'],
                    'comments': rec['vchComments'],
                    'experience': rec['intExperience'],
                    'headline': rec['vchHeadline'],
                    'consultant_cv_name': rec['vchResume'],
                }

                if sync_link_id in existing_records_ids:
                    pass
                else:
                    resource_data['sync_link_id'] = sync_link_id
                    self.sudo().create(resource_data)
        else:
            pass

        return {'status': 'success'}
