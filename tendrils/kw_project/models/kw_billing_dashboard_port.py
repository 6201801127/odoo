from odoo import models, fields, api
from datetime import  date
from odoo.exceptions import ValidationError

class BillingDashBoard(models.Model):
    _name = 'kw_billing_dashboard_port'
    _description= 'Billing Dashboard'
    _rec_name = 'wo_code'
    _order = "billing_target_date DESC"


    sbu_name = fields.Char('SBU')
    wo_code = fields.Char('WO Code')
    wo_name = fields.Char('WO Name')
    billing_amount = fields.Float()
    milestone_details = fields.Char('Milestone Name')
    billing_plan_date = fields.Date(string='Billing Plan Date')
    collection_plan_date = fields.Date(string='Milestone Date')
    billing_target_date = fields.Date(string='Billing Target Date')
    kw_milestone_id = fields.Integer()
    project_id = fields.Many2one('project.project')
    project_manager_id = fields.Many2one('hr.employee')
    account_leader_id = fields.Many2one('hr.employee')
    account_manager_id = fields.Many2one('hr.employee')
    reviewer_id = fields.Many2one('hr.employee')
    sbu_head_id = fields.Many2one('hr.employee')
    updated_by = fields.Integer()
    last_updated_on = fields.Char()
    next_execution_time = fields.Char()
    action_log_ids = fields.One2many('kw_billing_port_action_log','billing_port_id',string="Action log")
    active = fields.Boolean()
    is_target_date_less = fields.Boolean(compute='check_date_status')



    @api.depends('billing_target_date')
    def check_date_status(self):
        for rec in self:
            if rec.billing_target_date and rec.billing_target_date <= date.today():
                rec.is_target_date_less = True
            else:
                rec.is_target_date_less = False


    @api.model
    def update_billing_model_field(self, rec_id, given_date):
        data = self.env['kw_billing_dashboard_port'].search([('id', '=', rec_id)])
        sync_data = self.env['kw_sync_portlet_data'].sudo().search([('rec_id', '=', rec_id), ('status', '=', 0)])
        if len(given_date) > 0:
            # data.expected_date = given_date
            billing_port_log = self.env['kw_billing_port_action_log']
            value = {
                'action_taken_date': date.today(),
                'action_taken_by_id': self.env.user.employee_ids.id,
                'changed_date': given_date,
                'debt_port_id': data.id,
            }
            billing_port_log.create(value)
            if not sync_data:
                sync_value = {
                    'model_id': 'kw_billing_dashboard_port',
                    'rec_id': rec_id,
                    'created_on': date.today(),
                    'status': 0,
                }
                sync_data.create(sync_value)
            else:
                pass
        else:
            raise ValidationError('Please provide a valid date..')



    def write(self, vals):
        result = super(BillingDashBoard, self).write(vals)

        if 'billing_target_date' in vals:
            for record in self:
                self._create_billing_port_log(record, vals['billing_target_date'])

        return result


    def _create_billing_port_log(self, record, date_value):
        billing_port_log = self.env['kw_billing_port_action_log']
        value = {
            'action_taken_date': date.today(),
            'action_taken_by_id': self.env.user.employee_ids.id,
            'changed_date': date_value,
            'billing_port_id': record.id,}
        billing_port_log.create(value)

        sync_data = self.env['kw_sync_portlet_data'].sudo().search([('rec_id', '=', record.id), ('status', '=', 0)])
        if not sync_data:
            sync_value = {
                'model_id': 'kw_billing_dashboard_port',
                'rec_id': record.id,
                'created_on': date.today(),
                'status': 0,}
            sync_data.create(sync_value)
        else:
            pass






class BillingPortDashboardLog(models.Model):
    _name = 'kw_billing_port_action_log'
    _description= 'Billing Dashboard Action Log'

    action_taken_date = fields.Date(string="Action taken Date")
    action_taken_by_id = fields.Many2one('hr.employee',string="Action taken By")
    changed_date = fields.Date(string="Changed Closing Date")
    billing_port_id = fields.Many2one('kw_billing_dashboard_port')