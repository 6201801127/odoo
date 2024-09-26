# from odoo import models, fields, api


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
from odoo.exceptions import UserError
from odoo.tools import pycompat

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


class kw_greetings_template(models.Model):
    _name = 'kw_greetings_template'
    _description = "Greetings Templates."

    # _rec_name       =   'subject'

    category_id = fields.Many2one('kw_greetings_category', string="Catagory", required=True)
    name = fields.Char(string="Title", required=True)
    subject = fields.Char(string="Subject", required=True)
    message = fields.Text(string="Message")
    is_default = fields.Boolean(string=u'Default Template', default=False)

    template_body = fields.Html(
        string=u'Template Body', required=True, default='${object.subject} <br/>  ${object.message}'
    )

    template_preview = fields.Html(
        string=u'Template Preview',
        compute='_change_html_body')

    # @api.depends('depends')
    # def _compute_field(self):
    #     for record in self:
    #         record.field = something

    # get current user

    @api.model
    def create(self, vals):
        new_record = super(kw_greetings_template, self).create(vals)
        self.env.user.notify_success(message='Template created sucessfully')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_greetings_template, self).write(vals)
        self.env.user.notify_success(message='Template updated sucessfully')
        return res

    @api.depends('template_body')
    def _change_html_body(self):
        variables = {}
        if self.template_body:
            try:
                mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
                template = mako_env.from_string(tools.ustr(self.template_body))
            except Exception:
                _logger.info("Failed to load template %r", self.template_body, exc_info=True)
                return False

            variables['object'] = {
                'subject': self.subject,
                'message': self.message,

            }
            # variables['object'] = template_ctx
            body = template.render(variables)

            self.template_preview = body

    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['kw_greetings_template'].search(
            [('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("The title " + '"' + self.name + '"' + " already exists.")

    @api.multi
    def button_preview_template(self):
        view_id = self.env.ref('kw_greetings.kw_greeting_template_preview_view_form').id
        target_id = self.id
        # print(target_id)
        return {
            'name': 'Preview Template',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_greetings_template',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'mode': 'readonly', "toolbar": False}
        }
