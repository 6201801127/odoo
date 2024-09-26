
from datetime import date,datetime
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

emp_stages = [
                
              ('test_period', 'Probation'),
              ('contract', 'Contract'),
              ('deputation', 'Deputation'),
              ('employment', 'Regular'),
              ('notice_period', 'Notice Period'),
              ('relieved', 'Resigned'),
              ('terminate', 'Terminated'),
              ('retired','Retired'),
              ('suspended','Suspended'),
              ('superannuation','Superannuation'),
              ('deceased','Deceased'),
              ('absconding','Absconding'),
              ]


class EmployeeFormInherit(models.Model):
    _inherit = 'hr.employee'
    employment_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_bsscl', 'Contractual with BSSCL')], string='Stage', store=True)
    # validate_details = fields.Boolean("Validate Employee Details",compute='_compute_validate_emp_details',default=True)

    # @api.multi
    # def _compute_validate_emp_details(self):
    #     for record in self:
    #         if 'hide_personal' not in self._context and (self.env.user.has_group('hr.group_hr_manager') or record.user_id == self.env.user):
    #             record.validate_details = True
    #         else:
    #             record.validate_details = False
   

    # @api.model
    # def create(self, vals):
    #     stage_config = self.env['employee.stage.configuration'].sudo()
    #     result = super(EmployeeFormInherit, self).create(vals)
    #     stage_record = []
    #     stage_history_ids = []
    #     if result.employee_type:
    #         if result.employee_type == 'regular':
    #             stage_record = stage_config.search([('employee_type','=','regular'),('recruitment_type','=',result.recruitment_type),('existing_state','=',result.state)])
    #         elif result.employee_type == 'contractual_with_agency':
    #             stage_record = stage_config.search([('employee_type','=','contractual_with_3rd_party'),('existing_state','=','contract')])
    #         elif result.employee_type == 'contractual_with_stpi':
    #             stage_record = stage_config.search([('employee_type','=','contractual'),('existing_state','=','contract')])

    #         if stage_record:
    #             for stages in stage_record:
    #                 add_stages = {}
    #                 add_stages.update({
    #                     'designation_id':result.job_id.id if result.job_id else False,
    #                     'file_no':result.recruitment_file_no if result.recruitment_file_no else False,
    #                     'order_no':result.office_file_no if result.office_file_no else False,
    #                     'state':stages.existing_state,
    #                     'order_date':result.date_of_join,
    #                     'start_date':result.date_of_join,
    #                     'end_date':result.date_of_join + relativedelta(months=stages.days) if stages.days > 0 else False,
    #                     }) 
    #                 stage_history_ids.append((0, 0, add_stages))

    #                 if stages.existing_state == 'test_period' and result.employee_type == 'regular':
    #                     contract_record = self.env['hr.contract'].sudo().search([('employee_id','=',result.id)])
    #                     if contract_record:
    #                         contract_record.write({
    #                             'trial_date_end':result.date_of_join + relativedelta(months=stages.days) if stages.days > 0 else False,
    #                         })

    #             if stage_history_ids:
    #                 result.write({'stages_history':stage_history_ids})
    #     return result

    # @api.multi
    def start_grounding(self):
        pass
      

    # @api.multi
    # def set_as_employee(self):
    #     self.state = 'employment'
    #     stage_obj = self.stages_history.search([('employee_id', '=', self.id),
    #                                             ('state', '=', 'test_period')])
    #     if stage_obj:
    #         stage_obj.sudo().write({'end_date': date.today()})
    #     self.stages_history.sudo().create({'start_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'employment'})

    # @api.multi
    # def start_notice_period(self):
    #     self.state = 'notice_period'
    #     stage_obj = self.stages_history.search([('employee_id', '=', self.id),
    #                                             ('state', '=', 'employment')])
    #     if stage_obj:
    #         stage_obj.sudo().write({'end_date': date.today()})
    #     self.stages_history.sudo().create({'start_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'notice_period'})

    # @api.multi
    # def relived(self):
    #     if not self.lexit_progress == 100:
    #         raise UserError(_("""Please complete Exit process and try again...!"""))
    #     self.state = 'relieved'
    #     self.active = False
    #     stage_obj = self.stages_history.search([('employee_id', '=', self.id),
    #                                             ('state', '=', 'notice_period')])
    #     if stage_obj:
    #         stage_obj.sudo().write({'end_date': date.today()})
    #     self.stages_history.sudo().create({'end_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'relieved'})

    # @api.multi
    # def check_before_set_as_employee(self):
    #     if not self.lentry_progress == 100:
    #         raise UserError(_("""Please complete Entry process and try again...!"""))
    #     return {
    #         'name': _('Set as Employee'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'wizard.employee.stage',
    #         'view_id':self.env.ref('employee_stages.wizard_employee_form').id,
    #         'context': {'employee_id':self.id},
    #         'type': 'ir.actions.act_window',
    #         'target':'new',
    #     }


    # @api.multi
    # def start_test_period(self):
    #     self.state = 'test_period'
       
    #     self.stages_history.sudo().create({'start_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'test_period'})

    # @api.multi 
    # def employee_retired(self):
    #     self.state = 'retired'
    #     stage_obj = self.stages_history.search([('employee_id', '=', self.id),
    #                                             ('state', '=', 'employment')])
    #     if stage_obj:
    #         stage_obj.sudo().write({'end_date': date.today()})
    #     self.stages_history.sudo().create({'start_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'retired'})
    # @api.multi
    # def terminate(self):
    #     self.state = 'terminate'
    #     self.active = False
    #     stage_obj = self.stages_history.search([('employee_id', '=', self.id),
    #                                             ('state', '=', 'employment')])

    #     if stage_obj:
    #         stage_obj.sudo().write({'end_date': date.today()})
    #     else:
    #         pass
           
    #     self.stages_history.sudo().create({'end_date': date.today(),
    #                                        'employee_id': self.id,
    #                                        'state': 'terminate'})

    # state = fields.Selection(selection=[('test_period', 'Probation'),('contract', 'Contract'),('deputation', 'Deputation'),('employment', 'Regular')], string='Stage', track_visibility='always', copy=False,help="Employee Stages.\nTest period : Probation")


    # stages_history = fields.One2many('hr.employee.status.history', 'employee_id', string='Stage History',
    #                                  help='It shows the duration and history of each stages')
    # gratuity_check_no = fields.Char(string='Gratuity check no:')

    # reason = fields.Text('Reason')

    # state_updated_date =fields.Date('State_updated_state',default=date.today())

    def change_employee_stage(self):
        pass
        # if self:
        #     effective_date = False
        #     history_model = self.env['hr.employee.status.history'].sudo()
        #     history_record = history_model.search([
        #         ('employee_id', '=', self.id),
        #         ('state', '=', self.state)
        #     ],order='id desc',limit=1)
        #     if history_record and history_record.end_date:
        #         effective_date = history_record.end_date + relativedelta(days=1)
        #     contractual_with_stpi=self.employee_type if self.employee_type=='contractual_with_stpi' else None
        #     regular_with_stpi=self.employee_type if self.employee_type=='regular' else None
        #     return {
        #         'name': 'Change Employee stage',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'res_model': 'change.employee.stage',
        #         'type': 'ir.actions.act_window',
        #         'target': 'new',
        #         'view_id': self.env.ref('employee_stages.change_hr_employee_stages_view').id,
        #         'context': {
        #             'default_employee_id': self.id,'default_effective_date':effective_date ,'contractual_emp':contractual_with_stpi,'regular_with_stpi':regular_with_stpi}
        #     }

    # branch_own = fields.Boolean("branch",compute='_compute_branch',search="_lv_search_branch")

    # @api.multi
    # def _compute_branch(self):
    #     for record in self:
    #         pass
    
    # @api.multi
    # def _lv_search_branch(self, operator, value):
    #     domain = [('branch_id','in',self.env.user.branch_ids.ids)]
    #     return domain

