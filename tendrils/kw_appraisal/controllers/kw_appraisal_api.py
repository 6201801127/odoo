# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

class APIController(http.Controller):

    @http.route("/appraisal-result/", type="http", cors='*', auth="none", methods=["POST"], csrf=False)
    def send_appraisal(self):
        period_master = request.env['kw_assessment_period_master'].sudo().search([],order='id desc')
        appraisal_record = request.env['hr.appraisal'].sudo().search([('appraisal_year_rel','=',period_master[0].id or False)])
        data = []
        if appraisal_record:
            for record in appraisal_record:
                ratio = request.env['kw_appraisal_ratio'].sudo().search([
                    ('department','=',record.emp_id.department_id.id if record.emp_id.department_id else False),
                    ('division','=',record.emp_id.division.id if record.emp_id.division else False),
                    ('section','=',record.emp_id.section.id if record.emp_id.section else False),
                    ('practice','=',record.emp_id.practise.id if record.emp_id.practise else False),
                    ],limit=1)
                data.append({'emp_kw_ids':record.emp_id.kw_id,
                        'kra_score':record.kra_score,
                        'appraisal_score':record.score,
                        'total_score':record.total_score,
                        'increment_per':ratio.per_inc if ratio else False})
                # print(data)
            return json.dumps(data)
        else:
            return json.dumps({
                "status": "No Data Found",
                "message": f"Sorry, no data found for current year."
            })
                
