from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DeviceMaster(models.Model):
    _name = 'kw_device_master'
    _description = 'Device Master'
    _rec_name = 'device_id'

    device_id = fields.Integer("Device Id", required=True)
    sync_status = fields.Boolean("Synchronization status", )
    type = fields.Selection(string="Used For", selection=[('attendance','Attendance'),('baverage', 'Baverage'), ('meal', 'Meal'),('none','None')],default="attendance")

    location = fields.Selection(string="Location", selection=[('ho', 'HO'), ('branch', 'Branch')], requried=True)
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit',string="Infra Unit Location")

    _sql_constraints = [
        ('device_id_unique', 'unique (device_id,location)', 'Device Id already exists.'),
    ]

    @api.constrains('device_id', 'location')
    def device_master_duplicate_validation(self):
        for record in self:
            if record.location == False:
                raise ValidationError("Please Select Location.")
