from odoo import api, fields, models, _, tools

class PipEmployeeReport(models.Model):
    _name = "pip_employee_report"
    _description = "PIP Employee Report"
    _auto = False

    sequence= fields.Char(string='Code', readonly=True,default='New')
    emp_name = fields.Many2one('hr.employee', 'Employee')
    closure_remark = fields.Text('Feedback')
    requested_by = fields.Many2one('hr.employee', string="Request Raised By", readonly=True, default=lambda self:  self.env.user.employee_ids)
    requested_on = fields.Datetime(string="Request Raised On", readonly=True, default=lambda self: fields.Datetime.now())
    status = fields.Selection(
        [
        ('draft', 'Draft'), 
        ('submitted', 'Submitted'), 
        ('inprogress', 'In Progress'), 
        ('closed', 'Closed')], string='Status',required=True, default='draft', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select *,row_number() over (order by requested_on) as id from (
            select f.sequence as sequence,
                   f.employee_id as emp_name,
                   CASE WHEN f.state = 'closed' THEN p.comment
                   ELSE NULL
                   END AS closure_remark,
                   f.requested_by as requested_by,
                   f.requested_on as requested_on,
                   f.state as status,
              p.emp_id,dense_rank() OVER ( PARTITION BY p.emp_id ORDER BY p.create_date DESC) as xyz
              from kw_feedback_assessment_pip as f inner join assessment_pip_employee p on p.emp_id = f.id WHERE emp_id = f.id) as abc
              where xyz=1
            
        )""" % (self._table))   