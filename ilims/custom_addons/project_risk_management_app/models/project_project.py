from odoo import models, fields, api,_
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'project project'
    _order = "priority desc"

    # compute for risk incident smart button
    def _risk_incident_count(self):
        task_obj = self.env['project.task']
        for record in self:
            record.risk_incident_count = task_obj.search_count(
                [('project_id', 'in', record._ids), ('risk_incident', '=', True)])

    def _compute_reviewer_boolean(self):
        for rec in self:
            if rec.reviewer_id:
                print("rec.reviewer_id.id...", rec.reviewer_id.id, self.env.user.id)
                if rec.reviewer_id.id == self.env.user.id:
                    rec.reviewer_boolean = True
                else:
                    rec.reviewer_boolean = False

    def _compute_approver_boolean(self):
        for rec in self:
            if rec.approver_id:
                print("rec.reviewer_id.id...",rec.reviewer_id.id,self.env.user.id)
                if rec.approver_id.id == self.env.user.id:
                    rec.approver_boolean = True
                else:
                    rec.approver_boolean = False



    risk_lines_ids = fields.One2many('project.risk.line', 'project_id', string=" Risk Register",
                                     track_visibility='always')
    risk_incident_count = fields.Integer(compute='_risk_incident_count', track_visibility='always')
    risk_incident = fields.Boolean('Task Incident?', readonly=1, track_visibility='always')


    priority = fields.Selection([('0', 'Low'),
                                ('1', 'Normal'),
                                ('2', 'High'),
                                ('3', 'Important')], default='1', index=True, string='Priority')

    wbs = fields.Text(string='WBS')
    project_id = fields.Char(string='Project Id', copy=False, readonly=True, required=True, default=lambda self: _('New'))
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Char(string='Address')
    analytics_account = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account')
    project_duration = fields.Integer(string='Project Duration')
    project_category = fields.Many2one(comodel_name='project.category', string='Project Category')
    project_sub_category = fields.Many2one(comodel_name='project.category', string='Project Sub Category')
    feasibility_study = fields.Text(str='Feasibility Study')
    partner_id = fields.Many2one('res.partner', 'Customer')
    reviewer_id = fields.Many2one(comodel_name='res.users', string='Reviewer')
    approver_id = fields.Many2one(comodel_name='res.users', string='Approver')
    reviewer_remarks = fields.Text(string='Reviewer Remarks')
    approver_remarks= fields.Text(string='Approver Rejection Remarks')
    state = fields.Selection([('draft', 'Draft'), ('waiting for review', 'Waiting For Review'), ('waiting for approve', 'Waiting For Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                             string="Status",
                             default="draft")
    reviewer_boolean = fields.Boolean(string='Reviewer boolean', compute="_compute_reviewer_boolean")
    approver_boolean = fields.Boolean(string='Approver boolean', compute="_compute_approver_boolean")



    @api.onchange('start_date', 'end_date')
    def onchange_duration(self):
        for rec in self:
            print('re11211111111111111111111111c', rec)
            if rec.end_date and rec.start_date:
                d1 = fields.Datetime.from_string(rec.start_date)
                d2 = fields.Datetime.from_string(rec.end_date)
                interval = relativedelta(d2, d1)
                print("interval", interval)
                rec.project_duration = (interval.days + 1)

    @api.model
    def create(self, values):
        if values.get("project_id", 'New') == 'New':
            values['project_id'] = self.env['ir.sequence'].next_by_code('project.category.sequence') or _('New')
        result = super(ProjectProject, self).create(values)
        print("result...", result)
        return result
    #added by ajay
    def submit_for_review(self):
        self.state = 'waiting for review'

    def cancel(self):
        return True
    def review(self):
        self.state = 'waiting for approve'

    def approve(self):
        self.state = 'approved'


    # smart button in project
    def open_rist_incident_project(self):
        tree_view_id = self.env.ref('project_risk_management_app.view_risk_incident_tree').id
        form_view_id = self.env.ref('project_risk_management_app.view_risk_incident_menu').id
        kanban_view_id = self.env.ref('project.view_task_kanban').id
        pivot_view_id = self.env.ref('project.view_project_task_pivot').id
        return {
            'name': _('Risk Incident'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'project.task',
            'domain': [('project_id', 'in', self._ids), ('risk_incident', '=', True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_is_from_project': True, 'default_risk_incident': True}
        }

    def _compute_task_count(self):
        task_data = self.env['project.task'].read_group(
            [('project_id', 'in', self.ids), '|', '&', ('stage_id.is_closed', '=', False),
             ('stage_id.fold', '=', False), ('stage_id', '=', False), ('is_issue', '=', False),
             ('risk_incident', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)


# added by ajay
class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'project task'

    physical_milestone = fields.Float(string="Physical Milestone")
    payment_milestone = fields.Float(string="Payment Milestone")
    project_completion = fields.Float(string="Project Completion Percentage ")

    # @api.depends('stage_id')
    # def _compute_physical_milestone(self):
    #     for rec in self:
    #         if rec.stage_id == 'initial stage':
    #             rec.physical_milestone = 25
    #         elif rec.stage_id == 'planing':
    #             rec.physical_milestone = 50
    #         elif rec.stage_id == 'wip':
    #             rec.physical_milestone = 75
    #         elif rec.stage_id == 'done':
    #             rec.physical_milestone = 100
    #






class ProjectCategory(models.Model):
    _name = 'project.category'
    _rec_name = 'completes_name'
    _description = 'Project Category'

    name = fields.Char()
    parent_id = fields.Many2one('project.category', 'Parent Category')
    fixed = fields.Boolean('Fixed')
    completes_name = fields.Char(
        'Complete Name', compute='_compute_completes_name',
        store=True)

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        for rec in self:
            print('recrecrec', rec)
            if rec.parent_id:
                rec.fixed = True
            else:
                rec.fixed = False

    @api.depends('name', 'parent_id.completes_name')
    def _compute_completes_name(self):
        for category in self:
            if category.parent_id:
                category.completes_name = '%s / %s' % (category.parent_id.completes_name, category.name)
            else:
                category.completes_name = category.name

