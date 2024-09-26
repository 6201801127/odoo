from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_workstation_type_master(models.Model):
    _name = 'kw_workstation_type'
    _description = "A master model to create the Workstation Type"
    _order = "sequence"

    code = fields.Char(string="Code", required=True, size=100)
    name = fields.Char(string="Name", required=True, size=100)
    sequence = fields.Integer(string="Sequence")
    active = fields.Boolean('Active', default=True)
    total = fields.Integer('Total', compute='_get_workstation_count')
    assigned = fields.Integer('Assigned', compute='_get_workstation_count')
    unassigned = fields.Integer('Un-assigned', compute='_get_workstation_count')

    @api.model
    def create(self, vals):
        new_record = super(kw_workstation_type_master, self).create(vals)
        self.env.user.notify_success(message='Workstation Type Created Successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_workstation_type_master, self).write(vals)
        self.env.user.notify_success(message='Workstation Type Updated Successfully.')
        return res

    @api.multi
    def _get_workstation_count(self):
        for record in self:
            record.total = self.env['kw_workstation_master'].search_count([('workstation_type', '=', record.id)])
            record.assigned = self.env['kw_workstation_master'].search_count([('workstation_type', '=', record.id), ('employee_id', '!=', False)])
            record.unassigned = self.env['kw_workstation_master'].search_count([('workstation_type', '=', record.id), ('employee_id', '=', False)])

    @api.constrains('name','code')
    def check_constraints(self):
        for rec in self:
            if self.env['kw_workstation_type'].sudo().search([('name','=',rec.name)])-self:
                raise ValidationError(f'{rec.name} already exists!')
            if self.env['kw_workstation_type'].sudo().search([('code','=',rec.code)])-self:
                raise ValidationError(f'{rec.code} already exists!')

class WorkstationlegendColorCoding(models.Model):
    _name = 'kw_workstation_legend_color_coding'
    _description = "A master model to add the color coding to the work station."
    # _order = "sequence"

    color_code = fields.Char(string="Color", required=True, size=100)
    name = fields.Char(string="Name", required=True, size=100)
    code = fields.Char(string="Code", required=True, size=100)

    @api.model
    def get_legend_color(self, args):
        infra = dict()
        infra_id = self.env['kw_workstation_infrastructure'].search([('id', '=', int(args.get('infra_id')))])
        infra['infrastructure'] = self.env['kw_workstation_infrastructure'].search([])
        infra['infra_code'] = infra_id.code
        infra['employees'] = self.env['hr.employee'].search([])
        if infra_id.code and infra_id.code != 'all':
            workstation_data = self.search([('infrastructure.code', '=', infra_id.code)])
        else:
            workstation_data = self.search([])
        infra['workstations'] = [(station.id, station.name) for station in workstation_data]
        # print(infra)
        return infra

