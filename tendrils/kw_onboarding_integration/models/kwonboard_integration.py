from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwonboard_new_joinee_in(models.Model):
    _inherit = 'kwonboard_new_joinee'

    atten_mode_ids = fields.Many2many('kw_attendance_mode_master', 'new_joinee_attendance_rel',
                                      string="Attendance Mode")
    work_station_id = fields.Many2one('kw_workstation_master', string="Workstation")
    infra_id = fields.Many2one('kw_workstation_infrastructure', string="Infrastructure")

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

    @api.onchange('location')
    def _onchange_location(self):
        self.infra_id = False
        self.work_station_id = False
        self.client_location = False

    # @api.constrains('work_station_id')
    # def check_workstation(self):
    # 	for rec in self:
    # 		if rec.work_station_id and rec.state=='draft':
    # 			new_joinee_rec = self.env['kwonboard_new_joinee'].sudo().search([('work_station_id','=', rec.work_station_id.id)])-self
    # 			if new_joinee_rec:
    # 				raise ValidationError(f"This Workstation is already assigned to {new_joinee_rec.fullname}, choose another one")

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

# @api.constrains('workstation_id')
# def check_workstation(self):
# 	for rec in self:
# 		if rec.workstation_id:
# 			employee_rec = self.env['hr.employee'].sudo().search([('workstation_id','=', rec.workstation_id.id)])-self
# 			if employee_rec:
# 				raise ValidationError(f"This Workstation is already assigned to {employee_rec.name}, choose another one")
