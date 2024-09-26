from odoo import api, fields, models


class KwResBranch(models.Model):
    _name = 'kw_branch_guest_house'
    _description = "Guest House"
    _rec_name = "guest_house_name"

    guest_house_name = fields.Char('House Name', required=True)
    address = fields.Text('Guest_house Address', size=252)
    caretacker_name = fields.Char('CareTacker Name')
    contact_number = fields.Char('Telephone No')
    branch_code = fields.Many2one('kw_res_branch', string='Branch')
