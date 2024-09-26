from odoo import models, fields, api
from datetime import datetime,date

class ServiceRequest(models.Model):
    _name = "service_request"

   

    def get_tag_employee(self):
        presales_users = self.env.ref('kw_sales_monitoring.group_presales_member').mapped('users.id')
        tag_emp = self.env['hr.employee'].search([('user_id', 'in', presales_users)])
        return [('id', 'in', tag_emp.ids)]

    lead_name = fields.Char(string = "Lead Name")
    request_by_id = fields.Many2one('res.users',string ="Request By")
    assigned_member_id= fields.Many2one('hr.employee',string = "Assigned Member Name")
    request_department_id = fields.Many2one('hr.department',string="Department")
    request_service_id = fields.Many2one('request_for_service_master',string="Service Type")
    request_date = fields.Datetime(string ="Request Date")
    tag_member_id = fields.Many2one('hr.employee',string = "Tag Mamber",domain=get_tag_employee)



    def tag_member(self):
        view_id = self.env.ref("kw_sales_monitoring.service_reqest_add_tag_member_view").id
        return {
            'name': 'Assign Member for Service Request',
            'type': 'ir.actions.act_window',
            'res_model': 'service_request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
        }

    def update_assign_member(self):
        self.assigned_member_id = self.tag_member_id.id
        self.env.user.notify_success("Member Assigned Successfully.")
        