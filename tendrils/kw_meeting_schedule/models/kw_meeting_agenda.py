# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class kw_meeting_agenda(models.Model):
    _name           = 'kw_meeting_agenda'
    _description    = 'Meeting Agenda'
    _rec_name       = 'name'
    _order          = 'name ASC'

    name = fields.Text(
        string='Subject',
        required=True,
        # default=lambda self: ('New'),
        copy=False
    )

    proposal_ids = fields.One2many(
        string='Proposal',
        comodel_name='kw_meeting_agenda_proposals',
        inverse_name='agenda_id',
    )

    meeting_id = fields.Many2one(
        string='Meeting',
        comodel_name='kw_meeting_events',
        ondelete='restrict',
    )
    meeting_status = fields.Selection(related='meeting_id.state',
                                      readonly=True,
                                      store=False)

    is_deferred = fields.Boolean(
        string='Is Deferred',
    )

    activity_ids = fields.One2many(
        string='Activity',
        comodel_name='kw_meeting_agenda_activities',
        inverse_name='agenda_id',
    )
    no_of_activities    = fields.Integer('Activity Count',compute="_compute_activity_count")
    agenda_type         = fields.Integer('Agenda Type',default=1) ## 1- Old, 2- Newel added after meeting scedule

    @api.multi 
    @api.depends('activity_ids')
    def _compute_activity_count(self):
        for record in self:
            # print(record.agenda_type)            
            record.no_of_activities = len(record.activity_ids)


    @api.multi
    def action_meeting_status(self):
        # print(self)
        view_id     = self.env.ref('kw_meeting_schedule.kw_meeting_agenda_activity_view_form').id
        target_id   = self.id
        # context = self._context.copy()
        return {
            'name'      : 'Meeting Activities',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_meeting_agenda',
            'res_id'    : target_id,
            'view_type' : 'form',
            # 'view_mode': 'tree,form',
            'target'    : 'new',
            'views'     : [(view_id, 'form')],
            'view_id'   : view_id,
            'flags'     : {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
            # 'context': {"default_meeting_id": self.meeting_id,},
        }

    def action_agenda_status_deferred(self):
        for record in self:
            if not record.activity_ids:
                record.is_deferred = True
            else:
                raise UserError(
                    'You cannot mark agenda as deferred if activities exists.\n Please remove the activity records and try again.'
                )

    def action_agenda_delete(self):
        for record in self:
            if record.agenda_type == 2:
                record.activity_ids.unlink()
                record.unlink()
            else:
                raise ValidationError("You can not remove old agenda(s). ")

    
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """

        result = super(kw_meeting_agenda, self).create(values)
        for record in result:
            # print(record.agenda_type)
            if record.meeting_id.state in ['attendance_complete','draft_mom','final_mom']:
                    record.agenda_type = 2 ##newly added
            else:
                record.agenda_type = 1
    
        return result
    

