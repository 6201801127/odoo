import re
import json
import logging

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    
    ##----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    def _attachment_location_selection(self):
        locations = self.env['ir.attachment'].storage_locations()
        return list(map(lambda location: (location, location.upper()), locations))

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    attachment_location = fields.Selection(
        selection=lambda self: self._attachment_location_selection(),
        string='Storage Location',
        required=True,
        default='file',
        help="Attachment storage location.")
    
    attachment_location_changed = fields.Boolean(
        compute='_compute_attachment_location_changed',
        string='Storage Location Changed')
    
    
    binary_max_size = fields.Integer(
        string='File Size Limit',
        required=True,
        default=25,
        help="""Maximum allowed file size in megabytes. Note that this setting only adjusts
            the binary widgets accordingly. The maximum file size on your server can probably
            be restricted in several places. Note that a large file size limit and therefore
            large files in your system can significantly limit performance.""")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('kw_dms_utils.binary_max_size', self.binary_max_size)
        param.set_param('ir_attachment.location', self.attachment_location)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(binary_max_size=int(params.get_param('kw_dms_utils.binary_max_size', 25)))
        res.update(attachment_location=params.get_param('ir_attachment.location', 'file'))
        return res
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     ret_val = super(ResConfigSettings, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     modules = self.env['ir.module.module'].sudo().search([]).mapped('name')
    #     document = etree.XML(ret_val['arch'])
    #     for field in ret_val['fields']:
    #         if field.startswith("module_") and field[len("module_"):] not in modules:
    #             for node in document.xpath("//field[@name='%s']" % field):
    #                 if node.get("widget") != 'upgrade_boolean':
    #                     node.set("widget", "module_boolean")
    #     ret_val['arch'] = etree.tostring(document, encoding='unicode')
    #     return ret_val

    
    def attachment_force_storage(self):
        self.env['ir.attachment'].force_storage()
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('attachment_location')
    def _compute_attachment_location_changed(self):
        params = self.env['ir.config_parameter'].sudo()
        location = params.get_param('ir_attachment.location', 'file')
        for record in self:
            record.attachment_location_changed = location != self.attachment_location

