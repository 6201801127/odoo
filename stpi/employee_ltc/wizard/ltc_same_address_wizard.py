from odoo import api, fields, models,_


class SammeAddressWizard(models.TransientModel):
    _name = 'same_address_wizard'
    _description = 'Same Address Wizard'

    ltc_id=fields.Many2one('employee.ltc.advance', 'LTC')

    def button_confirm(self):
        self.ltc_id.state = 'approved'