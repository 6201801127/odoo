# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, tools
from datetime import datetime, date, timedelta
import json

class KwGuestHouseBooking(models.Model):
    _name = 'kw_guest_house_booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'booking_id'
    _description = 'Guest House Booking'


    def available_countries(self):
        available_countries = self.env['kw_guest_house_master'].search([])
        arr=[]
        for rec in available_countries:
            arr.append(rec.country_id.id)
        return [('id', 'in', arr if arr else False)]


    @api.model
    def available_tour(self):
        settled_tour_ids = self.env['kw_tour_settlement'].sudo().search([]).mapped('tour_id.id')
        available_tours = self.env['kw_tour'].sudo().search([
            ('employee_id', '=', self.env.user.employee_ids.id),
            ('state', 'in', ['Approved', 'Traveldesk Approved', 'Finance Approved']),
            ('id', 'not in', settled_tour_ids),
        ])
        return [('id', 'in', available_tours.ids)]

    
    booking_id = fields.Char(string='Booking ID', readonly = True, copy=False, default='New')
    company_id = fields.Many2one('res.company', string="Company", readonly=True, default = lambda self: self.env.user.company_id.id)
    requested_by_id = fields.Many2one('hr.employee', string = 'Requested By', default = lambda self: self.env.user.employee_ids.id, readonly = True)
    guest_type = fields.Selection(([('self', 'Self'), ('guest', 'Guest'), ('new_joinee', 'New Joinee')]), string = 'Guest Type', default = 'self', track_visibility='onchange') # ('team', 'Team') ('admin', 'Admin')another option
    # other_employee_ids = fields.Many2many('hr.employee', 'booking_emp_rel', 'booking_id', 'emp_id', string='Team Members')
    no_of_guests = fields.Integer(string = 'No. of Guests',track_visibility='onchange', autocomplete="off")
    description = fields.Text(string = 'Description',track_visibility='onchange', autocomplete="off")
    requesting_for_id = fields.Many2one('hr.employee', string = 'Requesting For', autocomplete="off")
    user_to_notify_ids = fields.Many2many('hr.employee', string='Notify User(s)', autocomplete="off")
    requesting_for = fields.Char(string = 'Requesting For', autocomplete="off")
    country_id = fields.Many2one('res.country', string = 'Country', domain=available_countries,track_visibility='onchange', autocomplete="off")
    state_id = fields.Many2one('res.country.state', string = 'State', track_visibility='onchange', autocomplete="off")
    city_id = fields.Many2one('res.city', string = 'City', domain="[('state_id', '=', state_id)]",track_visibility='onchange', autocomplete="off")
    guest_house_id = fields.Many2one('kw_guest_house_master', string = 'Guest House', track_visibility='onchange', autocomplete="off")
    guest_house_address = fields.Text(string = 'Address',related='guest_house_id.address', track_visibility='onchange')
    contact_person_1 = fields.Char(string = 'Contact Person', compute='fetch_contact_person')
    contact_person_2 = fields.Char(string = 'Contact Person', compute='fetch_contact_person')
    check_in_date_time = fields.Datetime(string = 'Check In Time',track_visibility='onchange', autocomplete="off")
    check_out_date_time = fields.Datetime(string = 'Check Out Time',track_visibility='onchange', autocomplete="off")
    remarks = fields.Text(string = 'Remarks', track_visibility='onchange', autocomplete="off")
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string = 'Room Type',track_visibility='onchange', autocomplete="off")
    booking_type = fields.Selection([('fully_book', 'Fully Book'), ('partially_book', 'Partially Book')], string = 'Booking Type',track_visibility='onchange', default="partially_book")
    available_room_ids = fields.Many2many('kw_room_master', string='Available Rooms',compute='filter_room',track_visibility='onchange')
    room_id = fields.Many2one('kw_room_master', string = 'Room No',track_visibility='onchange', autocomplete="off")
    tour_ref_id = fields.Many2one("kw_tour", string = 'Tour reference', domain=available_tour, track_visibility='onchange', autocomplete="off")
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'), ('cancellation_requested', 'Cancellation Requested'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected')], string = 'Status', default="draft",track_visibility='onchange')
    facilities_ids = fields.Many2many('kw_facilities_master', 'booking_facility_rel', 'booking_id', 'facility_id', related='guest_house_id.facilities_ids', string='Facilities', store=True, readonly = True)
    photo_ids = fields.One2many('kw_guest_house_photo_master', 'photo_guest_house_id', related = 'guest_house_id.photo_ids')
    room_availability = fields.Html(string='Room Availability', compute='_compute_room_availability', store=False)
    pending_at = fields.Many2many('hr.employee', string='Pending At', compute='get_pending_at')
    action_log_ids = fields.One2many('guest_house_booking_action_log', 'ref_id', string='Action Log Table')
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    manager_approve_reject_boolean = fields.Boolean(compute='check_button_access')
    manager_approve_cancel_boolean = fields.Boolean(compute='check_button_access')
    user_cancel_boolean = fields.Boolean(compute='check_button_access') #if logged in user watching his record which are in applied, ra_approved and approved state
    check_manager_boolean = fields.Boolean(compute='compute_check_user')
    show_table_boolean_user = fields.Boolean(compute='compute_check_user_teble_access')
    show_table_boolean_manager = fields.Boolean(compute='compute_check_user_teble_access')
    guest_house_auto_access_boolean = fields.Boolean(compute='compute_manual_or_auto_access')
    guest_house_manual_access_boolean = fields.Boolean(compute='compute_manual_or_auto_access')
    show_warning_for_single = fields.Boolean(compute='warning_for_room_type')
    show_warning_for_double = fields.Boolean(compute='warning_for_room_type')
    given_feedback_boolean = fields.Boolean()
    feedback_button_access_boolean = fields.Boolean(compute='check_button_access')


    @api.onchange('country_id')
    def available_states(self):
        available_states = self.env['kw_guest_house_master'].search([('state_id.country_id','=',self.country_id.id)])
        return{'domain': {'state_id': [('id', 'in',available_states.mapped('state_id').ids)]}}    
    

    @api.onchange('state_id')
    def available_guest_house(self):
        available_guest_houses = self.env['kw_guest_house_master'].search([('state_id', '=', self.state_id.id)])
        return {'domain': {'guest_house_id': [('id', 'in', available_guest_houses.ids)]}}
        

    @api.constrains('available_room_ids', 'room_type')
    def guest_house_room_availability(self):
        rooms = self.env['kw_room_master'].search([
            ('room_type', '=', self.room_type),
            ('guest_house_of_room_id','=',self.guest_house_id.id)
        ])
        if not rooms:
            raise ValidationError(f"There is no {self.room_type} type rooms in the Guest House.")
        elif rooms and len(self.available_room_ids.ids) == 0: 
            raise ValidationError("There is no rooms available for the selected dates.")
            
    @api.depends('room_type', 'guest_house_id')
    def warning_for_room_type(self):
        rooms = self.env['kw_room_master'].search([
            ('room_type', '=', self.room_type),
            ('guest_house_of_room_id','=',self.guest_house_id.id)
        ])
        if not self.id and self.room_type and not rooms:
            self.show_warning_for_single = True if self.room_type == 'single' else False
            self.show_warning_for_double = True if self.room_type == 'double' else False


    @api.constrains('check_in_date_time', 'check_out_date_time', 'guest_type')
    def _check_new_joinee_duration(self):
        if self.check_in_date_time and self.check_out_date_time and self.guest_type=='new_joinee':
            duration = self.check_out_date_time - self.check_in_date_time
            if duration > timedelta(days=15):
                raise ValidationError("New joinee bookings cannot exceed 15 days.")        
        
        
    @api.onchange('check_in_date_time', 'check_out_date_time')
    def guest_house_room_type_false(self):
        self.room_type=False

    @api.onchange('country_id')
    def _clear_for_country(self):
        self.state_id = False

    @api.onchange('state_id')
    def _clear_for_state(self):
        # self.city_id = False
        self.guest_house_id = False

    # @api.onchange('city_id')
    # def _clear_for_city(self):
    #     self.guest_house_id = False

    @api.onchange('room_type', 'booking_type')
    def room_id_room_type_false(self):
        self.room_id=False

    @api.onchange('guest_house_id')
    def guest_house_id_room_type_false(self):
        self.room_type=False


    @api.depends('requested_by_id')
    def compute_check_user(self):
        for rec in self:
            if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
                rec.check_manager_boolean = True


    @api.depends('requested_by_id', 'state', 'given_feedback_boolean')
    def check_button_access(self):
        for rec in self:
            rec.manager_approve_reject_boolean = True if rec.state=='applied' and self.env.user.has_group('kw_guest_house.guest_house_manager_group') else False
            rec.manager_approve_cancel_boolean = True if rec.state=='cancellation_requested' and self.env.user.has_group('kw_guest_house.guest_house_manager_group') else False
            rec.user_cancel_boolean = True if rec.requested_by_id == self.env.user.employee_ids and rec.state in ['applied', 'approved'] else False 
            rec.feedback_button_access_boolean = True if rec.state == 'approved' and not rec.given_feedback_boolean and rec.requested_by_id.id == self.env.user.employee_ids.id and rec.check_out_date_time.date() <= fields.Date.today() else False


    @api.depends('guest_house_id')
    def fetch_contact_person(self):
        for rec in self:
            if rec.guest_house_id:
                if rec.guest_house_id.contact_person_1_id:
                    rec.contact_person_1 = f"{rec.guest_house_id.contact_person_1_id.name} ({rec.guest_house_id.contact_no_1 if rec.guest_house_id.contact_no_1 else ' '})"
                else:
                    rec.contact_person_1 = False
            if rec.guest_house_id:
                if rec.guest_house_id.contact_person_2_id:
                    rec.contact_person_2 = f"{rec.guest_house_id.contact_person_2_id.name} ({rec.guest_house_id.contact_no_2 if rec.guest_house_id.contact_no_2 else ' '})"
                else:
                    rec.contact_person_2 = False
                
        
    @api.depends('guest_house_id')
    def compute_manual_or_auto_access(self):
        for rec in self:
            rec.guest_house_auto_access_boolean = True if self.env.user.has_group('kw_guest_house.guest_house_user_group') and rec.guest_house_id.auto_boolean == True else False
            if not self.env.user.has_group('kw_guest_house.guest_house_manager_group') and rec.guest_house_id.auto_boolean == False and rec.state not in ['draft', 'applied']:
                rec.guest_house_manual_access_boolean = True
            elif self.env.user.has_group('kw_guest_house.guest_house_manager_group') and rec.guest_house_id.auto_boolean == False:
                rec.guest_house_manual_access_boolean = True


    @api.constrains('guest_type')
    def guest_type_newjoinee_admin(self):
        if not self.env.user.has_group('kw_guest_house.guest_house_manager_group') and self.guest_type in ['new_joinee', 'admin']:
            raise ValidationError('Only Admin have the authority to apply for this guest type. Kindly contact to the Admin.')
    

    @api.depends('state')
    def _compute_css(self):
        for rec in self:
            if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
                current_date = datetime.now().date()
                check_in_date = rec.check_in_date_time.date() if rec.check_in_date_time else False
                if (rec.state in ['applied', 'approved'] and current_date <= check_in_date) or (rec.state == 'draft' and rec.requested_by_id.id == self.env.user.employee_ids.id):
                    rec.test_css = ''
                else:
                    rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            elif self.env.user.has_group('kw_guest_house.guest_house_user_group') and not self.env.user.has_group('kw_guest_house.guest_house_manager_group') and rec.requested_by_id.id == self.env.user.employee_ids.id:
                if rec.state == 'draft':
                    rec.test_css = ''
                else:
                    rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'

    
    @api.depends('state')
    def compute_check_user_teble_access(self):
        for rec in self:
            rec.show_table_boolean_manager = True if rec.state in ['draft', 'approved', 'applied'] and self.env.user.has_group('kw_guest_house.guest_house_manager_group') else False
            rec.show_table_boolean_user = True if rec.state in ['draft'] and not self.env.user.has_group('kw_guest_house.guest_house_manager_group') else False


    def get_pending_at(self):
        store_manager = self.env['res.users'].sudo().search([]).filtered(lambda user: user.has_group('kw_guest_house.guest_house_manager_group') == True)
        for rec in self:
            employee_ids = []
            if rec.state in ['applied', 'cancellation_requested']:
                employee_ids.extend(store_manager.mapped('employee_ids').ids) if store_manager else False
            rec.pending_at = [(6, 0, employee_ids)] if employee_ids else False


    @api.depends('check_in_date_time', 'check_out_date_time', 'guest_house_id')
    def _compute_room_availability(self):
        for booking in self:
            if booking.check_in_date_time and booking.check_out_date_time and booking.guest_house_id:
                start_date = booking.check_in_date_time.date()
                end_date = booking.check_out_date_time.date()
                num_days = (end_date - start_date).days + 1

                table = '<div style="overflow-x: auto;">'
                table += '<table style="border-collapse: collapse; border: 3px solid #ccc; width: auto; font-family: Arial, Helvetica, sans-serif;">'
                table += '<tr style="background-color: #e9e3e6; border: 1px solid #ccc;">'
                table += '<th style="position: sticky; left: 0; z-index: 1; padding: 10px; text-align: left; border: 1px solid #ccc; background-color: #ffffff;">Room</th>'

                for date in (start_date + timedelta(days=n) for n in range(num_days)):
                    table += f'<th style="padding: 7px; text-align: center; border: 1px solid #ccc;">{date.strftime("%d-%b-%y")}</th>'

                table += '</tr>'

                for room in booking.guest_house_id.room_ids:
                    table += f'<tr>'
                    table += f'<td style="position: sticky; left: 0; z-index: 1; font-weight: bold; padding: 10px; text-align: left; border: 1px solid #ccc; background-color: #ffffff;">{room.room_name} ({room.room_type})</td>'

                    for date in (start_date + timedelta(days=n) for n in range(num_days)):
                        availability = self.is_room_booked(room, date)

                        if availability['status'] == 'Available':
                            cell_color = 'background-color: #5ed792;'
                            info = availability['info']
                        elif availability['status'] == 'Booked':
                            cell_color = 'background-color: #ff6b6b;'
                            info = availability['info']
                        elif availability['status'] == 'Partially':
                            cell_color = 'background-color: #ffa94e;'
                            info = availability['info']
                        table += f'<td style="{cell_color} text-align: center; padding: 10px; color: black; border: 1px solid #ccc;" title={info}>{availability["status"]}</td>'

                    table += '</tr>'

                table += '</table>'
                table += '</div>'

                booking.room_availability = table
            else:
                booking.room_availability = ''
    

    def is_room_booked(self, room, date):
        user_id = self.env['res.users'].sudo().search([('groups_id', 'in', self.env.ref('kw_guest_house.guest_house_manager_group').id)], limit=1).id
        bookings = self.env['kw_guest_house_booking'].sudo(user=user_id).search([
            ('room_id', '=', room.id),
            ('check_in_date_time', '<=', date),
            ('check_out_date_time', '>=', date),
            ('state', '=', 'approved'),
        ])
        booked_count = len(bookings)
        if room.room_type == 'single':
            if booked_count == 1:
                availability = {'status': 'Booked', 'info': 'Booked'}
                return availability
            else:
                availability = {'status': 'Available', 'info': 'Available'}
                return availability
        elif room.room_type == 'double':
            if booked_count == 1:
                if bookings.booking_type == 'partially_book':
                    availability = {'status': 'Partially', 'info': f'"Name: {bookings.requested_by_id.name} \nGender: {bookings.requested_by_id.gender} \nDesignation: {bookings.requested_by_id.job_id.name} \nGuest Type: {"new joinee" if bookings.guest_type == "new_joinee" else bookings.guest_type}"'}
                    return availability
                elif bookings.booking_type == 'fully_book':
                    availability = {'status': 'Booked', 'info': 'Booked'}
                    return availability
            elif booked_count == 2:
                availability = {'status': 'Booked', 'info': 'Booked'}
                return availability
            else:
                availability = {'status': 'Available', 'info': 'Available'}
                return availability
        else:
            availability = {'status': 'Available', 'info': 'Available'}
            return availability


    @api.depends('room_type', 'check_in_date_time', 'check_out_date_time','booking_type')
    def filter_room(self):
        user_id = self.env['res.users'].sudo().search([('groups_id', 'in', self.env.ref('kw_guest_house.guest_house_manager_group').id)], limit=1).id
        booked_rooms = self.env['kw_guest_house_booking'].sudo(user=user_id).search([
                    '&','|', '|',
                    '&', ('check_in_date_time', '<=', self.check_in_date_time), ('check_out_date_time', '>=', self.check_out_date_time),
                    '&', ('check_in_date_time', '>=', self.check_in_date_time), ('check_in_date_time', '<', self.check_out_date_time), 
                    '&', ('check_out_date_time', '>', self.check_in_date_time), ('check_out_date_time', '<=', self.check_out_date_time),
                    ('state', '=', 'approved')
                ])
        self.available_room_ids=False
        if self.room_type and self.check_in_date_time and self.check_out_date_time:
    
            if self.room_type=='double':
                double_room_already_partially_booked = booked_rooms.filtered(lambda rec: rec.room_type == 'double' and rec.booking_type == 'partially_book')
                double_room_already_fully_booked = booked_rooms.filtered(lambda rec: rec.room_type == 'double' and rec.booking_type == 'fully_book')
                room_occurrences = {}
                for rec in double_room_already_partially_booked:
                    room_id = rec.room_id.id
                    room_occurrences[room_id] = room_occurrences.get(room_id, 0) + 1

                arr = [room_id for room_id, count in room_occurrences.items() if count == 2]

                for rec in double_room_already_fully_booked:
                    arr.append(rec.room_id.id)

                if self.booking_type == 'partially_book': 
                    records = self.env['kw_room_master'].search([('guest_house_of_room_id', '=', self.guest_house_id.id), ('room_type', '=', self.room_type), ('id', 'not in', arr)]).ids
                    self.available_room_ids = [(6,0,records)]

                elif self.booking_type == 'fully_book':
                    for rec in double_room_already_partially_booked:
                        arr.append(rec.room_id.id)
                    records = self.env['kw_room_master'].search([('guest_house_of_room_id', '=', self.guest_house_id.id), ('room_type', '=', self.room_type), ('id', 'not in', arr)]).ids
                    self.available_room_ids = [(6,0,records)]

            elif self.room_type=='single':
                arr=[]
                for rec in booked_rooms:
                    arr.append(rec.room_id.id)
                records = self.env['kw_room_master'].search([('guest_house_of_room_id', '=', self.guest_house_id.id), ('room_type', '=', self.room_type), ('id', 'not in', arr)]).ids
                self.available_room_ids = [(6,0,records)]   
             

    @api.model
    def create(self, values):
        check_in_date_time = values.get('check_in_date_time')
        check_out_date_time = values.get('check_out_date_time')

        check_in_date = datetime.strptime(check_in_date_time, '%Y-%m-%d %H:%M:%S').date()
        check_out_date = datetime.strptime(check_out_date_time, '%Y-%m-%d %H:%M:%S').date()

        existing_records = self.search([
            ('requested_by_id', '=', self.env.user.employee_ids.id),
            ('state', 'in', ['applied', 'approved']),
            ('guest_type', 'in', ['self', 'team']),
            '|',
            '&',
                ('check_in_date_time', '<=', check_in_date.strftime('%Y-%m-%d 23:59:59')),
                ('check_out_date_time', '>=', check_in_date.strftime('%Y-%m-%d 00:00:00')),
            '&',
                ('check_in_date_time', '<=', check_out_date.strftime('%Y-%m-%d 23:59:59')),
                ('check_out_date_time', '>=', check_out_date.strftime('%Y-%m-%d 00:00:00'))
        ])

        if existing_records and values.get('guest_type') in ['self', 'team']:
                raise ValidationError("Booking already exists! You can't create duplicate booking.")

        booking = super(KwGuestHouseBooking, self).create(values)
        return booking


    def write(self, values):
        result = super(KwGuestHouseBooking, self).write(values)
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_guest_house.guest_house_manager_group') == True)
        for rec in self:
            if rec.state == 'approved' and self.env.user.has_group('kw_guest_house.guest_house_manager_group') and ('room_type' in values or 'booking_type' in values or 'room_id' in values or 'check_in_date_time' in values or 'check_out_date_time' in values):
                contact_person_mail = []
                if rec.guest_house_id:
                    if rec.guest_house_id.contact_person_1_id and rec.guest_house_id.contact_person_1_id.work_email:
                        contact_person_mail.append(rec.guest_house_id.contact_person_1_id.work_email)
                    if rec.guest_house_id.contact_person_2_id and rec.guest_house_id.contact_person_2_id.work_email:
                        contact_person_mail.append(rec.guest_house_id.contact_person_2_id.work_email)
                    contact_person_mails = ','.join(contact_person_mail) if len(contact_person_mail) > 0 else ''
                if self.guest_type in ['new_joinee', 'admin']:
                    mail_template = self.env.ref('kw_guest_house.guesthouse_room_reallocation_newjoinee_admin_mail')
                    if self.guest_type == 'new_joinee':
                        notify_users = self.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                        notify_users_mails = ','.join(notify_users.mapped('work_email'))
                        mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, email_cc3 = contact_person_mails).send_mail(rec.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = rec.requesting_for_id.work_email, email_cc3 = contact_person_mails).send_mail(rec.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template = self.env.ref('kw_guest_house.guesthouse_room_reallocation_self_team_guest_mail')
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails).send_mail(rec.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
        return result


    def reminder_mail_new_joinee(self):
        check_out_date_threshold = datetime.now() + timedelta(days=5)
        start_date = check_out_date_threshold - timedelta(days=5)
        end_date = check_out_date_threshold

        booking_records = self.env['kw_guest_house_booking'].sudo().search([
            ('guest_type', '=', 'new_joinee'),
            ('state', '=', 'approved'),
            ('check_out_date_time', '>=', start_date.strftime('%Y-%m-%d %H:%M:%S')),
            ('check_out_date_time', '<=', end_date.strftime('%Y-%m-%d %H:%M:%S'))
        ])
        for booking_record in booking_records:
            contact_person_mail = []
            if booking_record.guest_house_id:
                if booking_record.guest_house_id.contact_person_1_id and booking_record.guest_house_id.contact_person_1_id.work_email:
                    contact_person_mail.append(booking_record.guest_house_id.contact_person_1_id.work_email)
                if booking_record.guest_house_id.contact_person_2_id and booking_record.guest_house_id.contact_person_2_id.work_email:
                    contact_person_mail.append(booking_record.guest_house_id.contact_person_2_id.work_email)
                contact_person_mails = ','.join(contact_person_mail) if len(contact_person_mail) > 0 else ''
            emp_data = self.env['res.users'].sudo().search([])
            store_manager = emp_data.filtered(lambda user: user.has_group('kw_guest_house.guest_house_manager_group') == True)
            mail_template = self.env.ref('kw_guest_house.guesthouse_room_check_out_newjoinee_mail')
            notify_users = booking_record.user_to_notify_ids.filtered(lambda employee: employee.work_email)
            notify_users_mails = ','.join(notify_users.mapped('work_email'))
            mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, email_cc3 = contact_person_mails).send_mail(booking_record.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
        

    def button_applied(self):
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_guest_house.guest_house_manager_group') == True)
        action_log_env=self.env['guest_house_booking_action_log']
        if not self.env.user.has_group('kw_guest_house.guest_house_manager_group') and self.guest_house_id.auto_boolean == False:
            self.state='applied'
            action_log_env.create({
            'ref_id':self.id,
            'action_by':self.env.user.name,
            'remark':"Applied",
            'state':'Applied'
            })
            if self.guest_type in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_apply_newjoinee_admin_mail')
                if self.guest_type == 'new_joinee':
                    notify_users = self.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), email_cc = self.requesting_for_id.work_email).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_apply_self_team_guest_mail')
                if self.guest_type == 'guest':
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), email_cc = self.requested_by_id.parent_id.work_email).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email'))).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self.env.user.has_group('kw_guest_house.guest_house_manager_group') or self.guest_house_id.auto_boolean == True:
            if len(self.available_room_ids.ids) == 0 or (len(self.available_room_ids.ids) > 0 and not self.room_id):
                raise ValidationError('Please select room!')
            else:
                self.state='approved'
                action_log_env.create({
                'ref_id':self.id,
                'action_by':self.env.user.name,
                'remark':"Approved",
                'state':'Approved'
                })
                contact_person_mail = []
                if self.guest_house_id:
                    if self.guest_house_id.contact_person_1_id and self.guest_house_id.contact_person_1_id.work_email:
                        contact_person_mail.append(self.guest_house_id.contact_person_1_id.work_email)
                    if self.guest_house_id.contact_person_2_id and self.guest_house_id.contact_person_2_id.work_email:
                        contact_person_mail.append(self.guest_house_id.contact_person_2_id.work_email)
                    contact_person_mails = ','.join(contact_person_mail) if len(contact_person_mail) > 0 else ''
                if self.guest_type in ['new_joinee', 'admin']:
                    mail_template = self.env.ref('kw_guest_house.guesthouse_admin_apply_or_auto_approval__newjoinee_admin_mail')
                    if self.guest_type == 'new_joinee':
                        notify_users = self.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                        notify_users_mails = ','.join(notify_users.mapped('work_email'))
                        mail_template.with_context(email_cc1 = notify_users_mails, email_cc2 = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        mail_template.with_context(email_cc1 = self.requesting_for_id.work_email, email_cc2 = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template = self.env.ref('kw_guest_house.guesthouse_admin_apply_or_auto_approval__self_team_guest_mail')
                    if self.guest_type == 'guest':
                        mail_template.with_context(email_cc1 = ','.join(store_manager.mapped('email')), email_cc2 = self.requested_by_id.parent_id.work_email, email_cc3 = contact_person_mails).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")   
                    else:
                        mail_template.with_context(email_cc1 = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails).send_mail(self.id,force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")

        sequence = self.env['ir.sequence'].next_by_code('kwguesthousebooking.sequence')
        self.booking_id = sequence or '/'


    def button_cancelled(self):
        view_id = self.env.ref('kw_guest_house.guest_house_booking_wizard_form').id
        if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
            return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'guest_house_booking_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id, 'state':'cancelled', 'log_state':'Cancelled', 'guest_type': self.guest_type}
        }

        else:
            return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'guest_house_booking_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id, 'state':'cancellation_requested', 'log_state':'Cancellation Requested', 'guest_type': self.guest_type}
        }
    

    def button_approved(self):
        view_id = self.env.ref('kw_guest_house.guest_house_booking_wizard_form').id
        if self.state=="applied":
            if len(self.available_room_ids.ids) == 0 or (len(self.available_room_ids.ids) > 0 and not self.room_id):
                    raise ValidationError('Please assign room!')
            else:
                return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'guest_house_booking_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'approved', 'log_state':'Approved', 'guest_type': self.guest_type}
            }

        elif self.state=="cancellation_requested":
            return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'guest_house_booking_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id, 'state':'cancelled', 'log_state':'Cancellation Approved', 'guest_type': self.guest_type}
            }

    def button_rejected(self):
        view_id = self.env.ref('kw_guest_house.guest_house_booking_wizard_form').id
        if self.state=="applied":
            return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'guest_house_booking_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id, 'state':'rejected', 'log_state':'Rejected', 'guest_type': self.guest_type}
            }            


    def button_feedback(self):
        view_id = self.env.ref('kw_guest_house.guest_house_feedback_wizard_form').id
        return {
        'name':"Feedback",
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'guest_house_feedback_wizard',
        'view_id': view_id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context':{'current_id': self.id}
        }          


    @api.constrains('check_in_date_time', 'check_out_date_time')
    def _check_in_out_dates(self):
        for booking in self:
            if booking.check_in_date_time and booking.check_out_date_time:
                if booking.check_in_date_time.date() >= fields.datetime.now().date():
                    if booking.check_in_date_time > booking.check_out_date_time:
                        raise ValidationError("Check-in date time cannot be greater than check-out date time.")
                else:
                    raise ValidationError("Check-in date cannot be past.")


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}

        if context.get('apply'):
            if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
                args += ['|', ('requested_by_id.user_id','=',self.env.user.id), '&', ('requested_by_id.user_id','!=',self.env.user.id), ('state', 'not in', ['draft', 'applied']), ]
            else:
                args += [('requested_by_id.user_id','=',self.env.user.id)]
        elif context.get('take_action'):
            if self.env.user.has_group('kw_guest_house.guest_house_manager_group'):
                args += [('state', 'in',['applied', 'approved', 'cancellation_requested'])]
            else:
                args += [('id', 'in',[])]

        return super(KwGuestHouseBooking, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
   

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(('You cannot duplicate a booking.'))
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('You have no access to delete this record.')
        return super(KwGuestHouseBooking, self).unlink()
    


class GuestHouseActionLogModel(models.Model):
    _name = 'guest_house_booking_action_log'

    ref_id = fields.Many2one('kw_guest_house_booking')
    date = fields.Date(string="Date", default = fields.date.today())
    action_by = fields.Char(string="Action Taken By")
    remark = fields.Text(string="Remark")
    state = fields.Char(string="State")



class GuestHouseWizard(models.TransientModel):
    _name = 'guest_house_booking_wizard'
    
    remarks = fields.Text(string="Remark", required=True)
    ref_id = fields.Many2one('kw_guest_house_booking', default= lambda self:self.env.context.get('current_id'))
    

    def proceed_with_remark(self):
        active_id = self.env.context.get('active_id')
        model_data = self.env['kw_guest_house_booking'].search([('id','=',active_id)])
        model_data.write({
                'state': self.env.context.get('state')
            })
        
        self.ref_id.action_log_ids.create({
        'ref_id':self.env.context.get('current_id'),
        'action_by':self.env.user.name,
        'remark':self.remarks,
        'state':self.env.context.get('log_state')
        })
        
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_guest_house.guest_house_manager_group') == True)

        contact_person_mail = []
        if model_data.guest_house_id:
            if model_data.guest_house_id.contact_person_1_id and model_data.guest_house_id.contact_person_1_id.work_email:
                contact_person_mail.append(model_data.guest_house_id.contact_person_1_id.work_email)
            if model_data.guest_house_id.contact_person_2_id and model_data.guest_house_id.contact_person_2_id.work_email:
                contact_person_mail.append(model_data.guest_house_id.contact_person_2_id.work_email)
            contact_person_mails = ','.join(contact_person_mail) if len(contact_person_mail) > 0 else ''
        
        if self.env.context.get('state') == 'approved': #approved by admin
            if self.env.context.get('guest_type') in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_admin_approve_newjoinee_admin_mail')
                if self.self.env.context.get('guest_type') == 'new_joinee':
                    notify_users = model_data.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = model_data.requesting_for_id.work_email, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_admin_approve_self_team_guest_mail')
                mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self.env.context.get('state') == 'rejected': #rejected by admin
            if self.env.context.get('guest_type') in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_admin_reject_newjoinee_admin_mail')
                if self.self.env.context.get('guest_type') == 'new_joinee':
                    notify_users = model_data.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = model_data.requesting_for_id.work_email, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_admin_reject_self_team_guest_mail')
                mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self.env.context.get('state') == 'cancellation_requested':  #cancellation request by user   
            if self.env.context.get('guest_type') in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_cancel_request_newjoinee_admin_to_admin')
                if self.self.env.context.get('guest_type') == 'new_joinee':
                    notify_users = model_data.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), email_cc = model_data.requesting_for_id.work_email, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_cancel_request_self_team_guest_to_admin')
                mail_template.with_context(email_to = ','.join(store_manager.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
      
        elif self.env.context.get('state') == 'cancelled' and self.env.context.get('log_state') == 'Cancellation Approved':    #cancellation approved by ADMIN
            if self.env.context.get('guest_type') in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_cancel_request_approved_newjoinee_admin_mail')
                if self.self.env.context.get('guest_type') == 'new_joinee':
                    notify_users = model_data.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = notify_users_mails, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light") 
                else:
                    mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc = model_data.requesting_for_id.work_email, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light") 
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_cancel_request_approved_self_team_guest_mail')
                mail_template.with_context(email_from = ','.join(store_manager.mapped('email')), email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self.env.context.get('state') == 'cancelled' and self.env.context.get('log_state') == 'Cancelled':  # cancellation request from admin.
            if self.env.context.get('guest_type') in ['new_joinee', 'admin']:
                mail_template = self.env.ref('kw_guest_house.guesthouse_request_cancelled_newjoinee_admin_mail_admin')
                if self.env.context.get('guest_type') == 'new_joinee':
                    notify_users = model_data.user_to_notify_ids.filtered(lambda employee: employee.work_email)
                    notify_users_mails = ','.join(notify_users.mapped('work_email'))
                    mail_template.with_context(email_cc = notify_users_mails, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    mail_template.with_context(email_cc = model_data.requesting_for_id.work_email, email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                mail_template = self.env.ref('kw_guest_house.guesthouse_request_cancelled_self_team_guest_mail_admin')
                mail_template.with_context(email_cc3 = contact_person_mails, remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")



class GuestHouseFeedbackWizard(models.TransientModel):
    _name = 'guest_house_feedback_wizard'
    
    booking_id = fields.Many2one('kw_guest_house_booking', default= lambda self:self.env.context.get('current_id'))
    requested_by_id = fields.Many2one('hr.employee', string = 'Requested By', related='booking_id.requested_by_id', readonly = True)
    guest_house = fields.Char(string = 'Guest House', related='booking_id.guest_house_id.guest_house_name')
    guest_house_address = fields.Text(string = 'Address', related='booking_id.guest_house_address')
    guest_type = fields.Selection(([('self', 'Self'), ('guest', 'Guest'), ('new_joinee', 'New Joinee')]), string = 'Guest Type', related='booking_id.guest_type')
    tour_ref = fields.Char(string = 'Tour reference', related='booking_id.tour_ref_id.code')
    no_of_guests = fields.Integer(string = 'No. of Guests', related='booking_id.no_of_guests')
    requesting_for = fields.Char(string = 'Requesting For', related='booking_id.requesting_for')
    country = fields.Char(string = 'Country', related='booking_id.country_id.name')
    state = fields.Char(string = 'State', related='booking_id.state_id.name')
    check_in_date_time = fields.Datetime(string = 'Check In Time', related='booking_id.check_in_date_time')
    check_out_date_time = fields.Datetime(string = 'Check Out Time', related='booking_id.check_out_date_time')
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string = 'Room Type', related='booking_id.room_type')
    booking_type = fields.Selection([('fully_book', 'Fully Book'), ('partially_book', 'Partially Book')], string = 'Booking Type', related='booking_id.booking_type')
    room_no = fields.Char(string = 'Room No', related='booking_id.room_id.room_name')
    rating = fields.Selection(([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]), string = 'Rating', default='0')
    feedback = fields.Text(string = 'Feedback')


    def proceed_with_feedback(self):
        active_id = self.env.context.get('active_id')
        model_data = self.env['kw_guest_house_booking'].search([('id','=',active_id)])
        model_data.write({
                'given_feedback_boolean': True
            })
        
        self.env['kw_house_master_feedback'].create({
            'booking_id': active_id,
            'rating': self.rating,
            'feedback':self.feedback
            })