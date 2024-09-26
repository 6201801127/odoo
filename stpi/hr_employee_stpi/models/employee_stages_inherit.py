from datetime import date,datetime
from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Empstatus_inh(models.Model):
    _inherit = 'hr.employee.status.history'

    effective_date = fields.Date('Effective Date')
    ndc_upload = fields.Binary('No Due Certificate',attachment=True)
    ndc_upload_filename = fields.Char('No Due Certificate Filename')


class EmpStage_inh(models.TransientModel):
    _inherit = 'change.employee.stage'

    file_no = fields.Char('File No.')
    order_no =fields.Char('Order No.')
    order_date =fields.Date('Order Date')
    Date_wef =fields.Date('Date wef/Extended')
    remarks = fields.Text('Remarks')
    effective_date = fields.Date('Effective Date')
    ndc_upload = fields.Binary('No Due Certificate',attachment=True)
    ndc_upload_filename = fields.Char('No Due Certificate Filename')
    to_date = fields.Date(string='To Date')
    days = fields.Char(string='Month(s)',compute='_compute_days')

    @api.constrains('order_date','effective_date')
    def _onchange_order_date(self):
        for record in self:
            if record.order_date and record.effective_date:
                if record.order_date > date.today() or record.order_date > record.effective_date:
                    record.order_date = False
                    raise ValidationError("Order date should be less than or equal to current date and effective date.")
        
    def change_stage(self):
        if self.employee_id:
            history_model = self.env['hr.employee.status.history'].sudo()
            history_record = history_model.search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', self.employee_id.state)
            ],order='id desc',limit=1)
            # print(history_record)

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
                                # 'Date_wef': self.Date_wef if self.Date_wef else False,
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

    # def change_stage(self):
    #     if self.employee_id:
    #         emp_id = self.env['hr.employee.status.history'].search([
    #             ('employee_id', '=', self.employee_id.id),
    #             ('state', '=', self.employee_id.state)
    #         ])
    #         for emp in emp_id:
    #             emp.end_date = date.today()
    #             emp.get_duration()

    #         self.employee_id.state = self.state
    #         self.employee_id.state_updated_date = date.today()
    #         self.employee_id.stages_history.sudo().create({'start_date': date.today(),
    #                                                        'employee_id': self.employee_id.id,
    #                                                        'designation_id': self.employee_id.job_id.id if self.employee_id.job_id else False,
    #                                                        'state': self.state,
    #                                                        'order_no': self.order_no if self.order_no else False,
    #                                                        'order_date': self.order_date if self.order_date else False,
    #                                                        'file_no': self.file_no if self.file_no else False,
    #                                                        'Date_wef': self.Date_wef if self.Date_wef else False,
    #                                                        'effective_date': self.effective_date if self.effective_date else False,
    #                                                        'ndc_upload': self.ndc_upload if self.ndc_upload else False,
    #                                                        'remarks': self.remarks if self.remarks else False,
    #                                                        })
    
    @api.onchange('state','effective_date')
    def _onchange_state(self):
        """Onchange to pop-up todate automatically"""
        self.to_date = False
        if self.state and self.effective_date:
            stage_config = self.env['employee.stage.configuration'].sudo()
            if self.employee_id.employee_type and self.employee_id.employee_type == 'regular':
                stage_record = stage_config.search([('employee_type','=',self.employee_id.employee_type),('recruitment_type','=',self.employee_id.recruitment_type),('existing_state','=',self.state)],limit=1)
            elif self.employee_id.employee_type == 'contractual_with_agency':
                stage_record = stage_config.search([('employee_type','=','contractual_with_3rd_party'),('existing_state','=',self.state)],limit=1)
            elif self.employee_id.employee_type == 'contractual_with_stpi':
                stage_record = stage_config.search([('employee_type','=','contractual'),('existing_state','=',self.state)],limit=1)
            
            if stage_record:
                date_start = self.effective_date + relativedelta(months=stage_record.days) if stage_record.days > 0 else False
                self.to_date = date_start
                self.Date_wef = date_start
                # self.days = stage_record.days
        
    @api.depends('to_date','effective_date')
    def _compute_days(self):
        for each in self:
            if each.to_date and each.effective_date:
                duration = relativedelta(each.to_date,each.effective_date)
                months = 0 
                months += duration.months
                if duration.years:
                    months+= duration.years*12
                each.days = str(months)+'.'+str(duration.days)
                # duration = fields.Date.from_string(each.to_date) - fields.Date.from_string(each.effective_date)
                # each.days = duration.days