from odoo import models, fields

class kw_wfh_reason_master(models.Model):
	_name='kw_wfh_reason_master'
	_description="Kwantify WFH Reason Master"
	_rec_name='reason'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	reason = fields.Char(string="Reason",required=True,track_visibility='onchange')
	type = fields.Many2many('kw_wfh_type_master','kw_wfh_type_master_rel','type_id','rel_type_id',string="Type")
	no_of_days = fields.Char(string="Max No Of Days Allowed")
	sequence = fields.Integer("Sequence", default=0,help="Gives the sequence order of reason.")
	back_date = fields.Boolean(string="Back Date", default=False)

