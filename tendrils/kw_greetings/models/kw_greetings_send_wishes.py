# -*- coding: utf-8 -*-
import babel
import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging

import functools
import lxml
from werkzeug import urls

from odoo import _, api, fields, models, tools
from odoo.http import request

from odoo.exceptions import UserError
from odoo.tools import pycompat
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class kw_greetings_send_wishes(models.Model):
    _name = 'kw_greetings_send_wishes'
    _description = "Send Well Wishes"

    _rec_name = 'subject'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    def _default_message(self):
        wish_message = ''

        if self.env.context.get('default_wish_message'):
            wish_message = self.env.context.get('default_wish_message')
        elif self.env.context.get('default_template_id'):
            wish_message = self.env['kw_greetings_template'].browse(self.env.context.get('default_template_id')).message
        # print(wish_message)
        return wish_message

    def _default_wish_for(self):
        return self.env.context.get('default_wish_for') or '4'

    wish_for = fields.Selection(string="Wish For",
                                selection=[('1', 'Birth Day'), ('2', 'Anniversary'), ('3', 'Year of Service'),
                                           ('4', 'Well Wishes')], default=_default_wish_for)
    send_wish_to = fields.Many2one('hr.employee', string="Send To")
    # send_wish_name  = fields.Char(string="Receiver Name", related="send_wish_to.name" )

    wish_message = fields.Text(string="Message", default=_default_message)

    def _default_headline(self):
        subject = ''
        if self.env.context.get('default_wish_subject'):
            subject = self.env.context.get('default_wish_subject')
        elif self.env.context.get('default_template_id'):
            subject = self.env['kw_greetings_template'].browse(self.env.context.get('default_template_id')).subject
        return subject

    subject = fields.Char(string="Subject", default=_default_headline)
    template_id = fields.Many2one('kw_greetings_template', string="Template")

    def _default_html_body(self):
        body = ''
        if self.template_id.template_body:
            # body = template.render(variables)
            body = self.render_message_template(self.template_id.template_body, self.subject, self.wish_message)

        elif self.template_body:
            body = self.template_body

        return body or False

    template_body = fields.Html(string="Template Body", default=_default_html_body)
    preview_template = fields.Html(string="Template Body", default=_default_html_body, compute='_compute_preview')

    # reply_message   = fields.Text(string="Reply Message")
    sender_id = fields.Many2one('res.users', string='Sender User', index=True, default=False)
    parent_id = fields.Many2one('kw_greetings_send_wishes', string='Parent Well Wish', index=True)
    child_ids = fields.One2many('kw_greetings_send_wishes', 'parent_id', string='Child Well Wishes')

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, default=_default_employee)
    department_id = fields.Many2one('hr.department', string="Department", related="send_wish_to.department_id")
    job_id = fields.Many2one('hr.job', string="Designation", related="send_wish_to.job_id")

    # reply_to        = fields.Many2one('hr.employee')

    def _default_wish_category(self):
        default_wish_cat = request.env['ir.config_parameter'].sudo().get_param(
            'kw_greetings.greetings_well_wish_category')
        if default_wish_cat:
            default_wish_cat = int(default_wish_cat)

        return self.env.context.get('default_wish_category') or default_wish_cat

    wish_category = fields.Many2one('kw_greetings_category', string="Wish Category", readonly=True,
                                    default=_default_wish_category)
    created_date_format = fields.Date(string=u'Created Date Formatted', default=False, compute='_format_created_date',
                                      store=True, index=True)

    @api.depends('create_date')
    def _format_created_date(self):
        for record in self:
            record.created_date_format = record.create_date.strftime('%Y-%m-%d')

    @api.depends('template_body')
    def _compute_preview(self):
        for record in self:
            record.preview_template = record.template_body

    # get current user
    @api.onchange('wish_category')
    def _set_default_template_domain(self):
        domain_id = self.wish_category.id
        # print(domain_id)
        return {'domain': {'template_id': [('category_id', '=', domain_id)], }}

    # get current user
    # @api.onchange('template_id')
    # def _get_image_string(self):

    #     self.subject        = self.template_id.subject       
    #     self.wish_message   = self.template_id.message

    # get current user
    @api.onchange('template_id', 'wish_message', 'subject')
    def _get_html_preview(self):
        # variables = {}
        if self.template_id.template_body:
            # subject         = False
            # wish_message    = False
            if not self.subject:
                self.subject = self.template_id.subject

            if not self.wish_message:
                self.wish_message = self.template_id.message

            body = self.render_message_template(self.template_id.template_body, self.subject, self.wish_message)
            # self.preview_template = body
            self.template_body = body
            self.preview_template = body

    @api.model
    def create(self, vals):
        new_record = super(kw_greetings_send_wishes, self).create(vals)
        # print("inside create ")

        if new_record:
            if (new_record.wish_for != '4') or (new_record.wish_for == '4' and new_record.parent_id.id > 0):
                self.post_message_to_private_channel(new_record)

        self.env.user.notify_success(message='Wish created sucessfully')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_greetings_send_wishes, self).write(vals)
        self.env.user.notify_success(message='Wish updated sucessfully')
        return res

    # send wish to selected users
    @api.multi
    def action_send_wish(self, vals):
        # super(kw_greetings_send_wishes, self).create(vals)
        self.env.user.notify_success(message='Wish has been sent sucessfully')
        # print("inside action_send_wish")

    # send wish to all users
    @api.multi
    def action_send_wish_all(self):
        greetings_birthday_category = int(
            request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_birthday_category'))
        greetings_anniversary_category = int(
            request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_anniversary_category'))
        greetings_year_of_service_category = int(
            request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_year_of_service_category'))
        # greetings_well_wish_category        = int(request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_well_wish_category'))  

        greeting_recods = self.env['hr_employee_greetings'].sudo().search([('send_wish_status', '=', 1)])
        vals = []
        for greeting_rec in greeting_recods:
            new_rec_vals = {}

            default_parent_id = False
            default_wish_subject = False
            default_wish_message = False
            greetings_default_category = False
            greetings_default_template = False

            # print(greeting_rec.emp_id)

            if greeting_rec.greeting_type_int == 4:
                default_templaterec = self.env['kw_greetings_send_wishes'].sudo().search(
                    [('parent_id', '=', int(greeting_rec.well_wish_id.id)), ('sender_id', '=', self.env.uid),
                     ('wish_for', '=', str(greeting_rec.greeting_type_int)), ('send_wish_to', '=', greeting_rec.emp_id.id),
                     ('created_date_format', '=', datetime.now().strftime('%Y-%m-%d'))])
            else:
                default_templaterec = self.env['kw_greetings_send_wishes'].sudo().search(
                    [('parent_id', '=', False), ('sender_id', '=', self.env.uid),
                     ('wish_for', '=', str(greeting_rec.greeting_type_int)), ('send_wish_to', '=', greeting_rec.emp_id.id),
                     ('created_date_format', '=', datetime.now().strftime('%Y-%m-%d'))])

            # if wishes are not already sent then
            if len(default_templaterec) == 0:

                new_rec_vals['send_wish_to'] = greeting_rec.emp_id.id
                new_rec_vals['sender_id'] = self.env.uid
                new_rec_vals['wish_for'] = str(greeting_rec.greeting_type_int)

                if greeting_rec.greeting_type == 'birth_day':
                    greetings_default_category = greetings_birthday_category
                elif greeting_rec.greeting_type == 'anniversary':
                    greetings_default_category = greetings_anniversary_category
                elif greeting_rec.greeting_type == 'year_of_service':
                    greetings_default_category = greetings_year_of_service_category
                else:
                    greetings_default_category = greeting_rec.well_wish_id.wish_category.id

                if greetings_default_category:
                    if greeting_rec.greeting_type_int != 4:
                        greetings_default_template = request.env['kw_greetings_template'].sudo().search(
                            [('category_id', '=', greetings_default_category), ('is_default', '=', True)], limit=1)
                        default_wish_subject = greetings_default_template.subject
                        default_wish_message = greetings_default_template.message

                    else:
                        default_wish_subject = greeting_rec.well_wish_id.subject
                        default_wish_message = greeting_rec.well_wish_id.wish_message
                        default_parent_id = greeting_rec.well_wish_id.id
                        greetings_default_template = greeting_rec.well_wish_id.template_id

                new_rec_vals['wish_category'] = greetings_default_category
                new_rec_vals['template_id'] = greetings_default_template.id

                new_rec_vals['wish_message'] = default_wish_message
                new_rec_vals['subject'] = default_wish_subject

                new_rec_vals['parent_id'] = default_parent_id
                new_rec_vals['template_body'] = self.render_message_template(greetings_default_template.template_body,
                                                                             default_wish_subject, default_wish_message)
                vals.append(new_rec_vals)

                

        if len(vals) > 0:
            new_records = super(kw_greetings_send_wishes, self).create(vals)
            # print(new_records)
            self.post_message_to_private_channel(new_records)

            self.env.user.notify_success(message='Wish has been sent sucessfully')
        
        return 1

    # function to render the template by passing the values and all
    def render_message_template(self, templte_body, subject, wish_message):
        variables = {}
        if templte_body:
            try:
                mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
                template = mako_env.from_string(tools.ustr(templte_body))
            except Exception:
                _logger.info("Failed to load template %r", templte_body, exc_info=True)
                return False

            variables['object'] = {
                'subject': subject,
                'message': wish_message,

            }
            # variables['object'] = template_ctx
            body = template.render(variables)
            return body

    # function to render the template by passing the values and all
    def post_message_to_private_channel(self, wish_record):
        if len(wish_record):
            # ir_config_params        = request.env['ir.config_parameter'].sudo()
            # send_mail_config        = ir_config_params.get_param('kw_onboarding.module_onboarding_mail_status')

            #  # For sending Email  content_subtype='html',
            # if send_mail_config:
            # template    = self.env.ref('kw_greetings.kw_sendwish_email_template')
            # self.env['mail.template'].sudo().browse(template.id).send_mail(new_record.id)  
            for new_record in wish_record:
                # print(new_record)
                ch_obj = self.env['mail.channel']
                if new_record.send_wish_to.user_id:
                    ch_name = new_record.send_wish_to.user_id.name + ', ' + self.env.user.name
                    ch = ch_obj.sudo().search([('name', 'ilike', str(ch_name))])
                    if not ch:
                        ch = ch_obj.sudo().search(
                            [('name', 'ilike', str(self.env.user.name + ', ' + new_record.send_wish_to.user_id.name))])

                    if not ch:
                        chnl = ch_obj.channel_get([new_record.send_wish_to.user_id.partner_id.id])
                        ch = ch_obj.browse([chnl['id']])

                    ch.message_post(attachment_ids=[], body=new_record.template_body, message_type='comment',
                                    partner_ids=[], subtype='mail.mt_comment', subject=new_record.subject,
                                    author_id=self.env.user.partner_id.id, notif_layout='mail.mail_notification_light')
