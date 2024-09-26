# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import requests
import json
from ast import literal_eval


class JobPositionsSync(models.Model):
    _name = "kw_recruitment_career_sync_log"
    _description = "Stores sync log with career site."
    _order = "create_date desc"

    name = fields.Char(string="Name")
    date = fields.Date(string='Date', default=fields.Date.context_today, )
    payload = fields.Char(string="Payload")
    status = fields.Char("Status")

    def sync_failed_log(self):
        source_id = self.env.ref('kw_recruitment.source_009')
        other_qualification_id = self.env.ref('kw_recruitment.kw_qualificatio_data1').id
        initial_stage_id = self.env.ref('hr_recruitment.stage_job1').id
        records = self.search([('status', '=', 'Failed')])
        if records:
            for record in records:
                data = {}
                json_acceptable_string = record.payload.replace("'", "\"")
                payload = json.loads(json_acceptable_string)

                location_id = self.env['kw_recruitment_location'].search([('code', '=', 'bhubaneshwar')], limit=1)

                data['exp_year'] = payload['exp_year']
                # data['stage_id'] = payload['exp_month']
                data['stage_id'] = initial_stage_id
                data['partner_name'] = payload['partner_name']
                data['email_from'] = payload['email_from']
                data['partner_mobile'] = payload['partner_mobile']
                data['qualification_ids'] = [[6, 0, [payload['qualification']]]]
                data['description'] = payload['description']
                data['job_location_id'] = location_id and location_id.id or False

                if payload['qualification'] == other_qualification_id:
                    data['other_qualification'] = 'Others'

                if 'file_name' and 'attachment' in payload:
                    file_name = payload['file_name']
                    doc_file = payload['attachment']
                    if 'document_ids' in self.env['hr.applicant'].sudo()._fields:
                        data['document_ids'] = [[0, 0, {'content_file': doc_file, 'file_name': file_name}]]
                    # else:
                    #     data['attachment_ids']  =  [[0, 0,
                    #                                     {'name': file_name,
                    #                                     'datas_fname': file_name,
                    #                                     'datas': doc_file,
                    #                                     'res_name': payload['name'],
                    #                                     'res_model': 'hr.applicant',
                    #                                     'res_model_name': 'Applicant'
                    #                                     }
                    #                                 ]]
                applicant = self.env['hr.applicant'].create(data)
        return True
