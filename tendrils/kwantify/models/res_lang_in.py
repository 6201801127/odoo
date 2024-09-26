# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import locale
import logging
import re
from operator import itemgetter

from odoo import api, fields, models, tools, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

DEFAULT_DATE_FORMAT = '%d-%b-%Y'
DEFAULT_TIME_FORMAT = '%I:%M %p'


class LangIn(models.Model):
    _inherit = "res.lang"

    @api.model
    def update_lang_date_format(self):
        lang_code = (tools.config.get('load_language') or 'en_US').split(',')[0]
        lang = self.search([('code', '=', lang_code)])
        lang.write({"date_format": DEFAULT_DATE_FORMAT, "time_format": DEFAULT_TIME_FORMAT})

    @api.model
    def get_date_format(self):
        lang_code = (tools.config.get('load_language') or 'en_US').split(',')[0]
        lang = self.search([('code', '=', lang_code)])
        return lang.date_format
	

    # @api.model
    # def install_lang(self):
    #     """
    #
    #     This method is called from odoo/addons/base/base_data.xml to load
    #     some language and set it as the default for every partners. The
    #     language is set via tools.config by the RPC 'create' method on the
    #     'db' object. This is a fragile solution and something else should be
    #     found.
    #
    #     """
    #     # config['load_language'] is a comma-separated list or None
    #     lang_code = (tools.config.get('load_language') or 'en_US').split(',')[0]
    #     lang = self.search([('code', '=', lang_code)])
    #     if not lang:
    #         self.load_lang(lang_code)
    #     IrDefault = self.env['ir.default']
    #     default_value = IrDefault.get('res.partner', 'lang')
    #     if default_value is None:
    #         IrDefault.set('res.partner', 'lang', lang_code)
    #         # set language of main company, created directly by db bootstrap SQL
    #         partner = self.env.user.company_id.partner_id
    #         if not partner.lang:
    #             partner.write({'lang': lang_code})
    #     return True
