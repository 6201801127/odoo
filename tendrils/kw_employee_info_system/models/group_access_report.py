# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class kw_group_access_report(models.Model):
    _name = "kw_group_access_report"
    _description = "Kwantify Group Access Report"
    _auto = False

    emp_code = fields.Char(string='Employee Code')
    user_name = fields.Char(string='User Name')
    designation = fields.Char(string='Designation')
    dept_id = fields.Char(string="Department")
    module_name = fields.Char(string='Module Name')
    group_name = fields.Char(string="Group Name")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                SELECT row_number() over() AS id ,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                hr.emp_code AS emp_code,
                hr.name AS user_name,
                (SELECT name FROM hr_department WHERE id = hr.department_id) AS dept_id,
                (SELECT name FROM hr_job WHERE id = hr.job_id) AS designation,
                m.name AS module_name,
                res.name AS group_name 
                FROM ir_module_category m 
                LEFT JOIN res_groups res ON res.category_id= m.id 
                JOIN res_groups_users_rel rel ON rel.gid = res.id
                JOIN res_users u ON u.id = rel.uid 
                JOIN hr_employee hr ON u.id = hr.user_id where hr.active is true
                 )""" % (self._table))
