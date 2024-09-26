# -*- coding: utf-8 -*-
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KwManageGuestHouse(models.Model):
    _name = 'kw_guest_house_master'
    _rec_name = 'guest_house_name'

    guest_house_name = fields.Char(string = 'Guest House', autocomplete="off")
    address = fields.Text(string = 'Address', autocomplete="off")
    gps_location = fields.Char(string = 'GPS Location')
    country_id = fields.Many2one('res.country', string = 'Country', autocomplete="off")
    state_id = fields.Many2one('res.country.state', string = 'State', domain="[('country_id', '=', country_id)]", autocomplete="off")
    city_id = fields.Many2one('res.city', string = 'City', domain="[('state_id', '=', state_id)]", autocomplete="off")
    contact_person_1_id = fields.Many2one('hr.employee', string = 'Contact Person 1', autocomplete="off")
    contact_person_2_id = fields.Many2one('hr.employee', string = 'Contact Person 2', autocomplete="off")
    contact_no_1 = fields.Char(string = 'Contact No:1', autocomplete="off")
    contact_no_2 = fields.Char(string = 'Contact No:2', autocomplete="off")
    care_taker = fields.Char(string = 'Care Taker', autocomplete="off")
    care_taker_no = fields.Char(string = 'Care Taker No', autocomplete="off")
    no_of_single_room = fields.Integer(string = 'No of Single Room', compute = 'compute_no_of_rooms', store = True)
    no_of_double_room = fields.Integer(string = 'No of Double Room', compute = 'compute_no_of_rooms', store = True)
    facilities_ids = fields.Many2many('kw_facilities_master', 'guest_house_facility_rel', 'guest_house_id', 'facility_id', string = 'Facilities')
    room_ids = fields.One2many('kw_room_master', 'guest_house_of_room_id', string = 'Rooms')
    photo_ids = fields.One2many('kw_guest_house_photo_master', 'photo_guest_house_id', string='Add Photos')
    available_single_room = fields.Integer(string='Available Single Room',compute='update_available_rooms_based_on_bookings')
    available_double_room = fields.Integer(string='Available Double Room',compute='update_available_rooms_based_on_bookings')
    auto_boolean = fields.Boolean(string='Auto Approval Mode', default = False)
    active_boolean = fields.Boolean(string='Active', default=True)

    @api.onchange('contact_person_1_id', 'contact_person_2_id')
    def _on_contact_person_change(self):
        if self.contact_person_1_id:
            self.contact_no_1 = self.contact_person_1_id.mobile_phone or ''
        if self.contact_person_2_id:
            self.contact_no_2 = self.contact_person_2_id.mobile_phone or ''

    @api.constrains('care_taker_no')
    def _check_care_taker_no(self):
        for record in self:
            if record.care_taker_no:
                if len(record.care_taker_no) != 10:
                    raise Warning("Care Taker Number should be 10 digits.")

                if not record.care_taker_no.isdigit():
                    raise Warning("Care Taker Number should only contain numeric digits.")


    #Compute function to calculate number of rooms for each type.
    @api.depends('room_ids')
    def compute_no_of_rooms(self):
        for room in self:
            room.no_of_single_room = len(room.room_ids.filtered(lambda r: r.room_type == 'single'))
            room.no_of_double_room = len(room.room_ids.filtered(lambda r: r.room_type == 'double'))
    
    # Restriction for duplicate guesthouse.
    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(('You cannot duplicate a Guest House.'))
    
    #Upload images function.
    def get_upload_images(self):
        for rec in self:
            view_id = self.env.ref('kw_guest_house.kw_upload_many_guesthouse_photos_form').id
            return {
                'name': 'Upload Images',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_upload_guest_house_image_wizard',
                'target': 'new',
                'context':{
                'default_guesthouse_id': rec.id
                }
            }
    
    #method for numbers of available rooms
    @api.depends('guest_house_name')
    def update_available_rooms_based_on_bookings(self):
        for rec in self:
            if rec.id:
                if rec.guest_house_name:
                    booking_query = f"""
                       		SELECT 
                                room_type,
                                COUNT(*) AS room_count
                            FROM (
                                SELECT 
                                    kw_room_master.room_type,
                                    kw_room_master.room_name
                                FROM 
                                    kw_guest_house_booking
                                INNER JOIN 
                                    kw_room_master ON kw_guest_house_booking.room_id = kw_room_master.id
                                WHERE 
                                    kw_room_master.guest_house_of_room_id = {rec.id}
                                    AND kw_guest_house_booking.state = 'approved'
                                    AND DATE(kw_guest_house_booking.check_in_date_time) <= current_date
                                    AND DATE(kw_guest_house_booking.check_out_date_time) >= current_date
                                GROUP BY
                                    kw_room_master.room_type, kw_room_master.room_name
                            ) AS booked_rooms
                            GROUP BY
                                booked_rooms.room_type;
                    """
                    self.env.cr.execute(booking_query)
                    results = self.env.cr.fetchall()
                    if len(results)==1:
                        room_type = results[0][0]
                        room_count = results[0][1]

                        if room_type == 'single':
                            rec.available_single_room = rec.no_of_single_room - room_count if room_count else rec.no_of_single_room
                            rec.available_double_room = rec.no_of_double_room - 0
                        elif room_type == 'double':
                            rec.available_double_room = rec.no_of_double_room - room_count if room_count else rec.no_of_double_room
                            rec.available_single_room = rec.no_of_single_room - 0
                    elif len(results)==2:
                        for result in results:
                            room_type = result[0]
                            room_count = result[1]

                            if room_type == 'single':
                                rec.available_single_room = rec.no_of_single_room - room_count if room_count else rec.no_of_single_room
                            elif room_type == 'double':
                                rec.available_double_room = rec.no_of_double_room - room_count if room_count else rec.no_of_double_room
                    elif len(results)==0:
                        rec.available_single_room = rec.no_of_single_room
                        rec.available_double_room = rec.no_of_double_room




