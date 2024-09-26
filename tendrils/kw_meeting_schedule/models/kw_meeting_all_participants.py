# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class kw_meeting_all_participants(models.Model):
    _name = 'kw_meeting_all_participants'
    _description = 'Meeting All Participants'

    # _rec_name       = 'name'
    _order = 'type,name'
    _auto = False

    name = fields.Char(string='Name', )
    email = fields.Char(string='Email ID', )
    attendee_type = fields.Char(string='Attendee Type', )

    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner', )
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )

    meeting_id = fields.Many2one(string='meeting', comodel_name='kw_meeting_events', )
    attendance_status = fields.Boolean(string='Attended Meeting', )

    attendee_id = fields.Integer(string='Attendee Id')
    type = fields.Integer(string='Type')

    @api.model_cr
    def init(self):
        """ Event all partcipants """
        tools.drop_view_if_exists(self._cr, 'kw_meeting_all_participants')
        self._cr.execute("""
            CREATE VIEW kw_meeting_all_participants AS (
           
                SELECT CONCAT('IU',id) AS id, id AS attendee_id, common_name AS name, email, employee_id, partner_id, 
                attendance_status, event_id AS meeting_id, 1 AS type, 'Internal User' AS attendee_type FROM kw_meeting_attendee

                UNION

                SELECT CONCAT('EU',id) AS id, id AS attendee_id, name, email, NULL AS employee_id, partner_id, 
                attendance_status, meeting_id, 2 AS type,'External User' AS attendee_type  FROM kw_meeting_external_participants
           
            ) 
    """)
