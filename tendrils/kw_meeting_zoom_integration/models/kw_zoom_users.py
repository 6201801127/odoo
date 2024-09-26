# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .zoomus.client import ZoomClient
import json, requests
from odoo.exceptions import UserError, ValidationError, Warning


class ZoomUsers(models.Model):
    _name = 'kw_zoom_users'
    _description = 'Zoom User Information'
    _order = 'first_name'
    _rec_name = 'full_name'

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = f'{rec.first_name} {rec.last_name}'

    zoom_id = fields.Char('Zoom ID')
    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name')
    full_name = fields.Char('Name', compute="_compute_full_name")
    email = fields.Char('Email', required=True)
    type = fields.Integer(string='Type', default=1, help="('1', 'Basic'),('2', 'Licensed'),('3', 'On-prem')")
    type_sel = fields.Selection([('1', 'Basic'), ('2', 'Licensed'), ('3', 'On-prem')], default='1', string='Type')
    role_name = fields.Char('Role Name')
    role_id = fields.Char('Role Name')
    pmi = fields.Char('PMI')
    use_pmi = fields.Boolean('Use PMI', default=False)
    vanity_url = fields.Char('Vanity URL')
    personal_meeting_url = fields.Char('Personal Meeting URL')
    timezone = fields.Char('Time Zone')
    verified = fields.Char('Verified')
    dept = fields.Char('Dept')
    created_at = fields.Char('Created at')
    last_login_time = fields.Char('Last Login Time')
    last_client_version = fields.Char('Last Client Version')
    pic_url = fields.Char('Pic URL')
    host_key = fields.Char('Host key')
    jid = fields.Char('JID')
    group_ids = fields.Text('Groups')
    im_group_ids = fields.Text('IM Groups')
    account_id = fields.Char('Account')
    language = fields.Char('Language')
    # language = fields.Many2one('res.country','Country')
    phone_country = fields.Text('Country')
    # phone_country = fields.Many2one('res.country','Country')
    phone_number = fields.Char('Phone No')
    status = fields.Selection([('active', 'Active'), ('inactive', 'InActive')], 'Status', default='active')
    user_id = fields.Many2one('res.users', string='User')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, readonly=True)
    type_id = fields.Char(compute='check_user', string="User Type", readonly=True, store=False, required=False)
    mapped_user = fields.Char(compute='check_user', string="User Mapped", readonly=True, store=False, required=False)
    active = fields.Boolean('Active', default=False)

    @api.constrains('zoom_id')
    def _check_zoom_id(self):
        records = self.search([]) - self
        for rec in records:
            if rec.zoom_id == self.zoom_id:
                raise ValidationError("Zoom User already exist.")

    @api.model
    def create(self, values):
        if values.get('group_ids') == []:
            values['group_ids'] = ''
        if values.get('im_group_ids') == []:
            values['im_group_ids'] = ''
        if values.get('email') and not values.get('user_id'):
            employee_data = self.env['hr.employee'].sudo().search([('zoom_email', '=', values.get('email'))])
            user_rec = employee_data.user_id
            values['user_id'] = user_rec.id if user_rec else None
        if values.get('user_id'):
            """Create zoom user API"""
            user_info = {
                "type": values.get('type'),
                "first_name": values.get('first_name'),
                "last_name": values.get('last_name'),
                "email": values.get('email')
            }
            user_data = self.create_user_api(user_info)
            if user_data.get('code') == 1005:
                raise UserError(_("Zoom User already exist in the account: %s.") % (self.zoom_id))
            else:
                if user_data.get('id'):
                    user_info['zoom_id'] = user_data.get('id')
                    user_data['zoom_id'] = user_data.get('id')
                    create_data = values
                    # print("create_data >> ", create_data)
                    create_data.update(user_data)
                    del create_data['id']
                    # print("create_data 2 >> ",create_data)
                    zoom_user = super(ZoomUsers, self).create(create_data)
                    if zoom_user:
                        zoom_user.user_id.sudo().write({'zoom_id': zoom_user.id})
                        for employee in zoom_user.user_id.employee_ids:
                            employee.sudo().write({'zoom_email': user_info.get('email')})

                    self.env.user.notify_success(
                        message='You might have got an email from zoom to authenticate.\nPlease approve the request.')
        else:
            zoom_user = super(ZoomUsers, self).create(values)

        return zoom_user

    @api.model
    def find_or_create(self, vals):
        zoom_id = vals.get('zoom_id') if vals.get('zoom_id') else False
        if zoom_id:
            zoom_user = self.search([('zoom_id', '=', zoom_id), '|', ('active', '!=', False), ('active', '=', False)],
                                    limit=1)
            employee_data = self.env['hr.employee'].sudo().search([('zoom_email', '=', vals.get('email'))])
            res_user = employee_data.user_id

            """Update user_id in zoom_user"""
            if zoom_user and not zoom_user.user_id and res_user:
                zoom_user.write({'user_id': res_user.id})
            elif not zoom_user and res_user:
                vals['user_id'] = res_user.id

            """Create new zoom_user"""
            if not zoom_user:
                zoom_user = self.create(vals)

            """Update zoom_id in res_users"""
            if res_user:
                res_user.sudo().write({"zoom_id": zoom_user.id})
            return zoom_user
        else:
            return False

    @api.multi
    def check_user(self):
        opt = {1: 'Basic', 2: 'Licensed', 3: 'On-prem'}
        for rec in self:
            rec.type_id = opt.get(rec.type) if opt.get(rec.type) else 'N/A'
            rec.mapped_user = 'Yes' if rec.user_id else 'No'
        return True

    @api.multi
    def check_zoom_user(self, args):
        if self.env.user.zoom_id and self.env.user.zoom_id.active == True:
            return {'status': 'success'}
        elif self.env.user.zoom_id and self.env.user.zoom_id.active == False:
            return {'status': 'pending'}
        else:
            return {'status': 'not found'}

    @api.model
    def create_or_write(self, vals):
        zoom_id = vals.get('zoom_id') if vals.get('zoom_id') else False
        zoom_user = self.search([('zoom_id', '=', zoom_id), '|', ('active', '!=', False), ('active', '=', False)],
                                limit=1)

        employee_data = self.env['hr.employee'].sudo().search([('zoom_email', '=', vals.get('email'))])
        res_user = employee_data.user_id

        zoom_user_update = vals
        """Update res_user_id in zoom_user table"""
        if zoom_user and not zoom_user.user_id and res_user:
            zoom_user_update['user_id'] = res_user.id

        """Create or Update zoom user"""
        zoom_user_update['active'] = True
        if zoom_user:
            zoom_user.write(zoom_user_update)
        elif not zoom_user and res_user:
            vals['user_id'] = res_user.id
            vals['active'] = True

        if not zoom_user:
            zoom_user = self.create(vals)

        if not res_user.zoom_id:
            res_user.sudo().write({"zoom_id": zoom_user.id})

        return zoom_user

    @api.multi
    def unlink(self):
        for record in self:
            # self.unlink_zoom_user_api({'zoom_id': record.zoom_id})
            # self.env['hr.employee'].sudo().search([('zoom_email', '=', record.email)]).write({"zoom_email": None})
            """ Delete zoom_id from res.users"""
            record.user_id.sudo().write({'zoom_id': False})
            """ Remove zoom_email from hr.employee"""
            record.user_id.employee_ids.sudo().write({'zoom_email': None})

        rec = super(ZoomUsers, self).unlink()
        self.env.user.notify_success(message='Zoom Users deleted successfully.')
        return rec

    @api.multi
    def unlink_zoom_user_api(self, vals):
        zoom_id = vals.get('zoom_id')
        params = self.get_config_params()
        if params.get('jwt_api_key') and params.get('jwt_api_secret'):
            client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))

        return True

    def get_config_params(self, *args, **kwargs):
        param = self.env['ir.config_parameter'].sudo()
        return {
            "jwt_api_key": str(param.get_param('kw_meeting_zoom_integration.api_key', False)),
            "jwt_api_secret": str(param.get_param('kw_meeting_zoom_integration.api_secret', False)),
            "event_token": str(param.get_param('kw_meeting_zoom_integration.webhook_token', False))
        }

    """
    Deactivate zoom user webhook
    """
    @api.multi
    def deactivate_zoom_user(self, vals):
        id_zoom = vals.get('id')
        zoom_users = self.sudo().search([('zoom_id', '=', id_zoom)])
        if zoom_users:
            zoom_users.sudo().write({'active': False})
        return True

    """
    Unlink Zoom User on User Delete & De-associated webhook
    """
    @api.multi
    def unlink_zoom_user_webhook(self, vals):
        id_zoom = vals.get('id')
        zoom_users = self.sudo().search([('zoom_id', '=', id_zoom)])
        if zoom_users:
            """ Delete zoom_id from res.users"""
            zoom_users.user_id.sudo().write({'zoom_id': False})
            zoom_users.user_id.employee_ids.sudo().write({'zoom_email': None})
            """ Delete from kw_zoom_users"""
            zoom_users.sudo().unlink()
        return True

    """
    Create & Update Zoom User Details on User Creation webhook
    """
    @api.multi
    def update_zoom_user(self, vals):
        if self.env.user:
            params = self.get_config_params()
            if params.get('jwt_api_key') and params.get('jwt_api_secret'):
                client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))
                id_zoom = vals.get('id')
                zoom_users = self.sudo().search([('zoom_id', '=', id_zoom)])
                """ create zoom user record if not exist """
                if not zoom_users:
                    vals['zoom_id'] = id_zoom
                    del vals['id']
                    zoom_users = self.find_or_create(vals)
                """  Get zoom user details and update zoom users """
                zoom_res = json.loads(client.user.get(id=id_zoom).content)
                if zoom_res.get('status') == 'active':
                    zoom_user_data = self._prepare_data(zoom_res)
                    zoom_users.sudo().write(zoom_user_data)
        return True

    """
    Zoom api call for user invitation
    """
    @api.multi
    def create_user_api(self, user_info):
        user_data = False
        params = self.get_config_params()
        if params.get('jwt_api_key') and params.get('jwt_api_secret'):
            client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))
            try:
                zoom_response = client.user.create(action="create", user_info=user_info)
                if zoom_response:
                    user_data = json.loads(zoom_response.content) if zoom_response else False
                # if zoom_response.content.get('code') == 1005:
                #     raise UserError(_("Zoom User already exist in the account: %s.") % (self.zoom_id))
                else:
                    raise UserError(_("Network error ! Please try again later.") % self.zoom_id)
            except:
                raise UserError(_("Network error ! Please try again later."))
        return user_data

    @api.model
    def _prepare_data(self, zoom_res):
        zoom_user_data = {"first_name": zoom_res.get('first_name', None),
                          "last_name": zoom_res.get('last_name', None),
                          "email": zoom_res.get('email', None),
                          "type": zoom_res.get('type', 1),
                          "role_name": zoom_res.get('role_name', None),
                          "role_id": zoom_res.get('role_id', None),
                          "pmi": zoom_res.get('pmi', 0),
                          "use_pmi": zoom_res.get('use_pmi', False),
                          "personal_meeting_url": zoom_res.get('personal_meeting_url', None),
                          "timezone": zoom_res.get('timezone', None),
                          "verified": zoom_res.get('verified', 0),
                          "dept": zoom_res.get('dept', None),
                          "created_at": zoom_res.get('created_at', None),
                          "last_login_time": zoom_res.get('last_login_time', None),
                          "pic_url": zoom_res.get('pic_url', None),
                          "host_key": zoom_res.get('host_key', None),
                          "jid": zoom_res.get('jid', None),
                          "group_ids": zoom_res.get('group_ids', []),
                          "im_group_ids": zoom_res.get('im_group_ids', []),
                          "account_id": zoom_res.get('account_id', None),
                          "language": zoom_res.get('language', None),
                          "phone_country": zoom_res.get('phone_country', None),
                          "phone_number": zoom_res.get('phone_number', None),
                          "status": zoom_res.get('status', None),
                          "active": True,
                          }
        # "cms_user_id": zoom_res.get('cms_user_id', None),
        # "job_title": zoom_res.get('job_title', None),
        # "location": zoom_res.get('location', None)
        # zoom_res['active'] = True
        # del zoom_res['id']
        # del zoom_res['job_title']
        # del zoom_res['location']
        return zoom_user_data

    """
    CRON to fetch zoom user details
    """
    @api.multi
    def fetch_zoom_users(self):
        if self.env.user:
            param = self.env['ir.config_parameter'].sudo()
            jwt_api_key = str(param.get_param('kw_meeting_zoom_integration.api_key', False))
            jwt_api_secret = str(param.get_param('kw_meeting_zoom_integration.api_secret', False))
            if jwt_api_key and jwt_api_secret:
                zoom_users = self.env['kw_zoom_users'].search([('active', '=', False)])
                if zoom_users:
                    client = ZoomClient(jwt_api_key, jwt_api_secret)
                    for user in zoom_users:
                        zoom_res = json.loads(client.user.get(id=user.zoom_id).content)
                        if zoom_res.get('status') == 'active':
                            zoom_user_data = self._prepare_data(zoom_res)
                            user.write(zoom_user_data)

        return True

    @api.multi
    def sync_zoom_users(self):
        if self.env.user:
            param = self.env['ir.config_parameter'].sudo()
            jwt_api_key = str(param.get_param('kw_meeting_zoom_integration.api_key', False))
            jwt_api_secret = str(param.get_param('kw_meeting_zoom_integration.api_secret', False))
            if jwt_api_key and jwt_api_secret:
                client = ZoomClient(jwt_api_key, jwt_api_secret)
                zoom_res = json.loads(client.user.list(page_size=100).content)
                # print(zoom_res)
