# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_meeting_room_master(models.Model):
    _name = 'kw_meeting_room_master'
    _description = 'Meeting Room Master'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Meeting Room Name', required=True,)
    capacity = fields.Integer(string='Room Capacity', )
    max_allocation = fields.Integer(string='Max Allocation', )
    floor_name = fields.Char(string=' Floor No.', )
    extn_no = fields.Char(string=' Extn No.', )
    block_name = fields.Char(string='Block Name', )
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id, required=True)
    location_id = fields.Many2one('kw_res_branch', string="Office Location", domain="[('company_id', '=', company_id)]",
                                  required=False)
    amenity_ids = fields.Many2many(string='Amenities', comodel_name='kw_meeting_amenity_master')
    visibility_status = fields.Boolean(string='Hide to Book Meeting?', default=True)
    restricted_access = fields.Boolean(string='Restricted Access', default=False)
    active = fields.Boolean('Active', default=True)
    department_ids = fields.Many2many('hr.department', 'meeting_room_department_rel', 'department_id', 'room_id',
                                      string="Department", default=False)
    # meeting_ids = fields.One2many(
    #     string='Meetings',
    #     comodel_name='kw_meeting_events',
    #     inverse_name='meeting_room_id',
    # )

    _sql_constraints = [
        ('name_unique', 'unique (location_id,name)', 'The meeting room name must be unique per location !')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            floor_name = '  (' + str(record.floor_name) + ')' if record.floor_name else ''
            record_name = record.name + floor_name
            result.append((record.id, record_name))
        return result

    @api.constrains('capacity', 'max_allocation')
    def room_max_compare(self):
        if self.max_allocation < self.capacity:
            raise ValidationError("Max Allocation should be greater than Room Capacity.")

    def toggle_access(self):
        if self.restricted_access == True:
            self.write({'restricted_access': False})
        else:
            self.write({'restricted_access': True})

    def toggle_active(self):
        if self.active == True:
            self.write({'active': False})
        else:
            self.write({'active': True})

    @api.model
    def create(self, vals):
        new_record = super(kw_meeting_room_master, self).create(vals)
        self.env.user.notify_success(message='Meeting room created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_meeting_room_master, self).write(vals)
        self.env.user.notify_success(message='Meeting room updated successfully.')
        return res
