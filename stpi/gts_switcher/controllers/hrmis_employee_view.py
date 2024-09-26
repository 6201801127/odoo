import odoo
from odoo import http, modules, tools
from odoo.http import request
from odoo.osv import expression
from odoo import models, fields, api, _


class HrmisEmployee(http.Controller):
    @http.route('/web/hrmis/employee', type='http', auth="none", sitemap=False)
    def web_login_hrms_coe_switch(self, redirect=None, **kw):
        request.website = request.env['website'].get_current_website()
        old_uid = False
        values = {}
        request.params['login_success'] = False
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            # return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            return http.redirect_with_hash(self._redirect_employee(uid, redirect=redirect,url=kw.get('url'), employee_id=kw.get('menu_id')))
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)

    def _redirect_employee(self, uid,redirect=None, url=None, employee_id=None):
            emp = http.request.env['hr.employee'].sudo().search([('hrmis_id','=',employee_id)],limit=1)
            emp_form_id = http.request.env['ir.model.data'].sudo().search([('name', '=', 'open_view_employee_list_my_coe'), ('model', '=', 'ir.actions.act_window')], limit=1)
            emplyoee_view_url = url + ('/web#id=' + str(emp.id) + '&action=' + str(emp_form_id.res_id) + '&model=hr.employee&view_type=form')
            if emp:
                return emplyoee_view_url
            else:
                return "/web/session/logout?redirect=/"
