from odoo import models, fields, api


class kw_onboarding_dms_integration_handbook(models.Model):
    # _inherit = 'kw_onboarding_handbook'

    _name = 'kw_onboarding_handbook'
    # #integration with DMS
    _inherit = [
        'kw_onboarding_handbook',
        'kw_dms.mixins.integration',
    ]
