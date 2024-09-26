# -*- coding: utf-8 -*-

from odoo import models, fields, api


class kw_meeting_time_master(models.Model):
    _name = 'kw_meeting_time_master'
    _description = 'Meeting '

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Time in AM/PM',
        required=True
    )

    # time_stamp = fields.Char(
    #     string='Time in HH24:MM:SS',required=True
    # )

    time_stamp = fields.Float('Time in HH24:MM ', required=True)

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Time in AM/PM already exists !'),
        ('time_stamp_unique', 'unique (time_stamp)', 'Time in HH24:MM already exists !')
    ]
