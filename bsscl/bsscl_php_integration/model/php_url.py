from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError,ValidationError
import re

class PhpUrl(models.Model):
	_name = 'php.url'
	_inherit=['mail.thread','mail.activity.mixin']

	url = fields.Char("Get User detail URL")
	url2 = fields.Char("Get User Attrs URL")
	url3 = fields.Char("Get logout URL")
	url4 = fields.Char("Get Regenerate URL")
	url5 = fields.Char("Redirect URL")
