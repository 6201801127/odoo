# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class kw_meeting_agenda_proposals(models.Model):
    _name = 'kw_meeting_agenda_proposals'
    _description = 'Meeting Proposals'
    _rec_name = 'name'
    _order = 'name ASC'

    @api.model
    def _get_agenda_domain(self):
        if self.env.context.get('default_meeting_id'):
            return [('meeting_id', '=', self.env.context.get('default_meeting_id'))]
        else:
            return []

    name = fields.Text(
        string='Input',
        required=True,
        copy=False
    )

    agenda_id = fields.Many2one(
        string='Agenda',
        comodel_name='kw_meeting_agenda',
        ondelete='restrict',
        domain=_get_agenda_domain
    )

    meeting_id = fields.Many2one(
        string='Meeting ',
        related='agenda_id.meeting_id',
        readonly=True,
        store=False
    )

    @api.constrains('agenda_id')
    def _check_proposal_ids(self):
        for proposal in self:
            # print(proposal.agenda_id)
            if proposal.agenda_id and proposal.agenda_id.meeting_id.meeting_start_status:
                raise UserError('You cannot add a proposal after the meeting has been taken place!')

    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
        for record in self:
            if record.meeting_id.meeting_start_status:
                raise UserError('You cannot modify a proposal after the meeting has been taken place!')
        result = super(kw_meeting_agenda_proposals, self).write(values)
        return result
