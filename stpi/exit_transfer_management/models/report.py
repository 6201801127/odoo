from odoo import models, fields, api
# PF Request
class ReportExit(models.Model):
    _name = "exit.management.report"
    _description = "Exit Management Report"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer ID")
    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    exit_type = fields.Selection([("Suspended", "Suspended"),
                                  ("Resigned", "Resigned"),
                                  ("Contract Expired ", "Contract Expired "),
                                  ("Superannuation", "Superannuation"),
                                  ("Terminated", "Terminated"),
                                  ("Deceased", "Deceased"),
                                  ("Terminated", "Terminated"),
                                  ("Absconding", "Absconding"),
                                  ("Transferred", "Transferred")
                                  ], string='Type of Exit')
    module=fields.Char('Module')
    module_id=fields.Char('Module ID')
    action_taken_by = fields.Many2one('hr.employee', string='Action Taken By')
    action_taken_on = fields.Many2one('hr.employee', string='Action Taken On')
