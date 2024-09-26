import datetime
from datetime import timedelta
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError
import requests, json
import werkzeug
import base64
from odoo.tools.mimetypes import guess_mimetype
import logging
import base64


_logger = logging.getLogger(__name__)

class DploadDocument(models.Model):
    _name = 'kw_upload_cv'
    _description = " Quick create Applicants application"
    _rec_name = 'file_name'
    _order = 'id desc'

    documents = fields.Binary(string='Upload Document', attachment=True, track_visibility='onchange', store=True)
    file_name = fields.Char("File Name", track_visibility='onchange')
    url = fields.Char("Url", track_visibility='onchange')
    # binary_data = fields.Text("Binary Data", track_visibility='onchange')
    applicant_id = fields.Many2one("hr.applicant")
    
    def check_document(self):
        allowed_extensions = ['pdf', 'docx', 'doc', 'odt']
        max_size = 2 * 1024 * 1024  # 2 MB

        for record in self:
            if record.documents:
                file_extension = record.file_name.split('.')[-1].lower()
                # print("========file_extension================",file_extension,mimetype)
                # if file_extension not in allowed_extensions:
                #     raise ValidationError("Invalid file type. Allowed types: %s" % ', '.join(allowed_extensions))

                if len(record.documents) > max_size:
                    raise ValidationError("File size exceeds the limit of 2MB.")

    @api.model
    def create(self, vals):
        record = super(DploadDocument, self).create(vals)
        
        attachment_id = self.env['ir.attachment'].search(
            [('res_id', '=', record.id), ('res_model', '=', 'kw_upload_cv'),
             ('res_field', '=', 'documents')])
        if attachment_id:
            attachment_id.write({'public': True})
            attachment_url = "/cv/download/" + str(attachment_id.id) + "/" + str(record.id)
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # base_url = 'http://172.27.30.120:8069' #testing
            url = base_url + attachment_url
            record.url = url
        return record
    
    @api.multi
    def call_parse_api(self):
        if self.documents:
            self.check_document()
            try:
                # if not self._context.get('parser'):
                #     attachment_id = self.env['ir.attachment'].search(
                #         [('res_id', '=', self.id), ('res_model', '=', 'kw_upload_cv'),
                #         ('res_field', '=', 'documents')])
                #     attachment_id.write({'public': True})
                #     # base64_data = attachment_id.datas
                #     # binary_data = base64.b64decode(base64_data)
                #     # encoded_binary_data = base64.b64encode(binary_data).decode('utf-8')

                #     attachment_url = "/cv/download/" + str(attachment_id.id) + "/" + str(self.id)
                #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

                #     # base_url = 'http://172.27.30.120:8069' #testing

                #     url = base_url + attachment_url
                #     # self.url = base_url + attachment_url
                #     update_query = f"""update kw_upload_cv set url='{url}' where id={self.id}"""
                #     # update_query = f"""update kw_upload_cv set url='{url}', binary_data='{encoded_binary_data}' where id={self.id}"""
                #     self.env.cr.execute(update_query)

                url = self.url            
                cv_parser_api_url = self.env['ir.config_parameter'].sudo().get_param('recruitment_parser_cv_url')

                payload = json.dumps({
                    "link": self.url if self.url else url,
                    # "link": encoded_binary_data,
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.post(cv_parser_api_url, headers=headers, data=payload).text
                data = json.loads(response)
                if data:
                    log_id = self.env['cv_skills_api_log'].sudo().create({'payload': payload,
                                                                'response': data,
                                                                'status': data.get('status'),
                                                                'ocr': data.get('ocr')})
                    exp_data = data.get('experience') if data.get('experience') else 0
                    cv_qualification = data.get('highest_qualification') if data.get('highest_qualification') else ''
                    return_qualification = False
                    q_data = self.env['kw_qualification_master']
                    cvq_data = self.env['cv_qualification_master']
                    if cv_qualification:
                        qualification_data = cvq_data.sudo().search([('name', 'ilike', cv_qualification)], limit=1)
                        if qualification_data:
                            return_qualification = qualification_data
                        else:
                            return_qualification = cvq_data.sudo().create({
                                'name': cv_qualification,
                            })
                    cv_skills = data.get('technical_skills') if data.get('technical_skills') else ''
                    return_skill = []
                    cv = self.env['cv_skill_master'].sudo()
                    if cv_skills:
                        skill_data = cv.search([('name', 'ilike', cv_skills)])
                        if skill_data:
                            return_skill = skill_data.ids
                        else:
                            for skill in cv_skills:
                                skill_data = cv.create({
                                    'name': skill,
                                })
                                return_skill.append(skill_data.id)
                    gender = ''
                    if data.get('gender') != None:
                        if 'Male' in data.get('gender'):
                            gender = 'male'
                        elif 'Female' in data.get('gender'):
                            gender = 'female'
                        else:
                            gender = 'others'
                    view_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
                    doc = [[0, 0, {'file_name': self.file_name,
                                'content_file': self.documents, }]]
                    action = {
                        'name': 'Upload CV',
                        'type': 'ir.actions.act_window',
                        'res_model': 'hr.applicant',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'current',
                        'view_id': view_id,
                        'context': {
                            'default_partner_name': data['applicant_name'] if 'applicant_name' in data else '',
                            'default_gender': gender,
                            'default_email_from': data.get('email') if data.get('email') else '',
                            'default_partner_mobile': data.get('mobile_no') if data.get('mobile_no') else '',
                            'default_current_location': data.get('current_location')[0] if data.get(
                                'current_location') else '',
                            'default_exp_year': exp_data.get('years') if exp_data else 0,
                            'default_exp_month': exp_data.get('months') if exp_data else 0,
                            'default_cv_qualification': return_qualification.id if return_qualification else '',
                            'default_cv_skill': return_skill if return_skill else [],
                            'default_document_ids': doc,
                            'default_qualification_ids': [(6, 0, q_data.sudo().search(
                                [('name', 'ilike', cv_qualification)]).ids)] if cv_qualification else [],
                            'default_cv_api_log_id':log_id.id,
                            'active_id': self.id,
                            },
                    }
                    return action
            except requests.exceptions.RequestException as e:
                _logger.error('Something went wrong.Please try again later: %s', e)
                raise UserError('Something went wrong.Please try again later: %s' % str(e))
            except json.JSONDecodeError as e:
                _logger.error('No response from server.Please try again later: %s', e)
                raise UserError('No response from server.Please try again later: %s' % str(e))
            except Exception as e:
                _logger.error('Unexpected error.Please try again later: %s', e)
                raise UserError('Unexpected error.Please try again later: %s' % str(e))
        else:
            raise ValidationError('Please Select the File first.')
