# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class TourRescheduleDetailsLog(models.Model):
    _name = "kw_tour_reschedule_details_log"
    _description = "Tour Reschedule Details Log"

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=45, second=0, microsecond=0)

        time_list = [(start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p'))]

        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p')))
        return time_list

    tour_reschedule_id = fields.Many2one('kw_tour_reschedule_log', 'Tour Reschedule', required=True)

    from_date = fields.Date(string="From Date", required=True, )
    from_time = fields.Selection(selection='_get_time_list', string="From Time")
    from_city_id = fields.Many2one('kw_tour_city', string="From City", required=True, )
    from_country_id = fields.Many2one('res.country', string="From Country", related="from_city_id.country_id")

    to_date = fields.Date(string="To Date", required=True, )
    to_time = fields.Selection(selection='_get_time_list', string="To Time")
    to_city_id = fields.Many2one('kw_tour_city', string="To City", required=True)
    to_country_id = fields.Many2one('res.country', string="To Country", related="to_city_id.country_id")

    travel_arrangement = fields.Selection(string="Travel Arrangement",
                                          selection=[('Self', 'Self'), ('Company', 'Company')], required=True)
    accomodation_arrangement = fields.Selection(string="Accommodation Arrangement",
                                                selection=[('Self', 'Self'),
                                                           ('Company', 'Company'),
                                                           ('Client Arrangement', 'Client Arrangement'),
                                                           ('Not Required', 'Not Required')
                                                           ], required=True, default="Company")

    travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode")
    currency_id = fields.Many2one("res.currency", "Currency")
    cost = fields.Integer("Cost")
    document = fields.Binary("Upload Document")
