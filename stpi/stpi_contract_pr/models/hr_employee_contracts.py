from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError

class InheritContractss(models.Model):
    _inherit = 'hr.contract'
    _description = 'HR Contract'

    recruitment_type = fields.Selection([('absorption', 'Absorption'),
                                     ('compassion', 'Compassionate Appt.'),
                                     ('deputation', 'Deputation'),
                                     ('deput_absorp', 'Deputation & Absorption'),
                                     ('direct', 'Direct recruitment'),
                                     ('drabsorp', 'DR & Absorption'),
                                     ('promo', 'Promotion'),
                                    ],string='Mode of Promotion')

    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',related='employee_id.employee_type',store=True
                                     )

    basicinc = fields.Float(string='Basic Increment %')
    da = fields.Float(string='DA %')
    supplementary_allowance = fields.Float(string='Supplementary Allowance')
    voluntary_provident_fund = fields.Float(string='Voluntary Provident Fund')
    xnohra = fields.Boolean(string='Rent Recovery?')
    pf_deduction = fields.Boolean(string='PF Deduction')
    transport_deduction = fields.Boolean(string='Transport Deduction')
    updated_basic = fields.Float(string='Basic + DA', compute='_compute_updated_basic_f_da')

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell', track_visibility='onchange')
    
    #added by Sangita to rename the core field name
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Type')
    #added by sangita to rename the expired stage to Past Service
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Past Service'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states',
       track_visibility='onchange', help='Status of the contract', default='draft')
    
    #added by sangita to rename End of Trial Period to End of Probation Period
    trial_date_end = fields.Date('End of Probation Period',
        help="End date of the trial period (if there is one).")



    city_id = fields.Many2one('res.city', string='City', store=True, compute='compute_hra_tier')

    employee_hra_cat = fields.Selection([('x', 'X'),
                                     ('y', 'Y'),
                                     ('z', 'Z'),
                                    ],string='HRA Category', compute='compute_hra_tier', store=True)
    city_tier = fields.Selection([('a', 'A'),
                                     ('a1', 'A1'),
                                     ('other', 'Other'),
                                    ],string='City Tier', compute='compute_hra_tier', store=True)


    misc_deduction = fields.Monetary(string="Misc. Deducation")
    license_dee = fields.Monetary(string=" License Fee")
    tds_amount = fields.Monetary('TDS')
    arrear_amount = fields.Monetary('Arrear')
    date_start = fields.Date('Start Date', required=True, default=fields.Date.today,track_visibility='onchange',help="Start date of the contract.")
    date_end = fields.Date('End Date',track_visibility='onchange',help="End date of the contract (if it's a fixed-term contract).")

    effective_from_date = fields.Date("Effective From")
    change_log_ids = fields.One2many("contract_basic_da_change_log","contract_id",string="Change Logs")
    check_vpf_manager = fields.Boolean(default=False, compute='_compute_updated_basic_f_da')
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Schedule')

    @api.multi
    @api.depends('employee_id')
    def compute_hra_tier(self):
        for rec in self:
            rec.city_id = rec.employee_id.branch_id.city_id.id
            rec.employee_hra_cat = rec.employee_id.branch_id.city_id.employee_hra_cat
            rec.city_tier = rec.employee_id.branch_id.city_id.city_tier

    @api.depends('wage','da')
    def _compute_updated_basic_f_da(self):
        for rec in self:
            rec.updated_basic = rec.wage * (1 + rec.da/100)
            if self.env.user.has_group('stpi_contract_pr.group_contract_vpf_officer'):
                rec.check_vpf_manager = True

    @api.onchange('basicinc')
    def update_basic(self):
        for rec in self:
            if rec.basicinc > 0:
                rec.wage += rec.wage * (rec.basicinc / 100)

    @api.model
    def create(self, vals):
        res = super(InheritContractss, self).create(vals)
        default_da = self.env['ir.config_parameter'].sudo().get_param('hr_contract.default_da_inc')
        res.da = int(default_da) if default_da else 0
        duplicate_contract = self.search([('employee_id', '=', res.employee_id.id), 
                                            ('state', 'not in', ['close','cancel'])]) - res
        if duplicate_contract:
            raise ValidationError(_("You already have a contract created"))
        return res

    @api.multi
    def write(self,vals):
        res = super(InheritContractss,self).write(vals)
        if 'effective_from_date' in vals or 'wage' in vals or 'da' in vals:
            log = self.env['contract_basic_da_change_log']
            for contract in self:
                val_dict = {
                    'date':contract.effective_from_date,
                    'wage':contract.wage,
                    'contract_id':contract.id,
                    'da':contract.da,
                    'basic_da':contract.updated_basic,
                }
                log.create(val_dict)
        return res


    #
    # @api.constrains('employee_id')
    # @api.onchange('employee_id')
    # def _get_add_city(self):
    #     for rec in self:
    #         # if rec.employee_id:
    #         #     rec.employee_type = rec.employee_id.employee_type
    #         #     rec.mode_of_promotion = rec.employee_id.mode_of_promotion
    #         if rec.city_id.name:
    #             if rec.city_id.name == 'Hyderabad' or rec.city_id.name == 'Delhi' or rec.city_id.name == 'Banglore' or rec.city_id.name == 'Mumbai' or rec.city_id.name == 'Chennai' or rec.city_id.name == 'Kolkata':
    #                 rec.city_tier = 'a1'
    #             elif rec.city_id.name == 'Ahmedabad' or rec.city_id.name == 'Surat' or rec.city_id.name == 'Kanpur' or rec.city_id.name == 'Patna' or rec.city_id.name == 'Kochi' or rec.city_id.name == 'Indore' or rec.city_id.name == 'Nagpur' or rec.city_id.name == 'Pune' or rec.city_id.name == 'Lucknow':
    #                 rec.city_tier = 'a'
    #             else:
    #                 rec.city_tier = 'other'


    # @api.constrains('pay_level')
    # @api.onchange('pay_level')
    # def _get_pay_wage(self):
    #     for rec in self:
    #         rec.wage = rec.pay_level.entry_pay


    def process_contract_cron(self):
        emp_contract = self.env['hr.contract'].search([('employee_type','=','regular'),('state', '=', 'open')])
        for employee in emp_contract:
            expiry_date = employee.date_start + relativedelta(years=1)
            todays_date = datetime.now().date()
            if expiry_date == todays_date:
                employee.state = 'close'
                create_contract = self.env['hr.contract'].create(
                    {
                        'state': 'open',
                        'name': employee.name,
                        'employee_id': employee.employee_id.id,
                        'department_id': employee.department_id.id,
                        'job_id': employee.job_id.id,
                        'pay_level_id': employee.pay_level_id.id,
                        'pay_level': employee.pay_level.id,
                        'struct_id': employee.struct_id.id,
                        'type_id': employee.type_id.id,
                        'date_start': datetime.now().date(),
                        'employee_type': 'regular',
                        'recruitment_type': employee.recruitment_type,
                        'wage': employee.wage,
                    }
                )

    @api.multi
    def action_mass_update_da(self):
        default_da = self.env['ir.config_parameter'].sudo().get_param('hr_contract.default_da_inc')
        da_efective_date = self.env['ir.config_parameter'].sudo().get_param('hr_contract.da_effective_date')
        try:
            if default_da:
                for rec in self:
                    data = {'da': float(default_da)}
                    if da_efective_date:
                        data['effective_from_date'] = da_efective_date
                    rec.write(data)
            else:
                raise ValidationError('Please set default DA percentage first!')
        except ValueError as err:
            raise ValidationError(f'{str(err).capitalize()}\n Please set correct value of DA percentage in configuration.')


    @api.multi
    def action_mass_update_basic(self):
        for rec in self:
            service_level = rec.pay_level.service_level
            data = {}
            # basic_effective_date = self.env['ir.config_parameter'].sudo()\
            #                                 .get_param('hr_contract.basic_effective_date')
            if service_level:
                promoted_level = rec.pay_level_id.entry_pay_ids\
                                        .filtered(lambda x: x.service_level == (service_level + 1))
                if promoted_level:
                    updated_wage = sum(promoted_level.mapped('entry_pay'))
                    data['wage'] = updated_wage
                    data['pay_level'] = promoted_level.id
                    data['effective_from_date'] = fields.Date.today()
                    rec.write(data)
        return True


        # default_basic = self.env['ir.config_parameter'].sudo().get_param('hr_contract.default_basic_inc')
        # basic_effective_date = self.env['ir.config_parameter'].sudo().get_param('hr_contract.basic_effective_date')
        # print("DTAA ARE",default_basic,basic_effective_date,type(basic_effective_date))
        # try:
        #     if default_basic:
        #         for rec in self:
        #             updated_basicinc = rec.basicinc + float(default_basic)
        #             updated_wage = rec.wage + (rec.wage * (updated_basicinc / 100))
        #             data = {'basicinc': updated_basicinc, 
        #                     'wage': updated_wage, 'code':'basic'}
        #             if basic_effective_date:
        #                 data['effective_from_date'] = basic_effective_date
        #             rec.write(data)
        #             # rec.update_basic()
        #     else:
        #         raise ValidationError('Please set default Basic percentage first!')
        # except ValueError as err:
        #     raise ValidationError(f'{str(err).capitalize()}\n Please set correct value of Basic percentage in configuration.')

    def update_log_basic_da(self):
        cur_date = date.today()
        if cur_date == date(cur_date.year, 1, 31):
            contract_ids = self.env['hr.contract'].search([('employee_type','=','regular'),
                                                            ('state', '=', 'open')])
            for contract in contract_ids:
                log_line = [[0, 0, {"date": cur_date,
                                    "wage": contract.wage,
                                    "da": contract.da,
                                    "basic_da": contract.updated_basic}]]
                contract.write({'change_log_ids': log_line})
        return True

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_domain'):
            args += [('employee_id.branch_id','in',self.env.user.branch_ids.ids)]

        return super(InheritContractss, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_domain'):
            domain += [('employee_id.branch_id','in',self.env.user.branch_ids.ids)]
            
        return super(InheritContractss, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

# class HrEmployeeContract(models.Model):
#     _inherit = 'hr.employee'

#     @api.multi
#     def view_hr_contract(self):
#         # return {
#         #         'type': 'ir.actions.act_window',

#         #         'name': 'Contracts',
#         #         'view_type': 'form',
#         #         'view_mode': 'tree',
#         #         'res_model': 'hr.contract',
#         #         'target': 'current',
#         #         'domain':[('employee_id','=',self.id)],
#         #         # 'context':{
#         #         #         'search_default_employee_id': self.id,
#         #         #         'default_employee_id': self.id,
#         #         #         'search_default_group_by_state': True,
#         #         #             }
#         #         }

#         self.ensure_one()
#         action = self.env['ir.actions.act_window'].for_xml_id('hr_contract', 'action_hr_contract')
#         action['domain'] = [('employee_id','=',self.id)]
#         return action
