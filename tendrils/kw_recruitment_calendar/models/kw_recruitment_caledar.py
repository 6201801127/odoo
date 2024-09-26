from email.policy import default
from odoo import api, fields, models, _
from odoo import tools
import datetime
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import calendar
import re


class RecruitmentPosition(models.Model):
    _name = "kw_recruitment_positions"
    _description = "Recruitment Position"
    _rec_name = 'code'

    @api.model
    def _get_year_list(self):
        years = 40
        return [(str(i), i) for i in range(years + 1)]

    def get_fiscal_year(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal

    name = fields.Char('Fiscal Year')
    fiscalyr = fields.Many2one('account.fiscalyear', string="FY", default=get_fiscal_year)
    employee_id = fields.Many2one('hr.employee', string="Rasied By", )
    published_by = fields.Char(string="Published By", compute='_compute_published_by', store=True)
    dept_id = fields.Many2one('hr.department', string='Department', domain=[('dept_type.code', '=', 'department')])
    division = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
    section = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'section')])
    practise = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'practice')])
    qualification_ids = fields.Many2many("kw_qualification_master", string="Qualification")
    exp_year = fields.Selection(string='Exp (Years)', selection='_get_year_list', default="0", required="1")
    designation = fields.Many2one('hr.job', string="Designation", required="1")
    project = fields.Many2one('crm.lead', string='Project')
    type_of_project = fields.Selection(string='Type Of Project',
                                       selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                       default='work')
    resource_type = fields.Selection(string='Resource Type', track_visibility='onchange',
                                     selection=[('fresher', 'Fresher'), ('lateral', 'Lateral')], default='fresher')
    technology = fields.Many2one('kw_skill_master', string="Technology")
    branch_id = fields.Many2one('kw_res_branch', string='Branch', required="1")
    mrf_id = fields.Char(string='MRF')
    jan = fields.Integer('Jan')
    jan_budget = fields.Integer('Jan Budget')
    feb = fields.Integer('Feb')
    feb_budget = fields.Integer('Feb Budget')
    mar = fields.Integer('Mar')
    mar_budget = fields.Integer('Mar Budget')
    apr = fields.Integer('Apr')
    apr_budget = fields.Integer('Apr Budget')
    may = fields.Integer('May')
    may_budget = fields.Integer('May Budget')
    jun = fields.Integer('Jun')
    jun_budget = fields.Integer('Jun Budget')
    jul = fields.Integer('Jul')
    jul_budget = fields.Integer('Jul Budget')
    aug = fields.Integer('Aug')
    aug_budget = fields.Integer('Aug Budget')
    sep = fields.Integer('Sep')
    sep_budget = fields.Integer('Sep Budget')
    octo = fields.Integer('Oct')
    octo_budget = fields.Integer('Oct Budget')
    nov = fields.Integer('Nov')
    nov_budget = fields.Integer('Nov Budget')
    dec = fields.Integer('Dec')
    dec_budget = fields.Integer('Dec Budget')
    total = fields.Integer('Total Resource', compute='_compute_total_resource', store=True)
    status = fields.Selection([('draft', 'Applied'), ('publish', 'Published'), ('reject', 'Rejected')], string="Status",
                              default='draft', readonly=True)
    total_budget = fields.Char('Total Budget', compute='_compute_total_budget')
    pending_at = fields.Char('Pending at', compute='_compute_pending_at')
    code = fields.Char(string="Reference No.", default="New", readonly="1")
    check_hod = fields.Boolean(string="HOD Check")
    recruitment_calender_id = fields.Many2one('kw_manpower_indent_form', string='MIF ref id')

    @api.depends('status')
    def _compute_pending_at(self):
        for rec in self:
            if rec.status == 'draft':
                rec.pending_at = 'RCM/TAG'
            else:
                rec.pending_at = ''

    def recruitment_calendar_data_update(self):
        recruitment_calender_data = self.env['kw_manpower_indent_form'].search([('state', '=', 'Grant')])

        for rec in recruitment_calender_data:
            fy_data = self.env['account.fiscalyear'].sudo().search(
                [('date_start', '<=', rec.effective_date_of_deployment),
                 ('date_stop', '>=', rec.effective_date_of_deployment)])
            rec_data = rec.effective_date_of_deployment.month
            mif_data = {}
            mif_data = {'recruitment_calender_id': rec.id,
                        'fiscalyr': fy_data.id,
                        'branch_id': rec.branch_id.kw_branch_id.id,
                        'resource_type': 'fresher' if int(rec.max_exp_year) < 0 and int(rec.min_exp_year) < 0 else 'lateral',
                        'exp_year': rec.max_exp_year if int(rec.max_exp_year) > 0 else 0,
                        'type_of_project': '',
                        'dept_id': rec.dept_name.id,
                        'designation': rec.job_position.id,

                        'technology': rec.technology.id,
                        'jan': rec.no_of_resource if rec_data == 1 else 0,
                        'feb': rec.no_of_resource if rec_data == 2 else 0,
                        'mar': rec.no_of_resource if rec_data == 3 else 0,
                        'apr': rec.no_of_resource if rec_data == 4 else 0,
                        'may': rec.no_of_resource if rec_data == 5 else 0,
                        'jun': rec.no_of_resource if rec_data == 6 else 0,
                        'jul': rec.no_of_resource if rec_data == 7 else 0,
                        'aug': rec.no_of_resource if rec_data == 8 else 0,
                        'sep': rec.no_of_resource if rec_data == 9 else 0,
                        'octo': rec.no_of_resource if rec_data == 10 else 0,
                        'nov': rec.no_of_resource if rec_data == 11 else 0,
                        'dec': rec.no_of_resource if rec_data == 12 else 0,
                        'employee_id': rec.req_raised_by_id.id,
                        }

            if not self.env['kw_recruitment_positions'].sudo().search([('recruitment_calender_id', '=', rec.id)]):
                self.env['kw_recruitment_positions'].sudo().create(mif_data)

    # @api.multi
    # def department_last_sequence(self,dept_id):
    #     print("method calleddddd")
    #     last_code = self.env['kw_recruitment_budget_lines'].search([('dept_id','=',dept_id.id)],order="id desc", limit=1)
    #     dept_id = str(last_code.name).split('/')[-1]
    #     print("dept_id========",dept_id)
    #     return int(dept_id) if last_code else 0

    @api.onchange('type_of_project')
    def _onchange_project_type(self):
        self.project = False
        if self.type_of_project == 'work':
            return {'domain': {'project': [('stage_id.code', '=', 'workorder')]}}
        elif self.type_of_project == 'opportunity':
            return {'domain': {'project': [('stage_id.code', '=', 'opportunity')]}}

    @api.onchange('dept_id')
    def _onchange_department(self):
        for rec in self:
            rec.division = False
            rec.section = False
            rec.practise = False
            # if rec.dept_id:
            return {'domain': {'division': [('parent_id', '=', rec.dept_id.id), ('dept_type.code', '=', 'division')]}}

    @api.onchange('division')
    def _onchange_division(self):
        for rec in self:
            # if rec.dept_id:
            rec.section = False
            rec.practise = False
            return {'domain': {'section': [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]}}

    @api.onchange('section')
    def _onchange_section(self):
        for rec in self:
            # if rec.section:
            rec.practise = False
            return {'domain': {'practise': [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]}}

    @api.depends('status')
    def _compute_published_by(self):
        for rec in self:
            if rec.write_uid and rec.status == 'publish':
                rec.published_by = rec.write_uid.employee_ids.name
                # print("rec--------------",rec.published_by)

    @api.model
    def default_get(self, fields):
        res = super(RecruitmentPosition, self).default_get(fields)
        res['employee_id'] = self.env.user.employee_ids.id
        res['dept_id'] = self.env.user.employee_ids.department_id.id
        res['division'] = self.env.user.employee_ids.division.id
        res['section'] = self.env.user.employee_ids.section.id
        res['practise'] = self.env.user.employee_ids.practise.id
        res['branch_id'] = self.env.user.branch_id.id
        if self.env.user.has_group('kw_wfh.group_hr_hod'):
            res['check_hod'] = True
        return res

    @api.depends('jan_budget', 'feb_budget', 'mar_budget', 'apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'octo_budget', 'nov_budget', 'dec_budget')
    def _compute_total_budget(self):
        for rec in self:
            total_budget = 0
            if rec.jan_budget:
                total_budget += rec.jan_budget
            if rec.feb_budget:
                total_budget += rec.feb_budget
            if rec.mar_budget:
                total_budget += rec.mar_budget
            if rec.apr_budget:
                total_budget += rec.apr_budget
            if rec.may_budget:
                total_budget += rec.may_budget
            if rec.jun_budget:
                total_budget += rec.jun_budget
            if rec.jul_budget:
                total_budget += rec.jul_budget
            if rec.aug_budget:
                total_budget += rec.aug_budget
            if rec.sep_budget:
                total_budget += rec.sep_budget
            if rec.octo_budget:
                total_budget += rec.octo_budget
            if rec.nov_budget:
                total_budget += rec.nov_budget
            if rec.dec_budget:
                total_budget += rec.dec_budget
            rec.total_budget = total_budget

    @api.depends('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'octo', 'nov', 'dec')
    def _compute_total_resource(self):
        for rec in self:
            total = 0
            if rec.jan:
                total += rec.jan
            if rec.feb:
                total += rec.feb
            if rec.mar:
                total += rec.mar
            if rec.apr:
                total += rec.apr
            if rec.may:
                total += rec.may
            if rec.jun:
                total += rec.jun
            if rec.jul:
                total += rec.jul
            if rec.aug:
                total += rec.aug
            if rec.sep:
                total += rec.sep
            if rec.octo:
                total += rec.octo
            if rec.nov:
                total += rec.nov
            if rec.dec:
                total += rec.dec
            rec.total = total

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        today = date.today() + timedelta(days=365)
        # for rec in self:
        #     rec.dept_id = self.employee_id.department_id.id
        #     rec.division = self.employee_id.division.id
        #     rec.section = self.employee_id.section.id
        #     rec.practise = self.employee_id.practise.id
        #     rec.branch_id = self.employee_id.user_id.branch_id.id
        fy = self.env['account.period'].search([('date_start', '<', today), ('date_stop', '>', today)])
        if fy:
            self.fiscalyr = fy.fiscalyear_id.id

    def send_calendar_action_emails(self, record, action, requester, email_to):
        template_obj = self.env.ref('kw_recruitment_calendar.recruitment_calendar_action_template')
        datas = self.env['kw_recruitment_budget_lines'].sudo().search([('parent_ref_id', '=', record.id)])
        mail = self.env['mail.template'].browse(template_obj.id).with_context(
            requester=requester,
            # email_cc = tag_cc,
            action=action,
            datas=datas,
            email_to=email_to).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        # self.env.user.notify_success("Mail sent successfully.")

    def call_publish_method(self):
        # if self.total == 0:
        #     print("inside=====================================")
        #     raise ValidationError("Resource Required Can't be Zero.")
        form_id = self.env.ref('kw_recruitment_calendar.budget_publish_confirmation_form').id
        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id,
            'res_model': 'kw_recruitment_positions',
            'res_id': self.id,
            'target': 'new'
        }

    @api.multi
    def publish_plan(self):
        """ A calendar request will be Approved """
        self.write({'status': 'publish'})
        self.sudo().create_budget_lines()
        self.sudo().send_calendar_action_emails(self, "Approved", self.employee_id.name, self.employee_id.work_email)

    def reject_plan(self):
        """ A calendar request will be rejected and email notification will be sent to person wh as raised the request """
        form_id = self.env.ref('kw_recruitment_calendar.budget_reject_confirmation_form').id
        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id,
            'res_model': 'kw_recruitment_positions',
            'res_id': self.id,
            'target': 'new'
        }

    def reject_plan_action(self):
        self.write({'status': 'reject'})
        self.send_calendar_action_emails(self, "Rejected", self.employee_id.name, self.employee_id.work_email)

    def draft_plan(self):
        self.write({'status': 'draft'})

    @api.model
    def get_fy_data(self, **kwargs):
        datalist = []
        fy = self.env['account.fiscalyear'].search([])
        if fy:
            for rec in fy:
                default_fy = True if rec.date_start < datetime.date.today() < rec.date_stop else False
                datalist.append({"id": rec.id, "name": rec.name, 'default_fy': default_fy})
        return datalist

    @api.model
    def get_resource_data(self, **kwargs):
        domain = []
        selected_fiscal_year = kwargs.get('selected_fiscal_year', False)
        if selected_fiscal_year:
            fy = self.env['account.fiscalyear'].search([('id', '=', int(selected_fiscal_year))])
            if fy:
                domain = [('fiscalyr', '=', fy.id), ('status', '=', 'publish')]
            else:
                domain = [('status', '=', 'publish')]
        vals = {}
        datalist = []
        if domain:
            records = self.sudo().search(domain)
            counter = 0
            for key, rec in enumerate(records):
                if rec.apr:
                    vals[counter] = self._prepare_data(rec, 'apr')
                    counter += 1
                if rec.may:
                    vals[counter] = self._prepare_data(rec, 'may')
                    counter += 1
                if rec.jun:
                    vals[counter] = self._prepare_data(rec, 'jun')
                    counter += 1
                if rec.jul:
                    vals[counter] = self._prepare_data(rec, 'jul')
                    counter += 1
                if rec.aug:
                    vals[counter] = self._prepare_data(rec, 'aug')
                    counter += 1
                if rec.sep:
                    vals[counter] = self._prepare_data(rec, 'sep')
                    counter += 1
                if rec.octo:
                    vals[counter] = self._prepare_data(rec, 'octo')
                    counter += 1
                if rec.nov:
                    vals[counter] = self._prepare_data(rec, 'nov')
                    counter += 1
                if rec.dec:
                    vals[counter] = self._prepare_data(rec, 'dec')
                    counter += 1
                if rec.jan:
                    vals[counter] = self._prepare_data(rec, 'jan')
                    counter += 1
                if rec.feb:
                    vals[counter] = self._prepare_data(rec, 'feb')
                    counter += 1
                if rec.mar:
                    vals[counter] = self._prepare_data(rec, 'mar')
                    counter += 1
            datalist.append(vals)
            return datalist
        else:
            return False

    @api.model
    def _prepare_data(self, rec, month):
        vals = {
            'rec_id': rec.id,
            'designation': rec.designation.name,
            'tech': rec.technology.name,
            'branch': rec.branch_id.city,
            'apr': rec.apr if month == "apr" else 0,
            'apr_budget': rec.apr_budget if month == "apr" and rec.apr_budget else 0,
            'may': rec.may if month == "may" else 0,
            'may_budget': rec.may_budget if month == "may" and rec.may_budget else 0,
            'jun': rec.jun if month == "jun" else 0,
            'jun_budget': rec.jun_budget if month == "jun" and rec.jun_budget else 0,
            'jul': rec.jul if month == "jul" else 0,
            'jul_budget': rec.jul_budget if month == "jul" and rec.jul_budget else 0,
            'aug': rec.aug if month == "aug" else 0,
            'aug_budget': rec.aug_budget if month == "aug" and rec.aug_budget else 0,
            'sep': rec.sep if month == "sep" else 0,
            'sep_budget': rec.sep_budget if month == "sep" and rec.sep_budget else 0,
            'octo': rec.octo if month == "octo" else 0,
            'octo_budget': rec.octo_budget if month == "octo" and rec.octo_budget else 0,
            'nov': rec.nov if month == "nov" else 0,
            'nov_budget': rec.nov_budget if month == "nov" and rec.nov_budget else 0,
            'dec': rec.dec if month == "dec" else 0,
            'dec_budget': rec.dec_budget if month == "dec" and rec.dec_budget else 0,
            'jan': rec.jan if month == "jan" else 0,
            'jan_budget': rec.jan_budget if month == "jan" and rec.jan_budget else 0,
            'feb': rec.feb if month == "feb" else 0,
            'feb_budget': rec.feb_budget if month == "feb" and rec.feb_budget else 0,
            'mar': rec.mar if month == "mar" else 0,
            'mar_budget': rec.mar_budget if month == "mar" and rec.mar_budget else 0,
        }
        return vals

    @api.model
    def save_resource_data(self, *args, **kwargs):
        data = kwargs.get('rec')
        # print(data)
        for rec in data:
            temp = rec['name'].split('_')
            self.browse(temp[1]).write({'%s_budget' % temp[2]: rec['value']})
        return True

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('self.rc_seq') or 'New'
        new_code = 'RC/' + code
        vals['code'] = new_code
        result = super(RecruitmentPosition, self).create(vals)
        if (result.apr or result.may or result.jun or result.jul or result.aug or result.sep or result.octo
                or result.nov or result.dec or result.jan or result.feb or result.mar):
            pass
        else:
            raise ValidationError("Resource required can't be blank.")
        users_data = self.env['res.users'].sudo().search([])
        rcm_head = users_data.filtered(lambda user: user.has_group('kw_recruitment.group_tag_budget_user') == True)
        work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
        self.send_calendar_action_emails(result, "Applied", 'Team', str(work_email))
        self.env.user.notify_success("Calendar created successfully.")
        return result

    @api.multi
    def write(self, vals):
        # print("write called=======",self,vals)
        if not (self._context.get('publish_plan_details') or self._context.get('reject_plan_details')):
            # print("inside first iffff=============")
            if self.total == 0 or vals.get('total') == 0:
                # print("self.total=============",self.total)
                raise ValidationError("Resource required cant be blank")

            self.env.user.notify_success("Records saved successfully.")
        return super(RecruitmentPosition, self).write(vals)

    # @api.multi
    # def unlink(self):
    #     for plan in self:
    #         if plan.status not in ('draft') and not self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
    #             raise UserError(_('Cannot delete plan(s) which are already submitted.'))
    #     return super(RecruitmentPosition, self).unlink()

    def create_budget_lines(self):
        self.env.user.notify_success("Calendar Published successfully.")
        if self.apr:
            for i in range(self.apr):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'apr', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'technology': self.technology.id, 'branch_id': self.branch_id.id,
                     'project': self.project.id,
                     'sort': 4,
                     'type_of_project': self.type_of_project, 'resource_type': self.resource_type,
                     'exp_year': self.exp_year,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                     # 'name':self.dept_id.code + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.may:
            for i in range(self.may):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'may', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type,
                     'technology': self.technology.id, 'branch_id': self.branch_id.id,
                     'exp_year': self.exp_year,
                     'sort': 5,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                     #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.jun:
            for i in range(self.jun):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'jun', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type,
                     'technology': self.technology.id, 'branch_id': self.branch_id.id,
                     'exp_year': self.exp_year,
                     'sort': 6,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                     #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.jul:
            for i in range(self.jul):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'jul', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 7,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.aug:
            for i in range(self.aug):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'aug', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 8,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.sep:
            for i in range(self.sep):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'sep', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 9,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.octo:
            for i in range(self.octo):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'octo', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 10,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.nov:
            for i in range(self.nov):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'nov', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 11,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.dec:
            for i in range(self.dec):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'dec', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 12,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.jan:
            for i in range(self.jan):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'jan', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 1,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.feb:
            for i in range(self.feb):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'feb', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 2,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        if self.mar:
            for i in range(self.mar):
                res = self.env['kw_recruitment_budget_lines'].create(
                    {'parent_ref_id': self.id, 'planned_month': 'mar', 'resource': 1, 'fiscalyr': self.fiscalyr.id,
                     'employee_id': self.employee_id.id, 'dept_id': self.dept_id.id, 'division': self.division.id,
                     'section': self.section.id, 'practise': self.practise.id, 'designation': self.designation.id,
                     'project': self.project.id, 'type_of_project': self.type_of_project,
                     'resource_type': self.resource_type, 'technology': self.technology.id,
                     'branch_id': self.branch_id.id, 'exp_year': self.exp_year, 'sort': 3,
                     'qualification_ids': [(6, 0, self.qualification_ids.ids)]})
                #   'name':self.dept_id.display_name + "/" + str(self.fiscalyr.name) + "/" + str(count),
                # count += 1
        return