class KwManageFacilities(models.Model):
    _name = 'kw_facilities_master'
    _rec_name = 'facility_name'

    facility_name = fields.Char(string = 'Facility',required=True, index=True)
    code = fields.Text(string = 'Code',required=True)
    active = fields.Boolean(string="Active", default=True)


    @api.constrains('facility_name')
    def _check_unique_facility_name(self):
        for record in self:
            duplicate_records = self.search([('facility_name', '=', record.facility_name), ('id', '!=', record.id)])
            if duplicate_records:
                raise ValidationError(f'The "{record.facility_name}" already exists!')



class KwRoomsMaster(models.Model):
    _name = 'kw_room_master'
    _rec_name = 'room_name'
    
    _sql_constraints = [
        ('room_uniq','unique(guest_house_of_room_id,room_name)','Room with same name already exists')
    ]

    guest_house_of_room_id = fields.Many2one('kw_guest_house_master', string = 'Guest House Name')
    room_name = fields.Char(string = 'Room No', required=True)
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string = 'Room Type', required=True)
    
    
class KwGuestHousePhotoMaster(models.Model):
    _name = 'kw_guest_house_photo_master'

    photo_guest_house_id = fields.Many2one('kw_guest_house_master', string = 'Guest House Name')
    photo = fields.Binary(string = 'Photo', attachment = 'True')
    
    def remove_upload_images(self):
        return self.unlink()
    

class KwUploadGuestHouseImageWizard(models.TransientModel):
    _name = 'kw_upload_guest_house_image_wizard'
    _description = 'Upload Multiple Images'
    
    photos_ids = fields.Many2many('ir.attachment', string='Images')
    guest_house_id = fields.Many2one('kw_guest_house_master')
    
    @api.constrains('photos_ids')
    def _check_image_size(self):
        for image in self.photos_ids:
            if image.file_size > 1024 * 1024:
                raise ValidationError("Image '{}' exceeds the maximum allowed size of 1 MB.".format(image.name))
    
    def upload_image(self):
        for rec in self.photos_ids:
            self.guest_house_id = self.env.context.get('default_guesthouse_id')
            if self.guest_house_id:
                self.guest_house_id.photo_ids.create({
                    'photo_guest_house_id': self.guest_house_id.id,
                    'photo':rec.datas,
                })