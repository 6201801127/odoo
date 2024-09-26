from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import base64, io, sys
from PIL import Image, JpegImagePlugin as JIP
from io import BytesIO
import re
from odoo.tools.mimetypes import guess_mimetype
import mimetypes, os


class kw_employee_social_image(models.Model):
    _name = 'kw_employee_social_image'
    _description = 'Employee Candid Image'
    _rec_name = 'emp_id'

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=True)

    no_of_skip = fields.Integer(string='No of Skips', default=0)
    social_image = fields.Binary(string='Employee Candid picture')
    image_name = fields.Char(string='Image Name')
    is_sync = fields.Boolean(string='Is Synced?')
    skip_date = fields.Date('Skip Date')
    active = fields.Boolean(default=True)

    def crop_image(self, image):
        basewidth, baseheight = 96, 63

        file_image = base64.b64decode(image)
        stream = io.BytesIO(file_image)
        img = Image.open(stream)

        if img.format == 'PNG':
            img = img.convert('RGB')
        owidth, oheight = img.size

        # # resize if bigger size
        if oheight > baseheight or owidth > basewidth:
            # resize
            if owidth < oheight:
                # Portrait
                wpercent = (basewidth / float(owidth))
                hsize = int((float(oheight) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            else:
                # Landscape
                wpercent = (baseheight / float(oheight))
                wsize = int((float(owidth) * float(wpercent)))
                img = img.resize((wsize, baseheight), Image.ANTIALIAS)

            # img = img.crop((0, 0, basewidth, baseheight))

        buffered = BytesIO()
        img.save(buffered, format="JPEG",
                 subsampling=JIP.get_sampling(img),
                 optimize=True,
                 quality=100)
        img_str = base64.b64encode(buffered.getvalue())
        return img_str

    @api.model
    def create(self, vals):
        if vals.get('social_image'):
            vals['social_image'] = self.crop_image(vals.get('social_image'))
        return super(kw_employee_social_image, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('social_image'):
            vals['social_image'] = self.crop_image(vals.get('social_image'))
            vals['is_sync'] = False
        return super(kw_employee_social_image, self).write(vals)

    @api.model
    def _check_image(self, user_id):
        feedback_url = f"/candid-image/upload/{user_id}"
        return feedback_url

    @api.model
    def check_employee_social_image(self, user):
        # kw_employee_social_notify config check is pending
        image_url = False
        if user.employee_ids:
            social_image = self.env['kw_employee_social_image'].sudo().search([('emp_id', '=', user.employee_ids[0].id)])
            if not social_image or (social_image and not social_image.social_image
                                    and (not social_image.skip_date or social_image.skip_date < datetime.today().date())):
                image_url = self._check_image(user.employee_ids[0].id)
        return image_url
