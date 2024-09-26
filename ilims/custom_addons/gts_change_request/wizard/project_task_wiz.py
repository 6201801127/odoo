from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError, MissingError, AccessDenied
from datetime import date, datetime, timedelta


class CRTask(models.TransientModel):
    _name = 'cr.task'

    date_deadline = fields.Date('Deadline')
    planned_hours = fields.Float('Estimated Hours')
    user_id = fields.Many2one('res.users', 'Assigned to')
    cr_id = fields.Many2one('change.request', 'CR')
    project_id = fields.Many2one('project.project', 'Project')
    stakeholder_ids = fields.Many2many('res.users', 'Stakeholders', compute='_get_stakeholder_project')

    @api.depends('project_id', 'project_id.stakeholder_ids')
    def _get_stakeholder_project(self):
        for record in self:
            stakeholders_list, p_user = [], []
            if record.cr_id.project_id and record.cr_id.project_id.stakeholder_ids:
                for lines in record.cr_id.project_id.stakeholder_ids:
                    if lines.status is True:
                        stakeholders_list.append(lines.partner_id.id)
                    users = self.env['res.users'].search([('partner_id', 'in', stakeholders_list)])
                    user = self.env['res.users'].search([('partner_id', '=', lines.partner_id.id)], limit=1)
                    if user:
                        if user.id == self.env.user.id:
                            p_user.append(user.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                self.stakeholder_ids = [(6, 0, [stakeholder.id for stakeholder in users])]
            else:
                record.stakeholder_ids = [(6, 0, p_user)]

    @api.model
    def default_get(self, fields):
        res = super(CRTask, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['cr_id'] = self.env.context.get('active_id')
            change_request = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))])
            if change_request:
                res['project_id'] = change_request.project_id.id
                res['planned_hours'] = change_request.planned_hours
        return res

    def button_create(self):
        if self.env.context.get('active_id'):
            change_request = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))])
            if change_request:
                task_dict = {
                    'project_id': change_request.project_id.id,
                    'date_deadline': self.date_deadline,
                    'planned_hours': self.planned_hours,
                    'user_id': self.user_id.id,
                    'name': change_request.name,
                    'description': change_request.description,
                }
                task = self.env['project.task'].create(task_dict)
                if task:
                    change_request.task_id = task.id
