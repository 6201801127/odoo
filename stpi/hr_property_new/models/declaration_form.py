from odoo import api, fields, models, tools, _
from datetime import datetime, date
from odoo.exceptions import ValidationError,UserError

class AnnualPropertyDeclaration(models.Model):
    _name= 'annual.property.declaration'
    _description = 'Annual Property Declaration'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    year_id = fields.Many2one('date.range',string="For The Year")
    employee_id = fields.Many2one('hr.employee', string="Name", default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job',string="Designation")

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def get_designation(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.employee_no = rec.employee_id.identify_id
            emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if emp_contract:
                for contract in emp_contract:
                    rec.scale_pay = contract.wage
                    rec.pay_level_id = contract.pay_level_id.id
                    
    property_sequence = fields.Char('Property Declaration Number',track_visibility='always')
    property_address = fields.Text('Name of the Distt. Subdivision, Tehsil & Vill. In which the property is situated')
    housing_building = fields.Text('Housing And Building')
    other_lands = fields.Text('Other Lands')
    present_value = fields.Float('Present Value')
    state_relation = fields.Text('If not in own name, state in whose name held of his/ her relationship to Govt. Servant')
    how_acquired = fields.Text('How acquired whether by purchase, lease**, mortgage, inheritance, gift or otherwise with date of acquisition and name with detail of person from whom acquired')
    annual_income = fields.Float('Annual Income from the property')

    @api.model
    def create(self, vals):
        res =super(AnnualPropertyDeclaration, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('hr.property.new')
        sequence = 'PD' + seq
        res.property_sequence = sequence
        return res

    @api.multi
    @api.depends('property_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.property_sequence:
                name = record.property_sequence
            else:
                name = 'PD'
            res.append((record.id, name))
        return res