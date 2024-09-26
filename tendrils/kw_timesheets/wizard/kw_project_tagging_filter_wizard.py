from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTaggingFilterWizard(models.TransientModel):
    _name           = 'project_tagging_filter_wizard'
    _description    = "Project Tagging Filter Wizard"
    
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    @api.multi
    def project_mapping_filter(self):
        tree_view_id = self.env.ref('kw_timesheets.kw_timesheet_project_tag_report_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet Project Taging Report',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'kw_timesheet_project_tag_report',
            'target': 'main',
            'context': {'from_date':self.from_date,'to_date': self.to_date}
        }
        self.env['kw_timesheet_project_tag_report'].with_context(from_date = self.from_date,to_date= self.to_date).init()
        return action