from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning

class EmplyoyeeTrip(models.Model):
    _name='employee.trip'
    _description = "Employee Trip"
    _rec_name = 'name'

    name=fields.Char()
    state=fields.Selection([('not_start','Not Start'),
                            ('in_progress','In Prgress'),
                            ('completed','Completed'),
                            ('cancel','Cancel')],default='not_start')

    fleet_id =fields.Many2one('fleet.vehicle',string='Vehical Id')
    driver_id =fields.Many2one('res.partner',string='Driver')
    travel_distance= fields.Float(string=' Travel Distance')
    uom_id = fields.Many2one('uom.uom',string="Unit Of Measure",ondelete='set null')
    last_odo_meter_reding = fields.Float('Last ODO Meter Reding')
    odo_end =fields.Float('ODO End')
    request_date= fields.Date(string='Request Date')

