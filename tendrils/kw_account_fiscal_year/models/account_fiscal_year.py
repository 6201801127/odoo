
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression


class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start desc"

    name = fields.Char('Fiscal Year', required=True)
    code = fields.Char('Code', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('End Date', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True,
                             copy=False, default='draft')
    lock_in = fields.Boolean(string="Lock In")
    lock_in_flag = fields.Integer(string="Lock In Flag", default=0)

    @api.onchange('lock_in')
    def get_lock_in_flag_boolean(self):
        for rec in self:
            if rec.lock_in:
                rec.lock_in_flag = 1

    @api.constrains('date_start','date_stop')
    def _check_duration(self):
        '''
        This method check date overlapping for fiscal year
        :return: if overlap date raise warning else pass
        '''
        for obj_fy in self:
            if obj_fy.date_stop < obj_fy.date_start:
                raise UserError(_('The start date of a fiscal year must less than its end date.'))
        return True

    @api.multi
    def create_period(self):
        '''
        This method create account period for each month of fiscal year.
        :param interval: default is 1. It is for creating period between FY start date and end date
        :return: create period between FY start date and end date and return True
        '''
        period_obj = self.env['account.period']
        for fy in self:
            # ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            ds = fy.date_start
            interval = 1
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de > fy.date_stop:
                    # de = datetime.strptime(fy.date_stop, '%Y-%m-%d')
                    de = fy.date_stop

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def finds(self, dt=None, company_id=False):
        '''
        This function return fiscal year for selected date and company
        :param dt: date to find fiscal year. If not passed then it check for current date
        :param company_id: company_id for find fiscal year. If not define it take usder's company
        :return: return recordset of fiscal year
        '''
        if not dt:
            dt = fields.Date.context_today
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        # if company_id:
        #     company_id = company_id
        # else:
        #     company_id = self.env.user.company_id.id
        company_id = company_id if company_id else self.env.user.company_id.id
        args.append(('company_id', '=', company_id))
        fy = self.search(args)
        if not fy:
            raise UserError(_('Fiscal Year is not define for selected date'))
        return fy

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        fy = self.search(domain + args, limit=limit)
        return fy.name_get()


class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"
    _order = "date_start, special desc"

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period',help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done':[('readonly',True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done':[('readonly',True)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True,
                                    states={'done':[('readonly',True)]}, index=True)
    state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True,
                             copy=False,
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id',
                                 string='Company', store=True, readonly=True)
    lock_in = fields.Boolean(string="Lock In")
    lock_in_flag = fields.Integer(string="Lock In Flag", default=0)

    @api.onchange('lock_in')
    def get_lock_in_flag_boolean(self):
        for rec in self:
            if rec.lock_in:
                rec.lock_in_flag = 1



    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'The name of the period must be unique per company!'),
    ]

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        '''
        check constrains to avoid date overlapping
        :return: true if dates are not overlapping otherwise raise warning
        '''
        for period in self:
            if period.date_stop < period.date_start:
                raise UserError(_('Duration of period is invalid'))

            if period.fiscalyear_id.date_stop < period.date_stop or \
               period.fiscalyear_id.date_stop < period.date_start or \
               period.fiscalyear_id.date_start > period.date_start or \
               period.fiscalyear_id.date_start > period.date_stop:
                return False

            pids = self.search([('date_stop', '>=', period.date_start),
                                ('date_start', '<=', period.date_stop), ('special', '=', False),
                                ('id', '<>', period.id)])
            for periods in pids:
                if period.fiscalyear_id.company_id.id==periods.fiscalyear_id.company_id.id:
                    raise UserError(_('The period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year'))
        return True

    @api.returns('self')
    def find(self, dt=None, company_id=False):
        '''
        method find period for specific date
        :param dt: date that is passed to find period
        :param company_id: conpany_id to find period
        :return: recordset of period if find otherwise raise warning 
        '''
        if not dt:
            dt = fields.Date.context_today
        args = [('date_start', '<=', dt), ('date_stop', '>=', dt)]
        if company_id:
            args.append(('company_id', '=', company_id))
        else:
            company_id = self.env.user.company_id.id
            args.append(('company_id', '=', company_id))
        result = self.search(args)
        if not result:
            raise UserError(_('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt)
        return result
