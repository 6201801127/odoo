# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
_logger = logging.getLogger(__name__)
import base64

class WebsiteJobApplication(http.Controller):

	@http.route([
		'''/jobapplication'''], type='http', auth="public", website=True)
	def shop(self, page=0, category=None, search='', ppg=False, **post):
		values ={}
		return http.request.render('bsscl_recruitment.job_application', values)

	@http.route('/save_data/',auth='public',methods=['POST',],website=True,csrf=False)
	def save_data(self,**kw):
		dic_d = {}
		if kw.get('First_Name'):
			dic_d.update({
				'partner_name':kw.get('First_Name'),
				'name':kw.get('First_Name')
			})
		if kw.get('Email_Address'):
			dic_d.update({
				'email_from':kw.get('Email_Address')
			})
		if kw.get('Phone'):
			dic_d.update({
				'partner_phone':kw.get('Phone')
			})
		if kw.get('Position'):
			dic_d.update({
				'job_id': int(kw.get('Position'))
			})




		if dic_d:
			rec_id = request.env['hr.applicant'].sudo().create(dic_d)

			if kw.get('upload'):
								request.env['ir.attachment'].sudo().create({

					'name':  kw.get('upload').filename,
					'type':  'binary','datas':base64.encodestring(kw['upload'].read()) if kw['upload'] else '','res_model':'hr.applicant',
					'res_id':rec_id.id
				})

		values={}
		return http.request.render('bsscl_recruitment.job_application_submitted',values)