# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
import re
from datetime import date, datetime, timedelta
from odoo.http import request, Response
import logging
_logger = logging.getLogger(__name__)


class KwProject(http.Controller):

    @http.route('/update_opportunity_debtor',type="json", cors='*', auth="public", methods=["POST"], csrf=False)
    def update_opportunity_debtor(self, **post_data):
        employees = request.env['hr.employee'].sudo().search([])
        if post_data:
            data =  post_data.get('data')
            if data:
                try:
                    for rec in data:
                        updated_by = employees.filtered(lambda emp: emp.kw_id == int(rec['updated_by']) if rec['updated_by'] else None)
                        request.env['kw_portlet_recieved_log'].create({
                            'rec_type':rec['type'] if rec['type'] else None,
                            'rec_id':rec['kw_id'] if rec['kw_id'] else None,
                            'changed_date':rec['updated_date'] if rec['updated_date'] else None,
                            'updated_by':updated_by.id if updated_by else None,
                            'status':0
                        })
                    return {'mesg': 'Successfully Updated', 'status': 1}
                except Exception as e:
                    _logger.error("Failed to create records: %s", str(e))
                    return {'mesg': 'Not Updated', 'status': 0}
        else:
            return {'mesg': 'No data provided', 'status': 0}