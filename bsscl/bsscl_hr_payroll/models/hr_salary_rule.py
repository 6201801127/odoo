# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrPayrollStructure(models.Model):
    """
    Salary structure used to defined
    - Basic
    - Allowances
    - Deductions
    """
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'

    @api.model
    def _get_parent(self):
        return self.env.ref('bsscl_hr_payroll.structure_base', False)

    name = fields.Char(required=True,string='Name / नाम')
    code = fields.Char(string='Reference / संकेत', required=True)
    company_id = fields.Many2one('res.company', string='Company / कंपनी', required=True, default=lambda self: self.env.company)
    note = fields.Text(string='Description / विवरण')
    parent_id = fields.Many2one('hr.payroll.structure', string='Parent / प्रबंधक', default=_get_parent)
    children_ids = fields.One2many('hr.payroll.structure', 'parent_id', string='Children / अधीनस्थ', copy=True)
    rule_ids = fields.Many2many('hr.salary.rule', 'hr_structure_salary_rule_rel', 'struct_id', 'rule_id', string='Salary Rules / वेतन नियम')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create a recursive salary structure. / आप एक पुनरावर्ती वेतन संरचना नहीं बना सकते।'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, code=_("%s (copy)") % (self.code))
        return super(HrPayrollStructure, self).copy(default)

    def get_all_rules(self):
        """
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        """
        all_rules = []
        for struct in self:
            all_rules += struct.rule_ids._recursive_search_of_rules()
        return all_rules

    def _get_parent_structure(self):
        parent = self.mapped('parent_id')
        if parent:
            parent = parent._get_parent_structure()
        return parent + self


