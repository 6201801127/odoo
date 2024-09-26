# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class MeetingHourExpenseReport(models.Model):
    _name           = "kw_meeting_tagwise_hour_expense_report"
    _description    = "Meeting Tagwise Hour Expense Statistics"
    _auto           = False
    _rec_name       = 'name'


    name            = fields.Char(string='Subject',) 
    meeting_tag     = fields.Many2one(string='Meeting Tag',comodel_name='calendar.event.type',)
    meeting_id      = fields.Many2one(string='Meeting',comodel_name='kw_meeting_events',)
    start           = fields.Datetime(string='Start Datetime',)
    # stop            = fields.Datetime(string='stop',)
    duration        = fields.Float(string='Duration',)
    meeting_year    = fields.Integer(string='Year',)

    @api.model_cr
    def init(self):
        # self._table = kw_meeting_tagwise_hour_expense_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            SELECT CONCAT(MS.id,'TG',KW.type_id) as id,MS.id as meeting_id,MS.name,MS.start,MS.stop,MS.duration,KW.type_id as meeting_tag ,date_part('year', MS.start) as meeting_year
            FROM kw_meeting_events MS
            INNER JOIN kwmeeting_category_rel KW ON KW.event_id = MS.id AND MS.recurrency =	False AND MS.state !='cancelled'

        )""" % (self._table))


   