from odoo import http
from odoo.http import request
import json

class FileForwardData(http.Controller):

    @http.route(['/filesforward'], type='http', auth='public', csrf=False, methods=['POST'])
    def get_forward_details(self, **kwargs):
        forward_details_data = request.env['folder.tracking.information'].sudo().search([])
        foward_det = []
        for rec in forward_details_data:
            vals={
                'fileforward_id': rec.id,
                'forwarded_by': rec.forwarded_by.name,
                'forwarded_date': rec.forwarded_date,
                'forwarded_to_user': rec.forwarded_to_user.name,
                'forwarded_to_dept': rec.forwarded_to_dept.name,
                'file_id': rec.create_let_id.id,
                'file_name': rec.create_let_id.folder_name,
                'file_number': rec.create_let_id.number,
            }
            foward_det.append(vals)
        data = {"response": foward_det}
        print('=========================letter==========================',foward_det)
        loaded_r = json.dumps(dict(response=str(foward_det)))
        return loaded_r


    @http.route(['/filesforwardcall'], type='http', auth='public', csrf=False, methods=['POST'])
    def get_forward_call_details(self, file_forward_id=None, **kwargs):
        foward_det = []
        if file_forward_id:
            forward_details_data = request.env['folder.tracking.information'].sudo().search([('id', '=', file_forward_id)], limit=1)
            if forward_details_data:
                for rec in forward_details_data:
                    vals = {
                        'fileforward_id': rec.id,
                        'forwarded_by': rec.forwarded_by.name,
                        'forwarded_date': rec.forwarded_date,
                        'forwarded_to_user': rec.forwarded_to_user.name,
                        'forwarded_to_dept': rec.forwarded_to_dept.name,
                        'file_id': rec.create_let_id.id,
                        'file_name': rec.create_let_id.folder_name,
                        'file_number': rec.create_let_id.number,
                    }
                    foward_det.append(vals)
                loaded_r = json.dumps(dict(response=str(foward_det)))
                return loaded_r
            else:
                message = "File Forward data not found"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r
        else:
            message = "Please pass the ID"
            loaded_r = json.dumps(dict(response=str(message)))
            return loaded_r








    @http.route(['/letterlist'], type='http', auth='public', csrf=False, methods=['POST'])
    def get_letter_list_details(self, **kwargs):
        letter_details_data = request.env['muk_dms.file'].sudo().search([])
        letter_det = []
        for rec in letter_details_data:
            vals={
                'id': rec.id,
                'file_name': rec.name,
            }
            letter_det.append(vals)
        data = {"response": letter_det}
        print('=========================letter==========================',letter_det)
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r

    @http.route(['/lettercall'], type='http', auth='public', csrf=False, methods=['POST'])
    def get_letter_call_details(self, letter_id=None, **kwargs):
        letter_det = []
        if letter_id:
            letter_details_data = request.env['muk_dms.file'].sudo().search([('id', '=', letter_id)], limit=1)
            if letter_details_data:
                for rec in letter_details_data:
                    vals = {
                        'id': rec.id,
                        'file_name': rec.name,
                        'attachment': rec.content,
                    }
                    letter_det.append(vals)
                loaded_r = json.dumps(dict(response=str(letter_det)))
                return loaded_r
            else:
                message = "File not found"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r
        else:
            message = "Please pass the ID"
            loaded_r = json.dumps(dict(response=str(message)))
            return loaded_r


    @http.route(['/closedfile'], type='json', auth='public', csrf=False, methods=['POST'])
    def get_closed_file(self, **kwargs):
        forward_details_data = request.env['folder.master'].sudo().search([('state', '=', 'closed')])
        foward_det = []
        for rec in forward_details_data:
            vals={
                'id': rec.id,
                'folder_name': rec.folder_name,
                'number': rec.number,
                'current_owner_id': rec.current_owner_id.id,
            }
            foward_det.append(vals)
        data = {'status': 200, 'response': foward_det, 'message': 'Success'}
        return data