class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    company_id = fields.Many2one('res.company', string='Company / कंपनी', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner / पार्टनर')
    name = fields.Char(required=True, string="Name / नाम")
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',
        string='Register Line / रजिस्टर लाइन', readonly=True)
    note = fields.Text(string='Description / विवरण' )


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'

    name = fields.Char(required=True, translate=True, string="Name / नाम")
    code = fields.Char(required=True, string="Code / कोड")
    parent_id = fields.Many2one('hr.salary.rule.category', string='Parent / प्रबंधक',
        help="Linking a salary category to its parent is used only for the reporting purpose.")
    children_ids = fields.One2many('hr.salary.rule.category', 'parent_id', string='Children / अधीनस्थ')
    note = fields.Text(string='Description / विवरण' )
    company_id = fields.Many2one('res.company', string='Company / कंपनी', default=lambda self: self.env.company)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive hierarchy of Salary Rule Category. / गलती! आप वेतन नियम श्रेणी का पुनरावर्ती पदानुक्रम नहीं बना सकते।'))


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _order = 'sequence, id'
    _description = 'Salary Rule'

    name = fields.Char(required=True, translate=True , string="Name / नाम")
    code = fields.Char(required=True,string="Code / कोड",
        help="The code of salary rules can be used as reference in computation of other rules. "
             "In that case, it is case sensitive. / वेतन नियमों की संहिता का उपयोग अन्य नियमों की गणना में संदर्भ के रूप में किया जा सकता है। "
             "उस मामले में, यह केस संवेदी है।")
    sequence = fields.Integer(required=True, index=True, default=5,
        help='Use to arrange calculation sequence / गणना क्रम को व्यवस्थित करने के लिए उपयोग करें',string='Sequence/ अनुक्रम')
    quantity = fields.Char(default='1.0',
        help="It is used in computation for percentage and fixed amount. "
             "For e.g. A rule for Meal Voucher having fixed amount of "
             u"1€ per worked day can have its quantity defined in expression "
             "like worked_days.WORK100.number_of_days. / इसका उपयोग प्रतिशत और निश्चित राशि के लिए गणना में किया जाता है। "
             "उदाहरण के लिए भोजन वाउचर के लिए एक नियम जिसकी निश्चित राशि है"
             u"1€ प्रति कार्य दिवस इसकी मात्रा को अभिव्यक्ति में परिभाषित कर सकता है"
             "काम_दिनों की तरह। WORK100.number_of_days।")
    category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
    active = fields.Boolean(default=True,string="क्रियाशील",
        help="If the active field is set to false, it will allow you to hide the salary rule without removing it. / यदि सक्रिय फ़ील्ड गलत पर सेट है, तो यह आपको वेतन नियम को हटाए बिना छिपाने की अनुमति देगा।")
    appears_on_payslip = fields.Boolean(string='Appears on Payslip / वेतन पर्ची पर दिखाई देता है', default=True,
        help="Used to display the salary rule on payslip. / वेतन पर्ची पर वेतन नियम प्रदर्शित करते थे।")
    parent_rule_id = fields.Many2one('hr.salary.rule', string='Parent Salary Rule / प्रबंधक वेतन नियम', index=True)
    company_id = fields.Many2one('res.company', string='Company / कंपनी' , default=lambda self: self.env.company)
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('range', 'Range'),
        ('python', 'Python Expression')
    ], string="Condition Based on / स्थिति के आधार पर", default='none', required=True)
    condition_range = fields.Char(string='Range Based on', default='contract.wage',
        help='This will be used to compute the % fields values; in general it is on basic, '
             'but you can also use categories code fields in lowercase as a variable names '
             '(hra, ma, lta, etc.) and the variable basic. / इसका उपयोग % फ़ील्ड मानों की गणना करने के लिए किया जाएगा; सामान्य तौर पर यह बुनियादी है, '
             'लेकिन आप चर नामों के रूप में लोअरकेस में श्रेणियों के कोड फ़ील्ड का भी उपयोग कर सकते हैं'
             '(एचआरए, एमए, एलटीए, आदि) और वेरिएबल बेसिक।')
    condition_python = fields.Text(string='Python Condition / पायथन की स्थिति', required=True,
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days
                    # inputs: object containing the computed inputs

                    # Note: returned value have to be set in the variable 'result'

                    result = rules.NET > categories.NET * 0.10''',
        help='Applied this rule for calculation if condition is true. You can specify condition like basic > 1000. / यदि शर्त सत्य है तो गणना के लिए इस नियम को लागू करें। आप बुनियादी > 1000 जैसी शर्त निर्दिष्ट कर सकते हैं।')
    condition_range_min = fields.Float(string='Minimum Range / न्यूनतम सीमा', help="The minimum amount, applied for this rule. / इस नियम के लिए लागू न्यूनतम राशि।")
    condition_range_max = fields.Float(string='Maximum Range / अधिकतम सीमा', help="The maximum amount, applied for this rule. / इस नियम के लिए लागू की गई अधिकतम राशि।")
    amount_select = fields.Selection([
        ('percentage', 'Percentage (%) / प्रतिशत (%)'),
        ('fix', 'Fixed Amount / निश्चित राशि'),
        ('code', 'Python Code / पायथन कोड'),
    ], string='Amount Type / राशि प्रकार', index=True, required=True, default='fix', help="The computation method for the rule amount. / नियम राशि के लिए गणना विधि।")
    amount_fix = fields.Float(string='Fixed Amount / निश्चित राशि')
    amount_percentage = fields.Float(string='Percentage / प्रतिशतता(%)',
        help='For example, enter 50.0 to apply a percentage of 50% / उदाहरण के लिए, 50% का प्रतिशत लागू करने के लिए 50.0 दर्ज करें')
    amount_python_compute = fields.Text(string='Python Code / पायथन कोड' ,
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable 'result'

                    result = contract.wage * 0.10''')
    amount_percentage_base = fields.Char(string='Percentage based on / प्रतिशत के आधार पर', help='result will be affected to a variable / परिणाम एक चर से प्रभावित होगा')
    child_ids = fields.One2many('hr.salary.rule', 'parent_rule_id', string='Child Salary Rule / अधीनस्थ वेतन नियम', copy=True)
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register / अंशदान रजिस्टर',
        help="Eventual third party involved in the salary payment of the employees. / अंततः कर्मचारियों के वेतन भुगतान में शामिल तीसरा पक्ष।")
    input_ids = fields.One2many('hr.rule.input', 'input_id', string='Inputs / इनपुट', copy=True)
    note = fields.Text(string='Description / विवरण')

    @api.constrains('parent_rule_id')
    def _check_parent_rule_id(self):
        if not self._check_recursion(parent='parent_rule_id'):
            raise ValidationError(_('Error! You cannot create recursive hierarchy of Salary Rules. / गलती! आप वेतन नियमों का पुनरावर्ती पदानुक्रम नहीं बना सकते।'))

    def _recursive_search_of_rules(self):
        """
        @return: returns a list of tuple (id, sequence) which are all the children of the passed rule_ids
        """
        children_rules = []
        for rule in self.filtered(lambda rule: rule.child_ids):
            children_rules += rule.child_ids._recursive_search_of_rules()
        return [(rule.id, rule.sequence) for rule in self] + children_rules

    #TODO should add some checks on the type of result (should be float)
    def _compute_rule(self, localdict):
        """
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """
        self.ensure_one()
        if self.amount_select == 'fix':
            try:
                return self.amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'percentage':
            try:
                return (float(safe_eval(self.amount_percentage_base, localdict)),
                        float(safe_eval(self.quantity, localdict)),
                        self.amount_percentage)
            except:
                raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).') % (self.name, self.code))
        else:
            try:
                safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

    def _satisfy_condition(self, localdict):
        """
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        """
        self.ensure_one()

        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'range':
            try:
                result = safe_eval(self.condition_range, localdict)
                return self.condition_range_min <= result and result <= self.condition_range_max or False
            except:
                raise UserError(_('Wrong range condition defined for salary rule %s (%s).') % (self.name, self.code))
        else:  # python code
            try:
                safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise UserError(_('Wrong python condition defined for salary rule %s (%s).') % (self.name, self.code))


class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _description = 'Salary Rule Input'

    name = fields.Char(string='Description / विवरण', required=True)
    code = fields.Char(required=True, string='Code / कोड',help="The code that can be used in the salary rules / वह कोड जिसका उपयोग वेतन नियमों में किया जा सकता है")
    input_id = fields.Many2one('hr.salary.rule', string='Salary Rule Input / वेतन नियम इनपुट', required=True)
