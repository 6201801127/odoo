from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError,ValidationError
import re

class ResPartner(models.Model):
	_inherit = 'res.partner'

	father_name = fields.Char("Father Name")
	property_id = fields.Boolean("Property")



class ResUsers(models.Model):
	_inherit = 'res.users'

	php_user_id = fields.Char("User ID")

