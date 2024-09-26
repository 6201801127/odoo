from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date,datetime

state_list = [
    ('Bihar','Bihar'),
    ('Delhi','Delhi'),
    ('Himachal Pradesh','Himachal Pradesh'),
    ('Jharkhand','Jharkhand'),
    ('Karnataka','Karnataka'),
    ('Maharashtra','Maharashtra'),
    ('Meghalaya','Meghalaya'),
    ('Odisha','Odisha'),
    ('Uttar Pradesh','Uttar Pradesh')
]

nature_of_payment = [
    ('Contractor','Contractor'),
    ('Employees','Employees'),
    ('Professional','Professional'),
    ('Rent','Rent'),
    ('Purchase Of Property','Purchase Of Property'),
    ('Payment to Non-Resident','Payment to Non-Resident'),
    ('Purchase of Goods','Purchase of Goods'),
    ('Commission Or Brokerage','Commission Or Brokerage'),
    ('Dividend','Dividend'),
]

under_section = [
    ('U/s-94C','U/s-94C'),
    ('U/s-92B','U/s-92B'),
    ('U/s-94J','U/s-94J'),
    ('U/s-94I','U/s-94I'),
    ('U/s-194IA','U/s-194IA'),
    ('U/s-195','U/s-195'),
    ('U/s-194Q','U/s-194Q'),
    ('U/s-194','U/s-194'),
    ('U/s-94H','U/s-94H')
]

