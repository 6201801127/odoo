from odoo import api, fields, models, tools


class LeaveSummaryReport(models.Model):
    _inherit = "hr.leave.report"

    branch_id = fields.Many2one("res.branch",string="Branch",related='employee_id.branch_id')
    leave_type = fields.Selection([
        ('allocation', 'Allocation'),
        ('request', 'Leaves')
    ], string='Request Type', readonly=True)

    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'hr_leave_report')
    #
    #     self._cr.execute("""
    #         CREATE or REPLACE view hr_leave_report as (
    #             SELECT row_number() over(ORDER BY leaves.employee_id) as id,
    #             leaves.employee_id as employee_id,
    #             leaves.branch_id as branch_id,
    #             leaves.name as name,
    #             leaves.number_of_days as number_of_days, leaves.type as type,
    #             leaves.category_id as category_id, leaves.department_id as department_id,
    #             leaves.holiday_status_id as holiday_status_id, leaves.state as state,
    #             leaves.holiday_type as holiday_type, leaves.date_from as date_from,
    #             leaves.date_to as date_to, leaves.payslip_status as payslip_status
    #             from (select
    #                 allocation.employee_id as employee_id,
	# 				allocation.branch_id as branch_id,
    #                 allocation.name as name,
    #                 allocation.number_of_days as number_of_days,
    #                 allocation.category_id as category_id,
    #                 allocation.department_id as department_id,
    #                 allocation.holiday_status_id as holiday_status_id,
    #                 allocation.state as state,
    #                 allocation.holiday_type,
    #                 null as date_from,
    #                 null as date_to,
    #                 FALSE as payslip_status,
    #                 'allocation' as type
    #             from hr_leave_allocation as allocation
    #             union all select
    #                 request.employee_id as employee_id,
	# 				request.branch_id as branch_id,
    #                 request.name as name,
    #                 (request.number_of_days * -1) as number_of_days,
    #                 request.category_id as category_id,+
    #                 request.department_id as department_id,
    #                 request.holiday_status_id as holiday_status_id,
    #                 request.state as state,
    #                 request.holiday_type,
    #                 request.date_from as date_from,
    #                 request.date_to as date_to,
    #                 request.payslip_status as payslip_status,
    #                 'request' as type
    #             from hr_leave as request) leaves
    #         );
    #     """)


# ('holiday_type','=','employee'),('holiday_status_id.active', '=', True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_check') and self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            args += ['|','|','&','&',('holiday_type','=','employee'),('holiday_status_id.active', '=', True),('branch_id','in',self.env.user.branch_ids.ids),('employee_id.user_id','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]
        else:
            args += ['|','&','&',('holiday_type','=','employee'),('holiday_status_id.active', '=', True),('employee_id.user_id','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]

        print("Args ",args)
        
        return super(LeaveSummaryReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_check') and self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            domain += ['|','|','&','&',('holiday_type','=','employee'),('holiday_status_id.active', '=', True),('branch_id','in',self.env.user.branch_ids.ids),('employee_id.user_id','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]
        else:
            domain += ['|','&','&',('holiday_type','=','employee'),('holiday_status_id.active', '=', True),('employee_id.user_id','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]

        print("Domain ",domain)
        return super(LeaveSummaryReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
