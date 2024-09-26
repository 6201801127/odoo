from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResourceQtyUpdateWizard(models.TransientModel):
    _name = 'resource_qty_update_wizard'
    _description = "Resource Quantity Update Wizard"

    resource_map_id = fields.Many2one('kw_resource_mapping_data', string='Employee Role')
    resource_no = fields.Integer(string='No of resource required')
    module_short_name = fields.Char(string='Opportunity Name')
    resource_available = fields.Integer(string='No of resource available')

    @api.multi
    def button_resource_qty_update(self):
        if self.resource_map_id:
            self.resource_map_id.resource_available = self.resource_available

    @api.constrains('resource_no','resource_available')
    def check_resource_available(self):
        if self.resource_no and self.resource_available:
            if int(self.resource_available ) > int(self.resource_no):
                raise ValidationError("Resource Availble should be equal to or less than Resources Required.")
