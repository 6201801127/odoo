# -*- coding: utf-8 -*-


import base64, re

from odoo import  _
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import ValidationError

extension_message = _("Extension '%(extension)s' not allowed. Allowed extensions are: '%(allowed_extensions)s.'")
mime_message = _("MIME type '%(mimetype)s' is not valid. Allowed types are: %(allowed_mimetypes)s.")
max_size_message = _('Maximum file size should be less than %(allowed_size)s MB.')

email_format_message = _('Your email is invalid for: %(email)s')


def validate_file_mimetype(image,allowed_extensions):
    if image:
        mimetype = guess_mimetype(base64.b64decode(image), default='image/png')

        if str(mimetype) not in allowed_extensions:
            message = mime_message % {'mimetype': mimetype, 'allowed_mimetypes': ', '.join(allowed_extensions)}
            raise ValidationError(message)


def validate_file_size(image, file_size_mb):
    if image:
        img_size = (len(image) * 3 / 4)
        sel_img_size_mb = (img_size / 1024) / 1024

        if sel_img_size_mb > float(file_size_mb):
            message = max_size_message % {'allowed_size': file_size_mb}
            raise ValidationError(message)


def validate_email(email):
    if email:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) != None:
            raise ValidationError(email_format_message % {'email': email})