class EmployeeStageHistory(models.Model):
    _name = 'hr.employee.status.history'
    _description = 'Status History'

    @api.depends('end_date')
    def get_duration(self):
        for each in self:
            if each.end_date and each.start_date:
               

                duration = relativedelta(each.end_date,each.start_date)
                months = 0 
                months += duration.months
                if duration.years:
                    months+= duration.years*12
                each.duration = str(months)+'.'+str(duration.days)

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    duration = fields.Char(compute=get_duration, string='Duration(Month)')
    state = fields.Selection(emp_stages, string='Stage')
    employee_id = fields.Many2one('hr.employee', invisible=1)
    designation_id =fields.Many2one('hr.job','Designation')
    file_no = fields.Char('File No.')
    order_no =fields.Char('Order No.')
    order_date =fields.Date('Order Date')
    Date_wef =fields.Date('Date wef/Extended')
    remarks = fields.Text('Remarks')
    effective_date = fields.Date('Effective Date')
    ndc_upload = fields.Binary('Upload Document',attachment=True)
    ndc_upload_filename = fields.Char('Upload Document Filename')


class WizardEmployee(models.TransientModel):
    _name = 'wizard.employee.stage'
    _description = 'Wizard employee stage'

    # @api.multi
    def set_as_employee(self):
        context = self._context
        employee_obj = self.env['hr.employee'].search([('id', '=', context.get('employee_id'))])
        if self.related_user:
            employee_obj.user_id = self.related_user
        employee_obj.set_as_employee()

    related_user = fields.Many2one('res.users', string="Related User")

