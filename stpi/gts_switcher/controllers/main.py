# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel.messages.pofile
import base64
import datetime
import functools
import glob
import hashlib
import imghdr
import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile
import time
import zlib

import jwt
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
from xml.etree import ElementTree
import unicodedata


import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_resource_path
from odoo.tools import crop_image, topological_sort, html_escape, pycompat
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlwt, file_open
from odoo.tools.safe_eval import safe_eval
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security

from odoo.addons.portal.controllers.web import Home

_logger = logging.getLogger(__name__)

db_monodb = http.db_monodb
# key = 'chalhatpagle'
key = ",jy`\;4Xpe7%KKL$.VNJ'.s6)wErQa"

def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)

def ensure_db(redirect='/web/database/selector'):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    db = request.params.get('db') and request.params.get('db').strip()
    request.website = request.env[
        'website'].get_current_website()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db


class Home(Home):

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect('/web', query=request.params, keep_hash=True)

    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        request.website = request.env['website'].get_current_website()
        if not request.session.uid:
            return werkzeug.utils.redirect('/login/intermediate', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid

        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')

    @http.route('/web/dbredirect', type='http', auth="none")
    def web_db_redirect(self, redirect='/', **kw):
        ensure_db()
        return werkzeug.utils.redirect(redirect, 303)

    def _login_redirect(self, uid, redirect=None):
        partner_sudo = request.env['res.users'].sudo().browse(uid)
        try:
            # if partner_sudo.access_type_ids and partner_sudo.partner_type in  ('portfolio','hq','coe', 'center', 'directorate', 'hrms'):
            if partner_sudo.access_type_ids:
                connection_rec = request.env['server.connection'].search([], limit=1)
                url = str(connection_rec.url).strip()
                encoded_jwt = jwt.encode({'token': partner_sudo.token}, key)
                password = str(encoded_jwt.decode("utf-8"))
                login =partner_sudo.login
                # login ='ragini@asdffd'

                if len(partner_sudo.access_type_ids) == 1:
                    for access in partner_sudo.access_type_ids:
                        if access.name == 'HRMS':
                            if connection_rec.instance_type =='coe':
                                data= url+'/web/switch'+ '?' + 'login' + '=' + login + '&' + 'password' + '='+ password
                                return data
                            elif connection_rec.instance_type == 'hrms':
                                return '/web'
                            else:
                                return redirect if redirect else '/web'
                else:
                    return redirect if redirect else '/web'
            else:
                return '/web'
        except Exception as e:
            return '/web'

        # return redirect if redirect else '/login/intermediate'

    # @http.route('/web/login2', type='http', auth="none", sitemap=False)
    @http.route('/web/login2', type='json', auth='public', cors='*')
    def web_login2(self, redirect=None, **kw):
        print('/web/login2.==... request.params.. kw.', request.params, kw)
        ensure_db()
        request.website = request.env['website'].get_current_website()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        # otherwise no real way to test debug mode in template as ?debug =>
        # values['debug'] = '' but that's also the fallback value when
        # missing variables in qweb
        if 'debug' in values:
            values['debug'] = True

        values['website'] = request.website
        print('/web/login values...', values)
        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/switch', type='http', auth="none", sitemap=False)
    def web_login_switch(self, redirect=None, **kw):
        request.website = request.env['website'].get_current_website()
        old_uid = False
        values = {}
        request.params['login_success'] = False
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            request.params['login_success'] = True
            return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            values = {'login_user': request.uid,}
            return request.render("gts_switcher.intermediate_login_fail_page", values)


        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/switch/hrms/coe', type='http', auth="none", sitemap=False)
    def web_login_hrms_coe_switch(self, redirect=None, **kw):
        request.website = request.env['website'].get_current_website()
        old_uid = False
        values = {}
        request.params['login_success'] = False
        try:
            uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
            user_id=request.env['res.users'].sudo().search([('id','=',uid)])
            for company_id in user_id.sudo().company_ids:
                if company_id.access_type == 'coe/hrms':
                    request.params['login_success'] = True
                    user_id.write({'company_id':company_id.id})
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            # request.params['login_success'] = False
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            if e.args == odoo.exceptions.AccessDenied().args:
                values['error'] = _("Wrong login/password")
            else:
                values['error'] = e.args[0]

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response








    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.website = request.env['website'].get_current_website()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None


        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'],request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        # otherwise no real way to test debug mode in template as ?debug =>
        # values['debug'] = '' but that's also the fallback value when
        # missing variables in qweb
        if 'debug' in values:
            values['debug'] = True
        values['website'] = request.website
        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # @http.route('/hrmis/switch', type='http', auth="none", sitemap=False)
    # def web_hrmis_switch(self, redirect=None, **kw):
    #     request.website = request.env['website'].get_current_website()
    #     old_uid = False
    #     values = {}
    #     request.params['login_success'] = False
    #     try:
    #         uid = request.session.authenticate(request.session.db, kw.get('login'), kw.get('password'))
    #         request.params['login_success'] = True
    #         return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
    #     except odoo.exceptions.AccessDenied as e:
    #         request.uid = old_uid
    #         values = {'login_user': request.uid, }
    #         return request.render("gts_switcher.intermediate_login_fail_page", values)