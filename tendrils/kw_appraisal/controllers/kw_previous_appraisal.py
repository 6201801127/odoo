from odoo import http
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.http import request

class previous_appraisal_status(http.Controller):
    @http.route('/previous_appraisal/', auth='public', website=True)
    def previous_appraisal(self, **args):
        # print("Appraisal controller worked")
        pid_search = request.env['kw_employee_score'].search([])
        for record in pid_search:
            pid = record.prd_no
            qst = {'q':'pid'}
            # print(pid)
            url = ("https://portal.csmpl.com/Appraisal/FinalApdetails.aspx?Pid=qst")
            # print(url)
        return werkzeug.utils.redirect("https://portal.csmpl.com/Appraisal/FinalApdetails.aspx?Pid=pid")

