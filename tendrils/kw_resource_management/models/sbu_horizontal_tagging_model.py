# from odoo import fields, models, api, tools
# from datetime import date
# import random
# import uuid
# from dateutil.relativedelta import relativedelta
# from datetime import datetime
# import logging
# _logger = logging.getLogger(__name__)

# class SBUhorizontalTagging(models.Model):
#     _name = 'sbu_horizontal_tagging_table'
#     _description = 'SBU Horizontal Tagging'
#     _order = "employee_id"
#     _auto = False

#     employee_id = fields.Many2one('hr.employee', string='Employee')
#     code = fields.Char(related='employee_id.emp_code', string='Employee Code')
#     name = fields.Char(related='employee_id.name', string='Employee Name')
#     designation = fields.Many2one('hr.job', string='Designation')
#     date_of_joining = fields.Date(string='Date of Joining')
#     emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
#     emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
#     employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
#     job_branch_id = fields.Many2one('kw_res_branch', string='Location')
#     sbu = fields.Many2one("kw_sbu_master", "SBU")
#     sbu_name = fields.Char(related='sbu.name', string="SBU")
#     sbu_type =  fields.Selection(
#          string='Resource Type',
#          selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('none', 'None')])

    
#     @api.model_cr
#     def init(self):
#         tools.drop_view_if_exists(self.env.cr, self._table)
#         query = f"""
#             CREATE OR REPLACE VIEW {self._table} AS (
#                 SELECT DISTINCT
#                 ROW_NUMBER() OVER () AS id,
#                 emp.id AS employee_id,
#                 emp.job_id AS designation,
#                 emp.date_of_joining AS date_of_joining,
#                 emp.emp_role AS emp_role,
#                 emp.emp_category AS emp_category,
#                 emp.employement_type AS employement_type,
#                 emp.job_branch_id AS job_branch_id,
#                 emp.sbu_master_id as sbu,
#                 CASE 
#                     WHEN emp.sbu_type IN ('sbu', 'horizontal', 'none') THEN emp.sbu_type
#                     ELSE 'none'  
#                 END as sbu_type
#             FROM
#                 hr_employee AS emp
#             )
#         """
#         self.env.cr.execute(query)

# class SBUhorizontalTaggingWizard(models.TransientModel):
#     _name = "sbu_horizontal_tagging_wizard"
#     _description = "Wizard"

#     sbu = fields.Many2one(
#         string='SBU/Horizontal',
#         comodel_name='kw_sbu_master',
#         domain="[('type', '=', sbu_type)]",
#     )


#     @api.model
#     def default_get(self, fields):
#         res = super(SBUhorizontalTaggingWizard, self).default_get(fields)
#         active_ids = self.env.context.get('active_ids', [])
#         res.update({
#             'employee_ids': active_ids,
#         })
#         return res

#     employee_ids = fields.Many2many(
#         string='Employee',
#         comodel_name='sbu_horizontal_tagging_table',
#         relation='sbu_tag_emp_id',
#         column1='sbu_emp_id',
#         column2='tagging_emp_id',
#     )

#     sbu_type = fields.Selection([
#         ('sbu', 'SBU'),
#         ('horizontal', 'Horizontal'),
#         ('none', 'None')
#     ], string='Resource Type', required=True)


#     @api.onchange('sbu_type')
#     def _onchange_sbu_type(self):
#         """Update domain for sbu field based on selected sbu_type"""
#         if self.sbu_type:
#             if self.sbu_type == 'sbu':
#                 domain = [('type', '=', 'sbu')]
#             elif self.sbu_type == 'horizontal':
#                 domain = [('type', '=', 'horizontal')]
#             else:
#                 domain = [] 
#             return {'domain': {'sbu': domain}}
#         else:
#             return {}


#     def confirm_sbu_type(self):
#         history_vals = []
#         for employee in self.employee_ids:
#             old_sbu_type = employee.employee_id.sbu_type
#             old_sbu = employee.employee_id.sbu_master_id
#             history_vals.append({
#                 'employee_id': employee.employee_id.id,
#                 'old_sbu_type': old_sbu_type,
#                 'old_sbu': old_sbu.id if old_sbu else False,
#                 'sbu_type': self.sbu_type,
#                 'tagged_by': self.env.user.id,
#                 'tagged_datetime': datetime.now(),
#                 'date_tagged': datetime.now().date(),
#                 'sbu': self.sbu.id,
#             })
#             emp_data = self.env['hr.employee'].search([('id','=',employee.employee_id.id)])
#             emp_data.write({'sbu_type':self.sbu_type,'sbu_master_id':self.sbu.id})
#         self.env['sbu_horizontal_tagging_history'].create(history_vals)
#         return {'type': 'ir.actions.act_window_close'}

# class SBUHorizontalTaggingHistory(models.Model):
#     _name = 'sbu_horizontal_tagging_history'
#     _description = 'SBU Horizontal Tagging History'

#     employee_id = fields.Many2one('hr.employee', string='Employee')

#     old_sbu_type = fields.Selection([
#         ('sbu', 'SBU'),
#         ('horizontal', 'Horizontal'),
#         ('none', 'None')
#     ], string='Old SBU Type')
#     old_sbu = fields.Many2one('kw_sbu_master', string='Old SBU')

#     sbu_type = fields.Selection([
#         ('sbu', 'SBU'),
#         ('horizontal', 'Horizontal'),
#         ('none', 'None')
#     ], string='Updated SBU Type')
#     date_tagged = fields.Date(string='Date Tagged')
#     tagged_datetime = fields.Datetime(string='Tagged Date Time')  

#     tagged_by = fields.Many2one('res.users', string='Tagged By')

#     sbu = fields.Many2one('kw_sbu_master', string='Updated SBU')