# -*- coding: utf-8 -*-
from datetime import date
from odoo.http import request
from odoo import models, fields,SUPERUSER_ID, api,_
from odoo.exceptions import AccessDenied
from odoo.tools import partition, pycompat, collections
import logging
import datetime
import contextlib

_logger = logging.getLogger(__name__)

class LoginUserDetail(models.Model):
    _inherit = 'res.users'
    _description = "User login details"

    @api.model
    def _check_credentials(self, password):
        # print("custom check credentials called================")
        try:
            # print("inside try of custom check credentials called================")
            result = super(LoginUserDetail, self)._check_credentials(password)
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            params = {'user_id': self._uid, 'name': self.name, 'ip_address': ip_address, 'status': "Success"}
            self.env['user_login_detail'].sudo().create(params)
            return result
        except Exception:
            # print("inside except of custom check credentials called================")
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            params = {'user_id': self._uid, 'name': self.name, 'ip_address': ip_address, 'status': "Failed", }
            request.env['user_login_detail'].sudo().create(params)
            raise AccessDenied()
        
    # @classmethod
    # def _login(cls, db, login, password):
    #     if not password:
    #         raise AccessDenied()
    #     ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
    #     try:
    #         with cls.pool.cursor() as cr:
    #             self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
    #             with self._assert_can_auth(login):
    #                 user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
    #                 # print("user==================",user)
    #                 if not user:
    #                     raise AccessDenied()
    #                 user = user.sudo(user.id)
    #                 user._check_credentials(password)
    #                 user._update_last_login()
    #     except AccessDenied:
    #         _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
    #         raise

    #     _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

    #     return user.id
    
    # @contextlib.contextmanager
    # def _assert_can_auth(self, login):
    #     if not request:
    #         yield
    #         return

    #     reg = self.env.registry
    #     failures_map = getattr(reg, '_login_failures', None)
    #     if failures_map is None:
    #         failures_map = reg._login_failures = collections.defaultdict(lambda : (0, datetime.datetime.min))

    #     # source = request.httprequest.remote_addr
    #     source = login
    #     (failures, previous) = failures_map[source]
    #     if self._on_login_cooldown(failures, previous):
    #         _logger.warn(
    #             "Login attempt ignored for %s on %s: "
    #             "%d failures since last success, last failure at %s. "
    #             "You can configure the number of login failures before a "
    #             "user is put on cooldown as well as the duration in the "
    #             "System Parameters. Disable this feature by setting "
    #             "\"base.login_cooldown_after\" to 0.",
    #             source, self.env.cr.dbname, failures, previous)
    #         raise AccessDenied(_("Too many login failures, please wait a bit before trying again."))

    #     try:
    #         yield
    #     except AccessDenied:
    #         (failures, __) = reg._login_failures[source]
    #         reg._login_failures[source] = (failures + 1, datetime.datetime.now())
    #         raise
    #     else:
    #         reg._login_failures.pop(source, None)


class user_login_detail(models.Model):
    _name = 'user_login_detail'
    _description = "User login details"
    _order = 'id DESC'

    user_id = fields.Integer("User ID")
    name = fields.Char(string="User Name")
    date_time = fields.Datetime(string="Login date / time", default=lambda self: fields.datetime.now())
    ip_address = fields.Char(string="IP Address")
    status = fields.Char(string="Login Status")
    emp_code = fields.Char('Employee Code', compute='_get_employee_code')

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]

    @api.model
    def get_year_options(self):
        return self._get_year_list()

    def _get_employee_code(self):
        for user in self:
            records = self.env['hr.employee'].search([('user_id', '=', user.user_id)])
            if records:
                user.emp_code = records.emp_code
