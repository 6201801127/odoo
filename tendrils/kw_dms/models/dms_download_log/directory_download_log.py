# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DirectoryDownloadLog(models.Model):

    _name           = 'kw_dms.directory_download_log'
    _description    = "Directory Download Log."

    _rec_name       = 'directory_id'


    user_id            = fields.Many2one('res.users', string="User", required=True)
    employee_id        = fields.Many2one('hr.employee', string="Employee")

    emp_department     = fields.Char(string="Department", related='employee_id.department_id.name', readonly=True)
    emp_designation    = fields.Char(string="Desigation", related='employee_id.job_id.name', readonly=True)

    directory_id       = fields.Many2one('kw_dms.directory', string="Downloaded Directory", required=True)

    