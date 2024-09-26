"""
Module for the IncidentWizard transient model.

This module imports necessary dependencies such as models, fields, and api from Odoo.
It also imports the ValidationError exception from Odoo's exceptions module.
The module defines the IncidentWizard class, which represents a transient model used for handling
incidents in the system.

Example:
    This module is utilized within the Odoo environment to manage incidents through a wizard interface.

Usage:
    Developers can use instances of the IncidentWizard class to handle incidents within the Odoo system.
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class IncidentWizard(models.TransientModel):
    """
    Transient model class representing the Incident Wizard.

    This class provides functionality for handling incidents through a wizard interface.
    """
    _name = 'incident.wizard'
    _description = 'Incident Wizard'
            

    team_id = fields.Many2one('helpdesk.ticket.team')
    user_id = fields.Many2one(
        'res.users',
        string='Team Members',

    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')

    def update_incident(self):
        """
        Update incident details.

        This method updates the incident details such as team assignment and user assignment.
        It retrieves the incident details based on the active ID from the context.
        Then, it assigns the specified team and user to the incident.
        Finally, it sends an email notification to the assigned user using the specified email template.

        Returns:
            None
        """
        context = dict(self._context)
        intObj = self.env["helpdesk.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.team_id = self.team_id
        int_details.user_id = self.user_id
        helpdesk_desk_users = self.env.user.email
        to_name = self.user_id.name
        to_eamil = self.user_id.email
        template = self.env.ref('helpdesk_mgmt.email_template_assigned_ticket')
        template.with_context(to_name=to_name, email_to=to_eamil, email_from=helpdesk_desk_users).send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
   
    @api.multi
    @api.onchange('team_id')
    def _onchange_team_id(self):
      
        if self.team_id:
            user_var = {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}
            ticket_assigned=self.env["helpdesk.ticket"].search(['|',('stage_id.code','=','IP'),('stage_id.code','=','H')])
            minimum=len(ticket_assigned)
            if ticket_assigned:
                for record in self.user_ids:
                    ticket = 0
                    for rec in ticket_assigned:
                        if rec.user_id == record:
                            ticket = ticket +1
                    ticket_got = ticket 
                    final_record=False
                    if ticket_got < minimum:
                        minimum = ticket_got
                        final_record = record
                        # employee_on_leave_id = self.env['kw_daily_employee_attendance'].search([('employee_id.user_id','=',final_record.id),('leave_status','!=',False),('attendance_recorded_date','=',date.today())],limit=1)
                    # print('finak', final_record)
                    if final_record:
                        self.user_id = final_record
            else:
                self.user_id = self.user_ids[0]
            return user_var
