from odoo import models,fields,api
import datetime
from odoo.exceptions import ValidationError


class KwLeaveCycleMaster(models.Model):
    _name = 'kw_leave_cycle_master'
    _description = "Leave Cycle master"
    _rec_name = 'branch_id'

    branch_id = fields.Many2one('kw_res_branch', string="Branch")

    from_month = fields.Selection(selection='_get_month_name_list', string='From Month')
    to_month = fields.Selection(selection='_get_month_name_list', string='To Month')
    from_day = fields.Selection(string='From Day', selection='_get_date_list')
    to_day = fields.Selection(string='To Day', selection='_get_date_list')

    from_date = fields.Date(string='From Date', )
    to_date = fields.Date(string='To Date', )
    cycle_period = fields.Integer(string="Year", )
    cycle_id = fields.Many2one('kw_leave_cycle_master', string="Leave Cycle")

    leave_cycle_period_ids = fields.One2many(
        string='Cycle Period',
        comodel_name='kw_leave_cycle_master',
        inverse_name='cycle_id',
    )

    no_of_periods = fields.Integer(compute='_compute_no_of_periods', string='Cycle Period')
    active = fields.Boolean('Active', default=True,
                            help="If the active field is set to false, it will allow you to hide the leave cycle without removing it.")

    _sql_constraints = [
        ('cycle_uniq', 'unique(branch_id,cycle_id,cycle_period)',
         "Branch cycle configuration already exists."),
    ]

    @api.constrains('branch_id', 'cycle_id', 'cycle_period')
    def _validate_cycle(self):
        cycle_model = self.env['kw_leave_cycle_master']
        for record in self:
            if record.branch_id and not record.cycle_id and not record.cycle_period:
                cycle_branch_record = cycle_model.search([
                    ('branch_id', '=', record.branch_id.id if record.branch_id else False),
                    ('cycle_id', '=', False),
                    ('cycle_period', '=', False)
                ]) - record
                if cycle_branch_record:
                    raise ValidationError('Exists! Already a cycle exist for same branch.')

            if record.branch_id and record.cycle_id and record.cycle_period:
                cycle_record = cycle_model.search([
                    ('branch_id', '=', record.branch_id.id),
                    ('cycle_id', '=', record.cycle_id.id),
                    ('cycle_period', '=', record.cycle_period)
                ]) - record
                if cycle_record:
                    raise ValidationError('Exists! Already a cycle exist for same branch,cycle and cycle period.')

    @api.model
    def _get_date_list(self):
        return [(str(i), i) for i in range(1, 31 + 1)]

    @api.model
    def _get_month_name_list(self):
        months_choices = []
        for i in range(1, 13):
            months_choices.append((str(i), datetime.date(2008, i, 1).strftime('%B')))
        return months_choices

    @api.multi
    def _compute_no_of_periods(self):
        for record in self:
            record.no_of_periods = len(record.leave_cycle_period_ids)

    @api.multi
    def generate_leave_cycle_period(self):
        now = datetime.datetime.now()
        for record in self:
            create_new_period = 0
            if record.leave_cycle_period_ids:
                cur_year_cycle = record.leave_cycle_period_ids.filtered(lambda rec: rec.cycle_period == now.year)
                if (not cur_year_cycle) or (cur_year_cycle and now.date() > cur_year_cycle.to_date):
                    create_new_period = 1

            else:
                create_new_period = 1

            if create_new_period:
                next_year = 0
                if int(record.to_month) < int(record.from_month) \
                        or (int(record.to_month) == int(record.from_month) and int(record.to_day) < int(record.from_day)):
                    next_year = 1

                self.create({'branch_id': record.branch_id.id,
                             'from_date': now.replace(day=int(record.from_day), month=int(record.from_month),
                                                      year=now.year),
                             'to_date': now.replace(day=int(record.to_day), month=int(record.to_month),
                                                    year=now.year + 1 if next_year == 1 else now.year),
                             'cycle_period': now.year,
                             'cycle_id': record.id, })

    @api.multi
    def create_leave_cycle_period(self,fisc_year):
        """Create leave cycle period for the given year"""
        kw_leave_cycle_master = self.env['kw_leave_cycle_master']
        #fisc_year_leave_cycle = kw_leave_cycle_master.search([('cycle_period','=',fisc_year),('cycle_id','>',0)])

        all_cycle_config_record = kw_leave_cycle_master.with_context(active_test=False).search(
            [('cycle_id', '=', False)])
        # print(all_cycle_config_record)
        now = datetime.datetime.now()
        for record in all_cycle_config_record:

            if not record.leave_cycle_period_ids.filtered(lambda rec: rec.cycle_period == fisc_year):
                next_year = 0
                if int(record.to_month) < int(record.from_month) \
                        or (int(record.to_month) == int(record.from_month) and int(record.to_day) < int(record.from_day)):
                    next_year = 1
                # print({'branch_id':record.branch_id.id,'from_date':now.replace(day=int(record.from_day),month=int(record.from_month),year=fisc_year),'to_date':now.replace(day=int(record.to_day),month=int(record.to_month),year=fisc_year+1 if next_year ==1 else fisc_year),'cycle_period':fisc_year,'cycle_id':record.id,'active':False})
                kw_leave_cycle_master.create({'branch_id': record.branch_id.id,
                                              'from_date': now.replace(day=int(record.from_day),
                                                                       month=int(record.from_month), year=fisc_year),
                                              'to_date': now.replace(day=int(record.to_day), month=int(record.to_month),
                                                                     year=fisc_year + 1 if next_year == 1 else fisc_year),
                                              'cycle_period': fisc_year,
                                              'cycle_id': record.id,
                                              'active': False})

        all_cycles = kw_leave_cycle_master.with_context(active_test=False).search([('cycle_id', '>', 0)])
        for cycle_rec in all_cycles:
            if cycle_rec.active and now.date() > cycle_rec.to_date:
                cycle_rec.active = False
            if not cycle_rec.active and cycle_rec.from_date <= now.date() <= cycle_rec.to_date:
                cycle_rec.active = False

    @api.multi
    def action_see_cycle_periods(self):
        self.ensure_one()
        action = self.env.ref('kw_hr_leaves.kw_leave_cycle_periods_window').read()[0]

        action['domain'] = [
            ('cycle_id', '!=', False),
            ('cycle_id', '=', self.ids[0]),
        ]

        return action
