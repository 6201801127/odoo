from odoo import models, fields, api
from odoo import tools
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.http import request

class CapabilityReport(models.Model):
    _name = "capability_report"
    _description = "Capability Report "
    _auto = False

    
    employee_id = fields.Many2one('hr.employee', string="Name Of The Employee")
    primary_skill_id = fields.Many2one('kw_skill_master', string="Primary")
    secondary_skill_id = fields.Many2one('kw_skill_master', string="Secondary")
    tertiarry_skill_id = fields.Many2one('kw_skill_master', string="Tertiary")
    self_primary_skill_id_score = fields.Float(string="Self Score")
    self_secondary_skill_id_score = fields.Float(string="Self Score")
    self_tertial_skill_id_score = fields.Float(string="Self Score")
    ra_primary_skill_id_score = fields.Float(string="RA Score")
    ra_secondary_skill_id_score = fields.Float(string="RA Score")
    ra_tertial_skill_id_score = fields.Float(string="RA Score")
    lnk_primary_skill_id_score = fields.Float(string="L&K Score")
    lnk_secondary_skill_id_score = fields.Float(string="L&K Score")
    lnk_tertial_skill_id_score = fields.Float(string="L&K Score")
    state = fields.Selection(string="Status", selection=[('1', 'Draft'), ('2', 'Submitted'), ('3', 'Ra Approved'), ('4', 'L & K Approved')])
    date = fields.Date()
    # current_quarter_bool = fields.Boolean()
    fiscal_year = fields.Many2one('account.fiscalyear', "Financial Year", required=True)
    current_quater = fields.Selection(string="Quarter",selection=[(1, 'First Quarter'),(2, 'Second Quarter'),(3, 'Third Quarter'),(4, 'Fourth Quarter')],required=True)

    avg_primary_skill_id_score = fields.Float(string="Avg Primary" , compute='_compute_avg_primary_score')
    avg_secondary_skill_id_score = fields.Float(string="Avg Secondary" , compute='_compute_avg_secondary_score')
    avg_tertial_skill_id_score = fields.Float(string="Avg Tertiary" , compute='_compute_avg_tertial_score')

    total_avg_score = fields.Float(string="Total Avg" , compute='_compute_avg_total_score')
    parent_id = fields.Many2one('hr.employee')
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        fiscal_year = self.env.context.get('fiscal_year') 
        current_quater = self.env.context.get('current_quater')
        query = f"""CREATE OR REPLACE VIEW {self._table} AS (
            WITH emp_data AS (
                    select h.id,r.primary_skill_id,h.parent_id,
                    r.secondary_skill_id,r.tertial_skill_id 
                    from hr_employee h 
                    left join resource_skill_data r on h.id = r.employee_id 
                    where 
                    department_id in (select id from hr_department where code='BSS')
                    AND h.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                    AND active = true
                        ),
		    skill_data as (
						select
						s.employee_id,
						s.self_primary_skill_id_score,
						s.ra_primary_skill_id_score,
						s.lnk_primary_skill_id_score,
						s.self_secondary_skill_id_score,
						s.ra_secondary_skill_id_score,
						s.lnk_secondary_skill_id_score,
						s.self_tertial_skill_id_score,
						s.ra_tertial_skill_id_score,
						s.lnk_tertial_skill_id_score,
						s.date_ ,
						s.default_fiscal_year,
						s.fiscal_quarter,
						s.state AS state
						from kw_skill_sheet s 
						where  
                        s.state !='1'
						AND
						s.default_fiscal_year = {fiscal_year.id if fiscal_year else 0}
						AND 
						s.fiscal_quarter = {current_quater if current_quater else 0}
						)
            SELECT row_number() over() as id,
					emp.id AS employee_id,
                    emp.parent_id AS parent_id,
					emp.primary_skill_id AS primary_skill_id,
					s.self_primary_skill_id_score AS self_primary_skill_id_score,
					s.ra_primary_skill_id_score AS ra_primary_skill_id_score,
					s.lnk_primary_skill_id_score AS lnk_primary_skill_id_score,
					emp.secondary_skill_id AS secondary_skill_id,
					s.self_secondary_skill_id_score AS self_secondary_skill_id_score,
					s.ra_secondary_skill_id_score AS ra_secondary_skill_id_score,
					s.lnk_secondary_skill_id_score AS lnk_secondary_skill_id_score,
					emp.tertial_skill_id AS tertiarry_skill_id,
					s.self_tertial_skill_id_score AS self_tertial_skill_id_score,
					s.ra_tertial_skill_id_score AS ra_tertial_skill_id_score,
					s.lnk_tertial_skill_id_score AS lnk_tertial_skill_id_score,
					s.date_ AS date,
					s.default_fiscal_year AS fiscal_year,
					s.fiscal_quarter AS current_quater,
					s.state AS state
					from emp_data emp 
					left join skill_data s on emp.id = s.employee_id
        )"""
        self.env.cr.execute(query)


    @api.depends('self_primary_skill_id_score', 'ra_primary_skill_id_score', 'lnk_primary_skill_id_score')
    def _compute_avg_primary_score(self):
        for record in self:
            scores = [record.self_primary_skill_id_score,record.ra_primary_skill_id_score,record.lnk_primary_skill_id_score,]
            non_zero_scores = [score for score in scores if score > 0]

            if len(non_zero_scores) == 3:
                record.avg_primary_skill_id_score = sum(scores) / 3
            elif len(non_zero_scores) == 2:
                record.avg_primary_skill_id_score = sum(non_zero_scores) / 2
            elif len(non_zero_scores) == 1:
                record.avg_primary_skill_id_score = non_zero_scores[0]
            else:
                record.avg_primary_skill_id_score = 0

    @api.depends('self_secondary_skill_id_score', 'ra_secondary_skill_id_score', 'lnk_secondary_skill_id_score')
    def _compute_avg_secondary_score(self):
        for record in self:
            scores = [record.self_secondary_skill_id_score,record.ra_secondary_skill_id_score,record.lnk_secondary_skill_id_score,]
            non_zero_scores = [score for score in scores if score > 0]

            if len(non_zero_scores) == 3:
                record.avg_secondary_skill_id_score = sum(scores) / 3
            elif len(non_zero_scores) == 2:
                record.avg_secondary_skill_id_score = sum(non_zero_scores) / 2
            elif len(non_zero_scores) == 1:
                record.avg_secondary_skill_id_score = non_zero_scores[0]
            else:
                record.avg_secondary_skill_id_score = 0

    @api.depends('self_tertial_skill_id_score', 'ra_tertial_skill_id_score', 'lnk_tertial_skill_id_score')
    def _compute_avg_tertial_score(self):
        for record in self:
            scores = [record.self_tertial_skill_id_score,record.ra_tertial_skill_id_score,record.lnk_tertial_skill_id_score,]
            non_zero_scores = [score for score in scores if score > 0]

            if len(non_zero_scores) == 3:
                record.avg_tertial_skill_id_score = sum(scores) / 3
            elif len(non_zero_scores) == 2:
                record.avg_tertial_skill_id_score = sum(non_zero_scores) / 2
            elif len(non_zero_scores) == 1:
                record.avg_tertial_skill_id_score = non_zero_scores[0]
            else:
                record.avg_tertial_skill_id_score = 0

    @api.depends('avg_primary_skill_id_score', 'avg_secondary_skill_id_score', 'avg_tertial_skill_id_score')
    def _compute_avg_total_score(self):
        for record in self:
            scores = [record.avg_primary_skill_id_score,record.avg_secondary_skill_id_score,record.avg_tertial_skill_id_score,]
            non_zero_scores = [score for score in scores if score > 0.0]

            if len(non_zero_scores) == 3:
                record.total_avg_score = sum(scores) / 3
            elif len(non_zero_scores) == 2:
                record.total_avg_score = sum(non_zero_scores) / 2
            elif len(non_zero_scores) == 1:
                record.total_avg_score = non_zero_scores[0]
            else:
                record.total_avg_score = 0.0



