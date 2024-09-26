from odoo import fields, models, api, tools


class SBU_Requisition(models.Model):
    _name = "sbu.requisition"
    _description = "sbu.requisition"

    @api.model
    def _get_user(self):
        return self.env.user

    @api.model
    def _get_designation(self):
        return self.env.user.employee_ids.job_id.name

    @api.model
    def _get_sbu(self):
        return self.env.user.employee_ids.sbu_master_id

    name = fields.Char(string="Sequence")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="Created By", default=_get_user)
    designation = fields.Char(string="Designation", default=_get_designation)
    opp_wo = fields.Selection(string='Opportunity/WO',
                              selection=[('opportunity', 'Opportunity'), ('work_order', 'Work Order')])
    sbu_id = fields.Many2one('kw_sbu_master', string="SBU", default=_get_sbu)
    sbu_line_ids = fields.One2many('sbu.requisition.line', 'sbu_line_id',
                                   string='Employee Details')

    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")
    note = fields.Text(string="Note")
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ('to_approve', 'To Approve'), ('approved', 'Approved')],
        default="draft")

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('kw_rcm') or _('New')
        res = super(SBU_Requisition, self).create(values)
        return res

    def button_confirm(self):
        self.state = 'confirm'

    def button_to_approve(self):
        self.state = 'to_approve'

    def button_approve(self):
        self.state = 'approved'


class SBU_Requisitionline(models.Model):
    _name = "sbu.requisition.line"
    _description = "sbu.requisition.line"

    @api.model
    def _get_year_list(self):
        years = 30
        return [(str(i), i) for i in range(years + 1)]

    sbu_line_id = fields.Many2one('sbu.requisition', string="Requisition")
    skill = fields.Char(string="Skill")
    designation = fields.Char(string="Designation")
    min_exp_year = fields.Selection(string='Min. Years', selection='_get_year_list', default="0")
    max_exp_year = fields.Selection(string='Max. Years', selection='_get_year_list', default="0")
    impl_man_month = fields.Char(string="Implementation Man Month")
    support_man_month = fields.Char(string="Support Man Month")
    fullfillment_type = fields.Selection(string='Fulfilment Type',
                                         selection=[('recruitment', 'By Recruitment'), ('internal', 'By Internal')])
    intial_demand = fields.Integer(string="Demand QTY")
    selected_resource_qty = fields.Integer(string="Process QTY")
