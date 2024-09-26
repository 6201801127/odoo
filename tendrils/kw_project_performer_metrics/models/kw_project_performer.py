from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
import calendar
import re



class ProjectPerformerMetrics(models.Model):
    _name = "kw_project_performer_metrics"
    _description = "Project Performer Metrices "
    _rec_name = "project_id"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]
    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)


    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]
    
    @api.depends('employee_id','state')
    def _check_user_for_editing(self):
        for rec in self:
            if self.env.user.has_group('kw_project_performer_metrics.group_quality_head') and rec.state == 'apply' :
                rec.enable_field_boolean = True
            elif self.env.user.has_group('kw_project_performer_metrics.group_quality_engineer') and rec.state == 'draft' and not self.env.user.has_group('kw_project_performer_metrics.group_quality_head'):
                rec.enable_field_boolean = True
            else:
                rec.enable_field_boolean = False
                

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    employee_id = fields.Many2one('hr.employee', string='Employee Name', default=_default_employee,)
    job_id = fields.Char(string="Designation",related='employee_id.job_id.name')
    department_id = fields.Char(string="Department",related='employee_id.department_id.name')
    name = fields.Char(string="Name",related='employee_id.name')
    emp_code = fields.Char(string="Employee Code",related='employee_id.emp_code')
    project_id = fields.Many2one('project.project', string="Project Name")
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")
    audit_schedule = fields.Float(string="Audit Rate")
    audit_compliance = fields.Float(string="Audit Compliance")
    product_review = fields.Float(string="Product Review")
    audit_score = fields.Float(string="Quantitative Project Management")
    state = fields.Selection([('draft', 'Draft'), ('apply', 'Applied'),('publish','Publish'),('reject','Reject')],default="draft")
    updated_on = fields.Date()
    updated_by =  fields.Many2one('hr.employee')
    enable_field_boolean = fields.Boolean(compute='_check_user_for_editing')
    remark = fields.Text()
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    total_score = fields.Integer(compute='_total_score',store=True)
    
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]
    
    @api.depends('audit_score', 'audit_compliance','product_review','audit_schedule')
    def _total_score(self):
        self.total_score = self.audit_score + self.audit_compliance + self.product_review + self.audit_schedule
        
            
    # @api.model
    # def create(self, vals):
    #     res = super(ProjectPerformerMetrics, self).create(vals)
    #     exist_rec = self.env['kw_project_performer_metrics'].search([('employee_id', '=', res.employee_id.id),
    #                                                  ('year', '=', res.year),
    #                                                  ('month', '=', res.month),
    #                                                  ('id', '!=', res.id),
    #                                                  ])
    #     if exist_rec:
    #         raise ValidationError(
    #             _(f'You are Not allowed to create multiple records for {res.employee_id.name} - Month combination'))
    #     else:
    #         return res

    @api.onchange('project_id')
    def _onchange_project_manager(self):
            if self.project_id:
                self.project_manager_id=self.project_id.emp_id


    @api.constrains('audit_schedule','audit_compliance','product_review','audit_score')
    def check_all_validation(self):
        for rec in self:
            if rec.audit_score <=0 or rec.audit_score >100 or rec.audit_schedule <=0 or rec.audit_schedule >100 or  rec.audit_compliance <=0 or rec.audit_compliance>100 or rec.product_review<=0 or rec.product_review >100:
                raise ValidationError("The value must be between 0 to 100.")


    def btn_apply(self):
        self.state = "apply"
        template = self.env.ref('kw_project_performer_metrics.kw_project_performer_metrics_email_template')
        user = self.env['res.users'].sudo().search([])
        manager = user.filtered(lambda user: user.has_group('kw_project_performer_metrics.group_quality_head') == True)
        # print("managers are printed",manager)
        for rec in manager:
            to_email=rec.email
            # print("to mail are printed",to_email)
            name =rec.name
            month = calendar.month_name[int(self.month)]
            template.with_context(email_to=to_email,state='Applied',name=name,month=month).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Project Performance Added Successfully.")


    
    def btn_grant(self):
        self.write({
            'state':'publish',
            'updated_on':date.today(),
            'updated_by':self.env.user.employee_ids.id
        })
        template = self.env.ref('kw_project_performer_metrics.kw_project_performer_metrics_email_template')
        mail_to = self.employee_id.work_email
        name =self.employee_id.name
        month = calendar.month_name[int(self.month)]
        template.with_context(email_to=mail_to,state='Published',name=name,month=month).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Project Performance Published Successfully.")

    
    def btn_reject(self):
        # self.write({
        #     'state':'reject',
        #     'updated_on':date.today(),
        #     'updated_by':self.env.user.employee_ids.id
        # })
        view_id = self.env.ref("kw_project_performer_metrics.metric_remark_view").id
        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'metric_remark',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id':self.id}
        }
        return action
        # template = self.env.ref('kw_project_performer_metrics.kw_project_performer_metrics_email_template')
        # mail_to = self.employee_id.work_email
        # name =self.employee_id.name
        # month = calendar.month_name[int(self.month)]
        # template.with_context(email_to=mail_to,state='Rejected',name=name,month=month).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

