
from openerp import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class ContributionReportWizard(models.Model):
    _name = 'hr.contribution.register.wizard'
    _description = "Contribution Register Report"
    
    
    @api.onchange('date_range')
    def get_dates(self):
        for s in self:
            if s.date_range:
                s.from_date = s.date_range.date_start
                s.to_date = s.date_range.date_end

    date_range = fields.Many2one('date.range', 'Date range')
    from_date = fields.Date(string='From Date', store=True, default=False, required=True)
    to_date = fields.Date(string='To Date', store=True, default=False, required=True)
    registor_id = fields.Many2many('hr.contribution.register',string="Register")
    department_id = fields.Many2many('hr.department',string="Department")
    employee_id = fields.Many2many('hr.employee',string="Employee")
    company_id =fields.Many2one('res.company', string="Company", default=lambda self:self.env.user.company_id.id)
    state = fields.Selection([('draft','Draft'),
                              ('verify','Waiting'),
                              ('done','Done'),
                              ('cancel','Rejected')
                            ],string="state")
    branch_id = fields.Many2many('res.branch',string="Branch")
    model_id = fields.Integer(string="ID",default=lambda self: self.env['ir.model'].search([('model','=','hr.employee')]).id)
    
    @api.multi
    def get_all_data(self):
        res = self.env['contribution.register.report'].search([])
        for r in res:
            print("",r.payslip_id)
        return self.env['contribution.register.report'].search([])
    
   
    @api.multi
    def show_register_summery_report_pdf(self):
        context = self.env.context
        report_id = self.env['ir.actions.report'].with_context(context).search(
            [('report_name', '=', 'register_report_branch.contribution_register_summery_report_template_id')], limit=1)
        if not report_id:
            raise UserError(
                _("Bad Report Reference") + _("This report is not loaded into the database summery: "))
        return {
            'context': context,
            'type': 'ir.actions.report',
            'report_name': report_id.report_name,
            'report_type': report_id.report_type,
            'report_file': report_id.report_file,
            'name': report_id.name,
        }
    
    @api.multi
    def show_register_report_pdf(self):
        context = self.env.context
        report_id = self.env['ir.actions.report'].with_context(context).search(
            [('report_name', '=', 'register_report_branch.contribution_register_report_template_id')], limit=1)
        if not report_id:
            raise UserError(
                _("Bad Report Reference") + _("This report is not loaded into the database:  "))
        return {
            'context': context,
            'type': 'ir.actions.report',
            'report_name': report_id.report_name,
            'report_type': report_id.report_type,
            'report_file': report_id.report_file,
            'name': report_id.name,
        }
    
    @api.multi
    def show_register_report(self):
        
#         print"iiiiiiiii8888888888888888iiiisssssssssssssss", rest
        regi_id=self.env['contribution.register.report']
        r_ids = regi_id.search([])
        r_ids.unlink()
        query= self.get_query()
#         print("????????????????????????????????",query)
        self.env.cr.execute(query)
        res = self.env.cr.dictfetchall()
        for record in res:
            vals = self.get_vals(record)
            rest = regi_id.create(vals)
            
        if self.registor_id:
 
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
                'context':{
                        'search_default_register': True,
                            }
            }
            
        if self.employee_id:
            
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
                'context':{
                        'search_default_employee': True,
                            }
            }
            
        elif self.department_id:
            
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
                'context':{
                        'search_default_department': True,
                            }
            }
            
        elif self.state == 'draft' or self.state == 'verify' or self.state == 'done' or self.state == 'cancel':
            
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
                'context':{
                        'search_default_states': True,
                            }
            }
            
        
        elif self.branch_id:
            
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
                'context':{
                        'search_default_branch': True,
                            }
            }
            
        else:
            
            return {
                'name': 'Register Report[' + str(self.from_date) +' To '+ str(self.to_date) +']',
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'contribution.register.report',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'target': 'current',
            }
        
    @api.multi
    def show_register_report_xlsx(self):
        self.show_register_report()
        # return self.env['report'].get_action(self,report_name="sales_performance.sale_performance_xls_report.xlsx")
        context = self.env.context
        report_id = self.env['ir.actions.report'].with_context(context).search(
            [('report_name', '=', 'register_report_branch.register_report_xls')], limit=1)
#         print("-------------------------report_id", report_id)
        if not report_id:
            raise UserError(_("Bad Report Reference") + _("This report is not loaded into the database: "))

        return {
            'context': context,
            'type': 'ir.actions.report',
            'report_name': report_id.report_name,
            'report_type': report_id.report_type,
            'report_file': report_id.report_file,
            'name': report_id.name,
        }
        
    def get_vals(self, record):
        con_reg_id = self.env['hr.contribution.register'].search([('id','=',record.get('register'))])