class ChangeEmployeeStage(models.TransientModel):
    _name ='change.employee.stage'
    _description = 'Change Employee Stage'

    def set_contract(self):
        if self.env.context.get('contractual_emp') != None:
            return 'contract'
        elif self.env.context.get('regular_with_stpi') != None:
            return 'employment'

    state = fields.Selection(selection=[('test_period', 'Probation'),('contract', 'Contract'),('deputation', 'Deputation'),('employment', 'Regular')], string='Stage',help="Employee Stages.\nTest period : Probation", default=set_contract)
    reason = fields.Text('Reason')
    employee_id =fields.Many2one('hr.employee',string='Employee')

    # def change_stage(self):
    #     if self.employee_id:
    #         emp_id= self.env['hr.employee.status.history'].search([
    #                                                         ('employee_id','=',self.employee_id.id),
    #                                                         ('state','=',self.employee_id.state)
    #                                                        ])
    #         for emp in  emp_id:
    #             emp.end_date = date.today()
    #             emp.get_duration()

    #         self.employee_id.state = self.state
    #         self.employee_id.state_updated_date = date.today()
    #         self.employee_id.stages_history.sudo().create({'start_date': date.today(),
    #                                                        'employee_id': self.employee_id.id,
    #                                                        'designation_id':self.employee_id.job_id.id if self.employee_id.job_id else False,
    #                                                        'state': self.state})
    
    file_no = fields.Char('File No.')
    order_no =fields.Char('Order No.')
    order_date =fields.Date('Order Date')
    Date_wef =fields.Date('Date wef/Extended')
    remarks = fields.Text('Remarks')
    effective_date = fields.Date('Effective Date')
    ndc_upload = fields.Binary('Upload Document',attachment=True)
    ndc_upload_filename = fields.Char('Upload Document Filename')
    to_date = fields.Date(string='To Date')
    days = fields.Char(string='Month(s)',compute='_compute_days')

    # @api.constrains('order_date','effective_date')
    # def _onchange_order_date(self):
    #     for record in self:
    #         if record.order_date and record.effective_date:
    #             if record.order_date > date.today() or record.order_date > record.effective_date:
    #                 record.order_date = False
    #                 raise ValidationError("Order date should be less than or equal to current date and effective date.")
        
    def change_stage(self):
        if self.employee_id:
            history_model = self.env['hr.employee.status.history'].sudo()
            history_record = history_model.search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', self.employee_id.state)
            ],order='id desc',limit=1)

            if history_record:
                history_record.end_date = self.effective_date
                history_record.get_duration()

            self.employee_id.write({
                'state':self.state,
                'state_updated_date':date.today(),
            })
            
            history_model.create({
                                'start_date': self.effective_date,
                                'employee_id': self.employee_id.id,
                                'designation_id': self.employee_id.job_id.id if self.employee_id.job_id else False,
                                'state': self.state,
                                'order_no': self.order_no if self.order_no else False,
                                'order_date': self.order_date if self.order_date else False,
                                'file_no': self.file_no if self.file_no else False,
                                'effective_date': self.effective_date if self.effective_date else False,
                                'ndc_upload': self.ndc_upload if self.ndc_upload else False,
                                'remarks': self.remarks if self.remarks else False,
                                'end_date':self.to_date
                                })
            
            if self.state == 'test_period' and self.employee_id.employee_type == 'regular':
                contract_record = self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id)])
                if contract_record:
                    contract_record.write({
                        'trial_date_end':self.to_date if self.to_date else False,
                    })
            
    
    
    # @api.onchange('state','effective_date')
    # def _onchange_state(self):
    #     """Onchange to pop-up todate automatically"""
    #     self.to_date = False
    #     if self.state and self.effective_date:
    #         stage_config = self.env['employee.stage.configuration'].sudo()
    #         if self.employee_id.employee_type and self.employee_id.employee_type == 'regular':
    #             stage_record = stage_config.search([('employee_type','=',self.employee_id.employee_type),('recruitment_type','=',self.employee_id.recruitment_type),('existing_state','=',self.state)],limit=1)
    #         elif self.employee_id.employee_type == 'contractual_with_agency':
    #             stage_record = stage_config.search([('employee_type','=','contractual_with_3rd_party'),('existing_state','=',self.state)],limit=1)
    #         elif self.employee_id.employee_type == 'contractual_with_stpi':
    #             stage_record = stage_config.search([('employee_type','=','contractual'),('existing_state','=',self.state)],limit=1)
            
    #         if stage_record:
    #             date_start = self.effective_date + relativedelta(months=stage_record.days) if stage_record.days > 0 else False
    #             self.to_date = date_start
    #             self.Date_wef = date_start
        
    # @api.depends('to_date','effective_date')
    # def _compute_days(self):
    #     for each in self:
    #         if each.to_date and each.effective_date:
    #             duration = relativedelta(each.to_date,each.effective_date)
    #             months = 0 
    #             months += duration.months
    #             if duration.years:
    #                 months+= duration.years*12
    #             each.days = str(months)+'.'+str(duration.days)
               


