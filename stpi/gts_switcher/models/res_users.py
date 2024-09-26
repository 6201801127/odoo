# -*- coding: utf-8 -*-
import odoo
from odoo import models, tools, fields, api, _
from odoo.http import request
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

import json
import base64
import os
import jwt
import xmlrpc.client

key = ",jy`\;4Xpe7%KKL$.VNJ'.s6)wErQa"


class ResUsers(models.Model):
    _inherit = 'res.users'

    token = fields.Char('Token', default='TOKEN1234567890')
    access_type = fields.Selection([('coe', 'Only COE'),
                                    ('hrms', 'Only HRMS'),
                                    ('coe_hrms', 'COE And HRMS'),
                                    ('coe/hrms', 'COE With HRMS'),
                                    ('all', 'All'),
                                    ], default='all')

    access_type_ids = fields.Many2many('access.type')

    def _check_credentials(self, password):
        """ Validates the current user's password.

        Override this method to plug additional authentication methods.

        Overrides should:

        * call `super` to delegate to parents for credentials-checking
        * catch AccessDenied and perform their own checking
        * (re)raise AccessDenied if the credentials are still invalid
          according to their own validation method

        When trying to check for credentials validity, call _check_credentials
        instead.
        """
        """ Override this method to plug additional authentication methods"""
        assert password
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [self.env.user.id]
        )
        [hashed] = self.env.cr.fetchone()
        if '.' in password and len(password) > 30:
            valid, replacement = False, None
            decoded_token = jwt.decode(str(password), key, algorithms=['HS256'])
            if decoded_token.get('token') == self.env.user.token:
                valid = True
        else:
            valid, replacement = self._crypt_context().verify_and_update(password, hashed)
            print('valid, replacement..', valid, replacement)
        if replacement is not None:
            self._set_encrypted_password(self.env.user.id, replacement)
        if not valid:
            raise AccessDenied()

    @api.multi
    def switch_instance(self):
        connection_obj = self.env['server.connection']
        connection_rec = connection_obj.search([], limit=1)
        if not connection_rec:
            raise UserError(_('No Server Connection setup !'))
        encoded_jwt = jwt.encode({'token': self.env.user.token}, key)
        action = {
            'name': connection_rec.name,
            'type': 'ir.actions.act_url',
            'url': str(connection_rec.url).strip() + "/web/switch?login=" + str(
                self.env.user.login) + "&password=" + str(encoded_jwt.decode("utf-8")),
            'target': 'new', }
        return action


# class ChangePasswordUser(models.TransientModel):
#     _inherit = 'change.password.user'
#     _description = "Change Password Wizard"
#
#     @api.multi
#     def change_password_button(self):
#         server_connection_id = self.env['server.connection'].search([('active', '=', True)])
#         url = server_connection_id.url
#         db = server_connection_id.db_name
#         common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
#         models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
#         # uid = common.authenticate(db, self.user_id.login, self.user_id.password, {})
#         user = models.execute_kw(db, self.user_id.id,self.user_id.password,'res.users', 'write',[[self.user_id.id], {'password': self.new_passwd}])
#         return super(ChangePasswordUser, self).change_password_button()
