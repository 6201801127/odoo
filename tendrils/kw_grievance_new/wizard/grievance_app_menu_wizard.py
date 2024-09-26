from multiprocessing import managers
from odoo import models, fields, api
from ast import literal_eval


class GrievanceAppMenuWizard(models.TransientModel):
    _name = 'grievance.app.menu.wizard'
    _description = 'Grievance App Menu Wizard'


    def action_for_raise_grievance(self):
        action_id = self.env.ref('kw_grievance_new.grievance_ticket_action_main').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=grievance.ticket&view_type=list',
            'target': 'self',
        }
       


    def action_for_raise_whistleblowing(self):
        action_id = self.env.ref('kw_grievance_new.whistleblowing_ticket_action_main').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_whistle_blowing&view_type=list',
            'target': 'self',
        }