class RecruitmentBudgetLines(models.Model):
    _name = "kw_recruitment_budget_lines"
    _description = "Recruitment Budget Lines"
    _rec_name = "name"
    _order = "id desc"

    @api.model
    def _get_year_list(self):
        years = 40
        return [(str(i), i) for i in range(years + 1)]

    name = fields.Char('Name')
    treasury_budget_id = fields.Many2one('kw_recruitment_treasury_budget_line', string="Treasury Budget Id")
    parent_ref_id = fields.Many2one('kw_recruitment_positions', string="Ref#")
    fiscalyr = fields.Many2one('account.fiscalyear', string="FY")
    employee_id = fields.Many2one('hr.employee', string="Rasied By",
                                  domain=[('employement_type.code', '!=', 'O'), ('active', '=', True)])
    dept_id = fields.Many2one('hr.department', string='Department', domain=[('dept_type.code', '=', 'department')])
    division = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
    section = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'section')])
    practise = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'practice')])
    designation = fields.Many2one('hr.job', string="Job Position", required="1")
    project = fields.Many2one('crm.lead', string='Project')
    type_of_project = fields.Selection(string='Type Of Project',
                                       selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                       default='work')
    resource_type = fields.Selection(string='Resource Type', track_visibility='onchange',
                                     selection=[('fresher', 'Fresher'), ('lateral', 'Lateral')], default='fresher')
    stage_id = fields.Many2one('hr.recruitment.stage', string="Stage")
    technology = fields.Many2one('kw_skill_master', string="Technology")
    branch_id = fields.Many2one('kw_res_branch', string='Branch', required="1")
    jan_budget = fields.Integer('Jan')
    feb_budget = fields.Integer('Feb')
    mar_budget = fields.Integer('Mar')
    apr_budget = fields.Integer('Apr')
    may_budget = fields.Integer('May')
    jun_budget = fields.Integer('Jun')
    jul_budget = fields.Integer('Jul')
    aug_budget = fields.Integer('Aug')
    sep_budget = fields.Integer('Sep')
    octo_budget = fields.Integer('Oct')
    nov_budget = fields.Integer('Nov')
    dec_budget = fields.Integer('Dec')
    planned_month = fields.Char('Month')
    status = fields.Selection([('draft', 'Draft'), ('publish', 'Published'), ('reject', 'Rejected')],
                              string="Status", default='draft', readonly=True)
    total_budget = fields.Integer('Total Budget', compute='_compute_total_budget', store=True)
    resource = fields.Integer(string="Resource")
    qualification_ids = fields.Many2many("kw_qualification_master", string="Qualification")
    exp_year = fields.Selection(string='Exp (Years)', selection='_get_year_list', default="0", required="1")
    resource_joined = fields.Many2one('hr.employee', 'Resource Joined')
    resource_tobe_joined = fields.Many2one('hr.applicant', 'Resource To Be Joined',
                                           domain=[('stage_id.code', '=', 'OA')])
    total_incurred = fields.Integer('Total [Incurred]')
    total_remaining = fields.Integer('Total [Remaining]', compute='_compute_total_budget', store=True)
    hiring_status = fields.Selection(string='Hiring Status',
                                     selection=[('joined', 'Joined'), ('hold', 'Hold'), ('to_be_hired', 'To be hired'),
                                                ('offered', 'Offered'), ('joined_left', 'Joined & Left'),
                                                ('cancelled', 'Cancelled'), ('mrf_yet', 'MRF Yet to be approved')])
    code = fields.Char(string="Reference No.", default="New", readonly="1")
    # ref_code = fields.Char(string= "Reference Code" ,compute='_compute_refenece_code', store=True) 
    year = fields.Integer(compute='compute_year', store=True)
    month = fields.Integer(compute='compute_year', store=True)
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='MRF')
    offer_id = fields.Many2one('hr.applicant.offer', string='Offer No')
    sort = fields.Integer(string='Sort')
    department_name = fields.Char(string='Department')
    Job_name = fields.Char(string='Designation')
    department_sequence = fields.Integer(string='Department Sequence')
    published_by = fields.Char(string="Published By", compute='_compute_budget_lines_published_by', store=True)

    @api.depends('status')
    def _compute_budget_lines_published_by(self):
        for rec in self:
            if rec.write_uid and rec.status == 'publish':
                rec.published_by = rec.write_uid.employee_ids.name

    @api.depends('create_date')
    def compute_year(self):
        for rec in self:
            if rec.create_date:
                rec.year = rec.create_date.year
                rec.month = int(rec.create_date.month)

    @api.multi
    def department_last_sequence(self, dept_id, filtered_records):
        # print("method calleddddd", dept_id)
        last_code = False
        if filtered_records:
            list_data = filtered_records.mapped('department_sequence')
            # print("===",max(list_data),list_data.index(max(list_data)))
            max_index = list_data.index(max(list_data))
            last_code = self.env['kw_recruitment_budget_lines'].search([('id', '=', filtered_records[max_index].id)])
        # else:
        #     last_code = self.env['kw_recruitment_budget_lines'].search([('dept_id','=',int(dept_id))],order="sort asc", limit=1)
        # print("last_code===2=====",last_code)
        dept_last_id = str(last_code.name if last_code else False).split('/')[-1]
        # print("dept_id========",dept_last_id)
        return int(dept_last_id) if dept_last_id not in ['False', ''] else 0

    # def get_fiscal_year(self):
    #     current_date = date.today()
    #     current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search([('date_start','<=',current_date),('date_stop','>=',current_date)],limit=1)
    #     self.fiscalyr = current_fiscal_year_id

    def call_publish_method(self):
        if self.mar_budget == 0:
            # print("inside mar budget====")
            raise ValidationError("Month wise Budgets cannot be Blank")

        form_id = self.env.ref('kw_recruitment_calendar.budget_line_publish_confirmation_form').id
        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id,
            'res_model': 'kw_recruitment_budget_lines',
            'res_id': self.id,
            'target': 'new'
        }

    def reject_plan(self):
        """ A Budget line will be rejected """

        template_obj = self.env.ref('kw_recruitment_calendar.recruitment_budget_action_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(
            requester=self.employee_id.name,
            # email_cc = tag_cc,
            action="Declined",
            email_to=self.employee_id.work_email).send_mail(self.id,
                                                            notif_layout='kwantify_theme.csm_mail_notification_light')
        self.write({'status': 'publish'})
        self.env.user.notify_success("Budget Declined successfully.")

    @api.multi
    def publish_budget(self):
        """ Current Selected Budget will be Approved """
        template_obj = self.env.ref('kw_recruitment_calendar.recruitment_budget_action_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(
            requester=self.employee_id.name,
            # email_cc = tag_cc,
            action="Published",
            email_to=self.employee_id.work_email).send_mail(self.id,
                                                            notif_layout='kwantify_theme.csm_mail_notification_light')
        self.write({'status': 'publish'})
        self.env.user.notify_success("Budget Published successfully.")

    # @api.depends('mar_budget','technology','designation','exp_year')
    # def _compute_refenece_code(self):
    #     for rec in self:
    #         if rec.create_date:
    #             rec.create_date = rec.create_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    #             month = rec.create_date.strftime("%b") 
    #             if rec.code and rec.technology and rec.designation and rec.mar_budget and rec.exp_year :
    #                 rec.ref_code = rec.code + "|" + rec.mar_budget + "|" + rec.designation.name + "|"  + rec.exp_year + "|" + rec.technology.name + "|" + month

    @api.model
    def create(self, values):
        # print("crete called=================",self,values)
        code = self.env['ir.sequence'].next_by_code('self.rb_seq') or 'New'
        new_code = 'RB/' + code
        values['code'] = new_code
        result = super(RecruitmentBudgetLines, self).create(values)
        self.env.user.notify_success("Records created successfully.")
        return result

    @api.onchange('resource_tobe_joined')
    def _onchange_resource_tobe_joined(self):
        monthly_ctc_amt = 0
        joining_date = self.resource_tobe_joined.offer_id.joining_date
        if self.resource_tobe_joined and not self.resource_joined:
            if self.resource_tobe_joined.offer_id and self.resource_tobe_joined.offer_id.offer_type:
                monthly_ctc_amt = self.resource_tobe_joined.offer_id.average_1_month
        if self.resource_joined and self.resource_tobe_joined:
            raise ValidationError("Cannot change the values.")

        self.get_monthly_ctc_data(monthly_ctc_amt, joining_date, self)

    @api.onchange('resource_joined')
    def _onchange_resource_joined(self):
        monthly_ctc_amt = 0
        joining_date = self.resource_joined.date_of_joining
        if self.resource_joined and self.resource_tobe_joined:
            monthly_ctc_amt = self.resource_joined.current_ctc
        self.get_monthly_ctc_data(monthly_ctc_amt, joining_date, self)

    @api.multi
    def get_monthly_ctc_data(self, monthly_ctc_amt, joining_date, record):
        monthly_ctc = {'4': monthly_ctc_amt,
                       '5': monthly_ctc_amt,
                       '6': monthly_ctc_amt,
                       '7': monthly_ctc_amt,
                       '8': monthly_ctc_amt,
                       '9': monthly_ctc_amt,
                       '10': monthly_ctc_amt,
                       '11': monthly_ctc_amt,
                       '12': monthly_ctc_amt,
                       '1': monthly_ctc_amt,
                       '2': monthly_ctc_amt,
                       '3': monthly_ctc_amt,
                       }
        if record.resource_tobe_joined and joining_date:
            acceptance_month = joining_date.month  # Offer Acceptance Month
            acceptance_day = joining_date.day  # Offer Acceptance day
            month_days = calendar.monthrange(joining_date.year, joining_date.month)[1]  # total month days
            incurred = 0
            if str(acceptance_month) in monthly_ctc:
                count = 0
                for rec in list(monthly_ctc)[list(monthly_ctc).index(str(acceptance_month)):]:
                    if count == 0:
                        incurred = round(
                            ((month_days - acceptance_day) + 1) * (int(monthly_ctc.get(f'{rec}')) / month_days))
                        record.total_incurred = incurred
                        record.total_remaining = int(record.total_budget) - int(record.total_incurred)
                        count += 1
                    else:
                        incurred += int(monthly_ctc.get(f'{rec}'))
                        record.total_incurred = incurred
                        record.total_remaining = int(record.total_budget) - int(record.total_incurred)
        else:
            # print("else part--")
            record.total_remaining = record.total_budget - record.total_incurred

    @api.onchange('apr_budget')
    def _onchange_apr_budget(self):
        for rec in self:
            if rec.apr_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget = rec.may_budget = rec.apr_budget

    @api.onchange('may_budget')
    def _onchange_may_budget(self):
        for rec in self:
            if rec.may_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget = rec.may_budget

    @api.onchange('jun_budget')
    def _onchange_jun_budget(self):
        for rec in self:
            if rec.jun_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget

    @api.onchange('jul_budget')
    def _onchange_jul_budget(self):
        for rec in self:
            if rec.jul_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget

    @api.onchange('aug_budget')
    def _onchange_aug_budget(self):
        for rec in self:
            if rec.aug_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget

    @api.onchange('sep_budget')
    def _onchange_sep_budget(self):
        for rec in self:
            if rec.sep_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget

    @api.onchange('octo_budget')
    def _onchange_octo_budget(self):
        for rec in self:
            if rec.octo_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget

    @api.onchange('nov_budget')
    def _onchange_nov_budget(self):
        for rec in self:
            if rec.nov_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget

    @api.onchange('dec_budget')
    def _onchange_dec_budget(self):
        for rec in self:
            if rec.dec_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget

    @api.onchange('jan_budget')
    def _onchange_jan_budget(self):
        for rec in self:
            if rec.jan_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget

    @api.onchange('feb_budget')
    def _onchange_feb_budget(self):
        for rec in self:
            if rec.feb_budget:
                rec.mar_budget = rec.feb_budget

    @api.depends('jan_budget', 'feb_budget', 'mar_budget', 'apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'octo_budget', 'nov_budget', 'dec_budget')
    def _compute_total_budget(self):
        for rec in self:
            total_budget = 0
            if rec.jan_budget:
                total_budget += rec.jan_budget
            if rec.feb_budget:
                total_budget += rec.feb_budget
            if rec.mar_budget:
                total_budget += rec.mar_budget
            if rec.apr_budget:
                total_budget += rec.apr_budget
            if rec.may_budget:
                total_budget += rec.may_budget
            if rec.jun_budget:
                total_budget += rec.jun_budget
            if rec.jul_budget:
                total_budget += rec.jul_budget
            if rec.aug_budget:
                total_budget += rec.aug_budget
            if rec.sep_budget:
                total_budget += rec.sep_budget
            if rec.octo_budget:
                total_budget += rec.octo_budget
            if rec.nov_budget:
                total_budget += rec.nov_budget
            if rec.dec_budget:
                total_budget += rec.dec_budget
            rec.total_budget = total_budget
            if rec.mar_budget:
                rec.total_remaining = rec.total_budget - rec.total_incurred


class CalendarSummary(models.Model):
    _name = "kw_calendar_summary"
    _description = "Calendar Summary"
    _auto = False

    create_date = fields.Date('Create Date')
    dept_id = fields.Many2one('hr.department', string='Department')
    designation = fields.Many2one('hr.job', string="Designation", required="1")
    technology = fields.Many2one('kw_skill_master', string="Technology")
    total_resource = fields.Integer('Numbers')
    planned_budget = fields.Char('Planned Budget')
    remaining_budget = fields.Char('Remaining Budget')
    hire_till_date = fields.Char('Hired till Date')
    remaining_to_hire = fields.Char('Remaining to Hire')
    incurred_annual = fields.Char('Incurred(Annual)')
    offered_to_join = fields.Char('Offered (To Join)')
    fy_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT
    row_number() over() AS id,
    dept_id AS dept_id,
    designation AS designation,
    technology AS technology,
    fiscalyr AS fy_id,
    create_date AS create_date,
    SUM(CASE WHEN CAST(apr_budget AS int) > 0 THEN CAST(apr_budget AS int)*12 ELSE 0 END) +
    SUM(CASE WHEN CAST(may_budget AS int) > 0 THEN CAST(may_budget AS int)*11 ELSE 0 END) +
    SUM(CASE WHEN CAST(jun_budget AS int) > 0 THEN CAST(jun_budget AS int)*10 ELSE 0 END) +
    SUM(CASE WHEN CAST(jul_budget AS int) > 0 THEN CAST(jul_budget AS int)*9 ELSE 0 END) +
    SUM(CASE WHEN CAST(aug_budget AS int) > 0 THEN CAST(aug_budget AS int)*8 ELSE 0 END) +
    SUM(CASE WHEN CAST(sep_budget AS int) > 0 THEN CAST(sep_budget AS int)*7 ELSE 0 END) +
    SUM(CASE WHEN CAST(octo_budget AS int) > 0 THEN CAST(octo_budget AS int)*6 ELSE 0 END) +
    SUM(CASE WHEN CAST(nov_budget AS int) > 0 THEN CAST(nov_budget AS int)*5 ELSE 0 END) +
    SUM(CASE WHEN CAST(dec_budget AS int) > 0 THEN CAST(dec_budget AS int)*4 ELSE 0 END) +
    SUM(CASE WHEN CAST(jan_budget AS int) > 0 THEN CAST(jan_budget AS int)*3 ELSE 0 END) +
    SUM(CASE WHEN CAST(feb_budget AS int) > 0 THEN CAST(feb_budget AS int)*2 ELSE 0 END) +
    SUM(CASE WHEN CAST(mar_budget AS int) > 0 THEN CAST(mar_budget AS int)*1 ELSE 0 END) as planned_budget,
    SUM(CAST(total AS int)) AS total_resource,
    SUM(CAST(total AS int)) AS remaining_to_hire,
    SUM(CAST(total AS int)) AS offered_to_join,
    SUM(CAST(total AS int)) AS incurred_annual,
    SUM(CAST(total AS int)) AS hire_till_date,
    SUM(CAST(total AS int)) AS remaining_budget
    FROM kw_recruitment_positions GROUP BY dept_id,designation,technology,fiscalyr,create_date
            )""" % (self._table))


class BudgetInherit(models.Model):
    _inherit = "kw_recruitment_requisition"
    _description = "budget add"

    budget_id = fields.Many2many('kw_recruitment_budget_lines', 'budget_line_mrf', string='Budget Reference')

    # @api.constrains('job_position','technology','dept_name','min_exp_year','no_of_resource')
    # def validate_job_position(self):
    #     # print('validation called=============',self.budget_id)
    #     designation = self.budget_id.mapped('designation.id')
    #     department = self.budget_id.mapped('dept_id.id')
    #     experience = self.budget_id.mapped('exp_year')
    #     technology = self.budget_id.mapped('technology.id')
    #     resource = len(self.budget_id)

    #     current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()

    #     budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(['|',('mrf_id','=',self.id),('mrf_id','=',False),('fiscalyr','=',current_fiscal_year_id.id),('offer_id','=',False),('dept_id','=',self.dept_name.id),('technology','=',self.technology.id),('designation','=',self.job_position.id),('exp_year','=',self.min_exp_year),('status','=','publish'),('resource_joined','=',False),('resource_tobe_joined','=',False),('mar_budget','!=',False)],order='department_sequence asc')
    #     # print("length========================++++++++++++++++++++",budget_lines,len(budget_lines))
    #     # print("inside constrains============",designation,department,experience,technology,resource)
    #     if (not self.job_position.id in designation) or (not self.dept_name.id in department) or (not self.min_exp_year in experience) or (not self.technology.id in technology) or (self.no_of_resource != resource):
    #         # print("validation called")
    #         # print('self===================================================',self.budget_id)
    #         if self.requisition_type == 'treasury' and len(budget_lines) != 0 and not self.budget_id:
    #             print("inside calender-----------------")
    #             raise ValidationError(f"Maximum number of resources can be {len(budget_lines)}.")

# class DesignationCode(models.Model):
#     _inherit="hr.job"
#     _description = 'Store last designation code sequence of budget according to job positions'


#     last_budget_sequence = fields.Char(string='Last Sequence' )
# calendar_id = fields.Many2one("kw_recruitment_positions")   


# @api.model
# def designation_last_sequence(self,designation):
#     print("method calleddddd")
#     last_code = self.env['kw_recruitment_budget_lines'].search([('designation','=',self.calendar_id.designation.id,)],order="id desc", limit=1)
#     print("=====",last_code)
