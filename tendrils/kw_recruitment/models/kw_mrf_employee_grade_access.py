# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class MrfEmployeeGrade(models.Model):
    _name        = "mrf_employee_grade_access"
    _description = "MRF Approver Department Configuration Master"

    grade_ids = fields.Many2many('kwemp_grade_master','mrf_employee_access_grade_rel','grade_id', 'mrf_employee_grade_id',string="Allow MRF access to Employee of Grade", required=True)
