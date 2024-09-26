import odoo
from odoo import http, modules, tools
from odoo.http import request
from odoo.osv import expression
from odoo import models, fields, api, _

class AssetIndent(http.Controller):
    @http.route('/asset/indent', type='http', auth="none", sitemap=False)
    def asset_detail(self, redirect=None, **kw):
        old_uid = False
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            return http.redirect_with_hash(self._asset_redirect(uid, redirect=redirect, asset_id=kw.get('menu_id')))
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)

    def _asset_redirect(self, uid, redirect=None,asset_id=None):
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        assei_form_id = http.request.env['ir.model.data'].sudo().search([('module', '=', 'account_asset'),('model','=','ir.actions.act_window')],limit=1)
        asset_url = url + ('/web#id=' + str(asset_id) + '&action=' + str( assei_form_id.res_id) + '&model=account.asset.asset&view_type=form')
        return asset_url


    @http.route('/hrmis/switch', type='http', auth="none", sitemap=False)
    def hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            appraisal_action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'appraisal_stpi'),
                                                                                ('name', '=', 'appraisal_menu_new_action'),
                                                                                ('model', '=', 'ir.actions.act_window')], limit=1)
            appraisal_url = url + ('/web#'  + '&action=' + str(appraisal_action.res_id) + '&model=appraisal.main&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)




    @http.route('/leaves/hrmis/switch', type='http', auth="none", sitemap=False)
    def leaves_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'hr_holidays'),
                                                                      ('name', '=','action_hr_holidays_dashboard'),
                                                                      ('model', '=', 'ir.actions.act_window')],
                                                                       limit=1)
            appraisal_url = url + ('/web#' + '&action=' + str(action.res_id) + '&model=hr.leave&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)



    @http.route('/employees/hrmis/switch', type='http', auth="none", sitemap=False)
    def employees_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'hr'),
                                                                      ('name', '=', 'open_view_employee_list_my'),
                                                                      ('model', '=', 'ir.actions.act_window')],
                                                                     limit=1)
            appraisal_url = url + ('/web#id='+ str(employee_id.id) + '&action=' + str(action.res_id) + '&model=hr.employee&view_type=form')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)



    @http.route('/ltc/hrmis/switch', type='http', auth="none", sitemap=False)
    def ltc_hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'employee_ltc'),
                                                                      ('name', '=', 'employeeltc_advance_action_draft'),
                                                                      ('model', '=', 'ir.actions.act_window')],
                                                                     limit=1)
            appraisal_url = url + ('/web#' + '&action=' + str(action.res_id) + '&model=employee.ltc.advance&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)



    @http.route('/indents/hrmis/switch', type='http', auth="none", sitemap=False)
    def indents_hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'indent_stpi'),
                                                                      ('name', '=', 'employeeIndent_request_action_draft'),
                                                                      ('model', '=', 'ir.actions.act_window')],
                                                                     limit=1)
            appraisal_url = url + (
                        '/web#' + '&action=' + str(action.res_id) + '&model=indent.request&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)



    @http.route('/loans/hrmis/switch', type='http', auth="none", sitemap=False)
    def loans_hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'ohrms_loan'),
                                                                      ('name', '=','hr_loan_menu_action'),
                                                                      ('model', '=', 'ir.actions.act_window')],limit=1)
            appraisal_url = url + (
                    '/web#' + '&action=' + str(action.res_id) + '&model=hr.loan&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)




    @http.route('/tour/hrmis/switch', type='http', auth="none", sitemap=False)
    def tour_hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'tour_request'),
                                                                      ('name', '=',  'tour_request_menu_action'),
                                                                      ('model', '=', 'ir.actions.act_window')], limit=1)
            appraisal_url = url + ('/web#' + '&action=' + str(action.res_id) + '&model=tour.request&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)



    @http.route('/reimbursements/hrmis/switch', type='http', auth="none", sitemap=False)
    def reimbursements_hrmis_detail(self, redirect=None, **kw):
        old_uid = False
        url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            action = http.request.env['ir.model.data'].sudo().search([('module', '=', 'reimbursement_stpi'),
                                                                      ('name', '=', 'reimbursement_menu_action'),
                                                                      ('model', '=', 'ir.actions.act_window')], limit=1)
            appraisal_url = url + (
                    '/web#' + '&action=' + str(action.res_id) + '&model=reimbursement&view_type=list')
            return http.redirect_with_hash(appraisal_url)

        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid, }
            return request.render("gts_switcher.intermediate_login_fail_page", values)