#         ir_model_fields = self.env['ir.model.fields'].search([('model_id','=',self.model_id),('state','=','manual')])
        test = ""
        dynamic={}
        data = ""
        for reg in con_reg_id:
            for ir_fields in reg.ir_model_fields:
#             test += ir_fields.name 
                if ir_fields.name:
                    val = record.get(ir_fields.name)
#                     print("val====",val)
                    if val:
#                         print("=====str(val)",str(val),"===ir_fields.field_description",ir_fields.field_description)
                        test += str(val) + '\n'
                        data += ir_fields.field_description + '\n'
       
        vals = {
            "employee_id": record.get('employee'),
            "pay_from_date": record.get('f_date'),
            "pay_to_date": record.get('t_date'),
            "dep_id": record.get('department'),
            "manager_id":record.get('manager'),
            "contib_regi": record.get('register'),
            "job_position": record.get('job'),
            "contract_id": record.get('contract'),
            "branch_id": record.get('branch'),
            "wage": record.get('wage'),
            "amt": record.get('amount'),
            "rate": record.get('rate'),
            "total": record.get('total'),
            "payslip_name": record.get('name'),
            "payslip_id":record.get('payslip'),
            "state":record.get('state'),
            "register_name":test,
            "register_info":data
        }
        
        return  vals
        
        
    
    def get_query(self):
        from_date = fields.Date.from_string(self.from_date)
        to_date = fields.Date.from_string(self.to_date)
        ir_model_fields = self.env['ir.model.fields'].search([('model_id','=',self.model_id),('state','=','manual')])
        test = ""
        for ir_fields in ir_model_fields:
            test += " ,emp. "+ir_fields.name+ " as  "+ir_fields.name+" "
        
        print("====test",test)
        query="""
            select emp.id as employee,
                    hp.id as payslip,
                    hp.state as state,
                    hp.date_from as f_date,
                    hp.date_to as t_date,
                    hp.name as name,
                    emp.department_id as department,
                    emp.parent_id as manager,
                    hpl.register_id as register,
                    emp.job_id as job,
                    hp.contract_id as contract,
                    hp.branch_id as branch,
                    contract.wage as wage,
                    sum(hpl.amount) as amount,
                    sum(hpl.rate) as rate,
                    sum(hpl.total) as total """
                    
        query += test
        
        print("=======query",query)
        
        query += """
            from hr_payslip_line as hpl
            inner join hr_payslip as hp on hpl.slip_id = hp.id
            inner join hr_contribution_register as hcr on hpl.register_id = hcr.id
            inner join hr_employee as emp on hp.employee_id = emp.id
            inner join hr_contract as contract on hp.contract_id = contract.id
            left outer join hr_department as dept on emp.department_id = dept.id
            left outer join hr_employee as manager on emp.parent_id = manager.id
            left outer join hr_job as job on emp.job_id = job.id
            where
                hp.state in ('done') and
                hp.date_from BETWEEN '{}'""".format(from_date)+""" AND '{}'""".format(to_date)+""" and
                hp.date_to BETWEEN '{}'""".format(from_date)+""" AND '{}'""".format(to_date)+"""

                """
        if self.employee_id:
            employee_id = [t for t in self.employee_id.ids]
            if len(employee_id)==1:
                query += " and emp.id = {} ".format((employee_id[0]))
            else:
                query +=" and emp.id in {} ".format(tuple(employee_id))
        
        
        if self.department_id:
            department_id = [t for t in self.department_id.ids]
            if len(department_id)==1:
                query += " and emp.department_id = {} ".format((department_id[0]))
            else:
                query +=" and emp.department_id in {} ".format(tuple(department_id))

        if self.registor_id:
            registor_id = [t for t in self.registor_id.ids]
            if len(registor_id)==1:
                query += " and hpl.register_id = {} ".format((registor_id[0]))
            else:
                query +=" and hpl.register_id in {} ".format(tuple(registor_id))
                
        if self.branch_id:
            branch_id = [t for t in self.branch_id.ids]
            if len(branch_id)==1:
                query += " and hp.branch_id = {} ".format((branch_id[0]))
            else:
                query +=" and hp.branch_id in {} ".format(tuple(branch_id))
       
        if self.state == 'draft':
            query += "and hp.state ='draft'"
            
        if self.state == 'verify':
            query += "and hp.state ='verify'"   
            
        if self.state == 'done':
            query += "and hp.state = 'done'"
            
        if self.state == 'cancel':
            query += "and hp.state = 'cancel'"
        

        query +=""" group by
                emp.id,
                hp.id,
                hp.state,
                emp.department_id,
                emp.job_id,
                emp.parent_id,
                hp.contract_id,
                hpl.register_id,
                hp.date_from,
                hp.date_to,
                hp.name,
                hp.branch_id,
                contract.wage,
                hpl.amount,
                hpl.rate,
                hpl.total
              """
        return query

