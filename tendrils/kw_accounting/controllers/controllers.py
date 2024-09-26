import json
from odoo import http
from odoo.addons.web.controllers.main import ReportController
from odoo.http import request

class PrtReportController(ReportController):

    @http.route(['/report/download'], type='http', auth="user",cors='*')
    def report_download(self, data, token, context=None):
        res = super(PrtReportController, self).report_download(data, token)
        if json.loads(data)[2] in ('open', 'print'):
            res.headers['Content-Disposition'] = res.headers['Content-Disposition'].replace('attachment', 'inline')
        return res


