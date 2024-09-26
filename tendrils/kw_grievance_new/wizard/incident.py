from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import random


class IncidentWizard(models.TransientModel):
    _name = 'grievance.incident.wizard'
    _description = 'Incident Wizard'

    team_id = fields.Many2one('grievance.ticket.team', default=lambda self: self._context.get("category_id"))
    user_id = fields.Many2one('res.users', string='Team Members')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')

    def update_incident(self):
        context = dict(self._context)
        intObj = self.env["grievance.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.team_id = self.team_id
        int_details.user_id = self.user_id
        grievance_desk_users = self.env.user.email
        to_name = self.user_id.name
        to_eamil = self.user_id.email
        if int_details.request == 'self':
            template = self.env.ref('kw_grievance_new.email_template_assigned_grievance_ticket')
            template.with_context(to_name=to_name, email_to=to_eamil, email_from=grievance_desk_users).send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass     
   
    @api.multi
    @api.onchange('team_id')
    def _onchange_team_id(self):
        context = dict(self._context)
        intObj = self.env["grievance.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        if self.team_id:
            user_var = {'domain': {'user_id': [('id', 'in', self.team_id.user_ids.ids)]}}

            # self.user_id = random.choice(int_details.category_id.user_ids.ids)

           # user_var = {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}


            # ticket_assigned=self.env["grievance.ticket"].search(['|',('stage_id.code','=','IP'),('stage_id.code','=','H')])
            # minimum=len(ticket_assigned)
            # if ticket_assigned:
            #     for record in self.user_ids:
            #         ticket = 0
            #         for rec in ticket_assigned:
            #             if rec.user_id == record:
            #                 ticket = ticket +1
            #         ticket_got = ticket 
            #         final_record=False
            #         if ticket_got < minimum:
            #             minimum = ticket_got
            #             final_record = record
            #             # employee_on_leave_id = self.env['kw_daily_employee_attendance'].search([('employee_id.user_id','=',final_record.id),('leave_status','!=',False),('attendance_recorded_date','=',date.today())],limit=1)
            #         print('finak', final_record)
            #         if final_record:
            #             self.user_id = final_record
            # else:
            #     self.user_id = self.user_ids[0]
            return user_var
