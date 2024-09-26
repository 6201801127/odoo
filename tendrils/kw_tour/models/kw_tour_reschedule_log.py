# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourRescheduleLog(models.Model):
    _name = "kw_tour_reschedule_log"
    _description = "Tour Reschedule Log"
    _rec_name = "tour_id"

    tour_id = fields.Many2one('kw_tour', required=True)
    date_travel = fields.Date("Start Date", required=True)
    date_return = fields.Date("Return Date", required=True)

    detail_ids = fields.One2many('kw_tour_reschedule_details_log', 'tour_reschedule_id', 'Details')
    reschedule_count = fields.Integer("Reschedule Count", default=1)
