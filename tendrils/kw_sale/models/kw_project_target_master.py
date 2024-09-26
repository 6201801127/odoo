# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime


class TargetMaster(models.Model):
    _name = 'kw_sale_target_master'
    _description = 'Sales Target'
    _order = 'id desc'

    fiscal_year = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    team_id = fields.Many2one('crm.team', string='Team')
    member_id = fields.Many2one('res.partner', string='Member')
    company_id = fields.Many2one('res.company', string='Company')
    type = fields.Selection([('team','Team'),('ind','individual'),('company','Company')], string='Type', default='ind')
    jan_planned = fields.Char('Jan Planned')
    jan_actual = fields.Char('Jan Actual')
    feb_planned = fields.Char('Feb Planned')
    feb_actual = fields.Char('Feb Actual')
    mar_planned = fields.Char('Mar Planned')
    mar_actual = fields.Char('Mar Actual')
    apr_planned = fields.Char('Apr Planned')
    apr_actual = fields.Char('Apr Actual')
    may_planned = fields.Char('May Planned')
    may_actual = fields.Char('May Actual')
    jun_planned = fields.Char('Jun Planned')
    jun_actual = fields.Char('Jun Actual')
    jul_planned = fields.Char('Jul Planned')
    jul_actual = fields.Char('Jul Actual')
    aug_planned = fields.Char('Aug Planned')
    aug_actual = fields.Char('Aug Actual')
    sep_planned = fields.Char('Sep Planned')
    sep_actual = fields.Char('Sep Actual')
    octo_planned = fields.Char('Oct Planned')
    octo_actual = fields.Char('Oct Actual')
    nov_planned = fields.Char('Nov Planned')
    nov_actual = fields.Char('Nov Actual')
    dec_actual = fields.Char('Dec Planned')
    dec_planned = fields.Char('Dec Actual')
    state = fields.Selection([('draft','Draft'),('freeze','Freeze')], string='Status')
    target_type = fields.Selection([('bill','Billing'),('work','Work Order'),('collect','Collection')], string='Target Type')
    total_planned = fields.Char(string='Total[Planned]')
    total_actual = fields.Char(string='Total[Actual]')

    @api.model
    def fetch_team_member(self, **kwargs):
        datalist = []
        team = self.env['crm.team'].browse(int(kwargs.get('team_id')))
        if team and team.member_ids:
            datalist.append({'id': team.user_id.id, 'name':team.user_id.name})
            for rec in team.member_ids:
                datalist.append({"id": rec.id, "name": rec.name})
        datalist1 = list({myObject['id']:myObject for myObject in datalist}.values())
        return datalist1

    @api.model
    def fetch_team(self, **kwargs):
        datalist = []
        team = self.env['crm.team'].search([])
        if team:
            for rec in team:
                datalist.append({"id": rec.id, "name": rec.name})
        return datalist

    @api.model
    def get_fy_data(self, **kwargs):
        datalist = []
        fy = self.env['account.fiscalyear'].search([])
        if fy:
            for rec in fy:
                default_fy = True if rec.date_start < datetime.date.today() < rec.date_stop else False
                datalist.append({"id": rec.id, "name": rec.name, 'default_fy': default_fy})
        return datalist

    @api.model
    def save_company_target(self, **kwargs):
        import pdb
        pdb.set_trace()
        datalist = []
        values = {}
        if kwargs.get('fiscal_year'):
            values['fiscal_year'] = kwargs.get('fiscal_year')
        if kwargs.get('rec') != []:
            for x in kwargs.get('rec'):
                if x.get('name')[4] == 'work':
                    values['target_type'] = 'work'
                    if x.get('name')[:-3] == 'apr':values['apr_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'may':values['may_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jun':values['jun_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jul':values['jul_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'aug':values['aug_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'sep':values['sep_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'oct':values['oct_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'nov':values['nov_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'dec':values['dec_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jan':values['jan_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'feb':values['feb_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'mar':values['mar_actual'] = x.get('value')
                    if x.get('name')[:-5] == 'total':values['total_actual'] = x.get('value')
                if x.get('name')[4] == 'bill':
                    if x.get('name')[:-3] == 'apr':values['apr_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'may':values['may_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jun':values['jun_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jul':values['jul_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'aug':values['aug_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'sep':values['sep_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'oct':values['oct_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'nov':values['nov_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'dec':values['dec_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'jan':values['jan_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'feb':values['feb_actual'] = x.get('value')
                    if x.get('name')[:-3] == 'mar':values['mar_actual'] = x.get('value')
                    if x.get('name')[:-5] == 'total':values['total_actual'] = x.get('value')
        return True
