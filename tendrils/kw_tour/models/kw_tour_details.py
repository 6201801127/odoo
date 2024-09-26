from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourDetails(models.Model):
    _name = "kw_tour_details"
    _description = "Tour Details"

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=45, second=0, microsecond=0)

        time_list = [(start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p'))]

        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list


    tour_id = fields.Many2one("kw_tour", "Tour", required=True, ondelete='cascade')
    tour_type = fields.Selection(string="Type", required=False,
                                 selection=[('Domestic', 'Domestic'), ('International', 'International')])
    from_date = fields.Date(string="From Date", required=True, )
    from_time = fields.Selection(selection='_get_time_list', string="From Time")

    from_country_id = fields.Many2one('res.country', string="From Country", related="from_city_id.country_id")
    from_city_id = fields.Many2one('kw_tour_city', string="From City", required=True)
    from_city_currency_id = fields.Many2one("res.currency", "Currency of From City")

    to_date = fields.Date(string="To Date", required=True, )
    to_time = fields.Selection(selection='_get_time_list', string="To Time")

    to_country_id = fields.Many2one('res.country', string="To Country", related="to_city_id.country_id")
    to_city_id = fields.Many2one('kw_tour_city', string="To City", required=True)
    to_city_class = fields.Many2one( related="to_city_id.classification_type_id", string="City Class")

    to_city_currency_id = fields.Many2one("res.currency", "Currency of To City")

    travel_arrangement = fields.Selection(string="Travel Arrangement",
                                          selection=[('Self', 'Self'), ('Company', 'Company')], required=True,
                                          default="Company")

    accomodation_arrangement = fields.Selection(string="Accommodation Arrangement",
                                                selection=[('Self', 'Self'),
                                                           ('Company', 'Company'),
                                                           ('Client Arrangement', 'Client Arrangement'),
                                                           ('Not Required', 'Not Required')
                                                           ], required=True, default="Company")
    travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode")
    currency_id = fields.Many2one("res.currency", "Currency")
    cost = fields.Integer("Ticket Cost")
    document = fields.Binary("Upload Document")
    document_name = fields.Char("File Name")

    state = fields.Selection(string='Status', related="tour_id.state",
                             selection=[
                                 ('Draft', 'Draft'),
                                 ('Applied', 'Applied'),
                                 ('Approved', 'Approved'),
                                 ('Forwarded', 'Forwarded'),
                                 ('Traveldesk Approved', 'Traveldesk Approved'),
                                 ('Finance Approved', 'Finance Approved'),
                                 ('Rejected', 'Rejected'),
                                 ('Cancelled', 'Cancelled')
                             ])

    @api.model
    def default_get(self, fields):
        res = super(TourDetails, self).default_get(fields)

        tour_start_city = self._context.get('default_from_city', False)
        tour_last_city = self._context.get('default_last_city', False)
        tour_travel_date = self._context.get('default_last_travel_date', False)
        last_travel_time = self._context.get('default_last_travel_time', False)
        # print("last_travel_time=============", last_travel_time)
        if tour_last_city:
            city = self.env['kw_tour_city'].browse(tour_last_city)
            res['from_city_id'] = city.id
            res['from_country_id'] = city.country_id.id

        if tour_travel_date:
            res['from_date'] = tour_travel_date
        if last_travel_time:
            res['from_time'] = last_travel_time

        return res

    @api.onchange('travel_arrangement')
    def set_travel_details(self):
        if self.state and self.state in ['Draft', 'Applied', 'Forwarded'] \
                and self.travel_arrangement and self.travel_arrangement == 'Self':
            self.travel_mode_id = self.currency_id = self.cost = self.document = False

    @api.onchange('from_city_id', 'to_city_id')
    def set_from_city_domain(self):
        if self.from_city_id:
            currency_ids = self.from_city_id.mapped('expense_ids.currency_type_id')
            self.from_city_currency_id = currency_ids and currency_ids[0].id
        else:
            self.from_city_currency_id = False

        if self.to_city_id:
            currency_ids = self.to_city_id.mapped('expense_ids.currency_type_id')
            self.to_city_currency_id = currency_ids and currency_ids[0].id
        else:
            self.to_city_currency_id = False
        all_currencies = self.from_city_currency_id | self.to_city_currency_id

        if self.currency_id and self.currency_id not in all_currencies:
            self.currency_id = False

    @api.onchange('from_date', 'to_date')
    def onchange_date(self):
        for record in self:
            if record.from_date and record.to_date:
                if record.from_date > record.to_date:
                    raise ValidationError("From Date cannot be greater than To Date.")
