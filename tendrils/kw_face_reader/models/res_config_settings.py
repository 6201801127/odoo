
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
   

    kw_face_reader_employee_image_path = fields.Char(
        string="Tendrils Face Reader Employee Image Path",
        help="Tendrils Face Reader Employee Image Path",
       
    )

    kw_face_reader_unmatched_image_path = fields.Char(
        string="Tendrils Face Reader Unmatched Image Path",
        help="Tendrils Face Reader Unmatched Image Path",
       
    )

    kw_face_reader_training_url = fields.Char(
        string="Tendrils Face Reader Training URL",
        help="Tendrils Face Reader Training URL",
       
    )

    kw_face_reader_url = fields.Char(
        string="Tendrils Face Reader URL",
        help="Tendrils Face Reader URL",
       
    )

    kw_face_reader_api_url = fields.Char(
        string="Tendrils Face Reader API URL",
        help="Tendrils Face Reader API URL",
       
    )

   

    @api.model
    def get_values(self):
        res     = super(ResConfigSettings, self).get_values()
        param   = self.env['ir.config_parameter'].sudo()

        res.update(
            kw_face_reader_employee_image_path = str(param.get_param('kw_face_reader.employee_image_path')),
            kw_face_reader_unmatched_image_path= str(param.get_param('kw_face_reader.unmatched_image_path')),
            kw_face_reader_training_url= str(param.get_param('kw_face_reader.training_url')),
            kw_face_reader_url= str(param.get_param('kw_face_reader.reader_url')),
            kw_face_reader_api_url= str(param.get_param('kw_face_reader.api_url')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_face_reader.employee_image_path', self.kw_face_reader_employee_image_path)
        param.set_param('kw_face_reader.unmatched_image_path', self.kw_face_reader_unmatched_image_path)
        param.set_param('kw_face_reader.training_url', self.kw_face_reader_training_url)
        param.set_param('kw_face_reader.reader_url', self.kw_face_reader_url)
        param.set_param('kw_face_reader.api_url', self.kw_face_reader_api_url)