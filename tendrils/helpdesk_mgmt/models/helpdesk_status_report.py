"""
Module for Helpdesk Status Report Model.

This module contains the model definition for generating helpdesk status reports in Odoo.

"""
from odoo import fields, models, api, tools


class HelpdeskStatusReport(models.Model):
    """
    Model for Helpdesk Status Report.

    This class represents the helpdesk status report model in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk_status_report').
        _description (str): Description of the model ('Helpdesk Status Report').
        _auto (bool): Indicates whether the model is automatically created in the database (False in this case).

    """
    _name = 'helpdesk_status_report'
    _description = 'Helpdesk Status Report'
    _auto = False



    id = fields.Integer(string="SL No")
    number = fields.Char(string='Ticket number', default="New",
                            readonly=True) 
    issue_name = fields.Char(string='Issue Name')       
    category_id = fields.Many2one('helpdesk.ticket.category',
                                  string='Category')
    # description = fields.Html(string='Subject', sanitize_style=True)
    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Status',
    )
    closed_date = fields.Datetime(string='Closed On')
    create_date = fields.Datetime(string='Created On')
    user_id = fields.Many2one('res.users',string='Assigned Engineer')
    users_id = fields.Many2one(comodel_name='res.users', string='Request Name')
    remarks_for_done = fields.Char(string='Action Taken') 

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT row_number() over() as id,
                    ht.number,
                    ht.name as issue_name,
                    ht.create_date,
                    ht.users_id,
                    ht.description,
                    ht.category_id,
                    ht.user_id,
                    ht.stage_id,
                    ht.closed_date,
                    ht.remarks_for_done
                    from helpdesk_ticket ht
                    )"""% (self._table))

    def helpdesk_status_report_action_view(self):
        form_view_id = self.env.ref("helpdesk_mgmt.ticket_view_form").id
        for rec in self:
            ticket_rec = self.env['helpdesk.ticket'].sudo().search([('number','=',rec.number)]).id
            return  {
                'name': 'Close',
                'type': 'ir.actions.act_window',
                'res_model': 'helpdesk.ticket',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ticket_rec,
                'target': 'self',
                'view_id':form_view_id,
            } 
