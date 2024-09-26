from odoo import fields, models, api, tools


class CentralBenchWizard(models.TransientModel):
    _name = "central_bench_wizard"
    _description = "Central Bench Engagement Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CentralBenchWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='sbu_resource_tagging',
        relation='sbu_tagging_employee_relation',
        column1='central_bench_id',
        column2='sbu_tagging_id',
    )

    engagement_plan = fields.Many2one('kw_engagement_master', string="Engagement Plan")
    till_date = fields.Date()
    future_engagement = fields.Selection(string='Future Engagement',
                                         selection=[('project', 'Project'), ('other', 'Other')])
    project_id = fields.Many2one('project.project')
    other_text = fields.Text(string="Other")
    plan_details = fields.Text(string="Plan Details")
    check_bool = fields.Boolean()

    # future_projection =  fields.Char(string="Future Projection")
    # sbu_tagging_id  =fields.Many2one('sbu_resource_tagging',default=lambda self: self._context.get('current_id'))

    @api.onchange('engagement_plan')
    def check_investment_resource(self):
        plan_master = self.env['kw_engagement_master'].search([('code', '=', 'ir')])
        if self.engagement_plan == plan_master:
            self.check_bool = True
        else:
            self.check_bool = False

    @api.onchange('future_engagement')
    def onchange_project(self):
        self.project_id = False
        self.other_text = False

    def engagement_to_project(self):
        for rec in self.employee_ids:
            self.env['central_bench_engagement_log'].sudo().create({
                'emp_id': rec.employee_id.id,
                'engagement_plan_id': self.engagement_plan.id,
                'engagement_plan': self.engagement_plan.name,
                'till_date': self.till_date,
                'future_engagement': self.future_engagement,
                'project_id': self.project_id.id,
                'other_text': self.other_text,
                'plan_details': self.plan_details,

            })


class CentralBenchEngagement(models.Model):
    _name = 'central_bench_engagement_log'
    _description = 'central_bench_engagement_log'

    emp_id = fields.Many2one('hr.employee', string='Employee')
    engagement_plan_id = fields.Many2one('kw_engagement_master')
    engagement_plan = fields.Char("Engagement Plan")
    till_date = fields.Date()
    future_engagement = fields.Selection(string='Future Engagement',
                                         selection=[('project', 'Project'), ('other', 'Other')], default='project')
    project_id = fields.Many2one('project.project', string='Project Name')
    other_text = fields.Text(string="Other")
    future_projection = fields.Char(string="Future Projection")
    plan_details = fields.Text(string="Plan Details")
