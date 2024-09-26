# -*- coding: utf-8 -*-
import os
import odoo
from odoo import api, fields, models, http
import time


class KwSessionClear(models.TransientModel):
    _name = 'kw_session_clear'
    _description = "Session timeout"

    @api.model
    def _clear_session(self):
        last_one_hr = time.time() - 60 * 60 * 8  # 8 hr
        sess_path = odoo.tools.config.session_dir
        for fname in os.listdir(sess_path):
            path = os.path.join(sess_path, fname)
            try:
                # os.unlink(path)
                # print('cleared session =====================  ')
                # print(os.path.getmtime(path) < last_one_hr)
                if os.path.getmtime(path) < last_one_hr:
                    os.unlink(path)
                    # print('cleared session =====================  ')
            except OSError:
                pass
