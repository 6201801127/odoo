# -*- coding: utf-8 -*-
from odoo import models, fields

class TrainingAttendance(models.Model):
    _name = 'kw_training_attendance_details'
    _description = "Kwantify Training Attendance Details"

    attendance_id = fields.Many2one("kw_training_attendance", string='Attendance',ondelete='cascade')
    training_id = fields.Many2one(related="attendance_id.training_id")
    participant_id = fields.Many2one("hr.employee", string='Employee',domain=['|',('active','=',True),('active','=',False)])
    attended = fields.Boolean('Attended',default=False)