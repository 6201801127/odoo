from odoo import models, tools, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    access_type = fields.Selection([('hrms', 'HRMS'),
                                    ('coe/hrms', 'COE/HRMS'),
                                    ])
