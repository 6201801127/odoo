from ast import literal_eval
from odoo import models, fields, api


class TourAccomodationDetails(models.Model):
    _name = "kw_tour_accomodation"
    _description = "Tour Accommodation"

    # @api.model
    # def get_city_domain(self):
    #     domain = [('id', '=', 0)]
    #     if self._context.get('tour_city_list'):
    #         domain = [('id', 'in', literal_eval(self._context['tour_city_list']))]
    #     return domain

    tour_id = fields.Many2one('kw_tour', required=True, ondelete="cascade")
    acc_arrange = fields.Selection(string="Accommodation Arrangement", selection=[('Company', 'Company')],
                                   default="Company", required=True)
    name = fields.Char('Name Of The Agency')
    arrangement = fields.Selection(string="Accommodation Type", selection=[
        ('Hotel', 'Hotel'), ('Guest House', 'Guest House')], required=False)
    guest_house_id = fields.Many2one('kw_tour_guest_house', "Guest House", ondelete="set null")
    contact_person = fields.Char('Contact Person')
    contact_no = fields.Char('Contact No.')
    country_id = fields.Many2one("res.country")
    city_id = fields.Many2one('kw_tour_city', "City")
    hotel_name = fields.Char("Hotel Name", required=False)
    telephone_no = fields.Char("Tel. No.")
    check_in_time = fields.Datetime("Check In Date & Time", required=False)
    check_out_time = fields.Datetime("Check Out Date & Time", required=False)
    no_of_night = fields.Integer("No. Of Days")
    advance_paid = fields.Float("Advance Booking Amount")
    currency_id = fields.Many2one("res.currency", "Currency")
    document = fields.Binary("Upload Document")
    hotel_display_name = fields.Char("Hotel/Guest House", compute="compute_hotel_guest_house")

    # @api.model
    # def _get_currency_domain(self):
    #     company_currency_id = self.env.user.company_id.currency_id.id
    #     return [("id", "in", [company_currency_id, self.env.ref("base.USD").id])]

    @api.depends('guest_house_id', 'hotel_name', 'arrangement')
    @api.multi
    def compute_hotel_guest_house(self):
        for accomodation in self:
            if accomodation.arrangement == "Hotel":
                accomodation.hotel_display_name = accomodation.hotel_name
            else:
                accomodation.hotel_display_name = accomodation.guest_house_id.name

    @api.onchange('check_in_time', 'check_out_time')
    def calculate_days(self):
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            common_days = 0
            if delta.days:
                common_days += delta.days
            total_hours = delta.seconds // 3600
            if total_hours:
                common_days += 1
            self.no_of_night = common_days

    @api.onchange('city_id')
    def change_guest_house_info(self):
        if self.city_id:
            if self.guest_house_id and not self.guest_house_id.city_id == self.city_id:
                self.guest_house_id = False

    @api.onchange('arrangement')
    def accomodation_details(self):
        if self.arrangement == "Guest House":
            self.name = False
            self.contact_person = False
            self.contact_no = False
            self.hotel_name = False
            self.telephone_no = False
        elif self.arrangement == "Hotel":
            self.guest_house_id = False