class EmployeeStageConfig(models.Model):
    _name='employee.stage.configuration'
    _description = 'Employee Stage Configuration'
    _rec_name = 'employee_type'

    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_3rd_party', 'Contractual with 3rd Party'),
                                      ('contractual', 'Contractual')], string='Employment Type', required=True)

    recruitment_type = fields.Selection([
                                        ('d_recruitment', 'Direct Recruitment(DR)'),
                                        ('transfer', 'Transfer(Absorption)'),
                                        ('i_absorption', 'Immediate Absorption'),
                                        ('deputation', 'Deputation'),
                                        ('c_appointment', 'Compassionate Appointment'),
                                        ('promotion', 'Promotion'),
                                    ], 'Recruitment Type', required=True)

    existing_state = fields.Selection(emp_stages, string='Existing State',help="Employee Stages.\nTest period : Probation")
    new_state = fields.Selection(emp_stages, string='New State',help="Employee Stages.\nTest period : Probation")
    days =fields.Integer('Month(s)')


    # def change_employee_state_cron(self):
    #     confg = self.env['employee.stage.configuration'].search([])
    #     for s in confg:
    #         res = self.env['hr.employee'].search([('employee_type','=',s.employee_type),
    #                                         ('recruitment_type','=',s.recruitment_type),
    #                                         ('state','=',s.existing_state)
    #                                              ])
    #         for line in res:
    #             if (date.today() - line.state_updated_date).days >=s.days:

    #                 emp_id = self.env['hr.employee.status.history'].search([
    #                     ('employee_id', '=', line.id),
    #                     ('state', '=', s.existing_state)
    #                 ])
    #                 for emp in emp_id:
    #                     emp.end_date = date.today()
    #                     emp.get_duration()

    #                 line.state = s.new_state
    #                 line.state_updated_date = date.today()
    #                 line.stages_history.sudo().create({'start_date': date.today(),
    #                                                    'employee_id': line.id,
    #                                                    'designation_id': line.job_id.id if line.job_id else False,
    #                                                    'state': s.new_state})
