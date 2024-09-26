from odoo import fields, models, api
from datetime import datetime

class HrEmployeeTransferApprove(models.TransientModel):
    _name = 'hr.employee.transfer.approve'
    _description = 'Hr employee transfer'


    assign_task = fields.Boolean(string = 'Assign tasks to another employee?', defaut = 'False')
    employee_transfer_id = fields.Many2one('hr.employee.transfer', readonly=1)
    branch_id = fields.Many2one('res.branch', string="Center", store=True)
    name = fields.Many2one('res.users', string = 'Slect another user')



    def transfer_assigned_to(self):
        if self.name:
            serch_id = self.env['mail.activity'].search([('user_id', '=', self.employee_transfer_id.employee_id.user_id.id)])
            for mail_act in serch_id:
                mail_act.user_id = self.name.id
