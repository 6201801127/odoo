from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class BugCycleReport(models.Model):
    _name = 'life_cycle_bug_report'
    _description = 'Bug life cycle  Report'
    _auto = False

    date = fields.Datetime(string="Open Date", default=fields.Datetime.now)
    number = fields.Char(string='Defect ID')
    employee_id = fields.Many2one('hr.employee',string="Logged By")
    project_id = fields.Many2one('project.project', required=True)
    module_id = fields.Many2one('bug_module_master','Module')
    sub_module_name_id = fields.Many2one('bug_sub_module_master','Sub Module Name')
    priority_id = fields.Many2one('priority_master','Priority')
    severity = fields.Many2one('severity_master','Severity') 
    description = fields.Text('Description')
    assigned_by = fields.Many2one('hr.employee', 'Last Action By')
    developer_id = fields.Many2one('hr.employee', string="Pending At")
    state = fields.Selection(string="State",
                             selection=[('Draft', 'Draft'),
                                        ('New', 'New/Reopen'),
                                        ('Progressive', 'Progressive'),
                                        ('Hold', 'Hold'),
                                        ('Done', 'Fixed & Deployed In Test Server'),
                                        ('Rejected', 'Rejected'),
                                        ('Closed', 'Closed')
                                        ])
    # screen_id = fields.Many2one("screen_master", 'Navigation')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    select row_number() over() as id,
                    a.open_date as date,
                    a.number as number,
                    a.employee_id as employee_id,
                    a.project_id as project_id,
                    a.module_id as module_id,
                    a.sub_module_name_id as sub_module_name_id,
                    a.priority_id as priority_id,
                    a.severity as severity,
                    a.description as description,
                    a.assigned_by as assigned_by,
                    a.developer_id as developer_id,
                    a.state as state
                    from kw_raise_defect as a
                    join defect_create_table as b on b.raise_defect_id = a.id
                    where a.state != 'Draft'
        )"""
        self.env.cr.execute(query)


    @api.multi    
    def bug_view_details_action_button(self):
        for rec in self:
            form_view_id = self.env.ref("kw_bug_life_cycle.kw_raise_form").id
            defect_rec = self.env['kw_raise_defect'].sudo().search([('number', '=', rec.number),
                                                                    ('state', '=',rec.state )]).id
            return  {
                'name': 'Form View',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_raise_defect',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': defect_rec,
                'target': 'self',
                'view_id':form_view_id,
                'context': {'edit': False, 'create': False, 'delete': False},

            }



    