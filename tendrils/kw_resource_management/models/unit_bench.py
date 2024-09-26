# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from datetime import date,datetime


class UnitBenchResource(models.Model):
    _name = 'unit_bench_resource'
    _description = 'unit Bench Resource'
    _auto = False
    _order = "employee_id"

    @api.depends('grade', 'band')
    def _compute_grade_band(self):
        for rec in self:
            if rec.band and rec.grade:
                rec.grade_band = rec.grade.name + ',' + ' ' + rec.band.name

    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    sbu_type = fields.Selection(string='Resource Type', selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name = fields.Char(related='sbu_id.name', string='SBU')
    department_id = fields.Many2one('hr.department', string='Department')
    resource_id = fields.One2many('project.project', 'emp_id')
    days_in_bench = fields.Date("Released On")
    interval_day = fields.Integer("Days in Bench")
    suggestion = fields.Char('Remarks', help="Inventory on hand")
    grade = fields.Many2one('kwemp_grade_master', string="Employee Grade")
    band = fields.Many2one('kwemp_band_master', string="Employee Band")
    grade_band = fields.Char("Grade/Band", compute='_compute_grade_band')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT row_number() over() as id,
            hr.id as employee_id,
            hr.job_id as designation,
            hr.name as name,
            hr.grade as grade,
			hr.emp_band as band,
            hr.date_of_joining as date_of_joining,
            hr.emp_role as emp_role,
            hr.emp_category as emp_category,
            hr.employement_type as employement_type,
            hr.job_branch_id as job_branch_id,
            hr.sbu_master_id as sbu_id,
            hr.sbu_type as sbu_type,
            hr.department_id as department_id,

            case when hr.id not in (select emp_id from kw_project_resource_tagging where active = false and hr.id = emp_id) 
                then hr.date_of_joining 
                else date((select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id)) 
            end as days_in_bench,

            case 
			  when hr.id not in (select emp_id from kw_project_resource_tagging where active = false and hr.id = emp_id) and hr.id  in (select tlog.employee_id from sbu_tag_untag_log tlog where tlog.status='tag' 
					and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id))
                 then (select current_date) - (select max(tlog.date) from sbu_tag_untag_log tlog 
			 where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id))
					   
             when hr.id  in (select emp_id from kw_project_resource_tagging where active = false and hr.id = emp_id) and 
					hr.id  not in (select tlog.employee_id from sbu_tag_untag_log tlog where tlog.status='tag' 
					and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id))
				then (select date_part('day'::text, now() - (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id)))
			when (select max(tlog.date) from sbu_tag_untag_log tlog 
			where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)) >=
				  (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id) 
				then (select current_date) - (select max(tlog.date) from sbu_tag_untag_log tlog 
		  	where  tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id) )
				
			when (select max(tlog.date) from sbu_tag_untag_log tlog 
			where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)) < 
			  (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id)
				  then (select date_part('day'::text, now() - (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id)))
				else (select date_part('day'::text, now() - hr.date_of_joining))
            end as interval_day,

            case when hr.id not in (select emp_id from kw_project_resource_tagging where active = false and hr.id = emp_id) and hr.id in (select tlog.employee_id from sbu_tag_untag_log tlog where tlog.status='tag' 
					and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id))
                then concat('Joined in ',(select name from kw_sbu_master where id=hr.sbu_master_id),' w.e.f ', to_char((select max(tlog.date) from sbu_tag_untag_log tlog 
			 	where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)), 'DD-Mon-YYYY'))
                when hr.id  in (select emp_id from kw_project_resource_tagging where active = false and hr.id = emp_id) and 
					hr.id  not in (select tlog.employee_id from sbu_tag_untag_log tlog where tlog.status='tag' 
					and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id))
                		then concat('Released from ', 
                		(select name from project_project p where id = (select project_id from kw_project_resource_tagging where active = false and hr.id = emp_id order by write_date desc limit 1)), 
               		 ' ', 'on', ' ', 
                		to_char((select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id), 'DD-Mon-YYYY'))
				when (select max(tlog.date) from sbu_tag_untag_log tlog 
			 	where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)) >=
					  (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id) then concat('Joined in ',(select name from kw_sbu_master where id=hr.sbu_master_id),' w.e.f ', to_char((select max(tlog.date) from sbu_tag_untag_log tlog 
			 	where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)), 'DD-Mon-YYYY'))
				when (select max(tlog.date) from sbu_tag_untag_log tlog 
			 	where tlog.status='tag' and hr.id = tlog.employee_id and tlog.sbu_id = (select sbu.name from kw_sbu_master sbu where sbu.id = hr.sbu_master_id)) < 
					  (select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id)
                then concat('Released from ', 
                (select name from project_project p where id = (select project_id from kw_project_resource_tagging where active = false and hr.id = emp_id order by write_date desc limit 1)), 
                ' ', 'on', ' ', 
                to_char((select max(write_date) from kw_project_resource_tagging where active = false and hr.id = emp_id), 'DD-Mon-YYYY')) 
				else
				concat('Joined in ',(select name from kw_sbu_master where id=hr.sbu_master_id),' w.e.f ', hr.date_of_joining)
            end as suggestion
            
        FROM hr_employee as hr 
        JOIN hr_department as hrd on hrd.id = hr.department_id
        WHERE hr.active = true 
        AND hrd.code = 'BSS' 
		AND hr.emp_role in (select id from kwmaster_role_name erole where erole.code in ('DL','R','S'))
        AND hr.emp_category in (select id from kwmaster_category_name where code in ('TTL','DEV','PM','BA','IFS','SS','SMS')) 
        AND hr.id not in (select pt.emp_id from kw_project_resource_tagging pt join project_project p on pt.project_id = p.id where pt.active = true and p.active = true )
        AND hr.sbu_master_id is not null 
        AND hr.sbu_type = 'sbu' 
        AND hr.employement_type not in (select id from kwemp_employment_type where code = 'O')
         )""" % (self._table))
        
    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search([('state','not in',['reject','cancel']),('applicant_id','=',rec.employee_id.id)],limit=1)
            rec.applied_eos = True if resignation else False
        
    def action_button_release(self):
        view_id = self.env.ref('kw_resource_management.resource_release_remark_wizard_view_form').id
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'resource_release_remark_wizard',
            'view_id': view_id,
            'context': {'current_id': self.id, 'employee_id': self.employee_id.id},
            'target': 'new',
        }
        # for rec in self:
            # rec.employee_id.sbu_master_id = False
            # rec.employee_id.sbu_type = False

    def unit_to_central_bench(self):
        unit_rec = self.env['unit_bench_resource'].sudo().search([])
        if unit_rec:
            filtered_rec = unit_rec.filtered(lambda x: x.interval_day > 7)
            query = ''
            for emp_rec in filtered_rec:
                old_sbu_id = emp_rec.sbu_id.id
                old_sbu_name = emp_rec.sbu_id.name

                if emp_rec and emp_rec.employee_id.id > 0:
                    query += f"UPDATE hr_employee SET sbu_master_id=NULL, sbu_type=NULL WHERE id={emp_rec.employee_id.id};"

                    # emp_rec.employee_id.write({
                    #     'sbu_master_id':False,
                    #     'sbu_type':False
                    # })
                    self.env['kw_resource_release_log'].sudo().create({
                        'reason':f'Auto released from unit bench ({old_sbu_name})',
                        'release_emp_id':emp_rec.employee_id.id,
                        'release_from':old_sbu_id
                    })
                    record_log = self.env['kw_emp_sync_log'].sudo().search([('model_id', '=', 'hr.employee'),('rec_id','=',emp_rec.employee_id.id),('code','=',1),('status','=',0)])
                    if not record_log.exists():
                        record_log.create( {'model_id': 'hr.employee', 'rec_id': emp_rec.employee_id.id, 'code': 1, 'status': 0})
                    else:
                        pass
            if query != '':
                self._cr.execute(query)
                

        current_date=date.today()
        central_bench_rec=self.env['sbu_bench_resource'].sudo().search([])
        history_data = self.env['central_bench_report_history'].sudo().search([('closed_bool','=', False)])
        bench_list = central_bench_rec.mapped('employee_id.id')
        filtered_history = history_data.filtered(lambda x : x.employee_id.id not in bench_list and x.closed_bool == False)
        if filtered_history :
            update_history = filtered_history.write({'closed_bool': True,'date_to': current_date})
        query1 = ""
        for data in central_bench_rec:
            filtered_data = history_data.filtered(lambda x : x.employee_id.id == data.employee_id.id)
            if filtered_data:
                query1 += f"UPDATE central_bench_report_history SET date_to='{current_date}' WHERE id={filtered_data.id};"
            else:
                query1 += f"insert into central_bench_report_history(employee_id,date_from,date_to,closed_bool) values({data.employee_id.id},'{current_date}','{current_date}',{False});"

        # print(query1)
        self._cr.execute(query1)
                   