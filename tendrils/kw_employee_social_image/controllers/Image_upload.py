import base64
import re
import uuid

import werkzeug
from odoo import http, api
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
from io import BytesIO
from datetime import datetime


class ImageUpload(http.Controller):

    @http.route('/candid-image/thank-you', auth='user', website=True, csrf=False)
    def thank_you(self, **kw):
        return request.render("kw_employee_social_image.image_upload_thanks_pages", {})

    @http.route(['/candid-image/upload',
                 '/candid-image/upload/<model("hr.employee"):employee>'], auth='user', website=True, csrf=False)
    def image_upload(self, employee=False, **kw):
        if not request.env.user.employee_ids:
            return werkzeug.utils.redirect('/web')

        if not employee:
            return werkzeug.utils.redirect(f'/candid-image/upload/{request.env.user.employee_ids[0].id}')

        record = request.env['kw_employee_social_image'].sudo().search([('emp_id', '=', request.env.user.employee_ids[0].id)])
        for rec in record:
            if rec.social_image:
                return werkzeug.utils.redirect('/candid-image/thank-you')

        return request.render("kw_employee_social_image.image_upload", {'skip': record.no_of_skip if record else 0,
                                                                        'emp': request.env.user.employee_ids[0].name})

    @http.route('/candid-image/submit-image', auth='user', website=False, type="json", csrf=False, methods=['POST'])
    def submit_image(self, **kw):
        # try:
        # print(kw)
        social_photo = False
        employee_id = request.env.user.employee_ids[0].id
        src = kw['socialPhoto']
        result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
        # print('image ext >> ', ext)
        # print('image data >> ', data)

        # image = base64.decodebytes(base64.encodestring(kw['socialPhoto']))
        # image = base64.encodestring(kw['socialPhoto'].encode('utf_8'))
        if data != b'':
            social_photo = data
        exist_img = request.env['kw_employee_social_image'].sudo().search([('emp_id', '=', employee_id)])
        if exist_img:
            exist_img.sudo().write({'social_image': social_photo})
        else:
            request.env['kw_employee_social_image'].sudo().create({
                'social_image': social_photo,
                'emp_id': employee_id,
                'image_name': f'social_image_{employee_id}.jpeg'})
        # return http.request.redirect('/candid-image/thank-you', )
        return {'success': True, 'url': '/candid-image/thank-you'}
        # except AccessError:
        #     # return werkzeug.utils.redirect('/web/login?error=access')
        #     return 'None'

    @http.route('/candid-image/skip-submit', auth='user', website=True, csrf=False)
    def skip_submit(self, **kw):
        try:
            record = request.env['kw_employee_social_image'].sudo().search(
                [('emp_id', '=', request.env.user.employee_ids[0].id)])
            if record:
                record.sudo().write({'no_of_skip': record.no_of_skip + 1, 'skip_date': datetime.today().date()})
            else:
                request.env['kw_employee_social_image'].sudo().create(
                    {'no_of_skip': 1,
                     'emp_id': request.env.user.employee_ids[0].id,
                     'skip_date': datetime.today().date()})
            return http.request.redirect('/web')
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
