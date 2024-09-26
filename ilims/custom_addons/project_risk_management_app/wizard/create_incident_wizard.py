from odoo import api, fields, models, _


class RiskIncidentTask(models.TransientModel):
    _name = 'risk.incident.task.wizard'
    _description = 'Risk Incident Task'

    risk_incident_name = fields.Char(" Incident for Risk", required=True)
    risk_description = fields.Text("Risk Description", required=True)
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.uid)
    project_id = fields.Many2one('project.project', 'Project', required=True)
    incident_photo = fields.Binary("Risk Incident Photo")

    @api.model
    def default_get(self, default_fields):
        res = super(RiskIncidentTask, self).default_get(default_fields)
        active_id = self._context.get('active_id')
        project_task_id = self.env['project.task'].browse(active_id)
        res.update({
            'project_id': project_task_id.project_id.id,
        })
        return res

    def create_incident_by_wizard(self):
        active_id = self._context.get('active_id')
        project_task_id = self.env['project.task'].browse(active_id)
        vals = {
            'name': self.risk_incident_name,
            'description': self.risk_description,
            'project_id': project_task_id.project_id.id,
            'user_id': self.user_id.id,
            'incident_photo': self.incident_photo,
            'incident_type': 'task',
            'parent_id': project_task_id.id,
            'stage_id': project_task_id.stage_id.id,
            'risk_incident': True,
        }
        self.env['project.task'].create(vals)


class RiskIncidentProject(models.TransientModel):
    _name = 'risk.incident.project.wizard'
    _description = 'Risk Incident Project'

    risk_incident_name = fields.Char("Incident For Risk", required=True)
    risk_description = fields.Text("Risk Description", required=True)
    incident_photo = fields.Binary("Risk Incident Photo")
    project_id = fields.Many2one('project.project', 'Project', required=True)
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.uid)

    @api.model
    def default_get(self, default_fields):
        res = super(RiskIncidentProject, self).default_get(default_fields)
        active_id = self._context.get('active_id')
        project_id = self.env['project.project'].browse(active_id)
        res.update({
            'project_id': project_id.id,
        })
        return res

    def create_incident_by_wizard(self):
        active_id = self._context.get('active_id')
        project_id = self.env['project.project'].browse(active_id)
        vals = {
            'name': self.risk_incident_name,
            'description': self.risk_description,
            'project_id': project_id.id,
            'user_id': self.user_id.id,
            'incident_photo': self.incident_photo,
            'incident_type': 'project',
            'risk_incident': True,
            'is_from_project': True,
        }
        self.env['project.task'].create(vals)
class SetDraftReview(models.TransientModel):

    _name = "set.draft.wizard"
    _description = "Set Draft Review"

    reason = fields.Text(string='Set To Draft Reason')

    def save_reason(self):
        context = dict(self._context)
        proObj = self.env["project.project"]
        pro_details = proObj.browse(context.get("active_id"))
        pro_details.reviewer_remarks = self.reason
        pro_details.write({'state':'draft'})

class RejectionReason(models.TransientModel):

    _name = "rejection.wizard"
    _description = "Set Draft Review"

    reason = fields.Text(string='Rejection Reason')

    def save_reason(self):
        context = dict(self._context)
        proObj = self.env["project.project"]
        pro_details = proObj.browse(context.get("active_id"))
        pro_details.approver_remarks = self.reason
        pro_details.write({'state':'rejected'})

