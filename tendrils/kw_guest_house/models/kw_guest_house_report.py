from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, tools

class KwGuestHouseReport(models.Model):
    _name = 'kw_guest_house_report'
    _auto = False

    guest_house_id = fields.Many2one('kw_guest_house_master', string = 'Guest House')
    address = fields.Text(string = 'Address')
    country = fields.Many2one('res.country', string = 'Country')
    state = fields.Many2one('res.country.state', string = 'State')
    city = fields.Many2one('res.city', string = 'City')
    no_of_single_room = fields.Integer(string = 'No of Single Room')
    no_of_double_room = fields.Integer(string = 'No of Double Room')
    available_single_room = fields.Integer(string = 'Available Single Rooms (Today)', related='guest_house_id.available_single_room')
    available_double_room = fields.Integer(string = 'Available Double Rooms (Today)', related='guest_house_id.available_double_room')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    select row_number() over() as  id,
                    id as guest_house_id,
                    address as address,
                    country_id as country,
                    state_id as state,
                    city_id as city,
                    no_of_single_room as no_of_single_room,
                    no_of_double_room as no_of_double_room
            from
                    kw_guest_house_master    
        )
        """
        self.env.cr.execute(query)



class KwGuestHouseBookingReport(models.Model):
    _name = 'kw_guest_house_booking_report'
    _auto = False

    booking_id = fields.Char(string='Booking ID')
    employee_name = fields.Many2one('hr.employee', string = 'Employee Name')
    guest_type = fields.Char(string = 'Guest Type')
    tour_ref = fields.Char(string = 'Tour Reference')
    # requesting_for_id = fields.Many2one('hr.employee', string = 'Requesting For')
    requesting_for = fields.Char(string = 'Requesting For')
    guest_house_id = fields.Many2one('kw_guest_house_master', string = 'Guest House')
    country = fields.Many2one('res.country', string = 'Country')
    state = fields.Many2one('res.country.state', string = 'State')
    city = fields.Many2one('res.city', string = 'City')
    check_in_date_time = fields.Datetime(string = 'Check In Time')
    check_out_date_time = fields.Datetime(string = 'Check Out Time')
    check_in_date = fields.Date(string = 'Check In Date')
    check_out_date = fields.Date(string = 'Check Out Date')
    room_type = fields.Char(string = 'Room Type')
    booking_type = fields.Char(string = 'Booking Type')
    room_no = fields.Many2one('kw_room_master', string = 'Room No')
    status = fields.Char(string = 'Status')
    no_of_guests = fields.Integer(string = 'No. of Guests')
    rating = fields.Char(string = 'Rating Out Of 5')
    feedback = fields.Char(string = 'Feedback')

    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""
            CREATE or REPLACE VIEW {self._table} as (
                SELECT
                    row_number() over() as id,
                    booking.booking_id,
                    booking.requested_by_id as employee_name,
                    booking.requesting_for as requesting_for,
                    CASE
                        WHEN booking.guest_type = 'new_joinee' THEN 'new joinee'
                        ELSE booking.guest_type
                    END AS guest_type,
                    tour.code as tour_ref,
                    booking.no_of_guests as no_of_guests,
                    booking.guest_house_id as guest_house_id,
                    booking.country_id as country,
                    booking.state_id as state,
                    booking.city_id as city,
                    booking.check_in_date_time as check_in_date_time,
                    booking.check_out_date_time as check_out_date_time,
                    date(booking.check_in_date_time) as check_in_date,
                    date(booking.check_out_date_time) as check_out_date,
                    booking.room_type as room_type,
                    CASE
                        WHEN booking.booking_type = 'fully_book' THEN 'fully book'
                        WHEN booking.booking_type = 'partially_book' THEN 'partially book'
                        ELSE booking.booking_type
                    END AS booking_type,
                    booking.room_id as room_no,
                    CASE
                        WHEN booking.state = 'cancellation_requested' THEN 'cancellation requested'
                        ELSE booking.state
                    END AS status,
                    feedback.rating as rating,
                    feedback.feedback as feedback
                FROM
                    kw_guest_house_booking booking
                LEFT JOIN
                    kw_tour tour ON booking.tour_ref_id = tour.id
                LEFT JOIN
                    kw_house_master_feedback feedback ON booking.id = feedback.booking_id
            )
        """
        self.env.cr.execute(query)


# booking.requesting_for_id as requesting_for_id,   (for admin guest_type)
