# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta
import mimetypes
from odoo import http
import csv
from io import StringIO
from odoo.http import request

class KwBugLifeCycle(http.Controller):
    @http.route('/download-csv-format/', type='http', auth='user')
    def generate_csv(self):
        output = StringIO()
        csv_writer = csv.writer(output)
        csv_writer.writerow(['sl_no','sub_reference','scenario_id', 'tc_id', 'pos_neg',	'scenario_description','test_case_description','test_data_action',	'expectation'])
        output.seek(0)
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Disposition', 'attachment; filename="csv_format.csv"'),
                ('Content-Type', 'text/csv')
            ]
        )

    @http.route('/download-test-scenario/<string:rec_ids>', type='http', auth='user')
    def generate_pdf_test_scenario(self, rec_ids=None, **kwargs):
        record_ids = [int(rec_id) for rec_id in rec_ids.split(',')]
        scenarios = request.env['test_scenario_master'].sudo().browse(record_ids)
        output = StringIO()
        csv_writer = csv.writer(output)
        csv_writer.writerow(['sl_no','sub_reference','scenario_id', 'tc_id', 'pos_neg',	'scenario_description','test_case_description','test_data_action',	'expectation'])

        for scenario in scenarios:
            csv_writer.writerow(['','', scenario.code, '', '', scenario.scenario_description, '', '', ''])
        output.seek(0)

        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Disposition', 'attachment; filename="test_scenarios.csv"'),
                ('Content-Type', 'text/csv')
            ]
        )

    @http.route('/download-snap-bug/<int:rec_id>', type='http', auth='user')
    def get_bug_snap_download(self,rec_id=None,**kwargs):
        bug_snap = request.env['bug_snap_log_table'].sudo().browse(rec_id)
        attachment = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'bug_snap_log_table'),
            ('res_id', '=', rec_id),
            ('res_field', '=', 'snap_shot')  # Adjust this if the field name is different
        ], limit=1)

        if not attachment:
            return request.not_found()
        file_data = base64.b64decode(attachment.datas)
        mime_type = attachment.mimetype or 'application/octet-stream'
        extension = mimetypes.guess_extension(mime_type) or ''
        if isinstance(bug_snap.date, datetime):
            date_obj = bug_snap.date
        else:
            date_obj = datetime.strptime(str(bug_snap.date), '%Y-%m-%d %H:%M:%S')  # Adjust format if necessary
        adjusted_date_obj = date_obj + timedelta(hours=5, minutes=30)
        formatted_date = adjusted_date_obj.strftime('%d-%m-%Y_%H-%M-%S')
        
        original_file_name = f"{bug_snap.snap_bug_id.number}/{formatted_date}{extension}"

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', mime_type),
                ('Content-Disposition', f'attachment; filename="{original_file_name}"')
            ]
        )