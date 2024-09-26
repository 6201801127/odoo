from odoo import models, fields, api


class KtTypeMaster(models.Model):
    _name = 'kw_kt_type_master'
    _description = 'KT Type Master'
    _rec_name = 'name'
    # _order = 'sequence'

    name = fields.Char("KT Type", required=True)
    code = fields.Char("KT Code", required=True)
    is_manual = fields.Boolean("Manual KT", required=True)
    # sequence = fields.Integer(string="Sequence")
    # active = fields.Boolean(
    #     help="The active field allows you to hide the date range type "
    #     "without removing it.", default=True)

    _sql_constraints = [('name_unique', 'unique (name)', 'KT type name must be unique!'),
                        ('code_unique', 'unique (code)', 'KT type code must be unique!')]
