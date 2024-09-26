# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tour_maximum_pending_days = fields.Integer('Pending Days For Notification')
    tour_traveldesk_maximum_pending_days = fields.Integer('Traveldesk Pending Days')
    tour_public_access_job_ids = fields.Many2many('hr.job', string='Designation For Public Access')
    tour_traveldesk_approval_email_ids = fields.Many2many('hr.employee', 'tour_traveldesk_email_notify_rel','employee_id','tour_id',string='Tour Traveldesk Email restrict')
    tour_others_approver = fields.Many2one('hr.employee', string='Group Tour Approver')
    tour_finance_users_l1_ids  = fields.Many2many('hr.employee', 'kw_tour_finance_notify_l1_rel','employee_id','tour_id',string='Tour Finance Mail Notification L1')
    tour_finance_users_l2_ids  = fields.Many2many('hr.employee', 'kw_tour_finance_notify_l2_rel','employee_id','tour_id',string='Tour Finance Mail Notification L2')
    tour_traveldesk_users_l1_ids  = fields.Many2many('hr.employee', 'kw_tour_traveldesk_notify_l1_rel','employee_id','tour_id',string='Tour Traveldesk Mail Notification L1')
    tour_traveldesk_users_l2_ids  = fields.Many2many('hr.employee', 'kw_tour_traveldesk_notify_l2_rel','employee_id','tour_id',string='Tour Traveldesk Mail Notification L2')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        tour_maximum_pending_days = param.get_param('tour_maximum_pending_days') or "0"
        tour_traveldesk_maximum_pending_days = param.get_param('tour_traveldesk_maximum_pending_days') or "0"
        tour_public_access_job_ids = param.get_param('tour_public_access_job_ids') or "[]"
        tour_traveldesk_approval_email_ids = param.get_param('tour_traveldesk_approval_email_ids') or "[]"
        tour_others_approver = param.get_param('tour_others_approver')
        tour_finance_users_l1_ids = param.get_param('tour_finance_users_l1_ids') or "[]"
        tour_finance_users_l2_ids = param.get_param('tour_finance_users_l2_ids') or "[]"
        tour_traveldesk_users_l1_ids = param.get_param('tour_traveldesk_users_l1_ids') or "[]"
        tour_traveldesk_users_l2_ids = param.get_param('tour_traveldesk_users_l2_ids') or "[]"
        res.update({
            'tour_maximum_pending_days': int(tour_maximum_pending_days),
            'tour_traveldesk_maximum_pending_days': int(tour_traveldesk_maximum_pending_days),
            'tour_public_access_job_ids':[(6, 0, literal_eval(tour_public_access_job_ids))],
            'tour_traveldesk_approval_email_ids':[(6, 0, literal_eval(tour_traveldesk_approval_email_ids))],
            'tour_others_approver': int(tour_others_approver),
            'tour_finance_users_l1_ids':[(6, 0, literal_eval(tour_finance_users_l1_ids))],
            'tour_finance_users_l2_ids': [(6, 0, literal_eval(tour_finance_users_l2_ids))],
            'tour_traveldesk_users_l1_ids':[(6, 0, literal_eval(tour_traveldesk_users_l1_ids))],
            'tour_traveldesk_users_l2_ids': [(6, 0, literal_eval(tour_traveldesk_users_l2_ids))],
        }) 

        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('tour_maximum_pending_days', self.tour_maximum_pending_days)
        param.set_param('tour_traveldesk_maximum_pending_days', self.tour_traveldesk_maximum_pending_days)
        param.set_param('tour_public_access_job_ids', self.tour_public_access_job_ids.ids)
        param.set_param('tour_traveldesk_approval_email_ids', self.tour_traveldesk_approval_email_ids.ids)
        param.set_param('tour_others_approver', self.tour_others_approver.id)
        param.set_param('tour_finance_users_l1_ids', self.tour_finance_users_l1_ids.ids)
        param.set_param('tour_finance_users_l2_ids', self.tour_finance_users_l2_ids.ids)
        param.set_param('tour_traveldesk_users_l1_ids', self.tour_traveldesk_users_l1_ids.ids)
        param.set_param('tour_traveldesk_users_l2_ids', self.tour_traveldesk_users_l2_ids.ids)