class CapabilityFilterReportWizard(models.TransientModel):
    _name = 'capability_filterd_report'
    _description = "Skill Sheet Filter Report Wizard"

    fis_year = fields.Many2one('account.fiscalyear', "Financial Year", required=True)
    fiscal_quarter = fields.Selection(string="Quarter",selection=[(1, 'First Quarter'),(2, 'Second Quarter'),(3, 'Third Quarter'),(4, 'Fourth Quarter')],required=True)

    @api.multi
    def capability_report_filter(self):
        self.env['capability_report'].with_context(fiscal_year= self.fis_year,current_quater= self.fiscal_quarter).init()
        tree_view_id = self.env.ref('kw_resource_management.capability_report_report_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': f'Capability Report  : Quater- {self.fiscal_quarter} Of {self.fis_year.name}',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'capability_report',
            'target': 'main',
            'context': {'fiscal_year': self.fis_year.id,'current_quater' : self.fiscal_quarter}
        }
        return action
    
class AvgCapabilityFilterReportWizard(models.TransientModel):
    _name = 'avg_capability_filterd_report'
    _description = "Avg Skill Sheet Filter Report Wizard"

    fis_year = fields.Many2one('account.fiscalyear', "Financial Year", required=True)
    fiscal_quarter = fields.Selection(string="Quarter",selection=[(1, 'First Quarter'),(2, 'Second Quarter'),(3, 'Third Quarter'),(4, 'Fourth Quarter')],required=True)

    @api.multi
    def avg_capability_report_filter(self):
        self.env['capability_report'].with_context(fiscal_year= self.fis_year,current_quater= self.fiscal_quarter).init()
        tree_view_id = self.env.ref('kw_resource_management.average_capability_report_report_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': f'Average Capability Report  : Quater- {self.fiscal_quarter} Of {self.fis_year.name}',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'capability_report',
            'target': 'main',
            'context': {'fiscal_year': self.fis_year.id,'current_quater' : self.fiscal_quarter}
        }
        return action


