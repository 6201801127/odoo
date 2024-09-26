
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime,date
from odoo.tools.float_utils import float_round
import calendar


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'HR Leave Type Changes For STPI'
    _rec_name = 'name'
    
    @api.one
    @api.depends('creadit_policy_id.no_pf_leaves_credit')
    def _compute_amount(self):
#         round_curr = self.currency_id.round
        amt = 0.0
        for line in self.creadit_policy_id:
            amt += line.no_pf_leaves_credit
#             print("????????????????????????",amt)
            self.amount_total = amt
#             print("///////////////////////",self.amount_total)
        return amt
    
#     name = fields.Selection([('Casual Leave','Casual Leave'),
#                                ('Half Pay Leave','Half Pay Leave'),
# #                                 ('Commuted Leave','Commuted Leave'),
#                                ('Earned Leave','Earned Leave'),
#                                ('Maternity Leave','Maternity Leave'),
#                                ('Special Casual Leave','Special Casual Leave'),
#                                ('Extra Ordinary Leave','Extra Ordinary Leave'),
#                                ('Paternity Leave','Paternity Leave'),
#                                ('Child Care Leave','Child Care Leave'),
#                                ('Restricted Holiday','Restricted Holiday'),
#                                ('Miscarriage Leave','Miscarriage Leave'),
#                                ('Contractual Casual Leave','Contractual Casual Leave')
#                         ],string='Name',required=True)
#     leave_type = fields.Selection([('Casual Leave','Casual Leave'),
#                                ('Half Pay Leave','Half Pay Leave'),
# #                                 ('Commuted Leave','Commuted Leave'),
#                                ('Earned Leave','Earned Leave'),
#                                ('Maternity Leave','Maternity Leave'),
#                                ('Special Casual Leave','Special Casual Leave'),
#                                ('Extra Ordinary Leave','Extra Ordinary Leave'),
#                                ('Paternity Leave','Paternity Leave'),
#                                ('Child Care Leave','Child Care Leave'),
#                                ('Restricted Holiday','Restricted Holiday'),
#                                ('Miscarriage Leave','Miscarriage Leave'),
#                                ('Contractual Casual Leave','Contractual Casual Leave')
#                                 ],required=True)
    name = fields.Many2one('leave.type.master', 'Name')
    leave_type = fields.Many2one('leave.type.master', 'Leave Type')
    leave_per_year = fields.Integer(string="Leave Per Year",readonly=True)
    carried_forward = fields.Boolean(string="Carried Forward")
    half_pay_allowed = fields.Boolean(string="Half Day Allowed")
    is_ltc = fields.Boolean(string='LTC Applicable?')
    leave_month = fields.Selection([('January','January'),
                                    ('February','February'),
                                    ('March','March'),
                                    ('April','April'),
                                    ('May','May'),
                                    ('June','June'),
                                    ('July','July'),
                                    ('August','August'),
                                    ('September','September'),
                                    ('October','October'),
                                    ('November','November'),
                                    ('December','December')
                                    ],string="Lapse Month")
    allow_service_leave = fields.Many2many('leave.employee.type',string="Allowed Service Type(s)")
    max_encash_leave = fields.Integer(string="Maximum Allowed Encashment")
    group_id = fields.Many2one('hr.leave.group',string="Group",invisible=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    use_balance_from_id = fields.Many2one('leave.type',string="Use Balance From")
    maximum_allow_leave = fields.Integer(string="Maximum Allowed Leaves")
    gende = fields.Selection([('male','Male'),
                                     ('female','Female'),
                                     ('transgender','All')
                                    ],string="Allowed Gender(s)")
    allow_emp_stage = fields.Many2many('leave.type.employee.stage',string="Allowed Employee Stage(s)")
    encash_leave = fields.Boolean(string="Encashed Leave")
    cerificate = fields.Boolean(string="Requires Attachment")
    sandwich_rule = fields.Boolean(string="Sandwich Rule Applicable")
    creadit_policy_id = fields.One2many('leave.type.credit.policy','leave_policy','Credit Leave Policy')
    commuted = fields.Boolean(string="Is Commuted Leave")
    amount_total = fields.Monetary(string='Total',store=True, readonly=True, compute='_compute_amount')
    
    allowed_prefix_leave = fields.Many2many('leave.type',string="Allowed Combination Leave(s)")
    mid_year_factor = fields.Float(string="Mid Year Factor",compute="compute_mid_year_factor")

    ## Modified : Nikunja (May 27 2021) : Start
    minimum_allow_leave = fields.Float(string="Minimum Allowed Leaves")
    ## Modified : Nikunja (May 27 2021) : End'''
    allocation_type_allow = fields.Selection([('one_time', 'One Time'),
        ('periodic', 'Periodic')
        ], string='Allocation Type',default='periodic')


    @api.multi
    def name_get(self):
        if not self._context.get('employee_id'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(HrLeaveType, self).name_get()
        res = []
        for record in self:
            name = record.name.code
            if record.allocation_type != 'no':
                name = "%(name)s" % {
                    'name': name,
                }
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        res = super(HrLeaveType, self).create(vals)
        leave_type_rec = self.env['hr.leave.type'].search(
            [('name', '=', res.name.id), ('id', '!=', res.id),('leave_type','=',res.leave_type.id)])
        if leave_type_rec:
            raise ValidationError(_('Exists ! Already a Leave Type exists in this name'))
        return res
    
    @api.depends('leave_per_year')
    def compute_mid_year_factor(self):
        for leave in self:
            leave.mid_year_factor = leave.leave_per_year / 12
    
    @api.constrains('amount_total')
    @api.onchange('amount_total')
    def get_leave_per_year(self):
        for leave in self:
            leave.leave_per_year = leave.amount_total

    @api.constrains('leave_type')
    @api.onchange('leave_type')
    def get_name(self):
        for leave in self:
            leave.name = leave.leave_type
#             print("leave^^^^^^^^^^^^^^^^^^^^^^^^^^^^^6",leave.name)

    def expire_leave(self,leave):
        print("Inside Function")
        try:
            today = date.today()
            current_month = today.strftime("%B")
            print('[[[[[[[[[[[[', current_month,today.day)
            if not leave.carried_forward and leave.leave_month and leave.leave_month == current_month and today.day == 31:
                employee_type = leave.allow_service_leave.mapped('tech_name')
                emp_stages = leave.allow_emp_stage.mapped('tech_name')
                employee_ids = self.env['hr.employee'].sudo().search([('employee_type','in',employee_type),('state','in',emp_stages)])
                if leave.gende and leave.gende != 'transgender':
                    employee_ids = employee_ids.filtered(lambda res:res.gende == leave.gende)

                if employee_ids:
                    print(len(employee_ids))
                    for employee in employee_ids:
                        try:
                            print("Remaining leave in --",leave.with_context(employee_id=employee.id).virtual_remaining_leaves," Employees is --",employee.name)
                            number_of_days = leave.with_context(employee_id=employee.id).virtual_remaining_leaves
                            if number_of_days > 0:
                                self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,state,holiday_type,number_of_days,create_uid,create_date,write_uid,write_date,is_lapsed,branch_id)
                                VALUES ({employee.id},{leave.id},'Yearly Lapse by System','Yearly Lapse by System','validate','employee',{number_of_days*-1},{self.env.user.id},'{datetime.now()}',{self.env.user.id},'{datetime.now()}',True,{employee.branch_id.id})""")
                            else:
                                pass
                        except Exception as e:
                            print(str(e))
                            continue
        except Exception as e:
            print(str(e))
            pass

    @api.multi
    def button_expried_leaves(self):
        for leave in self:
            self.expire_leave(leave)
    
    def cron_expire_leave(self):
        leave_type_records = self.env['hr.leave.type'].search([])
        for leave in leave_type_records:
            self.expire_leave(leave)

    def cron_expire_leave2(self):
        confg = self.env['hr.leave.type'].search([])
        today = date.today()
        year, month = today.year, today.month
        current_month_date = calendar.monthrange(year, month)[1]
        # print("0000000000000000000000000",current_month_date)
        for leave in confg:
            mydate = datetime.now()
            month = mydate.strftime("%B")
            for service_leave in leave.allow_service_leave:
                for emp_stages in leave.allow_emp_stage:
                    # print("22222222222222222222222222222",month,leave.leave_month)
                    # print("333333333333333333333",today.day,current_month_date)
                    if today.day == current_month_date:
                        if leave.leave_month == month:
                            if leave.gende == 'male' or leave.gende =='female':
                                        # print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
                                employee_ids = self.env['hr.employee'].search([('gende','=',leave.gende),
                                                                               ('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True)
                                                                               ])
                            elif leave.gende == 'transgender':
                                # print("BBBBBBBBBBBBBBBBBBBBBBBBBB",service_leave.tech_name,emp_stages.tech_name)
                                employee_ids = self.env['hr.employee'].search([('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True)
                                                                               ])
                                
                            for employee in employee_ids:
                                    # print("@@@@@@@@@@@@@@@@@@@@@@@@",employee)
                                if employee and not employee.leave_balance_id:
                                    total_leave = 0.0
                                    hr_leave_report = self.env['hr.leave.report'].search([('employee_id','=',employee.id),
                                                                                          ('holiday_type','=','employee'),
                                                                                          ('holiday_status_id','=',leave.id),
                                                                                          ('state','=','validate')
                                                                                          ])
                                    # print("?availabeleaveeeeeeeeee",hr_leave_report)
                                    for leave_report in hr_leave_report:
                                        total_leave += leave_report.number_of_days
                                        # print("<<<<<<<<<<}}}}}}}}}}}}}}}}}}",total_leave)
                                    if hr_leave_report:
                                        # print("1111111111111111111111111111111111",leave.id,employee.ids,date.today(),total_leave)
                                        hr_leave = self.env['hr.leave'].create({'holiday_status_id': leave.id,
                                                                                       'holiday_type': 'employee',
                                                                                       'employee_id': employee.id,
                                                                                       'request_date_from':date.today(),
                                                                                       'request_date_to':date.today(),
                                                                                       'number_of_days_display':total_leave,
                                                                                       'number_of_days':total_leave
                                                                                       })
                                        # print("allocationnnnnnnnnnn2222222222222222222222nn",hr_leave)
                                        hr_leave.sudo().action_approve()
                                        if hr_leave:
                                            leave_bal_id = self.env['hr.employee.leave.info'].create({
                                                                                                        'hr_employee_id':employee.id,
                                                                                                        'holiday_status_id':leave.id,
                                                                                                        'date':date.today(),
                                                                                                        'leave_info':'debit',
                                                                                                        'no_of_days':total_leave
                                                                                                    })
                                elif employee and employee.leave_balance_id:
                                        for credit_policy in leave.creadit_policy_id:
                                            SQL = """
                                                       
                                                select he.id from 
                                                hr_employee as he
                                                left outer join hr_employee_leave_info as heli on heli.hr_employee_id = he.id
                                                left outer join hr_leave_type as hlt on hlt.id = heli.holiday_status_id
                                                where 
                                                he.id in (%s)
                                                and hlt.leave_type in (%s)
                                                and heli.leave_info = 'debit'
                                                and EXTRACT(DAY FROM heli.date) = '%s'
                                                    """
                                            self.env.cr.execute(SQL, (
                                                employee.id,
                                                leave.leave_type,
                                                credit_policy.day
                                            ))
                                            res = self.env.cr.fetchall()
                                            # print("??????????????RESSSSSSSSSSSSSSSSSSSSS",res,today.day,today.strftime("%B"),credit_policy.day,credit_policy.month)
                                            if not res:
                                            # print("???????<<<<<<<<<<<<<<<<<<<<<???????????????",leave_bal_id)
                                                if today.day == credit_policy.day and today.strftime("%B") == credit_policy.month:
                                                    total_leave = 0.0
                                                    hr_leave_report = self.env['hr.leave.report'].search([('employee_id','=',employee.id),
                                                                                                          ('holiday_type','=','employee'),
                                                                                                          ('holiday_status_id','=',leave.id),
                                                                                                          ('state','=','validate')
                                                                                                          ])
                                                    # print("?availabeleaveeeeeeeeee",hr_leave_report)
                                                    for leave_report in hr_leave_report:
                                                        total_leave += leave_report.number_of_days
                                                        # print("<<<<<<<<<<}}}}}}}}}}}}}}}}}}",total_leave)
                                                    if hr_leave_report:
                                                        # print("1111111111111111111111111111111111",leave.id,employee.ids,date.today(),total_leave)
                                                        hr_leave = self.env['hr.leave'].create({'holiday_status_id': leave.id,
                                                                                                       'holiday_type': 'employee',
                                                                                                       'employee_id': employee.id,
                                                                                                       'request_date_from':date.today(),
                                                                                                       'request_date_to':date.today(),
                                                                                                       'number_of_days_display':total_leave,
                                                                                                       'number_of_days':total_leave
                                                                                                       })
                                                        # print("allocationnnnnnnnnnn2222222222222222222222nn",hr_leave)
                                                        hr_leave.sudo().action_approve()
                                                        # print("4444444444444444")
                                                        if hr_leave:
                                                            leave_bal_id = self.env['hr.employee.leave.info'].create({
                                                                                                                        'hr_employee_id':employee.id,
                                                                                                                        'holiday_status_id':leave.id,
                                                                                                                        'date':date.today(),
                                                                                                                        'leave_info':'debit',
                                                                                                                        'no_of_days':total_leave
                                                                                                                    })
                                                         
    @api.multi
    def button_expried_leaves2(self):
        today = date.today()
        for leave in self:
            mydate = datetime.now()
            month = mydate.strftime("%B")
            for service_leave in leave.allow_service_leave:
                for emp_stages in leave.allow_emp_stage:
                    if leave.leave_month == month:
                        if leave.gende == 'male' or leave.gende =='female':
                                    # print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
                            employee_ids = self.env['hr.employee'].search([('gende','=',leave.gende),
                                                                           ('employee_type','=',service_leave.tech_name),
                                                                           ('state','=',emp_stages.tech_name),
                                                                           ('active','=',True)
                                                                           ])
                        elif leave.gende == 'transgender':
                            # print("BBBBBBBBBBBBBBBBBBBBBBBBBB",service_leave.tech_name,emp_stages.tech_name)
                            employee_ids = self.env['hr.employee'].search([('employee_type','=',service_leave.tech_name),
                                                                           ('state','=',emp_stages.tech_name),
                                                                           ('active','=',True)
                                                                           ])
                        # print("Employees are ",len(employee_ids))
                        for employee in employee_ids:
                                # print("@@@@@@@@@@@@@@@@@@@@@@@@",employee)
                            if employee and not employee.leave_balance_id:
                                total_leave = 0.0
                                hr_leave_report = self.env['hr.leave.report'].search([('employee_id','=',employee.id),
                                                                                      ('holiday_type','=','employee'),
                                                                                      ('holiday_status_id','=',leave.id),
                                                                                      ('state','=','validate')
                                                                                      ])
                                # print("?availabeleaveeeeeeeeee",hr_leave_report)
                                for leave_report in hr_leave_report:
                                    total_leave += leave_report.number_of_days
                                    # print("<<<<<<<<<<}}}}}}}}}}}}}}}}}}",total_leave)
                                if hr_leave_report:
                                    # print("1111111111111111111111111111111111",leave.id,employee.ids,date.today(),total_leave)
                                    hr_leave = self.env['hr.leave'].create({'holiday_status_id': leave.id,
                                                                                   'holiday_type': 'employee',
                                                                                   'employee_id': employee.id,
                                                                                   'request_date_from':date.today(),
                                                                                   'request_date_to':date.today(),
                                                                                   'number_of_days_display':total_leave,
                                                                                   'number_of_days':total_leave
                                                                                   })
                                    # print("allocationnnnnnnnnnn2222222222222222222222nn",hr_leave)
                                    hr_leave.sudo().action_approve()
                                    if hr_leave:
                                        leave_bal_id = self.env['hr.employee.leave.info'].create({
                                                                                                    'hr_employee_id':employee.id,
                                                                                                    'holiday_status_id':leave.id,
                                                                                                    'date':date.today(),
                                                                                                    'leave_info':'debit',
                                                                                                    'no_of_days':total_leave
                                                                                                })
                            elif employee and employee.leave_balance_id:
                                    for credit_policy in leave.creadit_policy_id:
                                        SQL = """
                                                   
                                            select he.id from 
                                            hr_employee as he
                                            left outer join hr_employee_leave_info as heli on heli.hr_employee_id = he.id
                                            left outer join hr_leave_type as hlt on hlt.id = heli.holiday_status_id
                                            where 
                                            he.id in (%s)
                                            and hlt.leave_type in (%s)
                                            and heli.leave_info = 'debit'
                                            and EXTRACT(DAY FROM heli.date) = '%s'
                                                """
                                        self.env.cr.execute(SQL, (
                                            employee.id,
                                            leave.leave_type,
                                            credit_policy.day
                                        ))
                                        res = self.env.cr.fetchall()
                                        # print("??????????????RESSSSSSSSSSSSSSSSSSSSS",res,today.day,today.strftime("%B"),credit_policy.day,credit_policy.month)
                                        if not res:
                                        # print("???????<<<<<<<<<<<<<<<<<<<<<???????????????",leave_bal_id)
                                            if today.day == credit_policy.day and today.strftime("%B") == credit_policy.month:
                                                total_leave = 0.0
                                                hr_leave_report = self.env['hr.leave.report'].search([('employee_id','=',employee.id),
                                                                                                      ('holiday_type','=','employee'),
                                                                                                      ('holiday_status_id','=',leave.id),
                                                                                                      ('state','=','validate')
                                                                                                      ])
                                                # print("?availabeleaveeeeeeeeee",hr_leave_report)
                                                for leave_report in hr_leave_report:
                                                    total_leave += leave_report.number_of_days
                                                    # print("<<<<<<<<<<}}}}}}}}}}}}}}}}}}",total_leave)
                                                if hr_leave_report:
                                                    # print("1111111111111111111111111111111111",leave.id,employee.ids,date.today(),total_leave)
                                                    hr_leave = self.env['hr.leave'].create({'holiday_status_id': leave.id,
                                                                                                   'holiday_type': 'employee',
                                                                                                   'employee_id': employee.id,
                                                                                                   'request_date_from':date.today(),
                                                                                                   'request_date_to':date.today(),
                                                                                                   'number_of_days_display':total_leave,
                                                                                                   'number_of_days':total_leave
                                                                                                   })
                                                    hr_leave.sudo().action_approve()
                                                    if hr_leave:
                                                        leave_bal_id = self.env['hr.employee.leave.info'].create({
                                                                                                                    'hr_employee_id':employee.id,
                                                                                                                    'holiday_status_id':leave.id,
                                                                                                                    'date':date.today(),
                                                                                                                    'leave_info':'debit',
                                                                                                                    'no_of_days':total_leave
                                                                                                                })
    
    @api.multi                                                
    def button_mid_year_leave_allocate(self):
        for leave in self:
            mydate = datetime.now()
            month = mydate.strftime("%B")
            today = date.today()
            for line in leave.creadit_policy_id:
                for service_leave in leave.allow_service_leave:
                    for emp_stages in leave.allow_emp_stage:
                        if line.day == today.day and line.month == month:
                            if leave.gende == 'male' or leave.gende =='female':
                                employee_ids = self.env['hr.employee'].search([('gende','=',leave.gende),
                                                                               ('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True),
                                                                               ])
                            elif leave.gende == 'transgender':
                                employee_ids = self.env['hr.employee'].search([('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True)
                                                                               ('mid_year_factor','=',True)
                                                                               ])
                                print("employeeeeeeeeeee",employee_ids)

    @api.multi
    def button_allocate_leaves(self):
        for leave in self:
            mydate = datetime.now()
            month = mydate.strftime("%B")
            today = date.today()
            for line in leave.creadit_policy_id:
                for service_leave in leave.allow_service_leave:
                    for emp_stages in leave.allow_emp_stage:
                        if line.day == today.day and line.month == month:
                            # print("333333333333333333333",leave.gende,service_leave.tech_name,emp_stages.tech_name)
                            if leave.gende == 'male' or leave.gende =='female':
                                employee_ids = self.env['hr.employee'].search([('gende','=',leave.gende),
                                                                               ('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                                # ('active','=',True),
                                                                               ])
                                print("444444447----------------",employee_ids)
                            elif leave.gende == 'transgender':
                                employee_ids = self.env['hr.employee'].search([('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True)
                                                                               ])
                                print("44444444444444444444444444444444",employee_ids)
                            for employee in employee_ids:
                                print("@@@@@@@@@@@@@@@@@@@@@@@@",employee)
                                if employee and not employee.leave_balance_id:
                                    if leave.leave_type.code != 'Casual Leave':
                                        allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                       'holiday_type': 'employee',
                                                                                       'employee_id': employee.id,
                                                                                       'number_of_days_display':line.no_pf_leaves_credit,
                                                                                       'number_of_days':line.no_pf_leaves_credit,
                                                                                       'name':'System Leave Allocation',
                                                                                       'notes':'As Per Leave Policy','state':'validate'
                                                                                       })
                                        print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                        # allocate_leave.sudo().action_approve()
                                        print("allocationnnnnnnnnnnnn111111111111111arrpoved")
                                    if leave.leave_type.code == 'Casual Leave':
                                        if employee.differently_abled != 'yes':
                                            allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                           'holiday_type': 'employee',
                                                                                           'employee_id': employee.id,
                                                                                           'number_of_days_display': line.no_pf_leaves_credit,
                                                                                           'number_of_days': line.no_pf_leaves_credit,
                                                                                           'name':'System Leave Allocation',
                                                                                           'notes':'As Per Leave Policy','state':'validate'
                                                                                           })
                                            print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                            # allocate_leave.sudo().action_approve()
                                            print("allocationnnnnnnnnnnnn111111111111111arrpoved")
                                        else:
                                            leave_alloted = self.env['ir.config_parameter'].sudo().get_param('leaves_stpi.leaves_deffective_cl')
                                            print('---12121212-?------------------', leave_alloted)
                                            allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                           'holiday_type': 'employee',
                                                                                           'employee_id': employee.id,
                                                                                           'number_of_days_display': int(leave_alloted),
                                                                                           'number_of_days': int(leave_alloted),
                                                                                           'name':'System Leave Allocation',
                                                                                           'notes':'As Per Leave Policy','state':'validate'
                                                                                           })
                                            print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)    
                                    if allocate_leave:
                                        leave_bal_id = self.env['hr.employee.leave.info'].sudo().create({
                                                                                                'hr_employee_id':employee.id,
                                                                                                'holiday_status_id':leave.id,
                                                                                                'date':date.today(),
                                                                                                'leave_info':'credit',
                                                                                                'no_of_days':line.no_pf_leaves_credit
                                                                                            })
                                        print("allocationnnnnnnnnnnnn111111111111111arrpoved----------al", leave_bal_id)
                                elif employee and employee.leave_balance_id:
                                    print('========2==============')
                                    for credit_policy in leave.creadit_policy_id:
                                        SQL = """
                                                   
                                            select he.id from 
                                            hr_employee as he
                                            left outer join hr_employee_leave_info as heli on heli.hr_employee_id = he.id
                                            left outer join hr_leave_type as hlt on hlt.id = heli.holiday_status_id
                                            where 
                                            he.id in (%s)
                                            and hlt.leave_type in (%s)
                                            and heli.leave_info = 'credit'
                                            and EXTRACT(DAY FROM heli.date) = '%s'
                                                """
                                        self.env.cr.execute(SQL, (
                                            employee.id,
                                            leave.leave_type,
                                            credit_policy.day
                                        ))
                                        res = self.env.cr.fetchall()
                                        print('---------fetchall-----------', res)
                                        #   print("??????????????RESSSSSSSSSSSSSSSSSSSSS",res,today.day,today.strftime("%B"),credit_policy.day,credit_policy.month)
                                        if not res:
                                            if today.day == credit_policy.day and today.strftime("%B") == credit_policy.month:
                                                print("#############################################")
                                                allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                               'holiday_type': 'employee',
                                                                                               'employee_id': employee.id,
                                                                                               'number_of_days_display':line.no_pf_leaves_credit,
                                                                                               'number_of_days':line.no_pf_leaves_credit,
                                                                                               'name':'System Leave Allocation',
                                                                                               'notes':'As Per Leave Policy','state':'validate'
                                                                                               })
                                                print("allocationnnnnnnnnnnnn",allocate_leave)
                                                # allocate_leave.sudo().action_approve()
                                                print("truuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
                                                if allocate_leave:
                                                    leave_bal_id = self.env['hr.employee.leave.info'].sudo().create({
                                                                                                            'hr_employee_id':employee.id,
                                                                                                            'holiday_status_id':leave.id,
                                                                                                            'date':date.today(),
                                                                                                            'leave_info':'credit',
                                                                                                            'no_of_days':line.no_pf_leaves_credit
                                                                                                        })
                                                    # print("truuuuuuuuuuuuuuuuuuuallocate_leaveuuuuuuuuuuuuuuuuuuuuuuuuuu", allocate_leave)
                                        else:
                                            raise ValidationError(
                                                _('Not allowed'))


                                else:
                                    print('============3====================')
                                                    
    def cron_allocate_leave(self):
        confg = self.env['hr.leave.type'].search([])
        for leave in confg:
            mydate = datetime.now()
            month = mydate.strftime("%B")
            today = date.today()
            # year, month = today.year, today.month
            # print("0000000000000000000000000",year,month)
            # current_month_date = calendar.monthrange(year, month)[1]
            for line in leave.creadit_policy_id:
                for service_leave in leave.allow_service_leave:
                    for emp_stages in leave.allow_emp_stage:
                        # print("333333333333333333333",today.day,current_month_date)
                        print('poooooooooooooooooooooooo',line.day,today.day,line.month,month)
                        # if today.day == current_month_date:
                        if line.day == today.day and line.month == month:
                            if leave.gende == 'male' or leave.gende =='female':
                                employee_ids = self.env['hr.employee'].search([('gende','=',leave.gende),
                                                                               ('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True),
                                                                               ])
                            elif leave.gende == 'transgender':
                                employee_ids = self.env['hr.employee'].search([('employee_type','=',service_leave.tech_name),
                                                                               ('state','=',emp_stages.tech_name),
                                                                               ('active','=',True)
                                                                               ])
                            for employee in employee_ids:
                                # print("@@@@@@@@@@@@@@@@@@@@@@@@",employee)
                                if employee:
                                    # print("ifffffffffffffffffffffffffff")
                                    # allocate_leave = self.env['hr.leave.allocation'].create({'holiday_status_id': leave.id,
                                    #                                                'holiday_type': 'employee',
                                    #                                                'employee_id': employee.id,
                                    #                                                'number_of_days_display':line.no_pf_leaves_credit,
                                    #                                                'number_of_days':line.no_pf_leaves_credit,
                                    #                                                'name':'System Leave Allocation',
                                    #                                                'notes':'As Per Leave Policy'
                                    #                                                })
                                    # print("allocationnnnnnnnnnnnn",leave.leave_type)
                                    if leave.leave_type.code != 'Casual Leave':
                                        allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                       'holiday_type': 'employee',
                                                                                       'employee_id': employee.id,
                                                                                       'number_of_days_display':line.no_pf_leaves_credit,
                                                                                       'number_of_days':line.no_pf_leaves_credit,
                                                                                       'name':'System Leave Allocation',
                                                                                       'notes':'As Per Leave Policy','state':'validate'
                                                                                       })
                                        print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                        # allocate_leave.sudo().action_approve()
                                    elif leave.leave_type.code == 'Casual Leave':
                                        if employee.differently_abled != 'yes':
                                            allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                           'holiday_type': 'employee',
                                                                                           'employee_id': employee.id,
                                                                                           'number_of_days_display': line.no_pf_leaves_credit,
                                                                                           'number_of_days': line.no_pf_leaves_credit,
                                                                                           'name':'System Leave Allocation',
                                                                                           'notes':'As Per Leave Policy','state':'validate'
                                                                                           })
                                            print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                            # allocate_leave.sudo().action_approve()
                                            print("allocationnnnnnnnnnnnn111111111111111arrpoved")
                                        else:
                                            leave_alloted = self.env['ir.config_parameter'].sudo().get_param('leaves_stpi.leaves_deffective_cl')
                                            print('---12121212---?----------------', leave_alloted)
                                            allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                                                                           'holiday_type': 'employee',
                                                                                           'employee_id': employee.id,
                                                                                           'number_of_days_display': int(leave_alloted),
                                                                                           'number_of_days': int(leave_alloted),
                                                                                           'name':'System Leave Allocation',
                                                                                           'notes':'As Per Leave Policy','state':'validate'
                                                                                           })
                                            print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)  
                                        # allocate_leave.sudo().action_approve()
                                        
                                        # if allocate_leave:
                                        #     leave_bal_id = self.env['hr.employee.leave.info'].create({
                                        #                                                             'hr_employee_id':employee.id,
                                        #                                                             'holiday_status_id':leave.id,
                                        #                                                             'date':date.today(),
                                        #                                                             'leave_info':'credit',
                                        #                                                             'no_of_days':line.no_pf_leaves_credit
                                        #                                                         })
                                # elif employee and employee.leave_balance_id:
                                #     for credit_policy in leave.creadit_policy_id:
                                #         SQL = """
                                                   
                                #             select he.id from 
                                #             hr_employee as he
                                #             left outer join hr_employee_leave_info as heli on heli.hr_employee_id = he.id
                                #             left outer join hr_leave_type as hlt on hlt.id = heli.holiday_status_id
                                #             where 
                                #             he.id in (%s)
                                #             and hlt.leave_type in (%s)
                                #             and heli.leave_info = 'credit'
                                #             and EXTRACT(DAY FROM heli.date) = '%s'
                                #                 """
                                #         self.env.cr.execute(SQL, (
                                #             employee.id,
                                #             leave.leave_type,
                                #             credit_policy.day
                                #         ))
                                #         res = self.env.cr.fetchall()
                                #         print("??????????????RESSSSSSSSSSSSSSSSSSSSS",res,today.day,today.strftime("%B"),credit_policy.day,credit_policy.month)
                                #         print("-========================leavestype", leave.leave_type)
                                #         if not res:
                                #             if today.day == credit_policy.day and today.strftime("%B") == credit_policy.month:
                                #                 # print("#############################################")
                                #                 # allocate_leave = self.env['hr.leave.allocation'].create({'holiday_status_id': leave.id,
                                #                 #                                                'holiday_type': 'employee',
                                #                 #                                                'employee_id': employee.id,
                                #                 #                                                'number_of_days_display':line.no_pf_leaves_credit,
                                #                 #                                                'number_of_days':line.no_pf_leaves_credit,
                                #                 #                                                'name':'System Leave Allocation',
                                #                 #                                                'notes':'As Per Leave Policy'
                                #                 #                                                })
                                #                 if leave.leave_type != 'Casual Leave':
                                #                     allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                #                                                                    'holiday_type': 'employee',
                                #                                                                    'employee_id': employee.id,
                                #                                                                    'number_of_days_display':line.no_pf_leaves_credit,
                                #                                                                    'number_of_days':line.no_pf_leaves_credit,
                                #                                                                    'name':'System Leave Allocation',
                                #                                                                    'notes':'As Per Leave Policy','state':'validate'
                                #                                                                    })
                                #                     print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                #                     # allocate_leave.sudo().action_approve()
                                #                 elif leave.leave_type == 'Casual Leave':
                                #                     if employee.differently_abled != 'yes':
                                #                         allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                #                                                                        'holiday_type': 'employee',
                                #                                                                        'employee_id': employee.id,
                                #                                                                        'number_of_days_display': line.no_pf_leaves_credit,
                                #                                                                        'number_of_days': line.no_pf_leaves_credit,
                                #                                                                        'name':'System Leave Allocation',
                                #                                                                        'notes':'As Per Leave Policy','state':'validate'
                                #                                                                        })
                                #                         print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                #                         # allocate_leave.sudo().action_approve()
                                #                         print("allocationnnnnnnnnnnnn111111111111111arrpoved")
                                #                     else:
                                #                         allocate_leave = self.env['hr.leave.allocation'].sudo().create({'holiday_status_id': leave.id,
                                #                                                                        'holiday_type': 'employee',
                                #                                                                        'employee_id': employee.id,
                                #                                                                        'number_of_days_display': 12,
                                #                                                                        'number_of_days': 12,
                                #                                                                        'name':'System Leave Allocation',
                                #                                                                        'notes':'As Per Leave Policy','state':'validate'
                                #                                                                        })
                                #                         print("allocationnnnnnnnnnnnn111111111111111",allocate_leave)
                                #                 # print("allocationnnnnnnnnnnnn",allocate_leave)
                                #                 # allocate_leave.sudo().action_approve()
                                #                 if allocate_leave:
                                #                     leave_bal_id = self.env['hr.employee.leave.info'].create({
                                #                                                                             'hr_employee_id':employee.id,
                                #                                                                             'holiday_status_id':leave.id,
                                #                                                                             'date':date.today(),
                                #                                                                             'leave_info':'credit',
                                #                                                                             'no_of_days':line.no_pf_leaves_credit
                                #                                                                         })
                        
    @api.model
    def encashment_leave_from_reimbursement(self,employee_id,branch_id,leave_id,number_of_days):
        print(employee_id,branch_id,leave_id,number_of_days)
        try:
            self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,state,holiday_type,number_of_days,create_uid,create_date,write_uid,write_date,is_lapsed,branch_id)
            VALUES ({employee_id},{leave_id},'Encashment Lapse From Reimbursement','Encashment Lapse From Reimbursement','validate','employee',{number_of_days*-1},{self.env.user.id},'{datetime.now()}',{self.env.user.id},'{datetime.now()}',True,{branch_id})""")
        except Exception as e: 
            print(str(e))               
            pass
        self.env['hr.leave.allocation'].invalidate_cache()   
                       
class LeaveTypeCreditPolicy(models.Model):
    _name = 'leave.type.credit.policy'
    _description = 'Leave Policy'
    
    leave_policy = fields.Many2one('hr.leave.type',string="Leave Type")
    day = fields.Integer(string="Day")
    month = fields.Selection([('January','January'),
                                ('February','February'),
                                ('March','March'),
                                ('April','April'),
                                ('May','May'),
                                ('June','June'),
                                ('July','July'),
                                ('August','August'),
                                ('September','September'),
                                ('October','October'),
                                ('November','November'),
                                ('December','December')
                            ],string="Month")
    no_pf_leaves_credit = fields.Integer(string="No Of Leaves Creadit")
    
    
class LeaveGrroup(models.Model):
    _name = 'hr.leave.group'
    _description = 'Leave Group'
    _rec_name = 'name'
    
    name = fields.Char(string="Name")


class AssignShift(models.TransientModel):
    _name           = 'assign.shift'
    _description    = 'STPI Shift Assignment Wizard'

    def _get_default_employee_records(self):
        datas = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
        return datas

    branch_id = fields.Many2one('res.branch', string="Center")
    employee_id = fields.Many2many('hr.employee', string="Employee", default=_get_default_employee_records)
    shift_id = fields.Many2one('resource.calendar', string="Shift")

    @api.onchange('branch_id')
    def show_employee(self):
        if self.branch_id:
            self.employee_id = False
            return {'domain': {'employee_id': ([('user_id.default_branch_id', '=', self.branch_id.id)]),
                                'shift_id': ([('branch_id', '=', self.branch_id.id)])}}
        else:
            pass

    @api.model
    def create(self, vals):
        new_record = super(AssignShift, self).create(vals)
        for employees in new_record.employee_id:
            values={}
            if employees.resource_calendar_id.id != new_record.shift_id.id:
                print("=-------------", employees.resource_calendar_id)
                values['resource_calendar_id'] = new_record.shift_id.id
                values['tz'] = new_record.shift_id.tz
            print('-----------------------1234',employees,values)
            employees.write(values)
        self.env.user.notify_success(message='Employee Shift Assigned successfully.')
        return new_record   

class LeaveTypeMaster(models.Model):
    _name           = 'leave.type.master'
    _description    = 'name'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")