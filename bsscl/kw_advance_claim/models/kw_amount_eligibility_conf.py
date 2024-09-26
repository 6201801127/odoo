from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_amount_eligibility_conf(models.Model):
    _name = 'kw_advance_amount_eligibility_conf'
    _description = "Advance Amount Eligibility Configuration"
    # _rec_name = 'group_id'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    # location_ids = fields.Many2many('kw_res_branch', 'kw_advance_amt_eli_config_res_branch_rel',
    #                                 'adv_amt_eli_config_id', 'res_branch_id', string="Branch / SBU", required=True,
    #                                 ondelete='restrict')
    max_elig_amount = fields.Integer(string="Max Eligible Amount")
    interest = fields.Integer(string="Interest(%)")
    # grade_ids = fields.Many2many('kwemp_grade_master', 'kw_advance_amt_eli_config_grade_master',
    #                              'adv_amt_eli_config_id',
    #                              'grade_id', string='Grade', required=True, copy=False)
    # band_ids = fields.Many2many('kwemp_band_master', 'kw_advance_amt_eli_config_band_master', 'adv_amt_eli_config_id',
    #                             'band_id', String='Band', copy=False)
    active = fields.Boolean(string="Active", default=True)
    # group_id = fields.Many2one('kw_advance_group', string="Name", required=True)
    select_branch = fields.Selection([('all', 'All'), ('branch', 'Branch Specific')], string="Branch Type",
                                     default='all')
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')

    @api.onchange('select_branch')
    def onchange_select_branch(self):
        for rec in self:
            if rec.select_branch == 'all':
                branch_ids = self.env['res.branch'].search([])
            #     rec.location_ids = [(6, 0, branch_ids.ids)]
            # else:
            #     rec.location_ids = False

    @api.constrains('interest')
    def validate_interest(self):
        for record in self:
            if record.interest < 0:
                raise ValidationError("Interest cannot be less than 0.")
            elif record.interest > 100:
                raise ValidationError("Interest cannot be greater than 100.")
            else:
                return True

    @api.constrains('grade_ids', 'band_ids')
    def validate_grade_band(self):
        if self.grade_ids and self.band_ids:
            rec_id = self.env['kw_advance_amount_eligibility_conf'].sudo().search(
                [('grade_ids', 'in', self.grade_ids.ids), ('band_ids', 'in', self.band_ids.ids)]) - self
            if rec_id:
                for rec in rec_id:
                    raise ValidationError("Grade and Band cannot be same.")
        if self.grade_ids and not self.band_ids:
            rec_id = self.env['kw_advance_amount_eligibility_conf'].sudo().search(
                [('grade_ids', 'in', self.grade_ids.ids)]) - self
            if rec_id:
                for rec in rec_id:
                    raise ValidationError("Grade cannot be same.")
