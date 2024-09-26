from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class NotifyToPanel(models.Model):
    _name = 'kw_notify_to_panel'
    _description = 'Notify To Panel'
    _auto = False

    """ view fields """
    create_date = fields.Datetime(string="Create Date")
    applicant_id = fields.Many2one('hr.applicant',string="Applicant")
    job_id = fields.Many2one('hr.job',string="Applied Job")
    job_position_id = fields.Many2one('kw_hr_job_positions',string="Job Position")

    email_from = fields.Char(string="Email")
    stage_code = fields.Char(string="Code")
    stage_id = fields.Many2one('hr.recruitment.stage',string="Stage")
    panel_member_id = fields.Many2one('hr.employee',string="Panel Member")

    @api.multi
    def update_panel_member(self):
        form_view_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
        action = {
                'type': 'ir.actions.act_window',
                'name' : 'Applicant',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'res_model': 'hr.applicant',
                'target': 'self',
                'res_id':self.applicant_id.id,
                'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true','panel_member_data':self.job_position_id.panel_member.ids},
                }
        return action
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over() as id,a.id as applicant_id,a.stage_code as stage_code,a.create_date as create_date,a.job_id as job_id,a.job_position as job_position_id,a.email_from as email_from,a.stage_id as stage_id,a.panel_member_id as panel_member_id
        from hr_applicant a join kw_hr_job_positions c on a.job_position = c.id 
        and c.enable_applicant_screening = 'True' 
        and c.state='recruit' 
        where a.stage_code = 'IQ' and a.active ='True' 

            )""" % (self._table))
