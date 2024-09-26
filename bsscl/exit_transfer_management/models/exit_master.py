from odoo import models, fields, api

class ExitMaster(models.Model):
    _name = 'exit.master'
    _description = 'Exit Master'
    _rec_name = "name"

    name = fields.Char(string="Exit Type / निकास प्रकार",tracking=True)
    # group_id = fields.Many2one("res.groups", string="Access to group")
    user_type = fields.Selection([("user", "User"),
        ("hr", "HR")
    ],string='Type of User',tracking=True)
    
    _sql_constraints = [('name_uniq',
                         'unique (name)',
                         'Exit type already present!!')]
