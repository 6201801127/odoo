from datetime import datetime,date
from odoo.tools.misc import format_date
from odoo import models, fields, api, tools, _

class KwAppraisalPendingReport(models.Model):
    _name           = "kw_appraisal_pending_report"
    _description    = "Appraisal Pending Report"
    _auto           = False

    appraisal_id    = fields.Many2one('hr.appraisal',string='Appraisal Id')
    kw_ids          = fields.Integer(string="kw ids")
    employee_id     = fields.Many2one('hr.employee',string="Employee Name")
    
    designation     = fields.Char(string="Designation",related='employee_id.job_id.name')
    department_id      = fields.Many2one('hr.department',string="Department")
    # division        = fields.Char(string="Division",related='employee_id.division.name')
    # section         = fields.Char(string="Section",related='employee_id.section.name')
    # practice        = fields.Char(string='Practice',related='employee_id.practise.name')
    emp_survey_id   = fields.Many2one('survey.survey',string='Appraisal Form')
    
    state           = fields.Many2one('hr.appraisal.stages', string='Current Stage')
    pending_with    = fields.Many2one('hr.employee',string="Pending With")
    
    self_status     = fields.Char(string="Self Status")
    lm_status       = fields.Char(string="LM Status")
    ulm_status      = fields.Char(string='ULM Status')
    
    # @api.multi
    # def _reviewer(self):
    #     for record in self:
    #         if record.state:
    #             if record.state.sequence == 2:
    #                 record.pending_with = record.employee_id.id
    #             elif record.state.sequence == 3:
    #                 record.pending_with = record.appraisal_id.hr_manager_id.id if record.appraisal_id.hr_manager_id else False
    #             elif record.state.sequence == 4:
    #                 record.pending_with = record.appraisal_id.hr_collaborator_id.id if record.appraisal_id.hr_collaborator_id else False
    #             else:
    #                 record.pending_with = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select ROW_NUMBER () OVER (ORDER BY ha.id) as id,
                ha.id as appraisal_id,
                he.id as employee_id,
                he.department_id as department_id,
                su.id as emp_survey_id,
                ha.kw_ids as kw_ids,
                CASE suis.state
                    WHEN 'new' THEN 'In Progress'
                    WHEN 'skip' THEN 'Draft'
                    WHEN 'done' THEN 'Completed'
                    else 'Not Started'
                END AS self_status,

                CASE suil.state
                    WHEN 'new' THEN 'In Progress'
                    WHEN 'skip' THEN 'Draft'
                    WHEN 'done' THEN 'Completed'
                    else 'Not Started'
                END AS lm_status,

                CASE  
                    WHEN suiu.state='new' THEN 'In Progress'
                    WHEN suiu.state='skip' THEN 'Draft'
                    WHEN suiu.state='done' THEN 'Completed'
                    when ha.hr_collaborator = 'false' or (mgr2.id is not null and mgr3.id is null) then 'Not Required'
                    when suiu.state is null then 'Not Started'
                END AS ulm_status,
             
                ha.state as state,
                case sg.sequence
			when 2 then ha.emp_id
			when 3 then coalesce(mgr1.id,null)
			when 4 then coalesce(mgr2.id,null)
			else null
		end as pending_with
                from hr_appraisal ha
                join hr_employee he on he.id = ha.emp_id and he.active = 'true'
                LEFT JOIN hr_employee mgr1 on mgr1.id = he.parent_id
		LEFT JOIN hr_employee mgr2 on mgr2.id = mgr1.parent_id
		LEFT JOIN hr_employee mgr3 on mgr3.id = mgr2.parent_id
                left outer join survey_user_input suis on suis.id = ha.self_input_id
                left outer join survey_user_input suil on suil.id = ha.lm_input_id
                left outer join survey_user_input suiu on suiu.id = ha.ulm_input_id
                left outer join survey_survey su on su.id = ha.emp_survey_id
                left outer join hr_appraisal_stages sg on sg.id = ha.state
            ORDER BY he.name DESC

        )""" % (self._table))   

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            args += [('kw_ids','=',appraisal_id)]
        
        if self._context.get('filter_previous_period'):

            if len(ids) >= 2:
                appraisal_id = int(ids[1]['id']) if 'id' in ids[1] else 0

            args += [('kw_ids','=',appraisal_id)]

        return super(KwAppraisalPendingReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            domain += [('kw_ids','=',appraisal_id)]
        
        if self._context.get('filter_previous_period'):

            if len(ids) >= 2:
                appraisal_id = int(ids[1]['id']) if 'id' in ids[1] else 0

            domain += [('kw_ids','=',appraisal_id)]

        return super(KwAppraisalPendingReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
