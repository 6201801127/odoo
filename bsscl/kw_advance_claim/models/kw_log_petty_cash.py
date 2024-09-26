from odoo import models, fields, api

class kw_log_petty_cash(models.Model):
	_name='kw_advance_log_petty_cash'
	_description="Petty Cash log"
	
	from_user_id = fields.Char(string="From user")
	forwarded_to_user_id = fields.Char(string="To user")
	remark = fields.Char(string="Remark")