# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID


class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    def issue_count(self):
        task_obj = self.env['project.task']
        self.issue_number = task_obj.search_count([('lead_id', 'in', [a.id for a in self])])

    issue_number = fields.Integer(compute='issue_count', string='Tasks')

class crm_issue_wizard(models.TransientModel):
    _name = 'crm.issue.wizard'
    
    
    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        name = crm_brw.name
        return name
    
    
    project_id = fields.Many2one('project.project','Project', tracking=True)
    name = fields.Char('Task Name',default = get_name, tracking=True)
    user_id = fields.Many2one('res.users','Assigned To',default=lambda self: self.env.uid,
        index=True, track_visibility='always', tracking=True)

    def create_issue(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        vals = {'name': self.name,
                'project_id':self.project_id.id or False,
                'user_id': self.user_id.id or False,
                'partner_id': crm_brw.partner_id.id or False,
                'lead_id':crm_brw.id or False
                }
        self.env['project.task'].create(vals)
        
        
class project_issue(models.Model):
    _inherit='project.task'
    
    lead_id =  fields.Many2one('crm.lead', 'Opportunity', tracking=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
