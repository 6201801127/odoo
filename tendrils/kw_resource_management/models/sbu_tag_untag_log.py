from odoo import fields, models, api
from datetime import datetime
from datetime import date


class SbuTagUntag(models.Model):
    _name = 'sbu_tag_untag_log'
    _description = 'sbu_tag_untag_log'
    _rec_name = "employee_id"
    _auto = "false"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    status = fields.Selection([('tag', 'Tag'), ('untag', 'Un Tag')], string="Status")
    date = fields.Date(string="Date")
    action_by = fields.Many2one('hr.employee', string="Action Taken By")
    sbu_status = fields.Char('Tagged To(SBU/Horizontal)/Un Tagged From (SBU/Horizontal)', track_visibility='onchange')
    sbu_type = fields.Selection([('sbu', 'SBU'), ('horizontal', 'Horizontal')], string='SBU Type')
    sbu_id = fields.Char(string="SBU")
    access_token = fields.Char('Access Token')


class SbuTagUntagMailHistory(models.Model):
    _name = 'sbu_tag_untag_mail_log'
    _description = 'sbu_tag_untag_mail_log'
    _rec_name = "employee_id"
    _auto = "false"
    _order = "id desc"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_name = fields.Char(related='employee_id.name')
    designation = fields.Char(string='Designation')
    technology = fields.Char(string='Technology')
    department = fields.Char(string='Department')
    location = fields.Char(string="Location")
    type_of_employee = fields.Char(string="Type Of Employee")
    resource = fields.Selection(string='Replacement/New', track_visibility='onchange',
                                selection=[('new', 'New'), ('replacement', 'Replacement')])
    # replacement_of = fields.Char(string = "Replacement Of")
    # experience = fields.Char(string = "Experience")
    # qualification = fields.Char(string = "Qualification")
    # planned_project = fields.Char(string = "Planned Project") 
    joining_date = fields.Char(string="Date Of Joining")
    date = fields.Date(string='Tagging Date')

# class SbuApproveReject(models.Model):
#     _name = 'sbu_approve_reject'
#     _rec_name = "emp_id"
#     _description = "SBU Tagging"
#     _order = "id desc"

#     # name = fields.Char(string = "Name" )
#     emp_id = fields.Many2one('hr.employee', string='Employee')
#     emp_name = fields.Char(related='emp_id.name')
#     designation = fields.Char(string = 'Designation')
#     technology = fields.Char(string='Technology')
#     department = fields.Char(string='Department')
#     location = fields.Char(string = "Location")
#     type_of_employee =fields.Char(string = "Type Of Employee")
#     resource = fields.Selection(string='Replacement/New', track_visibility='onchange',
#                                 selection=[('new', 'New'), ('replacement', 'Replacement')])
#     # replacement_of = fields.Char(string = "Replacement Of")
#     # experience = fields.Char(string = "Experience")
#     # qualification = fields.Char(string = "Qualification")
#     # planned_project = fields.Char(string = "Planned Project") 
#     joining_date = fields.Char(string = "Date Of Joining")   
#     date = fields.Date(string='Tagging Date')
#     state = fields.Selection([('draft','Draft'),('approve','Approved'),('reject','Rejected')])
#     remark = fields.Text()
#     sbu_master_id = fields.Many2one('kw_sbu_master', string='SBU')
#     sbu_tagging = fields.Selection([('tag', 'Tag'),('untag', 'Un Tag')],string ='SBU Tagging',default='tag')
#     sbu_type = fields.Selection([('sbu', 'SBU'), ('horizontal', 'Horizontal')],string = 'Resource Type')
#     primary_skill_id =fields.Many2one('kw_skill_master',string='Skill')


#     @api.multi
#     def sbu_approve_button(self):
#         view_id = self.env.ref("kw_resource_management.sbu_approve_remark_view").id
#         print(view_id,"view id of sbu_approve button=================")
#         action = {
#             'name': 'Approve',
#             'type': 'ir.actions.act_window',
#             'res_model': 'sbu_approve_remark',
#             'view_mode': 'form',
#             'view_type': 'form',
#             'view_id': view_id,
#             'target': 'new',
#             'context': {'current_id':self.id}
#         }
#         return action

# @api.multi
# def sbu_reject_button(self):
#     view_id = self.env.ref("kw_resource_management.sbu_reject_remark_view").id
#     action = {
#         'name': 'Reject',
#         'type': 'ir.actions.act_window',
#         'res_model': 'sbu_reject_remark',
#         'view_mode': 'form',
#         'view_type': 'form',
#         'view_id': view_id,
#         'target': 'new',
#         'context': {'current_id':self.id}
#     }
#     return action
