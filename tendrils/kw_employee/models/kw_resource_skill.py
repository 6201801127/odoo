from odoo import models, fields, api
from odoo.osv import expression


class hr_resource_skill(models.Model):
    _inherit = 'hr.employee'
    # _description = "A model to create Skill against employee."
    # _rec_name = "emp_id"

    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill', store="True")
    skill_id = fields.Many2many('kw_skill_master', string='Additional Skill', store="True")
    # emp_id = fields.Many2one('hr.employee', string='Employee Name', required=True)
    # deg_rel = fields.Char(string="Designation", related='emp_id.job_id.name')

    # @api.model
    # def fields_get(self, allfields=None, attributes=None):
    #     fields_to_hide = ['__filter__13','__filter__16']
    #     res = super(hr_resource_skill, self).fields_get()
    #     for field in fields_to_hide:
    #         res[field]['selectable'] = False
    #     return res