class AccountInherit(models.Model):
    _name = 'account.account'
    _inherit = 'account.account'

    branch_id = fields.Many2one('accounting.branch.unit', 'Branch',required=True)
    is_budget_mandatory = fields.Boolean('Is Budget Mandatory', default=False)
    # group2 = fields.Many2one('group_type', string='Group Type', required=True)
    # group3 = fields.Many2one('group_head', string='Group Head', required=True) 
    # kw_code = fields.Char(string="Kwantify Code")
    # group_name = fields.Char(string="Group Name") 
    # account_subhead = fields.Char(string="Account Subhead")
    reconcile = fields.Boolean(string='Allow Reconciliation', default=True,
        help="Check this box if this account allows invoices & payments matching of journal items.")

    group_type = fields.Many2one('kw.group.type',string="Group Type")
    group_name = fields.Many2one('account.group.name',string="Group Name")
    account_head_id = fields.Many2one('account.head',string="Account Head")
    account_sub_head_id = fields.Many2one('account.sub.head',string="Account Sub Head")
    partner_type = fields.Selection([('customer','Customer'),('vendor','Vendor'),('employee','Employee')],string="Partner Type")
    sequence = fields.Integer(string="Sequence.")
    active = fields.Boolean(string='Archive',default=True)
    ledger_type = fields.Selection([('bank','Bank'),('cash','Cash'),('others','Other')],string="Ledger Type",default="others")
    effective_from =fields.Date("Effective From")
    tds = fields.Boolean(string="TDS Applicable")
    nature_of_payment = fields.Selection(nature_of_payment,string="Nature")
    under_section = fields.Selection(under_section,string="Under Section")
    tds_type = fields.Selection([('payable','Payable'),('receivabale','Receivabale')],string="TDS Type")
    kw_ledger_code = fields.Char("Tendrils Ledger Code")
    advance_ledger = fields.Boolean(string="Advance Ledger")
    advance_opening_balance = fields.One2many('advance_ledger_opening_balance','parent_id',string="Opening Balance")
    
    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id,group_type,user_type_id,group_name,account_head_id,account_sub_head_id,name)', 'The code or Name of the account must be unique per company !')
    ]

    @api.multi
    @api.constrains('user_type_id')
    def _check_user_type_id(self):
        data_unaffected_earnings = self.env.ref('account.data_unaffected_earnings')
        result = self.read_group([('user_type_id', '=', data_unaffected_earnings.id)], ['company_id'], ['branch_id'])
        for res in result:
            if res.get('company_id_count', 0) >= 2:
                account_unaffected_earnings = self.search([('company_id', '=', res['company_id'][0]),
                                                           ('user_type_id', '=', data_unaffected_earnings.id)])
                raise ValidationError(_('You cannot have more than one account with "Current Year Earnings" as type. (accounts: %s)') % [a.code for a in account_unaffected_earnings])


    @api.onchange('internal_type')
    def onchange_internal_type(self):
        self.reconcile = True
        if self.internal_type == 'liquidity':
            self.reconcile = True
            
    @api.onchange('group_type')
    def _onchange_group_type(self):
        self.user_type_id = False
        group_type = self.env['account.account.type'].sudo().search([('group_type','=',self.group_type.id)])
        result = {}
        if group_type:
            result = {'domain': {'user_type_id': [('id', 'in', group_type.ids)]}}
        else:
            result = {'domain': {'user_type_id': [('id', 'in', [])]}}
        return result
    
    @api.onchange('user_type_id')
    def _onchange_user_type_id(self):
        self.group_name = False
        group_name = self.env['account.group.name'].sudo().search([('group_head','=',self.user_type_id.id)])
        result = {}
        if group_name:
            result = {'domain': {'group_name': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'group_name': [('id', 'in', [])]}}
        return result

    @api.onchange('group_name')
    def _onchange_group_name(self):
        self.account_head_id = False
        group_name = self.env['account.head'].sudo().search([('group_name','=',self.group_name.id)])
        result = {}
        if group_name:
            result = {'domain': {'account_head_id': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'account_head_id': [('id', 'in', [])]}}
        return result

    @api.onchange('account_head_id')
    def _onchange_account_head_id(self):
        self.account_sub_head_id = False
        account_sub_head_ids = self.env['account.sub.head'].sudo().search([('account_head','=',self.account_head_id.id)])
        result = {}
        if account_sub_head_ids:
            result = {'domain': {'account_sub_head_id': [('id', 'in', account_sub_head_ids.ids)]}}
        else:
            result = {'domain': {'account_sub_head_id': [('id', 'in', [])]}}
        return result
    
    @api.multi
    def write(self,vals):
        if vals.get('account_sub_head_id'):
            subcat = self.env['account.sub.head'].search([('active','=',True),('id','=',int(vals.get('account_sub_head_id')))])
            group_type = vals.get('group_type') if 'group_type' in vals else self.group_type.id 
            user_type_id = vals.get('user_type_id') if 'user_type_id' in vals else self.user_type_id.id 
            account_head_id = vals.get('account_head_id') if 'account_head_id' in vals else self.account_head_id.id
            group_name = vals.get('group_name') if 'group_name' in vals else self.group_name.id
            account_sub_head_id = vals.get('account_sub_head_id') if 'account_sub_head_id' in vals else self.account_sub_head_id.id

            seq,dyseq = self.get_account_sequence(group_type,user_type_id,account_head_id,group_name,account_sub_head_id)
            # vals['code'] = subcat.group_head.group_type.code + subcat.group_head.code + subcat.code + seq 
            vals['code'] = (subcat.group_type.code or self.group_type.code or ' ') + "-" + (subcat.group_head.code or self.user_type_id.code or ' ') + "-" + (subcat.group_name.code or self.group_name.code or ' ') + "-" + (subcat.account_head.code or self.account_head_id.code or ' ') + "-" + (subcat.code or self.account_sub_head_id.code or ' ') + "-" + seq
            if dyseq:
                vals['sequence']=dyseq
        return super(AccountInherit, self).write(vals)

    @api.model
    def create(self, vals):
        if 'account_head_id' in vals:
            subcat = self.env['account.sub.head'].search([('active','=',True),('id','=',int(vals.get('account_sub_head_id')))])
            seq,dyseq = self.get_account_sequence(vals.get('group_type'),vals.get('user_type_id'),vals.get('account_head_id'),vals.get('group_name'),vals.get('account_sub_head_id'))
            vals['code'] = (subcat.group_head.group_type.code or ' ') + "-" + (subcat.group_head.code or ' ') + "-" + (subcat.group_name.code or ' ') + "-" + (subcat.account_head.code or ' ') + "-" + (subcat.code or ' ') + "-" + seq
            if dyseq:
                vals['sequence']=dyseq
        return super(AccountInherit, self).create(vals)


    def get_account_sequence(self,group_type,user_type_id,account_head_id,group_name,account_sub_head_id):
        records = self.env['account.account'].search([('group_type','=',group_type),('user_type_id','=',user_type_id),('group_name','=',group_name),('account_head_id','=',account_head_id),('account_sub_head_id','=',account_sub_head_id),('sequence','!=',False)], order='id desc',limit=1)
        codes = (records.code)[-3:] if records else False
        seq = 1
        input_string = records.code
        last_number = input_string.split('-')[-1] if input_string else '0'
        last_number_length = len(last_number)
        
        sequence_len = last_number_length if records else 3

        if last_number:
            seq = str(int(last_number) + 1).zfill(sequence_len)
            # len_rec = len((records.code)[-3:])
            # sum = str(int(codes) + 1)
            # if len(sum) == 3:
            #     seq = str(int(codes) + 1)
            # elif len(sum) == 2:
            #     seq = '0' + str(int(codes) + 1) 
            # elif len(sum) == 1:
            #     seq = '00' + str(int(codes) + 1)
            # else:
            #     pass
        sequence=int(codes if records else 0) + 1
        return seq,sequence

    @api.model
    def get_ledger_report_data(self,**args):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        period_list,ledger_list,project_wo_list = [],[],[]
        company_currency = self.env.user.company_id.currency_id.name
        branch_name = self.env['accounting.branch.unit'].browse(branch_id).name
        company_name = self.env.user.company_id.name
        group_type_ids = self.env['kw.group.type'].search_read([],['id','name'],order="code asc")
        group_head_ids = self.env['account.account.type'].search_read([],['id','name'],order="code asc")
        group_name_ids = self.env['account.group.name'].search_read([],['id','name'],order="code asc")
        account_head_ids = self.env['account.head'].search_read([],['id','name'],order="code asc")
        account_sub_head_ids = self.env['account.sub.head'].search_read([],['id','name'],order="code asc")
        ledger_ids = self.search([('active','=',True),('company_id','=',company_id),('branch_id','=',branch_id)])
        for ledger in ledger_ids:
            ledger_list.append({
                'id': ledger.id,
                'name':  "%s - %s - %s - %s - %s - %s (%s)" % (ledger.group_type.name,ledger.user_type_id.name,ledger.group_name.name,ledger.account_head_id.name,ledger.account_sub_head_id.name,ledger.name,ledger.code) 
            })
        department_ids = self.env['hr.department'].search_read([('active','=',True),('dept_type.code','=','department')],['id','name'])
        division_ids = self.env['hr.department'].search_read([('active','=',True),('dept_type.code','=','division')],['id','name'])
        section_ids = self.env['hr.department'].search_read([('active','=',True),('dept_type.code','=','section')],['id','name'])

        period_ids = self.env['account.period'].search([('fiscalyear_id','=',fy_id.id)])
        employee_ids = self.env['hr.employee'].search_read(['|',('active','=',True),('active','=',False)],['id','name','emp_code'])
        for period in period_ids:
            period_list.append({'date_start': period.date_start,'date_start_format': period.date_start.strftime("%d-%b-%Y"),'date_stop': period.date_stop,'date_stop_format': period.date_stop.strftime("%d-%b-%Y")})
        
        project_wo_ids = self.env['kw_project_budget_master_data'].search([])
        for project in project_wo_ids:
            project_wo_list.append({
                'id': project.id,
                'name': "%s - %s" % (project.wo_code, project.wo_name)
            })
        return [company_name,company_currency,ledger_list,department_ids,period_list,branch_name,fy_id.name,employee_ids,project_wo_list,division_ids,section_ids,group_type_ids,group_head_ids,group_name_ids,account_head_ids,account_sub_head_ids]

    def get_currency_separator_format(self,amount,format=True):
        currency_id = self.env.user.company_id.currency_id
        fmt = "%.{0}f".format(currency_id.decimal_places)
        lang = self.env['res.lang']._lang_get(self.env.context.get('lang') or 'en_US')
        balance_symbol = 'Cr' if amount < 0 else 'Dr'
        formatted_amount = lang.format(fmt, abs(round(amount,2)), grouping=True, monetary=True)\
            .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')            
        if format==True:
            return '%s %s' % (formatted_amount, balance_symbol)
        else:
            return '%s' % (formatted_amount)

    @api.model
    def get_accounts_onchange(self, **args):
        print(args)
        group_type = args.get('group_type',False)
        group_head = args.get('group_head',False)
        group_name = args.get('group_name',False)
        account_head = args.get('account_head',False)
        account_sub_head = args.get('account_sub_head',False)
        group_head_ids = self.env['account.account.type'].search_read([('group_type','=',int(group_type))],['id','name'],order="code asc")
        group_name_ids = self.env['account.group.name'].search_read([('group_type','=',int(group_type)),('group_head','=',int(group_head))],['id','name'],order="code asc")
        account_head_ids = self.env['account.head'].search_read([('group_type','=',int(group_type)),('group_head','=',int(group_head)),('group_name','=',int(group_name))],['id','name'],order="code asc")
        account_sub_head_ids = self.env['account.sub.head'].search_read([('group_type','=',int(group_type)),('group_head','=',int(group_head)),('group_name','=',int(group_name)),('account_head','=',int(account_head))],['id','name'],order="code asc")
        ledger_list = []
        ledger_ids = self.env['account.account'].search([('group_type','=',int(group_type)),('user_type_id','=',int(group_head)),('group_name','=',int(group_name)),('account_head_id','=',int(account_head)),('account_sub_head_id','=',int(account_sub_head))])
        for ledger in ledger_ids:
            ledger_list.append({
                'id': ledger.id,
                'name':  "%s - %s - %s - %s - %s - %s (%s)" % (ledger.group_type.name,ledger.user_type_id.name,ledger.group_name.name,ledger.account_head_id.name,ledger.account_sub_head_id.name,ledger.name,ledger.code) 
            })

        return [group_head_ids,group_name_ids,account_head_ids,account_sub_head_ids,ledger_list]

    @api.model
    def get_ledger_report_details(self, **args):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        from_date = args.get('from_date',False)
        to_date = args.get('to_date',False)
        period_from = args.get('period_from',False)
        period_to = args.get('period_to',False)
        account_id = args.get('account_id',False)
        budget_type = args.get('budget_type',False)
        department = args.get('department',False)
        employee_id = args.get('employee_id',False)
        project_wo_id = args.get('project_wo_id',False)
        division_id = args.get('division_id',False)
        section_id = args.get('section_id',False)
        filter = args.get('filter',False)

        report_data,sum_report_data,first_where_clause,second_where_clause = [],[],'',''
        if filter == 'current_date':
            filter_from_date = fy_id.date_start
            filter_to_date = date.today()
        else:
            filter_from_date = from_date if from_date != False else period_from if period_from != False else ''
            filter_to_date = to_date if to_date != False else period_to if period_to != False else ''
        
        adv_ob_id = self.env['advance_ledger_opening_balance'].search([('employee_id','=',int(employee_id)),('parent_id','=',int(account_id))])
        adv_ob = adv_ob_id.balance if adv_ob_id else 0


        if (from_date or period_from or filter) and (to_date or period_to or filter) and account_id:
            first_where_clause = f" aml.account_id = {account_id} and aml.date < '{filter_from_date}' and am.state = 'posted'"
            second_where_clause = f" account_id = {account_id} and date >= '{filter_from_date}' and date <= '{filter_to_date}'"
            join_clause = f" aml.account_id = {account_id}"

            if budget_type != '0':
                first_where_clause += f" and budget_type = '{budget_type}'"
                second_where_clause += f" and budget_type = '{budget_type}'"
                join_clause += f" and aml.budget_type = '{budget_type}'"

            if department != '0':
                first_where_clause += f" and aml.department_id = '{int(department)}'"
                second_where_clause += f" and department_id = '{int(department)}'"
                join_clause += f" and aml.department_id = '{int(department)}'"

            if project_wo_id != '0':
                first_where_clause += f" and aml.project_wo_id = '{int(project_wo_id)}'"
                second_where_clause += f" and project_id = '{int(project_wo_id)}'"
                join_clause += f" and aml.project_wo_id = '{int(project_wo_id)}'"

            if employee_id != '0':
                first_where_clause += f" and aml.employee_id = '{int(employee_id)}'"
                second_where_clause += f" and employee_id = '{int(employee_id)}'"
                join_clause += f" and aml.employee_id = '{int(employee_id)}'" 

            if division_id != '0':
                first_where_clause += f" and aml.division_id = '{int(division_id)}'"
                second_where_clause += f" and division_id = '{int(division_id)}'"
                join_clause += f" and aml.division_id = '{int(division_id)}'"

            if section_id != '0':
                first_where_clause += f" and aml.section_id = '{int(section_id)}'"
                second_where_clause += f" and section_id = '{int(section_id)}'"
                join_clause += f" and aml.section_id = '{int(section_id)}'"

            ob_query = f"select COALESCE(sum(balance),0) from account_move_line aml left join account_move am on am.id = aml.move_id where {first_where_clause}"
            self._cr.execute(ob_query)
            opening_balance = self._cr.fetchone()[0]
            
            ob_actual = float(opening_balance + adv_ob)
            ob_actual = self.get_currency_separator_format(ob_actual)

            ob_account_id = self.browse(int(account_id))
            ob_account = "%s - %s - %s - %s - %s - %s (%s)" % (ob_account_id.group_type.name,ob_account_id.user_type_id.name,ob_account_id.group_name.name,ob_account_id.account_head_id.name,ob_account_id.account_sub_head_id.name,ob_account_id.name,ob_account_id.code)
            
            
            ob_period = "%s To %s" % (filter_from_date.strftime("%d-%b-%Y") if not isinstance(filter_from_date, str) else datetime.strptime(filter_from_date, "%Y-%m-%d").strftime("%d-%b-%Y"), filter_to_date.strftime("%d-%b-%Y") if not isinstance(filter_to_date, str) else datetime.strptime(filter_to_date, "%Y-%m-%d").strftime("%d-%b-%Y"))
            ob_company_id = self.env['res.company'].browse(int(company_id))
            ob_company = ob_company_id.name
            ob_company_currency = ob_company_id.currency_id.name

            ob_branch_id = self.env['accounting.branch.unit'].browse(int(branch_id))
            ob_branch = ob_branch_id.name

            query = f"WITH OrderedMoves AS (\
                            SELECT\
                                aml.id as line_id,\
                                aml.move_id AS move_id,\
                                am.narration AS narration,\
                                aml.account_id AS account_id,\
                                aml.date AS date, \
                                aml.partner_id AS partner_id,\
                                aml.debit AS debit,\
                                aml.credit AS credit,\
                                ROW_NUMBER() OVER (PARTITION BY aml.account_id ORDER BY aml.date ASC,aml.id ASC) AS row_num,\
                                aml.budget_type as budget_type, \
                                aml.department_id as department_id, \
                                aml.division_id as division_id, \
                                aml.section_id as section_id, \
                                aml.project_wo_id as project_id, \
                                aml.employee_id as employee_id \
                            FROM account_move_line aml\
                            LEFT JOIN account_move am ON am.id = aml.move_id where am.state in ('posted') and {join_clause} \
                        )\
                        SELECT\
                            line_id,account_id,move_id,date,partner_id, \
                            COALESCE( \
                                LAG(cumulative_balance) OVER (PARTITION BY account_id ORDER BY date ASC, line_id ASC), \
                                COALESCE((select sum(balance) from account_move_line aml left join account_move am on am.id = aml.move_id where {first_where_clause}),0) \
                            ) + {adv_ob} AS opening_balance, \
                            debit,credit, \
                            cumulative_balance + {adv_ob} AS closing_balance,budget_type,department_id,division_id,section_id,employee_id,project_id\
                        FROM ( \
                            SELECT  \
                                line_id,account_id,move_id,date,partner_id,debit,credit, \
                                ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY date ASC, line_id ASC) AS row_num, \
                                SUM(debit - credit) OVER (PARTITION BY account_id ORDER BY date ASC, line_id ASC) AS cumulative_balance,budget_type,department_id,division_id,section_id,employee_id,project_id \
                            FROM \
                                OrderedMoves \
                        ) AS subquery \
                        WHERE  \
                            {second_where_clause} \
                        ORDER BY \
                            date asc, line_id asc;  \
                    "
            self._cr.execute(query)
            transaction_datas = self._cr.fetchall()
            count = 0
            for transaction in transaction_datas:
                move_id = self.env['account.move'].browse(transaction[2])
                invoice_id = self.env['account.invoice'].search([('move_id','=',move_id.id)],limit=1)
                serial_number = count + 1
                count = count + 1
                report_data.append({
                    'serial_number': serial_number,
                    'line_id': transaction[0],
                    'account_id': self.env['account.account'].browse(transaction[1]).name,
                    'move_id': move_id.name,
                    'bill_no': invoice_id.reference_number or '',
                    'voucher_id': move_id.id if move_id.move_type in ['receipt','payment','general','contra'] else invoice_id.id,
                    'voucher_type': 'move' if move_id.move_type in ['receipt','payment','general','contra'] else 'invoice',
                    'date': transaction[3].strftime("%d-%b-%Y"),
                    'partner_id': self.env['res.partner'].browse(transaction[4]).name if transaction[4] else '',
                    'narration': self.env['account.move'].browse(transaction[2]).narration,
                    'particulars': self.env['account.move'].browse(transaction[2]).particulars,
                    'budget_type': dict(self.env['account.move.line'].fields_get(allfields='budget_type')['budget_type']['selection'])[self.env['account.move.line'].browse(transaction[0]).budget_type] if self.env['account.move.line'].browse(transaction[0]).budget_type else False,
                    'department': self.env['account.move.line'].browse(transaction[0]).department_id.name if self.env['account.move.line'].browse(transaction[0]).department_id.name else '' ,
                    'division': self.env['account.move.line'].browse(transaction[0]).division_id.name if self.env['account.move.line'].browse(transaction[0]).division_id.name else '' ,
                    'section': self.env['account.move.line'].browse(transaction[0]).section_id.name if self.env['account.move.line'].browse(transaction[0]).section_id.name else '' ,
                    'employee': self.env['account.move.line'].browse(transaction[0]).employee_id.name if self.env['account.move.line'].browse(transaction[0]).employee_id.name else '' ,
                    'project': (self.env['account.move.line'].browse(transaction[0]).project_wo_id.wo_code +' - ' +self.env['account.move.line'].browse(transaction[0]).project_wo_id.wo_name) if self.env['account.move.line'].browse(transaction[0]).project_wo_id.wo_name else '' ,
                    'opening_balance': self.get_currency_separator_format(transaction[5]),
                    'debit': self.get_currency_separator_format(transaction[6],format=False),
                    'debit_balance': transaction[6],
                    'credit_balance': transaction[7],
                    'credit': self.get_currency_separator_format(transaction[7],format=False),
                    'closing_balance': self.get_currency_separator_format(transaction[8]),
                })
            sum_of_debit = sum(report_data[i]['debit_balance'] for i in range(len(report_data)))
            sum_of_credit = sum(report_data[i]['credit_balance'] for i in range(len(report_data)))
            
            sum_report_data.append({
                'serial_number': '-',
                'line_id': '-',
                'account_id': '-',
                'move_id': '-',
                'date': '-',
                'partner_id': '-',
                'narration': '-',
                'particulars': '-',
                'budget_type': '-',
                'department': '-',
                'employee': '-',
                'project': '-',
                'opening_balance': '-',
                'debit': self.get_currency_separator_format(sum_of_debit,format=False),
                'credit': self.get_currency_separator_format(sum_of_credit,format=False),
                'closing_balance': '-',
            })
        return [len(report_data),report_data,sum_report_data,ob_actual,ob_account,ob_period,ob_company,ob_branch,ob_company_currency]

    @api.model
    def advance_vs_payment_report(self, **args):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        ledger_ids = self.search_read([('active','=',True),('company_id','=',company_id),('branch_id','=',branch_id),('advance_ledger','=',True)],['id','name'])
        company_currency = self.env.user.company_id.currency_id.name
        branch_name = self.env['accounting.branch.unit'].browse(branch_id).name
        employee_ids = self.env['hr.employee'].search_read(['|',('active','=',True),('active','=',False)],['id','name','emp_code'])
        company_name = self.env.user.company_id.name
        return [company_name,company_currency,ledger_ids,fy_id.name,employee_ids,branch_name]
    
    @api.model
    def advance_vs_payment_report_details(self,**args):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        ledger_ids = self.search([('active','=',True),('company_id','=',company_id),('branch_id','=',branch_id),('advance_ledger','=',True)])
        
        employee_id = args.get('employee_id',False)
        ledger_id = args.get('ledger_id',False)
        date_from = args.get('date_from',False)
        date_to = args.get('date_to',False)

        ob_where_clause,aob_where_clause = '',''
        filter_from_date = fy_id.date_start if date_from == '' else date_from 
        filter_to_date = fy_id.date_stop if date_to == '' else date_to 

        if ledger_id and ledger_id != '0':
            ob_where_clause += f" aml.account_id = {int(ledger_id)}"
            aob_where_clause += f" aob.parent_id = {int(ledger_id)}"
        else:
            ob_where_clause += f" aml.account_id IN {tuple(ledger_ids.ids)}"
            aob_where_clause += f" aob.parent_id IN {tuple(ledger_ids.ids)}" 

        if employee_id and employee_id != '0':
            ob_where_clause += f" and aml.employee_id = {int(employee_id)}"
            aob_where_clause += f" and aob.employee_id = {int(employee_id)}" 
        

        query =  f"  \
                    with final_output as ( \
                        with opening_balance as( \
                            select aml.account_id, aml.employee_id, coalesce(sum(aml.balance),0) as opening_balance from  \
                            account_move_line aml left join account_move am on am.id = aml.move_id \
                            where {ob_where_clause} and aml.date < '{filter_from_date}' and aml.employee_id is not null and am.state != 'draft' \
                            group by aml.account_id, aml.employee_id \
                        union all  \
                            select aob.parent_id, aob.employee_id, coalesce(sum(aob.balance),0) as opening_balance from \
                            advance_ledger_opening_balance aob \
                            where {aob_where_clause} and aob.date < '{filter_from_date}' \
                            group by aob.parent_id, aob.employee_id \
                        ) \
                        select account_id, employee_id, sum(opening_balance) as opening_balance, 0 as debit, 0 as credit, sum(opening_balance) as closing_balance \
                        from opening_balance \
                        group by employee_id, account_id \
                        union all  \
                        select aml.account_id, aml.employee_id, \
                        0 as opening_balance, \
                        sum(case when aml.date >= '{filter_from_date}' and aml.date <= '{filter_to_date}' then aml.debit else 0 end) as debit, \
                        sum(case when aml.date >= '{filter_from_date}' and aml.date <= '{filter_to_date}' then aml.credit else 0 end) as credit, \
                        0 as closing_balance \
                        from account_move_line aml left join account_move am on am.id = aml.move_id \
                        where  {ob_where_clause} and aml.date >= '{filter_from_date}' and aml.date <= '{filter_to_date}' and am.state != 'draft' \
                        group by aml.employee_id,aml.account_id \
                    ) \
                    select account_id, employee_id, sum(opening_balance) as opening_balance,  \
                    sum(debit) as debit, sum(credit) as credit,  \
                    (sum(opening_balance) + sum(debit) - sum(credit)) as closing_balance from final_output where employee_id is not null\
                    group by account_id, employee_id \
                "
        self._cr.execute(query)
        transaction_datas = self._cr.fetchall()
        report_data,count,sum_report_data = [],0,[]
        for transaction in transaction_datas:
            serial_number = count + 1
            count = count + 1
            report_data.append({
                'serial_number': serial_number,
                'account_id': self.browse(transaction[0]).name,
                'employee_id': self.env['hr.employee'].browse(transaction[1]).display_name ,
                'ob': transaction[2],
                'opening_balance': self.get_currency_separator_format(transaction[2]),
                'debit': self.get_currency_separator_format(transaction[3],format=False),
                'credit': self.get_currency_separator_format(transaction[4],format=False),
                'closing_balance': self.get_currency_separator_format(transaction[5]),
                'debit_balance': transaction[3],
                'credit_balance': transaction[4],
                'cb': transaction[5],
            })
        
        sum_of_debit = sum(report_data[i]['debit_balance'] for i in range(len(report_data)))
        sum_of_credit = sum(report_data[i]['credit_balance'] for i in range(len(report_data)))
        sum_of_ob = sum(report_data[i]['ob'] for i in range(len(report_data)))
        sum_of_cb = sum(report_data[i]['cb'] for i in range(len(report_data)))
            
        sum_report_data.append({
            'serial_number': '-',
            'account_id': '-',
            'employee_id': '-',
            'opening_balance': self.get_currency_separator_format(sum_of_ob),
            'debit': self.get_currency_separator_format(sum_of_debit,format=False),
            'credit': self.get_currency_separator_format(sum_of_credit,format=False),
            'closing_balance': self.get_currency_separator_format(sum_of_cb),
        })
        return [report_data,sum_report_data]

    @api.model
    def preview_budget_account_vouchers(self,**args):
        args_budget_line_id = args.get('budget_line_id',False)
        budget_line_id = self.env['kw_project_budget_line_items'].browse(int(args_budget_line_id))

        move_line_ids = self.env['account.move.line'].search([('project_wo_id','=',budget_line_id.project_crm_id.id),('account_id.account_sub_head_id','=',budget_line_id.account_sub_head_id.id)])
        report_data,count,sum_report_data = [],0,[]
        
        for line in move_line_ids:
            invoice_id = self.env['account.invoice'].search([('move_id','=',line.move_id.id)],limit=1)
            serial_number = count + 1
            count = count + 1
            report_data.append({
                'sl_no': serial_number,
                'project_name' : str(line.project_wo_id.wo_code + "-" + line.project_wo_id.wo_name) if line.project_wo_id else '',
                'account_sub_head': budget_line_id.account_sub_head_id.name,
                'date': line.date,
                'voucher_no': line.move_id.name,
                'ledger_name': line.account_id.code + "-" + line.account_id.name,
                'debit': line.debit,
                'credit': line.credit,
                'formatted_debit': self.get_currency_separator_format(line.debit,format=False),
                'formatted_credit': self.get_currency_separator_format(line.credit,format=False),
                'voucher_id': line.move_id.id if line.move_id.move_type in ['receipt','payment','general','contra'] else invoice_id.id,
                'voucher_type': 'move' if line.move_id.move_type in ['receipt','payment','general','contra'] else 'invoice',
            })

        sum_of_debit = sum(report_data[i]['debit'] for i in range(len(report_data)))
        sum_of_credit = sum(report_data[i]['credit'] for i in range(len(report_data)))
            
        sum_report_data.append({
            'debit': self.get_currency_separator_format(sum_of_debit,format=False),
            'credit': self.get_currency_separator_format(sum_of_credit,format=False),
        })

        return [report_data,sum_report_data]

    @api.model
    def day_book_report(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        company_currency = self.env.user.company_id.currency_id.name
        branch_name = self.env['accounting.branch.unit'].browse(branch_id).name
        company_name = self.env.user.company_id.name

        return [company_name,company_currency,fy_id.name,branch_name]
    
    @api.model
    def day_book_report_details(self,**args):
        voucher_type = args.get('voucher_type',False)
        date_from = args.get('date_from',False)
        date_to = args.get('date_to',False)

        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()

        filter_from_date = fy_id.date_start if date_from == '' else date_from 
        filter_to_date = fy_id.date_stop if date_to == '' else date_to 
        
        domain = [('date','>=',filter_from_date),('date','<=',filter_to_date),('state','>=','posted')]
        
        if voucher_type != '0':
            if voucher_type in ['receipt','payment','general','contra']:
                domain += [('move_type','=',voucher_type)]
            if voucher_type == 'sales':
                domain += [('journal_id.type','=','sale')]
            if voucher_type == 'credit_note':
                domain += [('journal_id.type','=','sale')]
            if voucher_type == 'purchase':
                domain += [('journal_id.type','=','purchase')]
            if voucher_type == 'debit_note':
                domain += [('journal_id.type','=','purchase')]
        move_ids = self.env['account.move'].search(domain)

        final_output = []
        for move in move_ids:
            first_row,second_row = [],[]
            for line in move.line_ids[1:]:
                second_row.append({
                    'account_id': "%s - %s - %s - %s - %s" % (line.account_id.group_type.name,line.account_id.user_type_id.name,line.account_id.group_name.name,line.account_id.account_head_id.name,line.account_id.account_sub_head_id.name),
                    'account_name': "%s" % (line.account_id.name), 
                    'account_code': "%s" % (line.account_id.code),
                    'budget_type' : dict(self.env['account.move.line'].fields_get(allfields='budget_type')['budget_type']['selection'])[line.budget_type] if line.budget_type else '',
                    'debit' : self.get_currency_separator_format(line.debit,format=False),
                    'credit': self.get_currency_separator_format(line.credit,format=False),
                })
            first_row.append({
                'date': move.date.strftime("%d-%b-%Y"),
                'name': move.name,
                'move_type' : 'Payment' if move.move_type == 'payment' else 'Receipt' if move.move_type == 'receipt' else 'Contra' if move.move_type == 'contra' else 'General' if move.move_type == 'general' else 'Sales' if move.journal_id.type == 'sale' else 'Purchase',
                'narration': move.narration,
                'transactions': [{
                    'account_id': "%s - %s - %s - %s - %s" % (move.line_ids[0].account_id.group_type.name,move.line_ids[0].account_id.user_type_id.name,move.line_ids[0].account_id.group_name.name,move.line_ids[0].account_id.account_head_id.name,move.line_ids[0].account_id.account_sub_head_id.name),
                    'account_name': "%s" % (move.line_ids[0].account_id.name), 
                    'account_code': "%s" % (move.line_ids[0].account_id.code),
                    'budget_type' : dict(self.env['account.move.line'].fields_get(allfields='budget_type')['budget_type']['selection'])[move.line_ids[0].budget_type] if move.line_ids[0].budget_type else '',
                    'debit' : self.get_currency_separator_format(move.line_ids[0].debit,format=False),
                    'credit': self.get_currency_separator_format(move.line_ids[0].credit,format=False),
                }],
                'line_ids_length': len(move.line_ids),
            })
            final_output.append({
                'first_row': first_row,
                'second_row':second_row
            })
        return [final_output]

class AdvanceLedgerOpeningBalance(models.Model):
    _name = 'advance_ledger_opening_balance'
    _description = 'Advance Ledger Opening Balance'

    parent_id = fields.Many2one('account.account',string="Account")
    date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    opening_debit = fields.Float(string="Opening Debit")
    opening_credit = fields.Float(string="Opening Credit")
    balance = fields.Float(string="Balance",compute="_store_balance",store=True)

    @api.depends('opening_debit', 'opening_credit')
    def _store_balance(self):
        for line in self:
            line.balance = line.opening_debit - line.opening_credit