# -*- coding: utf-8 -*-
import pytz
from datetime import date,datetime
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug

class appraisal_inherits(models.Model):
    _inherit = "hr.appraisal"

    avg_score = fields.Float('Average Score',compute='count_avg_score')
    deg_id    = fields.Char(related='emp_id.job_id.name')

    def count_avg_score(self):
        for record in self:
            if record.state.sequence == 5 or record.state.sequence == 6:
                total_score = 0
                questions = 0
                for records in record.hr_manager_id:
                    if record.lm_input_id:
                        user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',record.lm_input_id.id)])
                    else:
                        user_input = self.env['survey.user_input'].search(['&',('appraisal_id', '=', record.id),('partner_id','=',records.user_id.partner_id.id)],limit=1)
                        user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',user_input.id)])
                    if len(user_input_line):
                        questions += len(user_input_line)
                        for data in user_input_line:
                            total_score += data.quizz_mark
                if questions !=0:
                    score = total_score/questions
                    record.avg_score = score
            else:
                pass

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     # print(self._context)
    #     if self._context.get('search_default_filter_current_financial_year'):
    #         current_date = date.today()
    #         current_year = date.today().year
    #         if current_date < date(current_year, 4, 1):
    #             start_date = date(current_year-1, 4, 1)
    #             end_date = str(date(current_year, 3, 31).year)[:2]
    #             final_date = str(start_date.year)+'-'+ end_date
    #             args += [('appraisal_year','=',final_date)]
    #     return super(appraisal_inherits, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)