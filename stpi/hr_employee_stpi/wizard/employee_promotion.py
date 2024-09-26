from odoo import models, fields, api
from datetime import datetime,timedelta, date
from dateutil.relativedelta import relativedelta

class EmployeePromotion(models.TransientModel):
    _name ='employee.promotion'
    _description = 'Employee Promotion'

    employee_id = fields.Many2one('hr.employee',string="Employee")
    mode_of_promotion = fields.Selection([('test_period','Probation'),
                                            ('contract','Contract'),
                                            ('deputation','Deputation'),
                                            ('employment','Regular')],string="Stage")
    new_desg_id = fields.Many2one('hr.job',string="New Designation - Post")
    pay_level_id = fields.Many2one('hr.payslip.paylevel',string="Pay Level")
    pay_cell_id = fields.Many2one('payslip.pay.level',string="Pay Cell")
    struct_id = fields.Many2one('hr.payroll.structure',string="Salary Type")
    concern_file_no = fields.Char(string="Personnel / Concern File No.")
    promotion_date = fields.Date(string="Joining / Promotion Date")
    order_no = fields.Char(string="Order No")
    order_date = fields.Date(string="Order Date")
    remarks = fields.Text(string="Remarks")

    @api.onchange('new_desg_id')
    def show_pay_level(self):
        self.pay_level_id = False
        self.pay_level_id = self.new_desg_id.pay_level_id.id
        return {'domain': {'pay_level_id': ([('id', '=', self.new_desg_id.pay_level_id.id)])}}
    
    @api.onchange('pay_level_id')
    def show_pay_cell(self):
        self.pay_cell_id = False
        self.pay_cell_id = self.pay_level_id.entry_pay_ids.ids
        return {'domain': {'pay_cell_id': ([('id', 'in', self.pay_level_id.entry_pay_ids.ids)])}}
    
    def give_promotion(self):
        contract_id = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
        if contract_id:
            contract_id.update({'state':'close','date_end': self.promotion_date - relativedelta(days=1)})

        stage_config = self.env['employee.stage.configuration'].sudo()
        stage_record = []
        stage_history_ids = []

        stage_record = stage_config.search([('employee_type','=',self.employee_id.employee_type),('recruitment_type','=',self.employee_id.recruitment_type),('existing_state','=',self.mode_of_promotion)])
        print(stage_record)
        if stage_record:
            for stages in stage_record:
                add_stages = {}
                if self.mode_of_promotion == 'employment':
                    add_stages.update({
                        'designation_id':self.new_desg_id.id if self.new_desg_id.id else False,
                        'file_no':self.concern_file_no if self.concern_file_no else False,
                        'order_no':self.order_no if self.order_no else False,
                        'state':self.mode_of_promotion,
                        'order_date':self.order_date,
                        'start_date':self.promotion_date,
                        'remarks': self.remarks
                        }) 
                    stage_history_ids.append((0, 0, add_stages))
                else:
                    add_stages.update({
                        'designation_id':self.new_desg_id.id if self.new_desg_id.id else False,
                        'file_no':self.concern_file_no if self.concern_file_no else False,
                        'order_no':self.order_no if self.order_no else False,
                        'state':self.mode_of_promotion,
                        'order_date':self.order_date,
                        'start_date':self.promotion_date,
                        'end_date':self.promotion_date + relativedelta(months=stages.days) if stages.days > 0 else False,
                        'remarks': self.remarks
                        }) 
                    stage_history_ids.append((0, 0, add_stages))

        self.employee_id.write({
            'state': self.mode_of_promotion,
            'job_id' : self.new_desg_id.id,
            'stages_history':stage_history_ids if stage_history_ids else False,
        })

        if self.employee_id.employee_type == 'regular':
            create_contract = self.env['hr.contract'].create(
                {
                    'state': 'open',
                    'name': self.employee_id.name,
                    'employee_id': self.employee_id.id,
                    'department_id': self.employee_id.department_id.id,
                    'job_id': self.new_desg_id.id,
                    'pay_level_id': self.pay_level_id.id,
                    'pay_level': self.pay_cell_id.id,
                    'struct_id': self.struct_id.id,
                    'date_start': self.promotion_date,
                    'employee_type': self.employee_id.employee_type,
                    'wage': self.pay_cell_id.entry_pay,
                    'supplementary_allowance': contract_id.supplementary_allowance,
                    'voluntary_provident_fund': contract_id.voluntary_provident_fund,
                    'xnohra': contract_id.xnohra,
                    'misc_deduction': contract_id.misc_deduction,
                    'license_dee': contract_id.license_dee,
                    'arrear_amount': contract_id.arrear_amount
                }
            )