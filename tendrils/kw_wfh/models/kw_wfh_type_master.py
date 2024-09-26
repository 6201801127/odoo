from odoo import models, fields


class kw_system_info(models.Model):
    _name = 'kw_system_info'
    _description = "System Info"

    name = fields.Char('Name')
    sequence = fields.Integer("Sequence", default=0, help="Gives the sequence order of reason.")


class kw_wfh_type_master(models.Model):
    _name = 'kw_wfh_type_master'
    _description = "Kwantify WFH Type Master"
    _rec_name = 'type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    type = fields.Char(string='Type')
