# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class mrfApproverDeptConfig(models.Model):
    _name        = "mrf_approver_department_config"
    _description = "MRF Approver Department Configuration Master"
    # _rec_name    = "approver_id"
    # 

    department_ids = fields.Many2many('hr.department','mrf_approver_config_department_rel','department_id', 'config_id',string="Department", required=True)
    approver_id     = fields.Many2one('hr.employee',string="Approver")
    allowed       = fields.Boolean('Allowed',default=True)


    @api.constrains('department_ids')
    def validation(self):
        duplicate_dept = self.env['mrf_approver_department_config'].sudo().search(
            [('department_ids', '=', self.department_ids.ids)]) - self
        if duplicate_dept:
                raise ValidationError('This department is already assign to other approver.')    