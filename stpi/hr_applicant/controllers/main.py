# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from werkzeug.exceptions import NotFound

class WebsiteHrApplicant(http.Controller):

    @http.route('/jobs/myapplications/<model("published.advertisement"):published_advertisement>', type='http', auth="public", website=True)
    def jobs_myapplications(self, published_advertisement, **kw):
        vals = {'published_advertisement':published_advertisement.sudo()}
        if 'email' in request.session:
            email_id = request.session['email']
            hr_applicants_submit = request.env['hr_applicant_submitted_temp'].sudo().search([('email', '=', email_id)])
            vals['hr_applicants_submit'] = hr_applicants_submit
        # Render page
        return request.render("hr_applicant.my_applications", vals)

    @http.route(
        ['/jobs/myapplication/info/<model("hr.applicant"):hr_applicant_id>',
         '/jobs/myapplication/temp/info/<model("hr_applicant_temp"):hr_applicant_id>'],
        type='http', auth="public", website=True
    )
    def jobs_myapplication_info(self, hr_applicant_id, **kwargs):
        return request.render("hr_applicant.my_application_info", {
            'myapplication_info': hr_applicant_id.sudo(),
        })

    @http.route('/logout-jobs/', type="http", auth="public", website=True)
    def logout_jobs(self, **kw):
        if 'email' in request.session:        
            request.session.pop('email')
        return request.redirect('/jobs')
