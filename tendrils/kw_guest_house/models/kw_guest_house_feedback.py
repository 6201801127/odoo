from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KwGuestHouseFeedback(models.Model):
    _name = 'kw_house_master_feedback'
    _rec_name = 'booking_id'

    booking_id = fields.Many2one('kw_guest_house_booking', string='Booking ID', track_visibility='onchange')
    requested_by_id = fields.Many2one('hr.employee', string = 'Requested By', related='booking_id.requested_by_id', readonly = True)
    guest_house = fields.Char(string = 'Guest House', track_visibility='onchange', related='booking_id.guest_house_id.guest_house_name')
    guest_house_address = fields.Text(string = 'Address', track_visibility='onchange', related='booking_id.guest_house_address')
    guest_type = fields.Selection(([('self', 'Self'), ('guest', 'Guest'), ('new_joinee', 'New Joinee')]), string = 'Guest Type', track_visibility='onchange', related='booking_id.guest_type')
    tour_ref = fields.Char(string = 'Tour reference', track_visibility='onchange', related='booking_id.tour_ref_id.code')
    no_of_guests = fields.Integer(string = 'No. of Guests',track_visibility='onchange', related='booking_id.no_of_guests')
    requesting_for = fields.Char(string = 'Requesting For', related='booking_id.requesting_for')
    country = fields.Char(string = 'Country', track_visibility='onchange', related='booking_id.country_id.name')
    state = fields.Char(string = 'State', track_visibility='onchange', related='booking_id.state_id.name')
    check_in_date_time = fields.Datetime(string = 'Check In Time',track_visibility='onchange', related='booking_id.check_in_date_time')
    check_out_date_time = fields.Datetime(string = 'Check Out Time',track_visibility='onchange', related='booking_id.check_out_date_time')
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string = 'Room Type',track_visibility='onchange', related='booking_id.room_type')
    booking_type = fields.Selection([('fully_book', 'Fully Book'), ('partially_book', 'Partially Book')], string = 'Booking Type',track_visibility='onchange', related='booking_id.booking_type')
    room_no = fields.Char(string = 'Room No',track_visibility='onchange', related='booking_id.room_id.room_name')
    rating = fields.Selection(([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]), string = 'Rating', default='0', track_visibility='onchange')
    feedback = fields.Text(string = 'Feedback',track_visibility='onchange')
    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}

        if context.get('feedback'):
            if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
                args += ['|', ('requested_by_id.user_id','=',self.env.user.id), ('requested_by_id.user_id','!=',self.env.user.id)]
            else:
                args += [('requested_by_id.user_id','=',self.env.user.id)]
    
        return super(KwGuestHouseFeedback, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(('You cannot duplicate a Feedback.'))
    
    @api.multi
    def unlink(self):
        raise UserError('You have no access to delete this record.')
