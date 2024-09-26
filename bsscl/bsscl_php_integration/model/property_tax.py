from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError,ValidationError
import re

class PropertyDetails(models.Model):
	_name = 'property.details'
	_inherit=['mail.thread','mail.activity.mixin']

	partner_id = fields.Many2one('res.partner',"Partner")
	old_holding_no = fields.Char("Old Holding No")
	new_holding_no = fields.Char("New Holding No")
	old_pid = fields.Char("Old PID")
	new_pid = fields.Char("New PID")
	ward = fields.Char("Ward")
	area = fields.Char("Area")
	builtup_area = fields.Char("Builtup Area")
	road = fields.Char("Road")
	road_type = fields.Char("Road Type")
	userid = fields.Integer("User ID")
	remark = fields.Char("Remarks")
	floor_ids = fields.One2many('property.floor.details', 'property_id', "Floor Details")
	active = fields.Boolean("Active")
	data_type = fields.Selection([('property', 'Property Tax'), ('other', 'Other')], string="Data Type")

class PropertyFloorDetails(models.Model):
	_name= 'property.floor.details'

	property_id = fields.Many2one('property.details', "Property")
	floor_no = fields.Char("Floor No")
	acquisition_year = fields.Char("Acquisition year")
	type_of_use = fields.Char("Type of use")
	construction_type = fields.Char("Construcation Type")
	rateble_area = fields.Char("Rateble area")
	use_factor = fields.Char("Use Factor")
	occupancy_factor = fields.Char("Occupancy Factor")