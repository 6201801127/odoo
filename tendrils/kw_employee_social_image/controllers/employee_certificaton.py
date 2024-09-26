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

    @http.route(['/employee_certification/update',
                 '/employee_certification/update/<model("hr.employee"):employee>'], auth='user', website=True, csrf=False)
    def update_employee_certification(self, employee=False, **kw):
        if not request.env.user.employee_ids:
            return werkzeug.utils.redirect('/web')

        record = request.env['kw_update_employee_certification'].sudo().search([('emp_id', '=', request.env.user.employee_ids[0].id)])
        return request.render("kw_employee_social_image.employee_certification", {'skip': record.no_of_skip if record else 0,
                                                                        'emp': request.env.user.employee_ids[0].name})

    @http.route('/redirect-employee-certfication', auth='user', website=True, csrf=False)
    def go_to_employee_certification(self, **kw):
        check_active_id = request.env['kw_emp_profile'].sudo().search([('user_id', '=', request.env.uid)]).id
        action_id = request.env.ref("kw_emp_profile.kw_employee_update_educational_action_window").id
        view_id= request.env.ref("kw_emp_profile.kw_employee_profile_educational_form_view").id
        
        record = request.env['kw_update_employee_certification'].sudo().search([('emp_id', '=', request.env.user.employee_ids[0].id)])
        if record:
            record.sudo().write({'profile_updated': 'updated'})
        else:
            request.env['kw_update_employee_certification'].sudo().create(
                {'no_of_skip': 0,
                    'emp_id': request.env.user.employee_ids[0].id,
                    'profile_updated': 'updated'
                    })
        request.session['skip_certfication'] = True
        profile_url = '/web#id='+str(check_active_id)+'&action='+str(action_id)+'&view='+str(view_id)+'&model=kw_emp_profile&view_type=form';
        return request.redirect(profile_url)

    @http.route('/employee-certification/skip-submit', auth='user', website=True, csrf=False)
    def skip_certification_submit(self, **kw):
        try:
            record = request.env['kw_update_employee_certification'].sudo().search(
                [('emp_id', '=', request.env.user.employee_ids[0].id)])
            if record:
                record.sudo().write({'no_of_skip': record.no_of_skip + 1, 'skip_date': datetime.today().date(),'profile_updated': 'skip'})
            else:
                request.env['kw_update_employee_certification'].sudo().create(
                    {'no_of_skip': 1,
                     'emp_id': request.env.user.employee_ids[0].id,
                     'skip_date': datetime.today().date(),
                     'profile_updated': 'skip'})
            request.session['skip_certfication'] = True
            return http.request.redirect('/web')
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
