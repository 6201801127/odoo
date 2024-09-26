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
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
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

        """# dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently."""
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class kw_announcement_template(models.Model):
    _name = 'kw_announcement_template'
    _description = "Announcement Templates."

    name = fields.Char(required=True, string='Name')
    model_id = fields.Many2one('ir.model', string='Applies to', help="The kind of document with with this template can be used")
    template_body = fields.Html(string=u'Template Body')

    @api.model
    def create(self, vals):
        new_record = super(kw_announcement_template, self).create(vals)
        # self.env.user.notify_success(message='Template created successfully')
        return new_record

    @api.model
    def make_announcement(self, template_id, record_id):
        announcement_rendered_content = self.env['kw_announcement_template'].render_template(template_id.template_body,
                                                                                             template_id.model_id.model,
                                                                                             record_id)

        general_category_id = self.env.ref('kw_announcement.kwannounce_gen_category').id

        cur_date = datetime.datetime.now().date()
        expire_date = cur_date + datetime.timedelta(days=7)
        upload_image = False

        model_sel_record = self.env[template_id.model_id.model].browse(record_id)
        if model_sel_record.image_medium:
            upload_image = model_sel_record.image_medium

        self.env['kw_announcement'].create(
            {'upload_image': upload_image, 'category_id': general_category_id, 'headline': template_id.name,
             'start_date': cur_date, 'expire_date': expire_date, 'description': announcement_rendered_content,
             'state': 'published', 'enable_comment': True})

    def render_template(self, template, model, res_id):
        variables = {}
        render_result = u""
        if template:
            record = self.env[model].browse(res_id)
            variables['object'] = record

            try:
                mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
                template = mako_env.from_string(tools.ustr(template))
                render_result = template.render(variables)

            except Exception:
                _logger.info("Failed to load template %r", template, exc_info=True)
                return False

            if render_result == u"False":
                render_result = u""

        return render_result
