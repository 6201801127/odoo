from datetime import datetime,date
from odoo.tools.misc import format_date
from odoo import models, fields, api, tools, _

class KwAppraisalAllData(models.Model):
    _name           = "appraisal_all_perod_data"
    _description    = "Appraisal All Period Data"
    _auto           = False

    appraisal_year = fields.Char(string="Appraisal Period")
    appr_id = fields.Many2one('hr.appraisal')
    emp_id = fields.Many2one('hr.employee', string="Employee", required=True)
    e_name = fields.Char(string='Employee Name',related='emp_id.name')
    employee_ra = fields.Many2one('hr.employee',)
    e_code = fields.Char(string="Employee Code", related="emp_id.emp_code")
    deg_id = fields.Many2one('hr.job',string='Designation')
    dept_id = fields.Many2one('hr.department',string='Department')
    division = fields.Many2one('hr.department',string='Division')
    section = fields.Many2one('hr.department',string='Practice')
    practice = fields.Many2one('hr.department',string='Section')
    state = fields.Many2one('hr.appraisal.stages', string='Current Stage', track_visibility='onchange')
    score = fields.Float(string="Appraisal Score",  
                         help='Score will visible after publish your appraisal')
    kra_score = fields.Float(string="KRA Score", help='KRA Score will visible after publish your appraisal')
    total_final_score = fields.Float(string="Total Score")
    employee_ctc = fields.Float(string="CTC")
    new_designation = fields.Many2one('hr.job',string='New Designation')
    increment_percentage = fields.Float(string="Increment(%)",compute="get_increment_amount",store=False)
    final_increment = fields.Float(string="Final Increment")
    final_ctc = fields.Float(string="Final CTC")

    
    
    
    @api.multi
    @api.depends('score','kra_score')
    def get_increment_amount(self):
        for record in self:
            appraisal_final_score = (record.score * 60)/100
            kra_final_score = (record.kra_score * 40)/100
            total_final_score = appraisal_final_score + kra_final_score
            record.increment_percentage = (total_final_score * 20)/100

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
        select row_number() over() as id, appraisal_year as appraisal_year,
        a.id as appr_id,
        a.emp_id as emp_id,
        b.job_id as deg_id,
        b.department_id as dept_id,
        b.parent_id as employee_ra,
        b.division as division,
        b.section as section,
        b.practise as practice,
        a.state as state,
        a.score as score,
        a.kra_score as kra_score,
        c.wage as employee_ctc,
	    ((a.score * 60)/100) + ((a.kra_score * 40)/100) as total_final_score,
        a.new_designation as new_designation,
        a.final_increment as final_increment,
        c.wage+a.final_increment as final_ctc
        from hr_appraisal a left join hr_employee b on a.emp_id = b.id left join hr_contract c on c.employee_id = b.id 
                )""" % (self._table))
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print("no_filter",args)
        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            # print(appraisal_id)
            args += [('appr_id.kw_ids','=',appraisal_id)]
            # print(args)

        return super(KwAppraisalAllData, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0
                # print("read_group",self.appr_id.kw_ids)
            domain += [('appr_id.kw_ids','=',appraisal_id)]
        
        return super(KwAppraisalAllData, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

