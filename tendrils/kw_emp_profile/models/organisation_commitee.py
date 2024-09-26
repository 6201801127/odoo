from odoo import models, fields, api
from odoo.exceptions import ValidationError
from itertools import chain


class organisation_committee(models.Model):
    _name = "organisation_committee"
    _description = "organisation committee"
    _rec_name = "name"

    name = fields.Char(string="Committee Name",required=True)
    members = fields.One2many('committee_member', 'committee_id_alt', string="Committee Members")

    chairperson = fields.One2many('committee_member', compute="_compute_committee_name", string="Chairperson")
    mom_controller = fields.One2many('committee_member', compute="_compute_committee_name", string="MOM Controller")
    coordinator = fields.One2many('committee_member', compute="_compute_committee_name", string="Coordinator")
    member = fields.One2many('committee_member', compute="_compute_committee_name", string="Members")

    @api.constrains('members')
    def check_members(self):
        for record in self:
            if not record.members:
                raise ValidationError("A committee must have at least one member.")

    @api.constrains('name')
    def check_name(self):
        if len(self.members) == 0:
            raise ValidationError("A committee must have at least one member.")

    @api.depends('members')
    def _compute_committee_name(self):
        for rec in self:
            rec.chairperson = rec.members.filtered(lambda x: x.is_chairperson is True)
            rec.mom_controller = rec.members.filtered(lambda x: x.is_mom_controller is True)
            rec.coordinator = rec.members.filtered(lambda x: x.is_coordinator is True)
            rec.member = rec.members.filtered(lambda x: x.is_member is True)


class CommitteeMember(models.Model):
    _name = "committee_member"
    _description = "Committee Member"
    _rec_name = "employee_id"

    committee_id_alt = fields.Many2one('organisation_committee', string="Committee")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    is_chairperson = fields.Boolean(string="Chairperson")
    is_mom_controller = fields.Boolean(string="MOM Controller")
    is_coordinator = fields.Boolean(string="Coordinator")
    is_member = fields.Boolean(string="Member", default=True)

    name = fields.Char(related='employee_id.name', string='Name', readonly=True)
    emp_code = fields.Char(related='employee_id.emp_code', string='Employee Code', readonly=True)
    job_id = fields.Many2one(related='employee_id.job_id', string='Job Position', readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', readonly=True)
    job_branch_id = fields.Many2one(related='employee_id.job_branch_id', string='Job Branch', readonly=True)


class committee_wizard(models.TransientModel):
    _name = "committee_wizard"
    _description = "committee wizard"

    employee_ids = fields.Many2many('hr.employee', 'committee_wizard_employee_rel', string="Employees", required="True")
    committee_ids = fields.Many2many('organisation_committee', 'wizard_committee_rel', string="Committees",
                                     required="True")
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)

    @api.depends()
    def _compute_css(self):
        for rec in self:
            rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'

    @api.model
    def create(self, vals):
        employee_data = vals.get('employee_ids', [])
        committee_data = vals.get('committee_ids', [])
        res = super(committee_wizard, self).create(vals)
        
        employee_ids = [rec[2] for rec in employee_data][0]
        committee_ids = [rec[2] for rec in committee_data][0]
        if committee_ids:
            committee_records = self.env['organisation_committee'].browse(committee_ids)
            if committee_records.exists():
                for committee_record in committee_records:
                    if employee_ids:
                        existing_employee_ids = committee_record.members.mapped('employee_id').ids
                        new_employee_ids = list(set(employee_ids) - set(existing_employee_ids))
                        committee_record.write({'members': [[0, 0, {'employee_id': new_employee_id}] for new_employee_id in new_employee_ids]})
        return res

    @api.multi
    def action_cancel(self):
        """Close the wizard."""
        return {'type': 'ir.actions.act_window_close'}
