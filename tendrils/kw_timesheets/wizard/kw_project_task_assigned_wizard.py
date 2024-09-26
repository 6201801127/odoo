from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class ProjectTaskAssignWizard(models.TransientModel):
    _name           = 'project_task_assign_report_wizard'
    _description    = "Project task assigned Filter Wizard"
    
    to_date = fields.Date(string='Date',default=date.today())

    @api.multi
    def project_task_assign_filter(self):
        tree_view_id = self.env.ref('kw_timesheets.kw_project_task_assign_report_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': f'Project Task assign Report : {self.to_date.strftime("%d-%b-%Y")}',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'kw_project_task_assign_report',
            'target': 'main',
            'context': {'to_date': self.to_date}
        }
        self.env['kw_project_task_assign_report'].with_context(to_date= self.to_date).init()
        return action