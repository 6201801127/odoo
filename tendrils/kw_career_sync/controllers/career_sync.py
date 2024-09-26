# -*- coding: utf-8 -*-
import json
import base64
from odoo import http
from odoo.http import request
from datetime import date, timedelta, datetime


class APIController(http.Controller):

    @http.route("/submit-applicant/<job_position_id>", type="http", cors='*', auth="none", methods=["POST"], csrf=False)
    def save_applicant(self, job_position_id=None, **payload):
        payload['job_position_id'] = job_position_id
        # print("Received Payload Is.", payload)
        data_payload = str(payload)
        log = request.env['kw_recruitment_career_sync_log'].sudo()
        #try:
        job_position_id = int(job_position_id)
        #except Exception:
        #    log.create({'name': 'Applicant Create', 'payload': data_payload, 'status': 'Failed', })
        if not job_position_id:
            return json.dumps({
                "status": "failed",
                "message": f"Invalid job position id, {job_position_id}."
            })
               
        else:
            job_position = request.env['kw_hr_job_positions'].sudo().search([('id', '=', job_position_id)])
            if len(job_position) == 0:
                return json.dumps({
                    "status": "failed",
                    "message": f"The job id, {job_position_id} is not available in the database."
                })
            if 'job_location_id' not in payload:
                return json.dumps({
                    "status": "failed",
                    "message": "Missing required parameter (job_location_id)."
                })
            job_location_id = int(payload['job_location_id'])
            job_location = request.env['kw_recruitment_location'].sudo().browse(job_location_id)
            if not job_location.exists():
                return json.dumps({
                    "status": "failed",
                    "message": f"The job location id, {job_location_id} is not available in the database."
                })
            if 'partner_name' not in payload:
                return json.dumps({
                    "status": "failed",
                    "message": "Missing required parameter (partner_name)."
                })
            if 'partner_mobile' not in payload:
                return json.dumps({
                    "status": "failed",
                    "message": "Missing Required Parameter (partner_mobile)"
                })
            if 'email_from' not in payload:
                return json.dumps({
                    "status": "failed",
                    "message": "Missing Required Parameter (email_from)"
                })
            else:
                Applicant = request.env['hr.applicant'].sudo()
                payload['job_position'] = job_position_id
                payload['name'] = f"{payload['partner_name']}'s Application"

                payload['current_ctc'] = float(payload['current_ctc']) if 'current_ctc' in payload else False
                payload['salary_expected'] = float(payload['salary_expected']) if 'salary_expected' in payload else False
                payload['notice_period'] = int(payload['notice_period']) if 'notice_period' in payload else False
                payload['job_location_id'] = int(payload['job_location_id']) if 'job_location_id' in payload else False

                payload['job_id'] = job_position.job_id.id if job_position.job_id else False
                # if ('job_location_id' in payload and payload['job_location_id'] == '') or ('job_location_id' not in payload):
                #     # del payload['job_location_id']
                #     if job_position.address_id and len(job_position.address_id) == 1:
                #         payload['job_location_id'] = job_position.address_id[0].id

                if ('job_location_id' in payload and payload['job_location_id'] == '') \
                        or ('job_location_id' not in payload):
                    if job_position.address_id and len(job_position.address_id) == 1:
                        payload['job_location_id'] = job_position.address_id[0].id
                # if ('job_location_id' in payload and payload['job_location_id'] != '') \
                #         and payload['job_location_id'] in job_position.address_id.ids:
                #     payload['job_location_id'] = payload['job_location_id']
                
                # payload['job_location_id'] = job_position.address_id.id if job_position.address_id else False
                payload['department_id'] = job_position.department_id.id if job_position.department_id else False
                if 'qualification' in payload:
                    if payload['qualification'] == "":
                        del payload['qualification']
                    else:
                        if payload['qualification'].isdigit():
                            qual_id = request.env['kw_qualification_master'].sudo().search([('id', '=', payload['qualification'])])
                            if len(qual_id) == 0:
                                return json.dumps({"status": "failed",
                                                   "message": f"The qualification id, {payload['qualification']} is not available in the database."})
                            else:
                                payload['qualification_ids'] = [[6, 0, [qual_id.id]]]
                        else:
                            return json.dumps({"status": "failed", "message": f"The qualification id should be in integer format."})
                # try:
                # Create applicant
                source_code = 'konnecta' if 'source' in payload and payload['source'] == 'konnecta' else 'website'
                source_id = request.env['utm.source'].sudo().search([('code', '=', source_code)])
                payload['source_id'] = source_id.id
                payload['code_ref'] = source_id.code
                payload['document_ids'] = []
                if 'attachment' in payload:
                    # base64.encodestring(payload['attachment'].read())
                    # filename = payload['attachment'].filename
                    file_name = payload['file_name'] if 'file_name' in payload else False
                    # file = base64.encodestring(payload['attachment'].read())
                    file = payload['attachment']
                    payload['document_ids'].append([0, 0, {'content_file': file, 'file_name': file_name}])
                    
                if 'passport_attachment' in payload:
                    passport_name = payload['passport_photo'] if 'passport_photo' in payload else False
                    passport_file = payload['passport_attachment']
                    payload['document_ids'].append([0, 0, {'content_file': passport_file, 'file_name': passport_name}])

                # if 'document_ids' in request.env['hr.applicant'].sudo()._fields and not payload['document_ids']:
                    # FileBase64 = base64.b64encode(file.read())
                    # payload['document_ids'] = [[0, 0, {'content_file': file, 'file_name': file_name}]]
                    # record = Applicant.create(payload)
                # else:
                del payload['passport_attachment'], payload['passport_photo'], payload['file_name'], payload['attachment'], payload['job_position_id']

                record = Applicant.create(payload)

                if 'document_ids' not in request.env['hr.applicant'].sudo()._fields and file_name:
                    if 'attachment' in payload and file_name:
                        record.sudo().write({'attachment_ids': [[0, 0, {'name': file_name,
                                                                        'datas_fname': file_name,
                                                                        'datas': file,
                                                                        'res_name': payload['name'],
                                                                        'res_model': 'hr.applicant',
                                                                        'res_model_name': 'Applicant',
                                                                        'res_id': record.id, }
                                                                    ]]
                                                })
                    if 'passport_attachment' in payload and file_name:
                        record.sudo().write({'attachment_ids': [[0, 0, {'name': passport_name,
                                                                        'datas_fname': passport_name,
                                                                        'datas': passport_file,
                                                                        'res_name': payload['name'],
                                                                        'res_model': 'hr.applicant',
                                                                        'res_model_name': 'Applicant',
                                                                        'res_id': record.id, }
                                                                    ]]
                                                })
                    # else:
                    #     record.sudo().write({'attachment_ids': [[0, 0, {'datas': file,
                    #                                                     'res_name': payload['name'],
                    #                                                     'res_model': 'hr.applicant',
                    #                                                     'res_model_name': 'Applicant',
                    #                                                     'res_id': record.id, }
                    #                                              ]]
                    #                          })
                log.create({
                    'name': 'Applicant Create',
                    'payload': data_payload,
                    'status': 'Success',
                })
                # except Exception as e:
                # print(e)
                #    log.create({
                #        'name': 'Applicant Create',
                #        'payload': data_payload,
                #        'status': 'Failed',
                #    })
                #    return json.dumps({"status": "failed", "message": "Error occurred during submission."})
                # else:
            return json.dumps({"status": "success", "message": "Applicant created successfully."})

    @http.route("/applicant-cv-matching", methods=['POST'], auth='none', type='json', csrf=False, cors='*',
                website=False)
    def applicant_cv_data(self, from_date, to_date):
        resource_json_data = {
            "FromDate": from_date,
            "ToDate": to_date,
        } 
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else False
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else False
        if not from_date_obj or not to_date_obj:
            return json.dumps([{'status': 401, 'message': 'Please enter correct from_date and to_date'}])
        if from_date_obj >= to_date_obj:
            return json.dumps([{'status': 401, 'message': 'Please enter from_date less than to_date'}])

        data = []
        applicant_data = request.env['hr.applicant'].sudo().search(
            [('create_date', '>=', from_date), ('create_date', '<=', to_date)])
        
        for applicant in applicant_data:
            attachment_cv = applicant.document_ids[0] if len(applicant.document_ids) > 1 else applicant.document_ids
            # print("applicant.document_ids >>> ",applicant.document_ids, attachment_cv)

            if attachment_cv:
                cv_dms_obj = attachment_cv.sudo().dms_file_id
                try:
                    # print(applicant.id, cv_dms_obj.id, cv_dms_obj.file_public_url)
                    if cv_dms_obj.file_public_url is False:
                        cv_dms_obj.create_public_url()
                except Exception as e:
                    # print(e)
                    pass
                # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # final_url = '%s/web/content/%s' % (base_url, attachment_cv.ir_attachment_id.id) 
                # file_url = f"{base_url}/web/content?id={attachment_cv.dms_file_id.id}&field=content&model=kw_dms.file&filename_field=name&download=true"
                file_url = cv_dms_obj.file_public_url
                if file_url is not False:
                    temp_applicant_dict = {
                        "job_position_id": applicant.job_position.id,
                        "applicant_id": applicant.id,
                        "applicant_cv": f"{file_url}&download=1" if attachment_cv.dms_file_id else ''
                    }
                    data.append(temp_applicant_dict)
        return data    
       


    @http.route("/submit-usa-applicant/<job_position_id>", type="http", cors='*', auth="none", methods=["POST"], csrf=False)
    def save_usa_applicant(self, job_position_id=None, **payload):
        # payload['job_position_id'] = job_position_id
        data_payload = str(payload)
        log = request.env['kw_recruitment_career_sync_log'].sudo()
        job_position_id = int(job_position_id)
        try:
        
            if not job_position_id:
                return json.dumps({
                    "status": "failed",
                    "message": f"Invalid job position id, {job_position_id}."
                })
                
            else:
                job_position = request.env['kw_hr_job_positions'].sudo().search([('id', '=', job_position_id)])
                if len(job_position) == 0:
                    return json.dumps({
                        "status": "failed",
                        "message": f"The job id, {job_position_id} is not available in the database."
                    })
                
                if 'partner_name' not in payload:
                    return json.dumps({
                        "status": "failed",
                        "message": "Missing required parameter (partner_name)."
                    })
                if 'partner_mobile' not in payload:
                    return json.dumps({
                        "status": "failed",
                        "message": "Missing Required Parameter (partner_mobile)"
                    })
                if 'email_from' not in payload:
                    return json.dumps({
                        "status": "failed",
                        "message": "Missing Required Parameter (email_from)"
                    })
                else:
                    curr = (str(payload['salary_expected']).split(' ')[0]) if 'salary_expected' in payload else False
                    if curr:
                        curr = request.env['res.currency'].sudo().search([('name','=',curr)])
                    Applicant = request.env['hr.applicant'].sudo()
                    payload['job_position'] = job_position_id
                    payload['name'] = f"{payload['partner_name']}'s Application"
                    
                    payload['current_ctc'] = float(payload['current_ctc']) if payload['current_ctc'] != 'false' else False
                    payload['salary_expected'] = float(str(payload['salary_expected']).split(' ')[1]) if 'salary_expected' in payload else False
                    if curr:
                        payload['company_currency_id'] = curr.id
                    payload['notice_period'] = int(payload['notice_period']) if 'notice_period' in payload else False
                    payload['job_id'] = job_position.job_id.id if job_position else False
                
                    payload['department_id'] = job_position.department_id.id if job_position.department_id else False
                    if 'qualification' in payload:
                        if payload['qualification'] == "":
                            del payload['qualification']
                        else:
                            if payload['qualification'].isdigit():
                                qual_id = request.env['kw_qualification_master'].sudo().search([('id', '=', payload['qualification'])])
                                if len(qual_id) == 0:
                                    return json.dumps({"status": "failed",
                                                    "message": f"The qualification id, {payload['qualification']} is not available in the database."})
                                else:
                                    payload['qualification_ids'] = [[6, 0, [qual_id.id]]]
                            else:
                                return json.dumps({"status": "failed", "message": f"The qualification id should be in integer format."})
                    # Create applicant
                    source_code = 'konnecta' if 'source' in payload and payload['source'] == 'konnecta' else 'website'
                    source_id = request.env['utm.source'].sudo().search([('code', '=', source_code)])
                    payload['source_id'] = source_id.id
                    payload['code_ref'] = source_id.code
                    payload['document_ids'] = []
                    del payload['qualification']
                    # del payload['job_location_id']
                    if 'attachment' in payload:
                        file_name = payload['file_name'] if 'file_name' in payload else False
                        file = payload['attachment']
                        payload['document_ids'].append([0, 0, {'content_file': file, 'file_name': file_name}])
                    record = Applicant.sudo().create(payload)

                    if 'document_ids' not in request.env['hr.applicant'].sudo()._fields and file_name:
                        if 'attachment' in payload and file_name:
                            record.sudo().write({'attachment_ids': [[0, 0, {'name': file_name,
                                                                            'datas_fname': file_name,
                                                                            'datas': file,
                                                                            'res_name': payload['name'],
                                                                            'res_model': 'hr.applicant',
                                                                            'res_model_name': 'Applicant',
                                                                            'res_id': record.id, }
                                                                        ]]})
    
                    log.create({
                        'name': 'Applicant Create',
                        'payload': data_payload,
                        'status': 'Success',
                    })
                    return json.dumps({"status": "success", "message": "Applicant created successfully."})
        except Exception as e:
            # print(e,"=====================exception")
            log.create({
                'name': 'Applicant Create',
                'payload': data_payload,
                'status': 'Failed' + e,
            })
            return json.dumps({"status": "success", "message": "Applicant creation of failed."})

