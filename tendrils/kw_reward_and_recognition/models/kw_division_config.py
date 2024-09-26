from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class DivisionConfig(models.Model):
    _name = "kw_division_config"
    _description = "Division Configuration"
    _rec_name = 'name'


    name = fields.Char(string="Division Name")
    department_ids = fields.Many2many('hr.department', 'department_kw_division_config_rel', 'dept_id', 'rel_dept_id',
                                      string="Department")
    reviewer_id = fields.Many2one('hr.employee', string="Reviewer",track_visibility='onchange')
    nominator_ids = fields.Many2many('hr.employee','nominator_kw_employee_rel', 'emp_id', 'rel_emp_id' ,string="Nominator",track_visibility='onchange')
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU",track_visibility='onchange')
    type = fields.Selection([('sbu', 'SBU'),('non_sbu', 'Non-SBU')])
    # award_count = fields.Integer(string="Award Count")

    @api.constrains('name')
    def _check_name(self):
        div_data = self.env['kw_division_config'].sudo().search([]) - self
        for rec in self:
            if rec.name in div_data.mapped('name'):
                raise ValidationError("Name already exist.")

    @api.model
    def create(self, vals):
        if 'reviewer_id' in vals and vals['reviewer_id']:
            rnr_review_group = self.env.ref('kw_reward_and_recognition.rnr_reviewer', False)
            reviewer = self.env['hr.employee'].sudo().browse(vals['reviewer_id'])
            if reviewer:
                rnr_review_group.sudo().write({'users': [(4, reviewer.user_id.id)]})
                self.env.user.notify_success("Users added to the Reviewer group")
        
        if 'nominator_ids' in vals and vals['nominator_ids']:
            rnr_nominator_group = self.env.ref('kw_reward_and_recognition.rnr_sbu', False)
            reviewer_users = self.env['hr.employee'].sudo().browse(vals['nominator_ids'][0][2])
            for rec in reviewer_users:
                rnr_nominator_group.sudo().write({'users': [(4, rec.user_id.id)]})
                self.env.user.notify_success("Users added to the Reviewer group")

        
        res = super(DivisionConfig, self).create(vals)
        self.env.user.notify_success(message='Division has been created successfully.')
        return res

    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee']
        if 'reviewer_id' in vals and vals['reviewer_id']:
            rnr_review_group = self.env.ref('kw_reward_and_recognition.rnr_reviewer', False)
            reviewer = employee.sudo().browse(vals['reviewer_id'])
            remove_users_access = self.reviewer_id if reviewer != self.reviewer_id else False
            multi_reviewer_ids = self.env['kw_division_config'].sudo().search([('reviewer_id','=',self.reviewer_id.id)])
            if reviewer:
                rnr_review_group.sudo().write({'users': [(4, reviewer.user_id.id)]})
                self.env.user.notify_success("Users added to the Reviewer group")
            if remove_users_access and len(multi_reviewer_ids) == 1:
                rnr_review_group.sudo().write({'users': [(3, remove_users_access.user_id.id)]})
        if 'nominator_ids' in vals and vals['nominator_ids']:
            rnr_nominator_group = self.env.ref('kw_reward_and_recognition.rnr_sbu', False)
            reviewer_users = employee.sudo().browse(vals['nominator_ids'][0][2])
            remove_users_access = self.nominator_ids - reviewer_users
            for rec in reviewer_users:
                rnr_nominator_group.sudo().write({'users': [(4, rec.user_id.id)]})
                self.env.user.notify_success("Users added to the Reviewer group")
            if len(remove_users_access)>0:
                for rec in remove_users_access:
                    rnr_nominator_group.sudo().write({'users': [(3, rec.user_id.id)]})

        res = super(DivisionConfig, self).write(vals)
        self.env.user.notify_success(message='Division has been updated successfully.')
        return res
