import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request, Response
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
import odoo.addons.calendar.controllers.main as main
import datetime
from datetime import date
from werkzeug.exceptions import BadRequest, Forbidden
from odoo.addons.restful.common import invalid_response
import ast
from ast import literal_eval
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError




class my_task_redirect_controller(http.Controller):
    @http.route('/view_details/', methods=["GET"], type='http', csrf=False, auth="public", website=True)
    def my_task_redirect(self):
        try:
            action_id = request.env.ref('task_management.my_task_management_takeaction').id
            view_id = request.env.ref("task_management.my_task_takeaction_list").id
            mytask_url = '/web#view_type=tree&action=%s&model=kw_task_management&view_id=%s' %(action_id,view_id)
            # print("in view action==============================",action_id,view_id,mytask_url)
            return http.request.redirect(mytask_url)
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
            
        