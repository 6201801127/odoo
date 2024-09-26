# -*- coding: utf-8 -*-

import requests, json, base64
import mimetypes
from urllib.request import urlopen
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo import http


class kw_project_crm_inherit(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one('crm.lead', string='Product Name', )
    category_id = fields.Many2one('kw_lead_category_master', string='Sub Product Name')

    client_name = fields.Char(string='Client Name', )
    type_of_lead = fields.Char(string='Type of Lead', )
    name_of_lead = fields.Char(string='Name of Lead', )
    financial_evaluation = fields.Char(string='Financial Evaluation', )
    tender_number = fields.Char(string='Tender Number', )
    tender_date = fields.Date(string='Tender Date', )
    pre_bid_date = fields.Date(string='Pre-Bid Date & Time', )
    submission_date = fields.Date(string='Submission Date & Time', )
    gen_bid_opening_date = fields.Date(string='Gen Bid Opening Date & Time', )
    tech_bid_date = fields.Date(string='Tech Bid Opening Date & time', )
    financial_opening_date = fields.Date(string='Financial Opening Date & Time', )
    document_type = fields.Binary(string='Upload Doc')
    competitor_id = fields.Many2one('res.partner', string="Competitor", domain=[('competitor', '=', True)])
    state = fields.Selection(string='Status', selection=[('Draft', 'Draft'),
                                                         ('PAC Applied', 'PAC Applied'),
                                                         ('Hold', 'Hold'),
                                                         ('PAC Approved', 'PAC Approved'),
                                                         ('Rejected', 'Rejected')],
                             default='Draft')
    
    



    @api.onchange('project_id')
    def _filter_category(self):
        self.category_id = False

    def apply_pac_button(self):
        self.write({'state': 'PAC Applied'})

    def approve_pac_button(self):
        self.write({'state': 'PAC Approved'})

    def reject_pac_button(self):
        self.write({'state': 'Rejected'})

    def withdraw_pac_button(self):
        self.write({'state': 'Draft'})

    def hold_pac_button(self):
        self.write({'state': 'Hold'})
