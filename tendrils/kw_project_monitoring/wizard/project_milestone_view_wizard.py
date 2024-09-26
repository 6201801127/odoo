from odoo import models, fields, api,_
from odoo.exceptions import UserError

class KwProjectMilestoneViewWizard(models.TransientModel):
    _name = 'kw_project_milestone_view_wizard'
    _description = 'Project Milestone Wizard'

    project_id = fields.Many2one('project.project', string='Project', required=True)

    @api.multi
    def search_project_data(self):
        self.ensure_one()
        milestones = self.env['kw_project_milestone'].search([('project_id', '=', self.project_id.id)])

        if not milestones:
            raise UserError('No milestones found for the selected project.')
        
        view_id = self.env.ref('kw_project_monitoring.kw_project_milestone_list_view').id
        return {
            'name': _('Project Milestones'),
            'type': 'ir.actions.act_window',
            'res_model': 'kw_project_milestone',
            'view_type': 'form',
            'view_mode': 'tree',  
            'view_id':view_id,
            'domain': [('id', 'in', milestones.ids)],
            'target': 'current',
            'context':{'view_milestone':True,'is_reviewing':True}
        }
