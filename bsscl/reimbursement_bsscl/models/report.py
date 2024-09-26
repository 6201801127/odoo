from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class ReportReimbursement(models.AbstractModel):
    _name = 'report.reimbursement'
    _description = "Reimbursement Report"


    @api.model
    def get_reimbursement_report(self, docids, data=None):
        lst = []
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for line in self.env['reimbursement'].browse(active_ids):
            lst.append((0, 0, {
                        'reimbursement_sequence': line.reimbursement_sequence,
                        'employee_id': line.employee_id.id,
                        'name': line.name,
                        'working_days': line.working_days,
                        'claimed_amount': line.claimed_amount,
                        'net_amount': line.net_amount,
                    }))
        return lst