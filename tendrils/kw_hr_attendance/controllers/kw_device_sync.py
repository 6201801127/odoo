# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SyncAttendanceDevice(http.Controller):
    @http.route("/sync_attendance_device", methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def sync_device(self, **args):
        try:
            device_id = ''
            device_record = request.env['kw_device_master'].sudo().search([('sync_status', '=', True)])
            mapped_device_ids = ",".join(device_record.mapped(lambda r: str(r.device_id)))
            if 'location' in args and args['location'] == 'HO':
                ho_ids = device_record.filtered(lambda r: r.location == 'ho')
                mapped_ho_ids = ",".join(ho_ids.mapped(lambda r: str(r.device_id)))
                device_id = mapped_ho_ids

            elif 'location' in args and args['location'] == 'Branch':
                branch_ids = device_record.filtered(lambda r: r.location == 'branch')
                mapped_branch_ids = ",".join(branch_ids.mapped(lambda r: str(r.device_id)))
                device_id = mapped_branch_ids
            else:
                device_id = mapped_device_ids

            data = {
                "device_id": device_id
            }
        except Exception as e:
            data = {'status': 500, 'error_log': str(e)}
        return data
