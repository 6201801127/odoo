from odoo import models,fields,api
from odoo.exceptions import ValidationError

class RosterPointMaster(models.Model):
    _name = "roster.point.master"
    _description = "Roster Point Master"

    name = fields.Integer(string='Number',required=True)
    job_id = fields.Many2one("hr.job",'Job Position',required=True)
    sanctionedpost = fields.Integer(string="Sanctioned Posts",compute="compute_sanctioned_post")

    state_id = fields.Many2one("res.country.state","State",required=True)
    branch_id = fields.Many2one("res.branch","Directorate",required=True,domain="['|',('parent_branch_id.code','=','HQ'),('code','=','HQ')]")
    category_id = fields.Many2one("employee.category","Category")

    is_group_a = fields.Boolean("Is Group A ?",compute="compute_if_group_a")

    @api.depends('job_id')
    @api.multi
    def compute_if_group_a(self):
        for point in self:
            group_id = point.mapped('job_id.pay_level_id.group_id')
            if group_id and group_id.code in ['a','A']:
                point.is_group_a = True
            else:
                point.is_group_a = False

    @api.multi
    @api.depends('job_id')
    def compute_sanctioned_post(self):
        for point in self:
            point.sanctionedpost = point.job_id.sanctionedpost

    @api.model
    def create(self, vals):
        if self.env.user.has_group("hr_recruitment.group_hr_recruitment_manager") and 'HQ' in self.env.user.branch_ids.mapped('code'):
            return super(RosterPointMaster, self).create(vals)
        else:
            raise ValidationError("Only Recruitment Managers From Head Quarter Can Create Roster Point Master(s).")

    @api.constrains('job_id')
    def validate_sanctioned_posts(self):
        for point in self:
            # if point.job_id.sanctionedpost < point.name:
            #     raise ValidationError("Number can't be greater than sanctioned post in job position.")
            if len(self.search([('job_id','=',point.job_id.id)])) > point.job_id.sanctionedpost:
                raise ValidationError("No. of roaster point can't be greater than sanctioned post in job position.")

    @api.multi
    def name_get(self):
        name_data = []
        for point in self:
            id = point.id
            name = str(point.name)
            if point.job_id:
                name += f' ({point.job_id.name})'
            if point.category_id:
                name += f' ({point.category_id.name})'
            if point.state_id:
                name += f' ({point.state_id.name})'
            if point.branch_id:
                name += f' ({point.branch_id.name})'

            name_data.append((id,name))
        return name_data
