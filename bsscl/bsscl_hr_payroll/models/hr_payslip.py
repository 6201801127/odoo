# -*- coding:utf-8 -*-

import babel
from datetime import date, datetime, time
import calendar
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
import re

def char_field_validation(string):
    state = True
    if string:
        pattern = "^[A-Za-z]+"
        state = re.match(pattern, string)
        return state
    return state

def char_number_field_validation(string):

    if string:
        pattern = r"^[A-Za-z0-9_-]+"
        if re.fullmatch(pattern, string) == None:
            return False
    return True


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _order = 'id desc'

    struct_id = fields.Many2one('hr.payroll.structure', string='Structure / संरचना',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Defines the rules that have to be applied to this payslip, accordingly '
             'to the contract chosen. If you let empty the field contract, this field isn\'t '
             'mandatory anymore and thus the rules applied will be all the rules set on the '
             'structure of all contracts of the employee valid for the chosen period / इस पेस्लिप पर लागू होने वाले नियमों को परिभाषित करता है, तदनुसार '
             'चुने गए अनुबंध के लिए। यदि आप फ़ील्ड अनुबंध को खाली करते हैं, तो यह फ़ील्ड नहीं है अब अनिवार्य है और इस प्रकार लागू होने वाले नियम सभी नियमों पर निर्धारित होंगे'
             'चुने हुए अवधि के लिए मान्य कर्मचारी के सभी अनुबंधों की संरचना')
    name = fields.Char(string='Payslip Name / पेस्लिप नाम', readonly=True,
        states={'draft': [('readonly', False)]})
    number = fields.Char(string='Reference / संकेत', readonly=True, copy=False,
        states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee / कर्मचारी', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Date From / तिथि से', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To /तिथि तक', readonly=True, required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
        states={'draft': [('readonly', False)]})
    # this is chaos: 4 states are defined, 3 are used ('verify' isn't) and 5 exist ('confirm' seems to have existed)
    state = fields.Selection([
        ('draft', 'Draft / प्रारूप'),
        ('verify', 'Waiting / इंतज़ार में'),
        ('done', 'Done / पूर्ण'),
        ('cancel', 'Rejected / अस्वीकार कर दिया'),
    ], string='Status / स्थति', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'. / * जब भुगतान पर्ची बनाई जाती है तो स्थिति \'ड्राफ्ट\' होती है
                \n* यदि भुगतान पर्ची सत्यापन के अधीन है, तो स्थिति \'प्रतीक्षारत\' है।
                \n* यदि भुगतान पर्ची की पुष्टि हो जाती है तो स्थिति \'हो गया\' पर सेट हो जाती है।
                \n* जब उपयोगकर्ता भुगतान पर्ची रद्द करता है तो स्थिति \'अस्वीकृत\' होती है।""")
    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines / पेस्लिप लाइन्स', readonly=True,
        states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company / कंपनी', readonly=True, copy=False,
                                 default=lambda self: self.env.company,
                                 states={'draft': [('readonly', False)]})
    worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id',
        string='Payslip Worked Days / पेस्लिप कार्य दिवस', copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    input_line_ids = fields.One2many('hr.payslip.input', 'payslip_id', string='Payslip Inputs / पेस्लिप इनपुट्स',
        readonly=True, states={'draft': [('readonly', False)]})
    paid = fields.Boolean(string='Made Payment Order ? / भुगतान आदेश दिया?', readonly=True, copy=False,
        states={'draft': [('readonly', False)]})
    note = fields.Text(string='Internal Note / आंतरिक टिप्पणी', readonly=True, states={'draft': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string='Contract / अनुबंध', readonly=True,
        states={'draft': [('readonly', False)]})
    details_by_salary_rule_category = fields.One2many('hr.payslip.line',
        compute='_compute_details_by_salary_rule_category', string='Details by Salary Rule Category / वेतन नियम श्रेणी द्वारा विवर')
    credit_note = fields.Boolean(string='Credit Note / क्रेडिट नोट', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Indicates this payslip has a refund of another / इंगित करता है कि इस भुगतान पर्ची में दूसरे का धनवापसी है")
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches / पेस्लिप बैच', readonly=True,
        copy=False, states={'draft': [('readonly', False)]})
    payslip_count = fields.Integer(compute='_compute_payslip_count', string="Payslip Computation Details / भुगतान पर्ची संगणना विवरण")

    @api.constrains('date_from','date_to')
    def _check_duplicate_paslip(self):
        model_id = self.env['hr.payslip'].sudo().search([]) - self
        print("Month=========",self.date_from.month, self.date_to.month)
        if model_id:
            for rec in self:
                for record in model_id:
                    if rec.employee_id == record.employee_id and (rec.date_from == record.date_from and rec.date_to == record.date_to):
                        raise ValidationError('you can not create payslip for same user in same date period')
        if self.date_from >= date.today() or self.date_to >= date.today():
            raise ValidationError('You can not create payslip for future date.')
        if self.date_from.month != self.date_to.month:
            raise ValidationError('You can not create payslip for more than one months')
        if self.date_from.month == self.create_date.month:
            input_dt = self.create_date
            res = calendar.monthrange(input_dt.year, input_dt.month)
            day = res[1]
            if day != self.create_date.day:
                raise ValidationError('You can not create payslip in mid of the months')
              

    @api.constrains('contract_id')
    @api.onchange('contract_id')
    def validate_contract_id(self):
        if self.employee_id:
            if not self.contract_id:
                raise ValidationError('User not in contract.')
            if self.contract_id.state != 'open':
                raise ValidationError('User contract not in running state.')
        
    @api.onchange('number', 'note')
    def validate_char_and_num(self):
        if self.number:
            data = self.number
            result = char_number_field_validation(self.number)
            if result == False:
                raise ValidationError('Only use digits and alphabates combinations !')
            note = char_number_field_validation(self.note)
            if note == False:
                raise ValidationError('Only use digits and alphabates combinations !')

    def _compute_details_by_salary_rule_category(self):
        for payslip in self:
            payslip.details_by_salary_rule_category = payslip.mapped('line_ids').filtered(lambda line: line.category_id)

    def _compute_payslip_count(self):
        for payslip in self:
            payslip.payslip_count = len(payslip.line_ids)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(self.filtered(lambda payslip: payslip.date_from > payslip.date_to)):
            raise ValidationError(_("Payslip 'From Date' must be earlier 'To Date'."))

    def action_payslip_draft(self):
        return self.write({'state': 'draft'})

    def action_payslip_done(self):
        self.compute_sheet()
        return self.write({'state': 'done'})

    def action_payslip_cancel(self):
        # if self.filtered(lambda slip: slip.state == 'done'):
        #     raise UserError(_("Cannot cancel a payslip that is done."))
        return self.write({'state': 'cancel'})

    def refund_sheet(self):
        for payslip in self:
            copied_payslip = payslip.copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()
        form_view_ref = self.env.ref('bsscl_hr_payroll.view_hr_payslip_form', False)
        tree_view_ref = self.env.ref('bsscl_hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': (_("Refund Payslip")),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(tree_view_ref and tree_view_ref.id or False, 'tree'), (form_view_ref and form_view_ref.id or False, 'form')],
            'context': {}
        }

    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('bsscl_hr_payroll.mail_template_payslip').id
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def check_done(self):
        return True

    def unlink(self):
        if any(self.filtered(lambda payslip: payslip.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
        return super(HrPayslip, self).unlink()

    # TODO move this function into hr_contract module, on hr.employee object
    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|', '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
        return True

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.name or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours

            # compute worked days
            work_data = contract.employee_id._get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            # print("------------------------------------",work_data,self.date_from,self.date_to)
            present_day = self.env['hr.attendance'].sudo().search([('employee_id','=',self.employee_id.id)])
            count= 0
            working_hour =0
            for rec in present_day:
                if rec.check_in.date() >= self.date_from and rec.check_in.date() <= self.date_to:
                    count = count+1
                    working_hour = working_hour + rec.open_worked_hours
            # print("present day ==================================",count,working_hour)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'present_days': count,
                'present_hours': working_hour,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []

        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            for input in inputs:
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': contract.id,
                }
                res += [input_data]
        return res

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
        #get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        #get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())

    # YTI TODO To rename. This method is not really an onchange, as it is not in any view
    # employee_id and contract_id could be browse records
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        #defaults
        res = {
            'value': {
                'line_ids': [],
                #delete old input lines
                'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
                #delete old worked days lines
                'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
                #'details_by_salary_head':[], TODO put me back
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang') or 'en_US'
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)

        if not contract_ids:
            return res
        contract = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.ensure_one()
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        if contracts:
            worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_ids:
                worked_days_lines += worked_days_lines.new(r)
            self.worked_days_line_ids = worked_days_lines

            input_line_ids = self.get_inputs(contracts, date_from, date_to)
            input_lines = self.input_line_ids.browse([])
            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines
            return

    @api.onchange('contract_id')
    def onchange_contract(self):
        if not self.contract_id:
            self.struct_id = False
        self.with_context(contract=True).onchange_employee()
        return

    def get_salary_line_total(self, code):
        self.ensure_one()
        line = self.line_ids.filtered(lambda line: line.code == code)
        if line:
            return line[0].total
        else:
            return 0.0


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _inherit = 'hr.salary.rule'
    _description = 'Payslip Line'
    _order = 'contract_id, sequence'

    slip_id = fields.Many2one('hr.payslip', string='Pay Slip / वेतन पर्ची', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule / नियम', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee / कर्मचारी', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract / अनुबंध', required=True, index=True)
    rate = fields.Float(string='Rate / दर(%)', default=100.0)
    amount = fields.Float(string='Amount / राशि')
    quantity = fields.Float(default=1.0 , string='Quantity / मात्रा')
    total = fields.Float(compute='_compute_total', string='Total / कुल')

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
                if not values['contract_id']:
                    raise UserError(_('You must set a contract to create a payslip line.'))
        return super(HrPayslipLine, self).create(vals_list)


class HrPayslipWorkedDays(models.Model):
    _name = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description / विवरण', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip / वेतन पर्ची', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10, string='Sequence/ अनुक्रम')
    code = fields.Char(required=True, help="The code that can be used in the salary rules / वह कोड जिसका उपयोग वेतन नियमों में किया जा सकता है",string='Code/ कोड')
    number_of_days = fields.Float(string='Number of Days / दिनों की संख्या')
    number_of_hours = fields.Float(string='Number of Hours / घंटों की संख्या')
    present_days = fields.Float(string='Days Present / उपस्थित दिन')
    present_hours = fields.Float(string='Hours Present / उपस्थित घंटे')
    contract_id = fields.Many2one('hr.contract', string='Contract / अनुबंध', required=True,
        help="The contract for which applied this input / वह अनुबंध जिसके लिए यह इनपुट लागू किया गया था")

    # @api.constrains('name', 'code')
    # @api.onchange('name', 'code')
    # def validate_char_and_num(self):
    #     if self.name:
    #         result = char_number_field_validation(self.name)
    #         if result == False:
    #             raise ValidationError('Only use characters and Digits for description')
    #     if self.code:
    #         result = char_number_field_validation(self.code)
    #         if result == False:
    #             raise ValidationError('Only use characters and Digits for code')

class HrPayslipInput(models.Model):
    _name = 'hr.payslip.input'
    _description = 'Payslip Input'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description / विवरण', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip / वेतन पर्ची', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10,string='Sequence/ अनुक्रम')
    code = fields.Char(required=True, help="The code that can be used in the salary rules / वह कोड जिसका उपयोग वेतन नियमों में किया जा सकता है",string='Code/ कोड')
    amount = fields.Float(help="It is used in computation. For e.g. A rule for sales having "
                               "1% commission of basic salary for per product can defined in expression "              "like result = inputs.SALEURO.amount * contract.wage*0.01. / इसका उपयोग गणना में किया जाता है। उदाहरण के लिए बिक्री के लिए एक नियम "
                               "प्रति उत्पाद के लिए मूल वेतन का 1% कमीशन अभिव्यक्ति में परिभाषित किया जा सकता है"
                               "लाइक रिजल्ट = इनपुट्स",string='Amount / राशि')
    contract_id = fields.Many2one('hr.contract', string='Contract / अनुबंध', required=True,
        help="The contract for which applied this input / वह अनुबंध जिसके लिए यह इनपुट लागू किया गया था")

    # @api.constrains('name', 'code')
    # @api.onchange('name', 'code')
    # def validate_char_and_num(self):
    #     if self.name:
    #         result = char_number_field_validation(self.name)
    #         if result == False:
    #             raise ValidationError('Only use characters and Digits for description')
    #     if self.code:
    #         result = char_number_field_validation(self.code)
    #         if result == False:
    #             raise ValidationError('Only use characters and Digits for code')


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _description = 'Payslip Batches'

    name = fields.Char(required=True, readonly=True,string='Description / विवरण', states={'draft': [('readonly', False)]})
    slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips / वेतन पर्ची', readonly=True,
                               states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft / प्रारूप'),
        ('done', 'Done / पूर्ण'),
        ('close', 'Close / बंद करना'),
    ], string='Status / स्थति', index=True, readonly=True, copy=False, default='draft')
    date_start = fields.Date(string='Date From / तिथि से', required=True, readonly=True,
                             states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date(string='Date To / तिथि तक', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    credit_note = fields.Boolean(string='Credit Note / क्रेडिट नोट', readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 help="If its checked, indicates that all payslips generated from here are refund payslips. / यदि इसकी जाँच की जाती है, तो यह इंगित करता है कि यहाँ से उत्पन्न सभी पेस्लिप्स रिफंड पेस्लिप्स हैं")

    @api.onchange('name')
    def validate_char_and_num(self):
        if self.name:
            data = self.name
            result = char_number_field_validation(self.name)
            if result == False:
                raise ValidationError('Only use digits and alphabates combinations !')
            
    @api.constrains('date_start','date_end')
    def _check_batch_date(self):
        if self.date_start >= self.date_end:
            raise ValidationError('Please select valid date period....End date should not less than or equal to start date.')
        if self.date_start >= date.today() or self.date_end >= date.today():
            raise ValidationError('You can not create payslip batch for future date.')
        if self.date_start.month != self.date_end.month:
            raise ValidationError('You can not create payslip batch for more than one months')
    def draft_payslip_run(self):
        return self.write({'state': 'draft'})

    def close_payslip_run(self):
        return self.write({'state': 'close'})

    def done_payslip_run(self):
        for line in self.slip_ids:
            line.action_payslip_done()
        return self.write({'state': 'done'})

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_('You Cannot Delete Done Payslips Batches / आप पूर्ण भुगतान पर्ची बैचों को हटा नहीं सकते'))
        return super(HrPayslipRun, self).unlink()
