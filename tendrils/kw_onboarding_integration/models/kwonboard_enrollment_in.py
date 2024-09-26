# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwonboard_enrollment_in(models.Model):
    _inherit = 'kwonboard_enrollment'

    atten_mode_ids = fields.Many2many('kw_attendance_mode_master', 'kwonboard_enrollment_attendance_rel',
                                      string="Attendance Mode")
    work_station_id = fields.Many2one('kw_workstation_master', string="Workstation")
    infra_id = fields.Many2one('kw_workstation_infrastructure', string="Infrastructure")
    infra_unit_loc_id = fields.Many2one('kw_res_branch_unit',string='Infra Unit Location')

    @api.onchange('worklocation_id')
    def onchange_worklocation(self):
        self.infra_id = False
        domain = {}
        for rec in self:
            domain['infra_id'] = [('address_id', '=', rec.worklocation_id.id)]
            return {'domain': domain}

    @api.onchange('infra_id')
    def onchange_infra(self):
        self.work_station_id = False
        domain = {}
        for rec in self:
            domain['work_station_id'] = [('infrastructure', '=', rec.infra_id.id)]
            return {'domain': domain}

    @api.onchange('tmp_location')
    def _onchange_location(self):
        self.infra_id = False
        self.work_station_id = False
        self.tmp_client_location = False

    @api.onchange('enable_attendance')
    def onchange_enable_attendance(self):
        if self.enable_attendance == 'no':
            self.atten_mode_ids = False

    @api.constrains('atten_mode_ids')
    def check_attendance_mode(self):
        attendance_rec = self.atten_mode_ids.mapped('alias')
        bothLis = ['portal', 'bio_metric']
        if len(attendance_rec) == 2:
            if all(item in attendance_rec for item in bothLis):
                pass
            else:
                raise ValidationError('You can only select 2 modes i.e Portal and Biometric')
        if len(attendance_rec) > 2:
            raise ValidationError('You can not select 3 attendance modes')

    @api.onchange('infra_unit_loc_id')
    def onchange_infra_loc(self):
        self.infra_id = False
        domain = {}
        for rec in self:
            domain['infra_id'] = [('branch_unit_id', '=', rec.infra_unit_loc_id.id)]
            return {'domain': domain}