from odoo import api, models, fields
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_stock_multi_locations = fields.Boolean('Storage Locations', implied_group='stock.group_stock_multi_locations',
                                                 help="Store products in specific locations of your warehouse (e.g. bins, racks) and to track inventory accordingly.",
                                                 default=True)
    group_uom = fields.Boolean("Units of Measure", implied_group='uom.group_uom', default=True)
    enable_unit_price = fields.Boolean("Enable Unit price")
    signature_authority_ids = fields.Many2many('hr.employee', 'stock_sign_auth_rel', 'sign_id', 'employee_id',
                                               string='Signature Authority')
    # out_of_stock =fields.Char()
    # out_of_stock_quantity =fields.Char()
    # dead_stock_bol =fields.Char()
    # dead_stock =fields.Char()
    # dead_stock_type = fields.Char()



    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.enable_unit_price
        param.set_param('kw_inventory.enable_unit_price', field1)
        self.env['ir.config_parameter'].set_param('kw_inventory.signature_authority_ids',
                                                  self.signature_authority_ids.ids)

    @api.model
    def get_values(self):
        res = super().get_values()
        signature_authority_ids = self.env['ir.config_parameter'].sudo().get_param(
            'kw_inventory.signature_authority_ids')
        employees = False
        if signature_authority_ids:
            employees = [(6, 0, literal_eval(signature_authority_ids))]
        res.update(signature_authority_ids=employees,
                   enable_unit_price=self.env['ir.config_parameter'].sudo().get_param('kw_inventory.enable_unit_price'))
        return res
