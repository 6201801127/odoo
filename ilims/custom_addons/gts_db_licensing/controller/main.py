import odoo
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home, Database, DBNAME_PATTERN
import jinja2
import os
import json
import re
import sys
from odoo.tools.translate import _
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.tools.config import config
# from pmis_addons.custom_addons.gts_db_licensing.models.config import obj

# custom_path = os.path.join(config["root_path"], "..", "..", "custom", "pmis_addons", "custom_addons", "gts_db_licensing", "models", "fonts", "config")

license_key_list = ['965A4TY730VG', 'PO9510LK630P', 'QTHNO816774L']

db_monodb = http.db_monodb

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.gts_db_licensing', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps


class ExtendDatabase(Database):

    def _render_template(self, **d):
        d.setdefault('manage',True)
        d['insecure'] = odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = odoo.tools.config['list_db']
        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        d['pattern'] = DBNAME_PATTERN
        # databases list
        d['databases'] = []
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = odoo.service.db.list_db_incompatible(d['databases'])
        except odoo.exceptions.AccessDenied:
            monodb = db_monodb()
            if monodb:
                d['databases'] = [monodb]
        return env.get_template("database_manager.html").render(d)

    @http.route('/web/database/create', type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, master_pwd, license, name, lang, password, **post):
        insecure = odoo.tools.config.verify_admin_password('admin')
        license_list = license_key_list
        # license_list = obj._license_key_list()
        if insecure and master_pwd:
            dispatch_rpc('db', 'change_admin_password', ["admin", master_pwd])
        try:
            if license not in license_list:
                raise Exception(_('Invalid License Key.'))
            if not re.match(DBNAME_PATTERN, name):
                raise Exception(
                    _('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'))
            # country code could be = "False" which is actually True in python
            country_code = post.get('country_code') or False
            dispatch_rpc('db', 'create_database',
                         [master_pwd, name, bool(post.get('demo')), lang, password, post['login'], country_code,
                          post['phone']])
            request.session.authenticate(name, post['login'], password)
            return http.local_redirect('/web/')
        except Exception as e:
            error = "Database creation error: %s" % (str(e) or repr(e))
        return self._render_template(error=error)
