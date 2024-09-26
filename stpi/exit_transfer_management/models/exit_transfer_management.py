
# -*- coding: utf-8 -*-\
import base64
from odoo import models, fields, api
from datetime import datetime,timedelta, date
from odoo.exceptions import UserError



class ExitTransferManagement(models.Model):
    _name = 'exit.transfer.management'
    _description = 'Exit Transfer Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    @api.depends("employee_id")
    def get_des_and_id(self):
        for rec in self:
            if rec.employee_id:
                rec.job_id = rec.employee_id.job_id.id
                rec.employee_no = rec.employee_id.identify_id
                rec.branch_id = rec.employee_id.branch_id.id
                rec.department_id = rec.employee_id.department_id.id

    name = fields.Char()
    employee_id = fields.Many2one("hr.employee", string="Employee Name")
    job_id = fields.Many2one("hr.job", string="Designation", compute="get_des_and_id", store=True,copy=False)
    branch_id = fields.Many2one("res.branch", string="Center", compute="get_des_and_id", store=True,copy=False)
    to_branch_id = fields.Many2one("res.branch", string="To Center", store=True,copy=False)
    roster_line_item = fields.Many2one('recruitment.roster', string="Roster line")
    department_id = fields.Many2one("hr.department", string="Department", compute="get_des_and_id", store=True,copy=False)
    employee_no = fields.Char(string="Employee Id", compute="get_des_and_id", store=True,copy=False)
    ignore_all = fields.Boolean('Ignore All', default=False)
    exit_reason = fields.Text("Exit Reason")
    date = fields.Date('Date',default=fields.Date.context_today)
    exit_date = fields.Date('Exit Date')
    exit_type = fields.Selection([("Suspended", "Suspended"),
                                  ("Resigned", "Resigned"),
                                  ("Contract Expired ", "Contract Expired "),
                                  ("technical resignation","Technical Resignation"),
                                  ("Superannuation", "Superannuation"),
                                  ("Deceased","Deceased"),
                                  ("Terminated","Terminated"),
                                  ("Absconding","Absconding"),
                                  ("Transferred","Transferred"),
                                  ("deputation","Deputation"),
                               ],string='Type of Exit')

    reg_type = fields.Selection([
                                  ("internal","Internal"),
                                  ("external","External"),
                                  ("deputation","Deputation")
                               ],string='Resignation Type')

    transferred_req = fields.Selection([
                                  ("yes","Yes"),
                                  ("no","No")
                               ],string='Transferred Required')

    dues_finance = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    employee_finance = fields.Many2one("hr.employee", store=True)
    remarks_finance = fields.Char(store=True)
    dues_general = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    employee_general = fields.Many2one("hr.employee", store=True)
    remarks_general = fields.Char(store=True)
    dues_personal = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_personal = fields.Char(store=True)
    employee_personal = fields.Many2one("hr.employee", string='Employee Name', store=True)
    dues_technical = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_technical = fields.Char(store=True)
    employee_technical = fields.Many2one("hr.employee", store=True)

    dues_ro = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_ro = fields.Char(store=True)
    employee_ro = fields.Many2one("hr.employee", store=True)

    dues_remark_finance = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    employee_remark_finance = fields.Many2one("hr.employee", store=True)
    remarks_remark_finance = fields.Char(store=True)
    dues_remark_general = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    employee_remark_general = fields.Many2one("hr.employee", store=True)
    remarks_remark_general = fields.Char(store=True)
    dues_remark_personal = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_remark_personal = fields.Char( store=True)
    employee_remark_personal = fields.Many2one("hr.employee", store=True)
    dues_remark_technical = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_remark_technical = fields.Char(store=True)
    employee_remark_technical = fields.Many2one("hr.employee", store=True)

    dues_remark_ro = fields.Selection([("Yes", "Yes"),
                                  ("No", "No"),
                               ], store=True)
    remarks_remark_ro = fields.Char(store=True)
    employee_remark_ro = fields.Many2one("hr.employee", store=True)

    state = fields.Selection([("draft", "Draft"),
                               ("verify", "Verify"),
                               ("send_for_approval", "Approval Waiting"),
                               ("complete", "Completed"),
                               ("cancel","Cancel")
                               ],string='Status', copy=False, default='draft', required=True, readonly=True)
    leave_line_ids = fields.One2many("leave.lines","exit_transfer_id", string="Submitted Lines")
    pending_leave_line_ids = fields.One2many("pending.leave.lines","exit_transfer_id", string="Pending Lines")
    upcoming_leave_line_ids = fields.One2many("upcoming.leave.lines","exit_transfer_id")

    pending_tour_req_ids = fields.One2many("pending.tour.request","exit_transfer_id", )
    submitted_tour_req_ids = fields.One2many("submitted.tour.request","exit_transfer_id")
    upcoming_tour_req_ids = fields.One2many("upcoming.tour.request","exit_transfer_id")

    # LTC and Advance
    pending_ltc_sequence_ids = fields.One2many("pending.employee.ltc.request", "exit_transfer_id",
                                               string="Pending for Approval LTC Advance")
    submitted_ltc_sequence_ids = fields.One2many("employee.ltc.request", "exit_transfer_id", string="Submitted LTC Advance")
    upcoming_ltc_sequence_ids = fields.One2many("upcoming.employee.ltc.request", "exit_transfer_id", string="Upcoming LTC Advance")

    # LTC Claim
    pending_ltc_claim_ids = fields.One2many("pending.ltc.claim.request", "exit_transfer_id", string="Pending  LTC Claim")
    submitted_ltc_claim_ids = fields.One2many("ltc.claim.request", "exit_transfer_id", string="Submitted  LTC Claim")
    upcoming_ltc_claim_ids = fields.One2many("upcoming.ltc.claim.request", "exit_transfer_id", string="Upcoming  LTC Claim")

    #tour Claim
    pending_tour_claim_req_ids = fields.One2many("pending.tour.claim.request", "exit_transfer_id", string="Pending Tour Claim")
    submitted_tour_claim_req_ids = fields.One2many("submitted.tour.claim.request", "exit_transfer_id", string=" Submitted Tour Claim")
    upcoming_tour_claim_req_ids = fields.One2many("upcoming.tour.claim.request", "exit_transfer_id", string=" Upcoming Tour Claim")

    # Vehicle Request
    pending_vehicle_req_ids = fields.One2many("pending.vehicle.request", "exit_transfer_id")
    submitted_vehicle_req_ids = fields.One2many("submitted.vehicle.request", "exit_transfer_id")
    upcoming_vehicle_req_ids = fields.One2many("upcoming.vehicle.request", "exit_transfer_id")

    # PF Request
    pending_pf_req_ids = fields.One2many("pending.pf.request", "exit_transfer_id")
    submitted_pf_req_ids = fields.One2many("submitted.pf.request", "exit_transfer_id")
    upcoming_pf_req_ids = fields.One2many("upcoming.pf.request", "exit_transfer_id")

    # Appraisal Request
    pending_appraisal_request_ids = fields.One2many("pending.appraisal.request", "exit_transfer_id")
    submitted_appraisal_request_ids = fields.One2many("submitted.appraisal.request", "exit_transfer_id")
    upcoming_appraisal_request_ids = fields.One2many("upcoming.appraisal.request", "exit_transfer_id")

    # income Tax
    pending_income_tax_ids = fields.One2many("pending.income.tax.request", "exit_transfer_id", string="Pending Income Tax request")
    submitted_income_tax_ids = fields.One2many("submitted.income.tax.request", "exit_transfer_id", string="Submitted Income Tax request")
    upcoming_income_tax_ids = fields.One2many("upcoming.income.tax.request", "exit_transfer_id", string="Upcoming Income Tax request")

    # income Tax
    pending_loan_request_ids = fields.One2many("pending.hr.loan.request", "exit_transfer_id", string="Pending Loan request")
    submitted_loan_request_ids = fields.One2many("submitted.hr.loan.request", "exit_transfer_id", string="Submitted Loan request")
    upcoming_loan_request_ids = fields.One2many("upcoming.hr.loan.request", "exit_transfer_id", string="Upcoming Loan request")
    not_transferrred_loan_request_ids = fields.One2many("nottransferred.hr.loan.request", "exit_transfer_id", string="Completed Loan request")

    # eFile
    my_correspondence_ids = fields.One2many("correspondence.exit.management", "exit_transfer_id", string="Correspondence")
    my_file_ids = fields.One2many("file.exit.management", "exit_transfer_id", string="Files")
    forward_to_user = fields.Many2one('res.users', string='User')

    #Indent
    pending_indent_req_ids = fields.One2many("pending.indent.request", "exit_transfer_id")
    submitted_indent_req_ids = fields.One2many("submitted.indent.request", "exit_transfer_id")
    upcoming_indent_req_ids = fields.One2many("upcoming.indent.request", "exit_transfer_id")

    #GRN
    pending_grn_ids = fields.One2many("pending.grn", "exit_transfer_id")
    submitted_grn_ids = fields.One2many("submitted.grn", "exit_transfer_id")
    upcoming_grn_ids = fields.One2many("upcoming.grn", "exit_transfer_id")

    #Issue Request
    pending_issue_req_ids = fields.One2many("pending.issue.request", "exit_transfer_id",string="Pending Issue Request")
    submitted_issue_req_ids = fields.One2many("submitted.issue.request","exit_transfer_id",string="Submitted Issue Request" )
    upcoming_issue_req_ids = fields.One2many("upcoming.issue.request","exit_transfer_id",string="Upcoming Issue Request" )

    #GRN Request
    pending_grn_req_ids = fields.One2many("pending.grn.request", "exit_transfer_id")
    submitted_grn_req_ids = fields.One2many("submitted.grn.request", "exit_transfer_id")
    upcoming_grn_req_ids = fields.One2many("upcoming.grn.request", "exit_transfer_id")

    #check birthday
    pending_check_birth_ids = fields.One2many("pending.check.birthday", "exit_transfer_id",string="Pending Check Birthday Request")
    submitted_check_birth_ids = fields.One2many("submitted.check.birthday", "exit_transfer_id",string="Submitted Check Birthday Request")
    upcoming_check_birth_ids = fields.One2many("upcoming.check.birthday" , "exit_transfer_id",string="Upcoming Check Birthday Request")

    #reimbursement
    pending_reimbursement_ids = fields.One2many("pending.reimbursement.request", "exit_transfer_id",string="Pending Reimbursement Request")
    submitted_reimbursement_ids = fields.One2many("submitted.reimbursement.request", "exit_transfer_id",string="Submitted Reimbursement Request")
    upcoming_reimbursement_ids = fields.One2many("upcoming.reimbursement.request", "exit_transfer_id",string="Upcoming Reimbursement Request")
    
    check_admin = fields.Boolean(string='Check Admin',compute="check_group")
    check_finance = fields.Boolean(string='Check Finance',compute="check_group")
    check_general = fields.Boolean(string='Check General',compute="check_group")
    check_personal = fields.Boolean(string='Check Personal',compute="check_group")
    check_technical = fields.Boolean(string='Check Technical',compute="check_group")
    check_ro = fields.Boolean(string='Check RO',compute="check_group")

    finance_approved = fields.Boolean()
    general_approved = fields.Boolean(string='General Approved')
    personal_approved = fields.Boolean(string='Personal Approved')
    technical_approved = fields.Boolean()
    ro_approved = fields.Boolean()
    edit_user = fields.Boolean(string='Check user',compute="check_group")
    noc_visible = fields.Boolean(string='Noc Visible',compute="check_noc")
    transfer_allowance = fields.Selection([("yes", "Yes"),
                               ("no", "No")
                               ],string='Transfer Allowance Required', copy=False)
    

    @api.depends('employee_id')
    def check_group(self):
        for record in self:
            if self.env.user.has_group("exit_transfer_management.group_exit_admin_department"):
                record.check_admin = True
                record.edit_user = True
            if self.env.user.has_group("exit_transfer_management.group_exit_finance_department"):
                record.check_finance = True
            if self.env.user.has_group("exit_transfer_management.group_exit_technical_department"):
                record.check_technical = True
            if self.env.user.has_group("exit_transfer_management.group_exit_personal_department"):
                record.check_personal = True
            if self.env.user.has_group("exit_transfer_management.group_exit_general_department"):
                record.check_general = True
            if record.employee_id.parent_id.user_id.id == self.env.user.id:
                record.check_ro = True
            if record.employee_id.user_id.id == self.env.user.id:
                record.edit_user = True

    def compute_status_scheduler(self):
        pending_records = self.env['exit.transfer.management'].sudo().search([('state','in',['draft','verify','send_for_approval'])])
        for rec in pending_records:
            rec.compute_exit_management()

    def reminder_mail_scheduler(self):
        current_date = date.today()
        pending_records = self.env['exit.transfer.management'].sudo().search([('state','=','verify')])
        reminder_records = pending_records.filtered(lambda x : (current_date - x.exit_date).days <= 15)
        if reminder_records:
            for record in reminder_records:
                template = self.env.ref('exit_transfer_management.exit_management_reminder_mail_template', 
                                            raise_if_not_found=False)
                mail = self.env['mail.template'].sudo().browse(template.id)
                if mail:
                    mail.sudo().send_mail(record.id,notif_layout="mail.mail_notification_light")




    @api.depends('employee_id')
    def check_noc(self):
        noc_visible_days = self.env['ir.config_parameter'].sudo().get_param(
                'noc_visible_days')
        for record in self:
            if record.state == 'send_for_approval':
                if self.exit_type == 'technical resignation' and self.reg_type == 'internal':
                    record.noc_visible = False
                else:
                    current_date = date.today()
                    diff_days = (record.exit_date - current_date).days
                    if diff_days <= int(noc_visible_days):
                        # print('hello its true')
                        record.noc_visible = True
           

                 
            
            


        
    
    


    claim_lines1_ids = fields.One2many("claim.lines1","exit_transfer_id", string="1`Upcoming Lines")

    leave_no_dues = fields.Boolean()
    leave_remark = fields.Text()

    @api.multi
    def finance_approve(self):
        for record in self:
            record.finance_approved = True

    @api.multi
    def general_approve(self):
        for record in self:
            record.general_approved = True

    @api.multi
    def personal_approve(self):
        for record in self:
            record.personal_approved = True

    @api.multi
    def technical_approve(self):
        for record in self:
            record.technical_approved = True

    @api.multi
    def ro_approve(self):
        for record in self:
            print("record.ro_approved", record.ro_approved)
            record.ro_approved = True

    @api.onchange('dues_finance')
    @api.constrains('dues_finance')
    def get_finance_employee(self):
        for res in self:
            me_emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if me_emp:
                for employee in me_emp:
                    res.employee_finance = employee.id

    @api.onchange('exit_type')
    def change_exit_type(self):
        for res in self:
            res.transferred_req = False
            res.to_branch_id = False


    @api.onchange('dues_general')
    @api.constrains('dues_general')
    def get_general_employee(self):
        for res in self:
            me_emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if me_emp:
                for employee in me_emp:
                    res.employee_general = employee.id


    @api.onchange('dues_personal')
    @api.constrains('dues_personal')
    def get_personal_employee(self):
        for res in self:
            me_emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if me_emp:
                for employee in me_emp:
                    res.employee_personal = employee.id


    @api.onchange('dues_technical')
    @api.constrains('dues_finance')
    def get_technical_employee(self):
        for res in self:
            me_emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if me_emp:
                for employee in me_emp:
                    res.employee_technical = employee.id


    @api.onchange('dues_ro')
    @api.constrains('dues_ro')
    def get_ro_employee(self):
        for res in self:
            me_emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if me_emp:
                for employee in me_emp:
                    res.employee_ro = employee.id


    @api.model
    def create(self, vals):
        res = super(ExitTransferManagement, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('exit.transfer.management')
        sequence = 'Exit Management - ' + str(seq)
        res.name = sequence
        return res

    def button_ignore_all(self):
        for rec in self:
            rec.ignore_all=True


    def button_forward_all(self):
        for rec in self:
            if rec.forward_to_user:
                for line in rec.my_file_ids:
                    line.file_id.current_owner_id = rec.forward_to_user.id
                    me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                    self.env['exit.management.report'].sudo().create({
                        "exit_transfer_id": self.id,
                        "employee_id": self.employee_id.id,
                        "exit_type": self.exit_type,
                        "module": 'File Forwarded',
                        "module_id": str(line.file_name),
                        "action_taken_by": (me.id),
                    })
                    line.sudo().unlink()
                for line in rec.my_correspondence_ids:
                    line.correspondence_id.current_owner_id = rec.forward_to_user.id
                    line.sudo().unlink()
                    me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                    self.env['exit.management.report'].sudo().create({
                        "exit_transfer_id": self.id,
                        "employee_id": self.employee_id.id,
                        "exit_type": self.exit_type,
                        "module": 'Correspondence Forwarded',
                        "module_id": str(line.letter_no),
                        "action_taken_by": (me.id),
                    })

    #### GRN INDENT ISUUE related methods
    def _get_submitted_grn(self):
        submit_grn = []
        if self.employee_id.user_id.has_group('indent_stpi.group_grn_create'):
            indents = self.env['indent.request'].search([('employee_id','=',self.employee_id.id),
                                                 ('branch_id','=',self.branch_id.id),
                                                 ('state','=','approved'),
                                                 ('indent_type','=','grn')])
            if indents:
                submit_grn = [[0, 0, {
                        "exit_transfer_id": self.id,
                        "indent_id": indent.id,
                        "number":indent.indent_sequence,
                        "indent_type":indent.indent_type,
                        "employee_id": indent.employee_id.id,
                        "state": indent.state}] for indent in indents]
        return submit_grn
    
    def _get_pending_grn(self):
        pending_grn = []
        if self.employee_id.user_id.has_group('indent_stpi.group_grn_manager'):
            # categorys = self.env['product.category'].search([('user_id', 'in', self.employee_id.user_id.ids),
            #                                                          ('indent_category','=',True)])
            # if categorys:
            #     item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
            #                                              ('branch_id','=',self.branch_id.id)])
            # items = self.env['indent.request.items'].search([('item_category_id','in',item_stocks.ids)])
            # if items:
            indents = self.env['indent.request'].search([('state','=','to_approve'),
                                                               ('branch_id','=',self.branch_id.id),
                                                               ('indent_type' ,'=', 'grn')])
            pending_grn = [[0, 0, {
                    "exit_transfer_id": self.id,
                    "indent_id": indent.id,
                    "number":indent.indent_sequence,
                    "indent_type":indent.indent_type,
                    "employee_id": indent.employee_id.id,
                    "state": indent.state}] for indent in indents]
        return pending_grn
    
    def _get_upcoming_grn(self):
        pending_grn = []
        if self.employee_id.user_id.has_group('indent_stpi.group_grn_manager'):
            categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
                                                                     ('indent_category','=',True)])
            if categorys:
                item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
                                                         ('branch_id','=',self.branch_id.id)])
                items = self.env['indent.request.items'].search([('item_category_id','in',item_stocks.ids)])
                if items:
                    indents = items.mapped('request_id').filtered(lambda r: r.state == 'draft' and r.branch_id == self.branch_id and r.indent_type == 'grn')
                    pending_grn = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "indent_id": indent.id,
                            "number":indent.indent_sequence,
                            "indent_type":indent.indent_type,
                            "employee_id": indent.employee_id.id,
                            "state": indent.state}] for indent in indents]
        return pending_grn
    
    def _get_pending_grn_request(self):
        pending_grn_request = []
        if self.employee_id.user_id.has_group('indent_stpi.group_grn_manager'):
            # categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
            #                                                          ('indent_category','=',True)])
            # if categorys:
            #     item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
            #                                              ('branch_id','=',self.branch_id.id)])
            #     items = self.env['issue.request'].search([('item_category_id','in',item_stocks.ids)])
            #     if items:
            # indents = items.filtered(lambda r: r.state == 'to_approve_proceed' and r.branch_id == self.branch_id and r.indent_type == 'grn')
            indents = self.env['issue.request'].search([('state','=','to_approve'),
                                                               ('branch_id','=',self.branch_id.id),
                                                               ('indent_type' ,'=', 'grn')])
            pending_grn_request = [[0, 0, {
                    "exit_transfer_id": self.id,
                    "issue_id": indent.id,
                    "item_id":indent.item_id.id,
                    "employee_id": indent.employee_id.id,
                    "requested_quantity":indent.requested_quantity,
                    "approved_quantity":indent.approved_quantity,
                    "item_category_id":indent.item_category_id.id,
                    "indent_grn":indent.Indent_id.id,
                    "state": indent.state}] for indent in indents]
        elif self.employee_id.user_id.has_group('indent_stpi.group_grn_create'):
            indents = self.env['issue.request'].search([('state','=','to_approve_proceed'),
                                                               ('branch_id','=',self.branch_id.id),
                                                               ('indent_type' ,'=', 'grn')])
            pending_grn_request = [[0, 0, {
                    "exit_transfer_id": self.id,
                    "issue_id": indent.id,
                    "item_id":indent.item_id.id,
                    "employee_id": indent.employee_id.id,
                    "requested_quantity":indent.requested_quantity,
                    "approved_quantity":indent.approved_quantity,
                    "item_category_id":indent.item_category_id.id,
                    "indent_grn":indent.Indent_id.id,
                    "state": indent.state}] for indent in indents]
        return pending_grn_request
    
    def _get_submited_grn_request(self):
        submited_grn_request = []
        if self.employee_id.user_id.has_group('indent_stpi.group_grn_manager'):
            categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
                                                                     ('indent_category','=',True)])
            if categorys:
                item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
                                                         ('branch_id','=',self.branch_id.id)])
                items = self.env['issue.request'].search([('item_category_id','in',item_stocks.ids)])
                if items:
                    indents = items.filtered(lambda r: r.state == 'to_approve' and r.branch_id == self.branch_id and r.indent_type == 'grn')
                    submited_grn_request = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "issue_id": indent.id,
                            "item_id":indent.item_id.id,
                            "employee_id": indent.employee_id.id,
                            "requested_quantity":indent.requested_quantity,
                            "approved_quantity":indent.approved_quantity,
                            "item_category_id":indent.item_category_id.id,
                            "indent_grn":indent.Indent_id.id,
                            "state": indent.state}] for indent in indents]
        return submited_grn_request
    
    def _get_submitted_indent(self):
        submitted_indent = []
        indents = self.env['indent.request'].search([('employee_id','=',self.employee_id.id),
                                                 ('branch_id','=',self.branch_id.id),
                                                 ('state','=','approved'),
                                                 ('indent_type','=','issue')])
        if indents:
            submitted_indent = [[0, 0, {
                    "exit_transfer_id": self.id,
                    "indent_id": indent.id,
                    "number":indent.indent_sequence,
                    "indent_type":indent.indent_type,
                    "employee_id": indent.employee_id.id,
                    "state": indent.state}] for indent in indents]
        return submitted_indent
    
    def _get_pending_indent(self):
        pending_indent = []
        if self.employee_id.user_id.has_group('indent_stpi.group_indent_approver'):
            categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
                                                                     ('indent_category','=',True)])
            if categorys:
                item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
                                                         ('branch_id','=',self.branch_id.id)])
                request_id = self.env['indent.request'].search([('branch_id','=',self.branch_id.id),
                                                                ('indent_type','=','issue'),
                                                                ('state','=','draft')])
                items = self.env['indent.request.items'].search([('item_category_id','in',item_stocks.ids),
                                                                 ('request_id','in',request_id.ids)])
                if items:
                    indents = items.mapped('request_id')
                    pending_indent = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "indent_id": indent.id,
                            "number":indent.indent_sequence,
                            "indent_type":indent.indent_type,
                            "employee_id": indent.employee_id.id,
                            "state": indent.state}] for indent in indents]
        return pending_indent
        
    def _get_pending_issue(self):
        pending_issue = []
        if self.employee_id.user_id.has_group('indent_stpi.group_indent_approver'):
            categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
                                                                     ('indent_category','=',True)])
            if categorys:
                item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
                                                         ('branch_id','=',self.branch_id.id)])
                request_id = self.env['indent.request'].search([('branch_id','=',self.branch_id.id),
                                                                ('indent_type','=','issue'),
                                                                ('state','in',('to_approve','inprogress'))])
                items = self.env['issue.request'].search([('item_category_id','in',item_stocks.ids),
                                                                 ('Indent_id','in',request_id.ids),
                                                                 ('issue_state','=',False)])
                if items:
                    indents = items
                    pending_issue = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "issue_id": indent.id,
                            "item_id":indent.item_id.id,
                            "employee_id": indent.employee_id.id,
                            "requested_quantity":indent.requested_quantity,
                            "approved_quantity":indent.approved_quantity,
                            "item_category_id":indent.item_category_id.id,
                            "indent_grn":indent.Indent_id.id,
                            "state": indent.state}] for indent in indents]
        return pending_issue
    
    def _get_submited_issue(self):
        submited_issue = []
        if self.employee_id.user_id.has_group('indent_stpi.group_indent_approver'):
            categorys = self.env['product.category'].search([('user_id', '=', self.employee_id.user_id.id),
                                                                     ('indent_category','=',True)])
            if categorys:
                item_stocks = self.env['indent.stock'].search([('category_id','in',categorys.ids),
                                                         ('branch_id','=',self.branch_id.id)])
                items = self.env['issue.request'].search([('item_category_id','in',item_stocks.ids)])
                if items:
                    indents = items.filtered(lambda r: r.state == 'approved' and r.branch_id == self.branch_id and r.indent_type == 'issue')
                    submited_issue = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "issue_id": indent.id,
                            "item_id":indent.item_id.id,
                            "employee_id": indent.employee_id.id,
                            "requested_quantity":indent.requested_quantity,
                            "approved_quantity":indent.approved_quantity,
                            "item_category_id":indent.item_category_id.id,
                            "indent_grn":indent.Indent_id.id,
                            "state": indent.state}] for indent in indents]
        return submited_issue


    @api.multi
    def compute_exit_management(self):
        # Leave
        self.pending_leave_line_ids.unlink()
        self.leave_line_ids.unlink()
        # self.upcoming_leave_line_ids.unlink()
        
        # Reimbursement
        self.pending_reimbursement_ids.unlink()
        self.submitted_reimbursement_ids.unlink()
        # self.upcoming_reimbursement_ids.unlink()
        
        # Loan
        self.pending_loan_request_ids.unlink()
        self.submitted_loan_request_ids.unlink()
        self.not_transferrred_loan_request_ids.unlink()
        self.upcoming_loan_request_ids.unlink()
        
        # PF
        self.pending_pf_req_ids.unlink()
        self.submitted_pf_req_ids.unlink()
        self.upcoming_pf_req_ids.unlink()
        
        # Income Tax
        self.pending_income_tax_ids.unlink()
        self.submitted_income_tax_ids.unlink()
        # self.upcoming_income_tax_ids.unlink()

        #LTC
        self.pending_ltc_sequence_ids.unlink()
        self.submitted_ltc_sequence_ids.unlink()
        # self.upcoming_ltc_sequence_ids.unlink()
        self.pending_ltc_claim_ids.unlink()
        self.submitted_ltc_claim_ids.unlink()
        # self.upcoming_ltc_claim_ids.unlink()

        #Appraisal
        self.pending_appraisal_request_ids.unlink()
        self.submitted_appraisal_request_ids.unlink()
        # self.upcoming_appraisal_request_ids.unlink()

        #Tour
        self.pending_tour_req_ids.unlink()
        self.submitted_tour_req_ids.unlink()
        self.pending_tour_claim_req_ids.unlink()
        self.submitted_tour_claim_req_ids.unlink()

        #indent grn
        self.pending_grn_ids.unlink()
        self.submitted_grn_ids.unlink()
        self.pending_grn_req_ids.unlink()
        self.submitted_grn_req_ids.unlink()
        self.pending_indent_req_ids.unlink()
        self.submitted_indent_req_ids.unlink()
        self.pending_issue_req_ids.unlink()
        self.submitted_issue_req_ids.unlink()

        #eFile
        self.my_correspondence_ids.unlink()
        self.my_file_ids.unlink()

        #Cheque Birthday
        self.pending_check_birth_ids.unlink()
        self.submitted_check_birth_ids.unlink()
        



        # Leaves
        pending_leave_line_ids = []
        if self.employee_id.user_id.has_group('hr_holidays.group_hr_holidays_manager'):
            pending_leave_ids = self.env['hr.leave'].search([('employee_id.parent_id', '=', self.employee_id.id),
                                                                ("state", "in", ['confirm','validate1'])])
            pending_leave_line_ids = [[0, 0, {
                                        "exit_transfer_id": self.id,
                                        "employee_id": leave.employee_id.id,
                                        "leave_id": leave.id,
                                        "leave_type_id": leave.holiday_status_id.id,
                                        "from_date": leave.request_date_from,
                                        "to_date": leave.request_date_to,
                                        "state": leave.state}] for leave in pending_leave_ids]
            
        submitted_leaves_ids = self.env['hr.leave'].search([("employee_id","=", self.employee_id.id),
                                                                ("state", "in", ['draft','confirm','validate1'])])
        leave_line_ids = [[0, 0, {
                            "exit_transfer_id": self.id,
                            "leave_id": leave.id,
                            "leave_type_id": leave.holiday_status_id.id,
                            "from_date": leave.request_date_from,
                            "to_date": leave.request_date_to,
                            "state": leave.state}] for leave in submitted_leaves_ids]

        # upcoming_leave_line_ids = self.env['hr.leave'].search([("employee_id", "=", self.employee_id.id),
        #                                                         ("request_date_from", ">=", self.date),
        #                                                         ("state", "=", 'validate')])
        
        # upcoming_leave_line_ids = [[0, 0, {
        #                             "exit_transfer_id": self.id,
        #                             "leave_id": leave.id,
        #                             "leave_type_id": leave.holiday_status_id.id,
        #                             "from_date": leave.request_date_from,
        #                             "to_date": leave.request_date_to,
        #                             "state": leave.state}] for leave in upcoming_leave_line_ids]
        
        # Reimbursement
        pending_reimbursement_ids = []
        if self.employee_id.user_id.has_group('reimbursement_stpi.group_approving_authority'):
            pending_reimburse_ids = self.env['reimbursement'].sudo().search([('employee_id.branch_id', 'in', self.employee_id.user_id.branch_ids.ids),
                                                                                    ('state', 'in', ['waiting_for_approval', 'forwarded'])])
            pending_reimbursement_ids = [[0, 0, {
                                            "reiburs_id": reimburse.id,
                                            "employee_id": reimburse.employee_id.id,
                                            "reimbursement_type_id": reimburse.reimbursement_type_id.id,
                                            "claim_sub": reimburse.date_range.id,
                                            "claimed_amount":reimburse.claimed_amount,
                                            "net_amount": reimburse.approved_amount,
                                            "state": reimburse.state}] for reimburse in pending_reimburse_ids]
        submitted_reimburse_ids = self.env['reimbursement'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', 'in', ['waiting_for_approval', 'forwarded'])])
        submitted_reimbursement_ids = [[0, 0, {
                                        "reiburs_id": reimburse.id,
                                        "employee_id": reimburse.employee_id.id,
                                        "reimbursement_type_id": reimburse.reimbursement_type_id.id,
                                        "claim_sub": reimburse.date_range.id,
                                        "claimed_amount":reimburse.claimed_amount,
                                        "net_amount": reimburse.approved_amount,
                                        "state": reimburse.state}] for reimburse in submitted_reimburse_ids]
        # upcoming_reimburse_ids = self.env['reimbursement'].sudo().search([('employee_id', '=', self.employee_id.id),
        #                                                                         ('create_date', '>=', datetime.now()),
        #                                                                         ('state', '=', 'approved')])
        # upcoming_reimbursement_ids = [[0, 0, {
        #                                 "reiburs_id": reimburse.id,
        #                                 "employee_id": reimburse.employee_id.id,
        #                                 "reimbursement_type_id": reimburse.reimbursement_type_id.id,
        #                                 "claim_sub": reimburse.date_range.id,
        #                                 "claimed_amount":reimburse.claimed_amount,
        #                                 "net_amount": reimburse.approved_amount,
        #                                 "state": reimburse.state}] for reimburse in upcoming_reimburse_ids]

        # Loan
        pending_loan_request_ids = []
        if self.employee_id.user_id.has_group('ohrms_loan.group_loan_approver'):
            pending_loan_req_ids = self.env['hr.loan'].sudo().search([('employee_id.branch_id', 'in', self.employee_id.user_id.branch_ids.ids),
                                                                        ('state', 'in', ['waiting_approval_1', 'waiting_approval_2'])])
            pending_loan_request_ids = [[0, 0, {
                                            "loan_id": loan.id,
                                            "type_id": loan.type_id.id,
                                            "employee_id": loan.employee_id.id,
                                            "installment": loan.installment,
                                            "total_amount": loan.total_amount,
                                            "total_interest": loan.total_interest,
                                            "total_paid_amount": loan.total_paid_amount,
                                            "balance_amount": loan.balance_amount,
                                            "state": loan.state}] for loan in pending_loan_req_ids]
        submitted_loan_req_ids = self.env['hr.loan'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                    ('state', 'in', ['waiting_approval_1', 'waiting_approval_2'])])
        submitted_loan_request_ids = [[0, 0, {
                                        "loan_id": loan.id,
                                        "type_id": loan.type_id.id,
                                        "employee_id": loan.employee_id.id,
                                        "installment": loan.installment,
                                        "total_amount": loan.total_amount,
                                        "total_interest": loan.total_interest,
                                        "total_paid_amount": loan.total_paid_amount,
                                        "balance_amount": loan.balance_amount,
                                        "state": loan.state}] for loan in submitted_loan_req_ids]
        upcoming_loan_request_ids, not_transferrred_loan_request_ids = [], []
        if self.exit_type == 'Transferred':
            upcoming_loan_request_ids = self.env['hr.loan'].search([("employee_id", "=", self.employee_id.id),
                                                                    ("state", "=", 'approve')])
            lis_loan_id = self.upcoming_loan_request_ids.mapped('loan_id.id')
            filtered_upcoming_loan_request_ids = upcoming_loan_request_ids.filtered(lambda x: x.id not in lis_loan_id)
            upcoming_loan_request_ids = [[0, 0, {
                                        "loan_id": loan.id,
                                        "no_of_emi_paid": len(loan.loan_lines.filtered(lambda x: x.paid)),
                                        "no_of_emi_pending": len(loan.loan_lines.filtered(lambda x: not x.paid))}] for loan in filtered_upcoming_loan_request_ids]
        else:
            not_transferred_loan_req_ids = self.env['hr.loan'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                            ('state', '=', 'approve')])
            not_transferrred_loan_request_ids = [[0, 0, {
                                        "loan_id": loan.id,
                                        "no_of_emi_paid": len(loan.loan_lines.filtered(lambda x: x.paid)),
                                        "no_of_emi_pending": len(loan.loan_lines.filtered(lambda x: not x.paid))}] for loan in not_transferred_loan_req_ids]

        # PF Withdrawl
        pending_pf_req_ids = []
        if self.employee_id.user_id.has_group('pf_withdrawl.group_pf_withdraw_approver'):
            pending_pf_ids = self.env['pf.widthdrawl'].sudo().search([('employee_id.branch_id', 'in', self.employee_id.user_id.branch_ids.ids),
                                                                        ('state', '=', 'to_approve')])
            pending_pf_req_ids = [[0, 0, {
                                    "pf_id": pf.id,
                                    "employee_id": pf.employee_id.id,
                                    "advance_amount": pf.advance_amount,
                                    "purpose": pf.purpose,
                                    "state": pf.state}] for pf in pending_pf_ids]
        submitted_pf_ids = self.env['pf.widthdrawl'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'to_approve')])
        submitted_pf_req_ids = [[0, 0, {
                                    "pf_id": pf.id,
                                    "employee_id": pf.employee_id.id,
                                    "advance_amount": pf.advance_amount,
                                    "purpose": pf.purpose,
                                    "state": pf.state}] for pf in submitted_pf_ids]
        upcoming_pf_ids = self.env['pf.widthdrawl'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                    ('state', '=', 'approved'), ('date', '>=', self.date)])
        upcoming_pf_req_ids = [[0, 0, {
                                    "pf_id": pf.id,
                                    "employee_id": pf.employee_id.id,
                                    "advance_amount": pf.advance_amount,
                                    "purpose": pf.purpose,
                                    "state": pf.state}] for pf in upcoming_pf_ids]        


        # Income Tax
        pending_income_tax_ids = []
        if self.employee_id.user_id.has_group('tds.group_manager_hr_declaration'):
            pending_tax_ids = self.env['hr.declaration'].sudo().search([('employee_id.branch_id', 'in', self.employee_id.user_id.branch_ids.ids),
                                                                                ('state', '=', 'to_approve')])
            pending_income_tax_ids = [[0, 0, {
                                        "running_fy_id": income_tax.id,
                                        "date_range_id": income_tax.date_range.id,
                                        "employee_id": income_tax.employee_id.id,
                                        "total_gross": income_tax.tax_salary_final,
                                        "taxable_income": income_tax.taxable_income,
                                        "tax_payable": income_tax.tax_payable,
                                        "tax_paid": income_tax.tax_paid,
                                        "total_rem": income_tax.pending_tax,
                                        "state": income_tax.state}] for income_tax in pending_tax_ids]
        submitted_tax_ids = self.env['hr.declaration'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'to_approve')])
        submitted_income_tax_ids = [[0, 0, {
                                        "running_fy_id": income_tax.id,
                                        "date_range_id": income_tax.date_range.id,
                                        "employee_id": income_tax.employee_id.id,
                                        "total_gross": income_tax.tax_salary_final,
                                        "taxable_income": income_tax.taxable_income,
                                        "tax_payable": income_tax.tax_payable,
                                        "tax_paid": income_tax.tax_paid,
                                        "total_rem": income_tax.pending_tax,
                                        "state": income_tax.state}] for income_tax in submitted_tax_ids]
        # upcoming_tax_ids = self.env['hr.declaration'].sudo().search([('employee_id', '=', self.employee_id.id),
        #                                                             ('date', '>=', self.date), ('state', '=', 'approved')])

        # upcoming_income_tax_ids = [[0, 0, {
        #                                 "running_fy_id": income_tax.id,
        #                                 "date_range_id": income_tax.date_range.id,
        #                                 "employee_id": income_tax.employee_id.id,
        #                                 "total_gross": income_tax.tax_salary_final,
        #                                 "taxable_income": income_tax.taxable_income,
        #                                 "tax_payable": income_tax.tax_payable,
        #                                 "tax_paid": income_tax.tax_paid,
        #                                 "total_rem": income_tax.pending_tax,
        #                                 "state": income_tax.state}] for income_tax in upcoming_tax_ids]

        #LTC
        pending_ltc_sequence_ids,pending_ltc_claim_ids = [],[]
        if self.employee_id.user_id.has_group('employee_ltc.group_ltc_manager'):
            pending_ltc_advance_ids = self.env['employee.ltc.advance'].sudo().search([('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),('state','=','to_approve')])
            pending_claim_ids = self.env["employee.ltc.claim"].search([('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),("state", "in", ['to_approve'])])
            pending_ltc_sequence_ids = [[0, 0, {
                                        'ltc_sequence_id': ltc.id,
                                        'employee_id': ltc.employee_id.id,
                                        'place_of_trvel': ltc.place_of_trvel,
                                        'block_year_id': ltc.block_year.id,
                                        'state': ltc.state}] for ltc in pending_ltc_advance_ids]

            pending_ltc_claim_ids = [[0, 0, {
                                    "ltc_availed_for_id": res.id,
                                    "employee_id": res.employee_id.id,
                                    "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
                                    "place_of_trvel": res.place_of_trvel,
                                    "total_claimed_amount": res.total_claimed_amount,
                                    "balance_left": res.balance_left,
                                    "state": res.state
                                    }] for res in pending_claim_ids] 
            
        submitted_ltc_advance_ids = self.env['employee.ltc.advance'].search([("employee_id", "=", self.employee_id.id),("state", "in", ['draft', 'to_approve'])])
        submitted_ltc_sequence_ids = [[0, 0, {
                                        'ltc_sequence_id': ltc.id,
                                        'employee_id': ltc.employee_id.id,
                                        'place_of_trvel': ltc.place_of_trvel,
                                        'block_year_id': ltc.block_year.id,
                                        'state': ltc.state}] for ltc in submitted_ltc_advance_ids]

        # upcoming_ltc_advance_ids = self.env['employee.ltc.advance'].search([("employee_id", "=", self.employee_id.id),("depart_date", ">=", self.date),("state", "in", ['approved'])])
        # upcoming_ltc_sequence_ids = [[0, 0, {
        #                                 'ltc_sequence_id': ltc.id,
        #                                 'employee_id': ltc.employee_id.id,
        #                                 'place_of_trvel': ltc.place_of_trvel,
        #                                 'block_year_id': ltc.block_year.id,
        #                                 'state': ltc.state}] for ltc in upcoming_ltc_advance_ids]
        
        submitted_claim_ids = self.env['employee.ltc.claim'].search([("employee_id", "=", self.employee_id.id),("state", "in", ['draft', 'to_approve'])])
        submitted_ltc_claim_ids = [[0, 0, {
                                    "ltc_availed_for_id": res.id,
                                    "employee_id": res.employee_id.id,
                                    "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
                                    "place_of_trvel": res.place_of_trvel,
                                    "total_claimed_amount": res.total_claimed_amount,
                                    "balance_left": res.balance_left,
                                    "state": res.state
                                    }] for res in submitted_claim_ids] 

        # upcoming_claim_ids = self.env['employee.ltc.claim'].search([("employee_id", "=", self.employee_id.id),("create_date", ">=", datetime.now()),("state", "in", ['approved'])])
        # upcoming_ltc_claim_ids = [[0, 0, {
        #                             "ltc_availed_for_id": res.id,
        #                             "employee_id": res.employee_id.id,
        #                             "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
        #                             "place_of_trvel": res.place_of_trvel,
        #                             "total_claimed_amount": res.total_claimed_amount,
        #                             "balance_left": res.balance_left,
        #                             "state": res.state
        #                             }] for res in upcoming_claim_ids] 

        #Appraisal
        pending_appraisal_request_ids = []
        if self.employee_id.user_id.has_group('appraisal_stpi.group_manager_appraisal'):
            pending_manager_appraisal_ids = self.env['appraisal.main'].search([('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),("state", "=", 'reviewing_authority_review')])
            pending_appraisal_request_ids += [[0, 0, {
                                            "employee_id": res.employee_id.id,
                                            'appraisal_id': res.id,
                                            "abap_id": res.abap_period.id,
                                            "template_id": res.template_id.id,
                                            "state": res.state
                                            }] for res in pending_manager_appraisal_ids]

        if self.employee_id.user_id.has_group('appraisal_stpi.group_reporting_authority_appraisal'):
            print("reporting_authoritu")
            pending_reporting_appraisal_ids = self.env['appraisal.main'].search([('employee_id.appraisal_reporting_officer', '=', self.employee_id.id),("state", "=", 'self_review')])
            print(pending_reporting_appraisal_ids)
            pending_appraisal_request_ids += [[0, 0, {
                                            "employee_id": res.employee_id.id,
                                            'appraisal_id': res.id,
                                            "abap_id": res.abap_period.id,
                                            "template_id": res.template_id.id,
                                            "state": res.state
                                            }] for res in pending_reporting_appraisal_ids]
        
        if self.employee_id.user_id.has_group('appraisal_stpi.group_reviewing_authority_appraisal'):
            pending_reviewing_appraisal_ids = self.env['appraisal.main'].search([('employee_id.appraisal_reviewing_officer', '=', self.employee_id.id),("state", "=", 'reporting_authority_review')])
            pending_appraisal_request_ids += [[0, 0, {
                                            "employee_id": res.employee_id.id,
                                            'appraisal_id': res.id,
                                            "abap_id": res.abap_period.id,
                                            "template_id": res.template_id.id,
                                            "state": res.state
                                            }] for res in pending_reviewing_appraisal_ids]

        submitted_appraisal_ids = self.env['appraisal.main'].search([("employee_id", "=", self.employee_id.id),("state", "in", ['draft', 'self_review'])])
        submitted_appraisal_request_ids = [[0, 0, {
                                            "employee_id": res.employee_id.id,
                                            'appraisal_id': res.id,
                                            "abap_id": res.abap_period.id,
                                            "template_id": res.template_id.id,
                                            "state": res.state
                                            }] for res in submitted_appraisal_ids]

        # upcoming_appraisal_ids = self.env['appraisal.main'].search([("employee_id", "=", self.employee_id.id),("create_date", ">=", datetime.now()),("state", "in", ['reporting_authority_review'])])
        # upcoming_appraisal_request_ids = [[0, 0, {
        #                                     "employee_id": res.employee_id.id,
        #                                     "abap_id": res.abap_id,
        #                                     "template_id": res.template_id,
        #                                     "state": res.state
        #                                     }] for res in upcoming_appraisal_ids]

        #Tour
        pending_tour_req_ids = []
        if self.employee_id.user_id.has_group('tour_request.group_tour_request_approvere'):
            pending_tour_ids = self.env['tour.request'].search([('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),("state", "in", ['waiting_for_approval'])])
            pending_tour_req_ids = [[0, 0, {
                                            "tour_request_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "purpose": res.purpose,
                                            "request_date": res.date,
                                            "state": res.state
                                            }] for res in pending_tour_ids]
        
        submitted_tour_ids = self.env['tour.request'].search([("employee_id", "=", self.employee_id.id),("state", "in", ['draft', 'waiting_for_approval'])])
        submitted_tour_req_ids = [[0, 0, {
                                            "tour_request_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "purpose": res.purpose,
                                            "request_date": res.date,
                                            "state": res.state
                                            }] for res in submitted_tour_ids]
        
        pending_tour_claim_req_ids = []
        if self.employee_id.user_id.has_group('tour_request.group_tour_claim_approvere'):
            pending_tour_claim_ids = self.env['employee.tour.claim'].search(
                            [('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),
                             ("state", "in", ['submitted'])])
            pending_tour_claim_req_ids = [[0, 0, {
                                            "tour_claim_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "total_claimed_amount": res.total_claimed_amount,
                                            "balance_left": res.balance_left,
                                            "state": res.state
                                            }] for res in pending_tour_claim_ids]
        
        submitted_tour_claim_ids = self.env['employee.tour.claim'].search([("employee_id", "=", self.employee_id.id),("state", "in",['draft', 'submitted'])])
        submitted_tour_claim_req_ids = [[0, 0, {
                                            "tour_claim_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "total_claimed_amount": res.total_claimed_amount,
                                            "balance_left": res.balance_left,
                                            "state": res.state
                                            }] for res in submitted_tour_claim_ids]
        
        #Cheque Request
        pending_check_birth_ids = []
        if self.employee_id.user_id.has_group('birthday_check.group_approvar_birthday'):
            pending_birthday_approver_ids = self.env['cheque.requests'].search([('employee_id.branch_id','in',self.employee_id.user_id.branch_ids.ids),("state", "in", ['to_approve'])])
            pending_check_birth_ids = [[0, 0, {
                                            "check_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "name": res.name,
                                            "birthday": res.birthday,
                                            "state": res.state
                                            }] for res in pending_birthday_approver_ids]
        
        submitted_checkbirth_ids = self.env['cheque.requests'].search([("employee_id", "=", self.employee_id.id),("state", "in", ['draft', 'to_approve'])])
        submitted_check_birth_ids = [[0, 0, {
                                            "check_id": res.id,
                                            "employee_id": res.employee_id.id,
                                            "name": res.name,
                                            "birthday": res.birthday,
                                            "state": res.state
                                            }] for res in submitted_checkbirth_ids]

        #eFile
        correspondence_ids = self.env['muk_dms.file'].search([("current_owner_id", "=", self.employee_id.user_id.id), ("folder_id", "=", False)])

        my_correspondence_ids = [[0, 0, {
                                            "correspondence_id": res.id,
                                            "letter_no": res.letter_number,
                                            "file_assign_id": res.folder_id.id,
                                            }] for res in correspondence_ids]

        file_ids = self.env['folder.master'].search([("current_owner_id", "=", self.employee_id.user_id.id)])
        my_file_ids = [[0, 0, {
                                "file_id": res.id,
                                "file_name": res.folder_name,
                                "number": res.number,
                                "state": res.state
                                }] for res in file_ids]

        ##### pending GRN/GRN REQUEST/INDENT/INDENT REQUEST/ISSUE/ #####
        pending_grn_ids = self._get_pending_grn()
        submitted_grn_ids = self._get_submitted_grn()
        self._get_upcoming_grn()
        pending_grn_req_ids = self._get_pending_grn_request()
        submitted_grn_req_ids = self._get_submited_grn_request()
        pending_indent_req_ids = self._get_pending_indent()
        submitted_indent_req_ids = self._get_submitted_indent()
        pending_issue_req_ids = self._get_pending_issue()
        submitted_issue_req_ids = self._get_submited_issue()
        
        ##### End block ########

        self.sudo().write({'pending_leave_line_ids': pending_leave_line_ids,
                    'leave_line_ids': leave_line_ids,
                    # 'upcoming_leave_line_ids': upcoming_leave_line_ids,
                    'pending_reimbursement_ids': pending_reimbursement_ids,
                    'submitted_reimbursement_ids': submitted_reimbursement_ids,
                    #'upcoming_reimbursement_ids': upcoming_reimbursement_ids,
                    'pending_loan_request_ids': pending_loan_request_ids,
                    'submitted_loan_request_ids': submitted_loan_request_ids,
                    'not_transferrred_loan_request_ids': not_transferrred_loan_request_ids,
                    'upcoming_loan_request_ids': upcoming_loan_request_ids,
                    'pending_pf_req_ids': pending_pf_req_ids,
                    'submitted_pf_req_ids': submitted_pf_req_ids,
                    'upcoming_pf_req_ids': upcoming_pf_req_ids,
                    'pending_income_tax_ids': pending_income_tax_ids,
                    'submitted_income_tax_ids': submitted_income_tax_ids,
                    #'upcoming_income_tax_ids': upcoming_income_tax_ids
                    'pending_ltc_sequence_ids': pending_ltc_sequence_ids,
                    'submitted_ltc_sequence_ids': submitted_ltc_sequence_ids,
                    # 'upcoming_ltc_sequence_ids': upcoming_ltc_sequence_ids,
                    'pending_ltc_claim_ids': pending_ltc_claim_ids,
                    'submitted_ltc_claim_ids': submitted_ltc_claim_ids,
                    # 'upcoming_ltc_claim_ids': upcoming_ltc_claim_ids,
                    'pending_appraisal_request_ids': pending_appraisal_request_ids,
                    'submitted_appraisal_request_ids': submitted_appraisal_request_ids,
                    # 'upcoming_appraisal_request_ids': upcoming_appraisal_request_ids,
                    'pending_grn_ids':pending_grn_ids,
                    'submitted_grn_ids':submitted_grn_ids,
                    'pending_grn_req_ids':pending_grn_req_ids,
                    'submitted_grn_req_ids':submitted_grn_req_ids,
                    'pending_indent_req_ids':pending_indent_req_ids,
                    'submitted_indent_req_ids':submitted_indent_req_ids,
                    'pending_issue_req_ids':pending_issue_req_ids,
                    'submitted_issue_req_ids':submitted_issue_req_ids,
                    
                    'pending_tour_req_ids': pending_tour_req_ids,
                    'submitted_tour_req_ids': submitted_tour_req_ids,
                    'pending_tour_claim_req_ids': pending_tour_claim_req_ids,
                    'submitted_tour_claim_req_ids': submitted_tour_claim_req_ids,
                    'pending_check_birth_ids': pending_check_birth_ids,
                    'submitted_check_birth_ids': submitted_check_birth_ids,
                    'my_correspondence_ids': my_correspondence_ids,
                    'my_file_ids': my_file_ids,
                    })

    @api.multi
    def mail_list(self):
        finance_group = self.env.ref('exit_transfer_management.group_exit_finance_department').id
        technical_group = self.env.ref('exit_transfer_management.group_exit_technical_department').id
        personal_group = self.env.ref('exit_transfer_management.group_exit_personal_department').id
        general_group = self.env.ref('exit_transfer_management.group_exit_general_department').id
        employee_manager_group = self.env.ref('hr.group_hr_manager').id
        
        finance_group_users = self.env['res.groups'].sudo().browse(finance_group).users\
                                .filtered(lambda x: self.branch_id in x.branch_ids)
        technical_group_users = self.env['res.groups'].sudo().browse(technical_group).users\
                                .filtered(lambda x: self.branch_id in x.branch_ids)
        personal_group_users = self.env['res.groups'].sudo().browse(personal_group).users\
                                .filtered(lambda x: self.branch_id in x.branch_ids)
        general_group_users = self.env['res.groups'].sudo().browse(general_group).users\
                                .filtered(lambda x: self.branch_id in x.branch_ids)
        employee_manager_group_users = self.env['res.groups'].sudo().browse(employee_manager_group).users\
                                .filtered(lambda x: self.to_branch_id in x.branch_ids)

        finance_users_mail = self.env['hr.employee'].sudo().search([('user_id', 'in', finance_group_users.mapped('id'))])\
                                                            .mapped('work_email')
        technical_users_mail = self.env['hr.employee'].sudo().search([('user_id', 'in', technical_group_users.mapped('id'))])\
                                                            .mapped('work_email')
        personal_users_mail = self.env['hr.employee'].sudo().search([('user_id', 'in', personal_group_users.mapped('id'))])\
                                                            .mapped('work_email')
        general_users_mail = self.env['hr.employee'].sudo().search([('user_id', 'in', general_group_users.mapped('id'))])\
                                                            .mapped('work_email')
        employee_manager_mail = self.env['hr.employee'].sudo().search([('user_id', 'in', employee_manager_group_users.mapped('id'))])\
                                                            .mapped('work_email')
        return {'finance_group_users': finance_group_users.mapped('id'), 'finance_users_mail': finance_users_mail,
                'technical_group_users': technical_group_users.mapped('id'), 'technical_users_mail': technical_users_mail,
                'personal_group_users': personal_group_users.mapped('id'), 'personal_users_mail': personal_users_mail,
                'general_group_users': general_group_users.mapped('id'), 'general_users_mail': general_users_mail,
                'employee_manager_group_users':employee_manager_group_users.mapped('id'),'employee_manager_mail':employee_manager_mail}

    @api.multi
    def button_verify(self):
        if self.exit_type == 'technical resignation' and self.reg_type == 'internal':
            self.sudo().write({'state': 'send_for_approval','finance_approved':True,'general_approved':True,'personal_approved':True,'technical_approved': True,'ro_approved':True})
           
        else:
            self.compute_exit_management()
            user_id = self.employee_id.user_id.id
            template = self.env.ref('exit_transfer_management.email_template_notify_user', 
                                        raise_if_not_found=False)
            mail = self.env['mail.template'].sudo().browse(template.id)
            create_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)])
            mail_lis = self.mail_list()
            if mail:
                # Mail for Employee
                ctx = {'email_from': create_employee_id.work_email,
                        'email_to': self.employee_id.work_email,
                        'subject': f'{self.employee_id.name} | {self.name}',
                        'employee_name': self.employee_id.name,
                        'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',self.employee_id.work_email)],limit=1).name}
                mail.with_context(ctx).send_mail(self.id, force_send=False, raise_exception=False)
                # Mail for Finance
                for i, user_mail in enumerate(mail_lis.get('finance_users_mail')):
                    ctx = {'email_from': create_employee_id.work_email,
                            'email_to': user_mail,
                            'subject': f'{self.employee_id.name} | {self.name}',
                            'employee_name': self.employee_id.name,
                            'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name}
                    mail.with_context(ctx).send_mail(self.id, force_send=False, 
                                                        raise_exception=False)
                # Mail for Technical
                for i, user_mail in enumerate(mail_lis.get('technical_users_mail')):
                    ctx = {'email_from': create_employee_id.work_email,
                            'email_to': user_mail,
                            'subject': f'{self.employee_id.name} | {self.name}',
                            'employee_name': self.employee_id.name,
                            'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name}
                    mail.with_context(ctx).send_mail(self.id, force_send=False, 
                                                        raise_exception=False)
                # Mail for Personal
                for i, user_mail in enumerate(mail_lis.get('personal_users_mail')):
                    ctx = {'email_from': create_employee_id.work_email,
                            'email_to': user_mail,
                            'subject': f'{self.employee_id.name} | {self.name}',
                            'employee_name': self.employee_id.name,
                            'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name}
                    mail.with_context(ctx).send_mail(self.id, force_send=False,
                                                        raise_exception=False)
                # Mail for General
                for i, user_mail in enumerate(mail_lis.get('general_users_mail')):
                    ctx = {'email_from': create_employee_id.work_email,
                            'email_to': user_mail,
                            'subject': f'{self.employee_id.name} | {self.name}',
                            'employee_name': self.employee_id.name,
                            'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name}
                    mail.with_context(ctx).send_mail(self.id, force_send=False,
                                                        raise_exception=False)
            # if user_id:
            #     self.activity_schedule(summary='Exit Transfer Management', activity_type_id=1,
            #                             date_deadline=date.today(),user_id=user_id)
            self.sudo().write({'state': 'verify'})
        return True

    @api.multi
    def get_current_status(self):
        self.compute_exit_management()
        return True

    # def button_verify(self):
    #     if self.pending_leave_line_ids:
    #         for line in self.pending_leave_line_ids:
    #             line.unlink()

    #     if self.leave_line_ids:
    #         for line in self.leave_line_ids:
    #             line.unlink()

    #     if self.upcoming_leave_line_ids:
    #         for line in self.upcoming_leave_line_ids:
    #             line.unlink()

    #     group_id = self.env.ref('hr_holidays.group_hr_holidays_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search([("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_leaves_ids = self.env['hr.leave'].search([("employee_id","in",HrEmployees.ids),
    #                                               ("state","in",['confirm','validate1'])])
    #                     if pending_leaves_ids:
    #                         for res in pending_leaves_ids:
    #                             self.pending_leave_line_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "leave_id": res.id,
    #                                 "leave_type_id": res.holiday_status_id.id,
    #                                 "from_date": res.request_date_from,
    #                                 "to_date": res.request_date_to,
    #                                 "state": res.state
    #                             })


    #     submitted_leaves_ids = self.env['hr.leave'].search([("employee_id","=",self.employee_id.id),
    #                                               ("state","in",['draft','confirm','validate1'])])

    #     upcoming_leave_line_ids = self.env['hr.leave'].search([("employee_id","=",self.employee_id.id),
    #                                               ("request_date_from",">=",self.date),
    #                                               ("state","in",['validate'])])

    #     if submitted_leaves_ids:
    #         for res in submitted_leaves_ids:
    #             self.leave_line_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "leave_id": res.id,
    #                 "leave_type_id": res.holiday_status_id.id,
    #                 "from_date": res.request_date_from,
    #                 "to_date": res.request_date_to,
    #                 "state": res.state
    #             })

    #     if upcoming_leave_line_ids:
    #         for res in upcoming_leave_line_ids:
    #             self.upcoming_leave_line_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "leave_id": res.id,
    #                 "leave_type_id": res.holiday_status_id.id,
    #                 "from_date": res.request_date_from,
    #                 "to_date": res.request_date_to,
    #                 "state": res.state
    #             })

    #     #tour and travel
    #     if self.pending_tour_req_ids:
    #         for line in self.pending_tour_req_ids:
    #             line.unlink()

    #     if self.submitted_tour_req_ids:
    #         for line in self.submitted_tour_req_ids:
    #             line.unlink()

    #     if self.upcoming_tour_req_ids:
    #         for line in self.upcoming_tour_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('tour_request.group_tour_request_approvere')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_tour_req_ids = self.env['tour.request'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                       ("state", "in", ['waiting_for_approval'])])
    #                     if pending_tour_req_ids:
    #                         for res in pending_tour_req_ids:
    #                             self.pending_tour_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "tour_request_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "purpose": res.purpose,
    #                                 "request_date": res.date,
    #                                 "state": res.state
    #                             })

    #     submitted_tour_req_ids = self.env['tour.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                       ("state", "in", ['draft', 'waiting_for_approval'])])
    #     if submitted_tour_req_ids:
    #         for res in submitted_tour_req_ids:
    #             self.submitted_tour_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "tour_request_id": res.id,
    #                 "purpose": res.purpose,
    #                 "request_date": res.date,
    #                 "state": res.state
    #             })

    #     upcoming_tour_req_ids = self.env['tour.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                       ("date",">=",self.date),("state", "in", ['approved'])])
    #     if upcoming_tour_req_ids:
    #         for res in upcoming_tour_req_ids:
    #             self.upcoming_tour_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "tour_request_id": res.id,
    #                 "purpose": res.purpose,
    #                 "request_date": res.date,
    #                 "state": res.state
    #             })

    #     # tour claim
    #     if self.pending_tour_claim_req_ids:
    #         for line in self.pending_tour_claim_req_ids:
    #             line.unlink()

    #     if self.submitted_tour_claim_req_ids:
    #         for line in self.submitted_tour_claim_req_ids:
    #             line.unlink()

    #     if self.upcoming_tour_claim_req_ids:
    #         for line in self.upcoming_tour_claim_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('tour_request.group_tour_claim_approvere')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_tour_claim_req_ids = self.env['employee.tour.claim'].search(
    #                         [("employee_id", "in", HrEmployees.ids),
    #                          ("state", "in", ['waiting_for_approval'])])
    #                     if pending_tour_claim_req_ids:
    #                         for res in pending_tour_claim_req_ids:
    #                             self.pending_tour_claim_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "tour_claim_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "total_claimed_amount": res.total_claimed_amount,
    #                                 "balance_left": res.balance_left,
    #                                 "state": res.state
    #                             })

    #     submitted_tour_claim_req_ids = self.env['employee.tour.claim'].search([("employee_id", "=", self.employee_id.id),
    #                                                                            ("state", "in",['draft', 'waiting_for_approval'])])
    #     if submitted_tour_claim_req_ids:
    #         for res in submitted_tour_claim_req_ids:
    #             self.submitted_tour_claim_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "tour_claim_id": res.id,
    #                 "total_claimed_amount": res.total_claimed_amount,
    #                 "balance_left": res.balance_left,
    #                 "state": res.state
    #             })

    #     upcoming_tour_claim_req_ids = self.env['employee.tour.claim'].search([("employee_id", "=", self.employee_id.id),
    #                                                                           ("create_date", ">=", datetime.now()),
    #                                                                           ("state", "in", ['approved'])])
    #     if upcoming_tour_claim_req_ids:
    #         for res in upcoming_tour_claim_req_ids:
    #             self.upcoming_tour_claim_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "tour_claim_id": res.id,
    #                 "total_claimed_amount": res.total_claimed_amount,
    #                 "balance_left": res.balance_left,
    #                 "state": res.state
    #             })

    #     # LTC Advance
    #     if self.pending_ltc_sequence_ids:
    #         for line in self.pending_ltc_sequence_ids:
    #             line.unlink()

    #     if self.submitted_ltc_sequence_ids:
    #         for line in self.submitted_ltc_sequence_ids:
    #             line.unlink()

    #     if self.upcoming_ltc_sequence_ids:
    #         for line in self.upcoming_ltc_sequence_ids:
    #             line.unlink()


    #     group_id = self.env.ref('employee_ltc.group_ltc_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_ltc_sequence_ids = self.env['employee.ltc.advance'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                         ("state", "in", ['to_approve'])])
    #                     if pending_ltc_sequence_ids:
    #                         for res in pending_ltc_sequence_ids:
    #                             self.pending_ltc_sequence_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "ltc_sequence_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "place_of_trvel": res.place_of_trvel,
    #                                 "block_year_id": res.block_year.id,
    #                                 "state": res.state
    #                             })

    #     submitted_ltc_sequence_ids = self.env['employee.ltc.advance'].search([("employee_id", "=", self.employee_id.id),
    #                                                                       ("state", "in", ['draft', 'to_approve'])])

    #     if submitted_ltc_sequence_ids:
    #         for res in submitted_ltc_sequence_ids:
    #             self.submitted_ltc_sequence_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "ltc_sequence_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "place_of_trvel": res.place_of_trvel,
    #                 "block_year_id": res.block_year.id,
    #                 "state": res.state
    #             })

    #     upcoming_ltc_sequence_ids = self.env['employee.ltc.advance'].search([("employee_id", "=", self.employee_id.id),
    #                                                                          ("depart_date", ">=", self.date),
    #                                                                          ("state", "in", ['approved'])])
    #     if upcoming_ltc_sequence_ids:
    #         for res in upcoming_ltc_sequence_ids:
    #             self.upcoming_ltc_sequence_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "ltc_sequence_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "place_of_trvel": res.place_of_trvel,
    #                 "block_year_id": res.block_year.id,
    #                 "state": res.state
    #             })


    #     # LTC Claim
    #     if self.pending_ltc_claim_ids:
    #         for line in self.pending_ltc_claim_ids:
    #             line.unlink()

    #     if self.submitted_ltc_claim_ids:
    #         for line in self.submitted_ltc_claim_ids:
    #             line.unlink()

    #     if self.upcoming_ltc_claim_ids:
    #         for line in self.upcoming_ltc_claim_ids:
    #             line.unlink()

    #     group_id = self.env.ref('employee_ltc.group_ltc_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_ltc_claim_ids = self.env["employee.ltc.claim"].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                    ("state", "in", ['to_approve'])])
    #                     if pending_ltc_claim_ids:
    #                         for res in pending_ltc_claim_ids:
    #                             self.pending_ltc_claim_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "ltc_availed_for_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
    #                                 "place_of_trvel": res.place_of_trvel,
    #                                 "total_claimed_amount": res.total_claimed_amount,
    #                                 "balance_left": res.balance_left,
    #                                 "state": res.state
    #                             })

    #     submitted_ltc_claim_ids = self.env['employee.ltc.claim'].search([("employee_id", "=", self.employee_id.id),
    #                                                                      ("state", "in", ['draft', 'to_approve'])])

    #     if submitted_ltc_claim_ids:
    #         for res in submitted_ltc_claim_ids:
    #             self.submitted_ltc_claim_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "ltc_availed_for_id": res.id,
    #                 "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
    #                 "employee_id": res.employee_id.id,
    #                 "place_of_trvel": res.place_of_trvel,
    #                 "total_claimed_amount": res.total_claimed_amount,
    #                 "balance_left": res.balance_left,
    #                 "state": res.state
    #             })

    #     upcoming_ltc_claim_ids = self.env['employee.ltc.claim'].search([("employee_id", "=", self.employee_id.id),
    #                                                                     ("create_date", ">=", datetime.now()),
    #                                                                     ("state", "in", ['approved'])])
    #     if upcoming_ltc_claim_ids:
    #         for res in upcoming_ltc_claim_ids:
    #             self.upcoming_ltc_claim_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "ltc_availed_for_id": res.id,
    #                 "ltc_availed_for_m2o": res.ltc_availed_for_m2o.id,
    #                 "employee_id": res.employee_id.id,
    #                 "place_of_trvel": res.place_of_trvel,
    #                 "total_claimed_amount": res.total_claimed_amount,
    #                 "balance_left": res.balance_left,
    #                 "state": res.state
    #             })

    #     # Vehicle Request
    #     if self.pending_vehicle_req_ids:
    #         for line in self.pending_vehicle_req_ids:
    #             line.unlink()

    #     if self.submitted_vehicle_req_ids:
    #         for line in self.submitted_vehicle_req_ids:
    #             line.unlink()

    #     if self.upcoming_vehicle_req_ids:
    #         for line in self.upcoming_vehicle_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('employee_vehicle_request.group_employee_manager_v')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_vehicle_req_ids = self.env['employee.fleet'].search([("employee", "in", HrEmployees.ids),
    #                                                                                 ("state", "in", ['waiting'])])
    #                     if pending_vehicle_req_ids:
    #                         for res in pending_vehicle_req_ids:
    #                             self.pending_vehicle_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "vehicle_id": res.id,
    #                                 "employee_id": res.employee.id,
    #                                 "from_location": res.from_location,
    #                                 "to_location": res.to_location,
    #                                 "state": res.state
    #                             })

    #     submitted_vehicle_req_ids = self.env['employee.fleet'].search([("employee", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['draft', 'waiting'])])
    #     if submitted_vehicle_req_ids:
    #         for res in submitted_vehicle_req_ids:
    #             self.submitted_vehicle_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "vehicle_id": res.id,
    #                 "employee_id": res.employee.id,
    #                 "from_location": res.from_location,
    #                 "to_location": res.to_location,
    #                 "state": res.state
    #             })

    #     upcoming_vehicle_req_ids = self.env['employee.fleet'].search([("employee", "=", self.employee_id.id),
    #                                                                  ("req_date", ">=", self.date),
    #                                                                  ("state", "in", ['confirm'])])
    #     if upcoming_vehicle_req_ids:
    #         for res in upcoming_vehicle_req_ids:
    #             self.upcoming_vehicle_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "vehicle_id": res.id,
    #                 "employee_id": res.employee.id,
    #                 "from_location": res.from_location,
    #                 "to_location": res.to_location,
    #                 "state": res.state
    #             })

    #     # PF Request
    #     if self.pending_pf_req_ids:
    #         for line in self.pending_pf_req_ids:
    #             line.unlink()

    #     if self.submitted_pf_req_ids:
    #         for line in self.submitted_pf_req_ids:
    #             line.unlink()

    #     if self.upcoming_pf_req_ids:
    #         for line in self.upcoming_pf_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('pf_withdrawl.group_pf_withdraw_approver')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_pf_req_ids = self.env['pf.widthdrawl'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                            ("state", "in", ['to_approve'])])
    #                     if pending_pf_req_ids:
    #                         for res in pending_pf_req_ids:
    #                             self.pending_pf_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "pf.widthdrawl": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "advance_amount": res.advance_amount,
    #                                 "purpose": res.purpose,
    #                                 "state": res.state
    #                             })

    #     submitted_pf_req_ids = self.env['pf.widthdrawl'].search([("employee_id", "=", self.employee_id.id),
    #                                                              ("state", "in", ['draft', 'to_approve'])])
    #     if submitted_pf_req_ids:
    #         for res in submitted_pf_req_ids:
    #             self.submitted_pf_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "pf.widthdrawl": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "advance_amount": res.advance_amount,
    #                 "purpose": res.purpose,
    #                 "state": res.state
    #             })

    #     upcoming_pf_req_ids = self.env['pf.widthdrawl'].search([("employee_id", "=", self.employee_id.id),
    #                                                             ("date", ">=", self.date),
    #                                                             ("state", "in", ['approved'])])
    #     if upcoming_pf_req_ids:
    #         for res in upcoming_pf_req_ids:
    #             self.upcoming_pf_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "pf.widthdrawl": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "advance_amount": res.advance_amount,
    #                 "purpose": res.purpose,
    #                 "state": res.state
    #             })

    #     # Appraisal Request
    #     if self.pending_appraisal_request_ids:
    #         for line in self.pending_appraisal_request_ids:
    #             line.unlink()

    #     if self.submitted_appraisal_request_ids:
    #         for line in self.submitted_appraisal_request_ids:
    #             line.unlink()

    #     if self.upcoming_appraisal_request_ids:
    #         for line in self.upcoming_appraisal_request_ids:
    #             line.unlink()

    #     group_id = self.env.ref('appraisal_stpi.group_manager_appraisal')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_appraisal_request_ids = self.env['appraisal.main'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                        ("state", "in", ['self_review'])])
    #                     if pending_appraisal_request_ids:
    #                         for res in pending_appraisal_request_ids:
    #                             self.pending_appraisal_request_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "abap_id": res.abap_id,
    #                                 "template_id": res.template_id,
    #                                 "state": res.state
    #                             })

    #     submitted_appraisal_request_ids = self.env['appraisal.main'].search([("employee_id", "=", self.employee_id.id),
    #                                                                          ("state", "in", ['draft', 'self_review'])])
    #     if submitted_appraisal_request_ids:
    #         for res in submitted_appraisal_request_ids:
    #             self.submitted_appraisal_request_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "abap_id": res.abap_id,
    #                 "template_id": res.template_id,
    #                 "state": res.state
    #             })

    #     upcoming_appraisal_request_ids = self.env['appraisal.main'].search([("employee_id", "=", self.employee_id.id),
    #                                                                         ("create_date", ">=", datetime.now()),
    #                                                                         ("state", "in", ['reporting_authority_review'])])
    #     if upcoming_appraisal_request_ids:
    #         for res in upcoming_appraisal_request_ids:
    #             self.upcoming_appraisal_request_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "abap_id": res.abap_id,
    #                 "template_id": res.template_id,
    #                 "state": res.state
    #             })

    #     # income tax
    #     if self.pending_income_tax_ids:
    #         for line in self.pending_income_tax_ids:
    #             line.unlink()

    #     if self.submitted_income_tax_ids:
    #         for line in self.submitted_income_tax_ids:
    #             line.unlink()

    #     if self.upcoming_income_tax_ids:
    #         for line in self.upcoming_income_tax_ids:
    #             line.unlink()

    #     group_id = self.env.ref('tds.group_manager_hr_declaration')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_income_tax_ids = self.env['hr.declaration'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                 ("state", "in", ['to_approve'])])
    #                     if pending_income_tax_ids:
    #                         for res in pending_income_tax_ids:
    #                             self.pending_income_tax_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "running_fy_id": res.id,
    #                                 "date_range_id": res.date_range.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "total_gross": res.tax_salary_final,
    #                                 "taxable_income": res.taxable_income,
    #                                 "tax_payable": res.tax_payable,
    #                                 "tax_paid": res.tax_paid,
    #                                 "total_rem": res.pending_tax,
    #                                 "state": res.state
    #                             })

    #     submitted_income_tax_ids = self.env['hr.declaration'].search([("employee_id", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['draft', 'to_approve'])])

    #     if submitted_income_tax_ids:
    #         for res in submitted_income_tax_ids:
    #             self.submitted_income_tax_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "running_fy_id": res.id,
    #                 "date_range_id": res.date_range.id,
    #                 "employee_id": res.employee_id.id,
    #                 "total_gross": res.tax_salary_final,
    #                 "taxable_income": res.taxable_income,
    #                 "tax_payable": res.tax_payable,
    #                 "tax_paid": res.tax_paid,
    #                 "total_rem": res.pending_tax,
    #                 "state": res.state
    #             })

    #     upcoming_income_tax_ids = self.env['hr.declaration'].search([("employee_id", "=", self.employee_id.id),
    #                                                                  ("date", ">=", self.date),
    #                                                                  ("state", "in", ['approved'])])

    #     if upcoming_income_tax_ids:
    #         for res in upcoming_income_tax_ids:
    #             self.upcoming_income_tax_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "running_fy_id": res.id,
    #                 "date_range_id": res.date_range.id,
    #                 "employee_id": res.employee_id.id,
    #                 "total_gross": res.tax_salary_final,
    #                 "taxable_income": res.taxable_income,
    #                 "tax_payable": res.tax_payable,
    #                 "tax_paid": res.tax_paid,
    #                 "total_rem": res.pending_tax,
    #                 "state": res.state
    #             })



    #     # Loan
    #     if self.pending_loan_request_ids:
    #         for line in self.pending_loan_request_ids:
    #             line.unlink()

    #     if self.submitted_loan_request_ids:
    #         for line in self.submitted_loan_request_ids:
    #             line.unlink()



    #     group_id = self.env.ref('ohrms_loan.group_loan_approver')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_loan_request_ids = self.env['hr.loan'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                 ("state", "in", ['waiting_approval_1','waiting_approval_2'])])
    #                     if pending_loan_request_ids:
    #                         for res in pending_loan_request_ids:
    #                             self.pending_loan_request_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "loan_id": res.id,
    #                                 "type_id": res.type_id.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "installment": res.installment,
    #                                 "total_amount": res.total_amount,
    #                                 "total_interest": res.total_interest,
    #                                 "total_paid_amount": res.total_paid_amount,
    #                                 "balance_amount": res.balance_amount,
    #                                 "state": res.state
    #                             })

    #     submitted_loan_request_ids = self.env['hr.loan'].search([("employee_id", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['waiting_approval_1', 'waiting_approval_2', 'draft'])])

    #     if submitted_loan_request_ids:
    #         for res in submitted_loan_request_ids:
    #             self.submitted_loan_request_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "loan_id": res.id,
    #                 "type_id": res.type_id.id,
    #                 "employee_id": res.employee_id.id,
    #                 "installment": res.installment,
    #                 "total_amount": res.total_amount,
    #                 "total_interest": res.total_interest,
    #                 "total_paid_amount": res.total_paid_amount,
    #                 "balance_amount": res.balance_amount,
    #                 "state": res.state
    #             })

    #     if self.exit_type == 'Transferred':
    #         if self.upcoming_loan_request_ids:
    #             for line in self.upcoming_loan_request_ids:
    #                 line.unlink()
    #         upcoming_loan_request_ids = self.env['hr.loan'].search([("employee_id", "=", self.employee_id.id),
    #                                                                      ("state", "in", ['approve']),('balance_amount', '!=', 0)],limit=1)

    #         if upcoming_loan_request_ids:
    #             paid = 0
    #             unpaid = 0
    #             for res in upcoming_loan_request_ids:
    #                 for line in res.loan_lines:
    #                     if line.paid:
    #                         paid+=1
    #                     else:
    #                         unpaid+=1
    #                 self.upcoming_loan_request_ids.create({
    #                     "exit_transfer_id": self.id,
    #                     "loan_id": res.id,
    #                     "no_of_emi_paid": paid,
    #                     "no_of_emi_pending": unpaid,
    #                 })
    #     else:
    #         if self.not_transferrred_loan_request_ids:
    #             for line in self.not_transferrred_loan_request_ids:
    #                 line.unlink()
    #         not_transferrred_loan_request_ids = self.env['hr.loan'].search([("employee_id", "=", self.employee_id.id),
    #                                                                      ("state", "in", ['approve']),('balance_amount', '!=', 0)],limit=1)

    #         if not_transferrred_loan_request_ids:
    #             paid = 0
    #             unpaid = 0
    #             for res in not_transferrred_loan_request_ids:
    #                 for line in res.loan_lines:
    #                     if line.paid:
    #                         paid+=1
    #                     else:
    #                         unpaid+=1
    #                 self.not_transferrred_loan_request_ids.create({
    #                     "exit_transfer_id": self.id,
    #                     "loan_id": res.id,
    #                     "no_of_emi_paid": paid,
    #                     "no_of_emi_pending": unpaid,
    #                 })

    #     # File management
    #     if self.my_correspondence_ids:
    #         for line in self.my_correspondence_ids:
    #             line.unlink()

    #     if self.my_file_ids:
    #         for line in self.my_file_ids:
    #             line.unlink()

    #     my_correspondence_ids = self.env['muk_dms.file'].search([("current_owner_id", "=", self.env.user.id), ("folder_id", "=", False)])

    #     if my_correspondence_ids:
    #         for res in my_correspondence_ids:
    #             self.my_correspondence_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "correspondence_id": res.id,
    #                 "letter_no": res.letter_number,
    #                 "file_assign_id": res.folder_id.id,
    #             })

    #     my_file_ids = self.env['folder.master'].search([("current_owner_id", "=", self.env.user.id)])

    #     if my_file_ids:
    #         for res in my_file_ids:
    #             self.my_file_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "file_name": res.folder_name,
    #                 "file_id": res.id,
    #                 "number": res.number,
    #                 "state": res.state
    #             })

    #     #Indent Request
    #     if self.pending_indent_req_ids:
    #         for line in self.pending_indent_req_ids:
    #             line.unlink()

    #     if self.submitted_indent_req_ids:
    #         for line in self.submitted_indent_req_ids:
    #             line.unlink()

    #     if self.upcoming_indent_req_ids:
    #         for line in self.upcoming_indent_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('indent_stpi.group_Indent_request_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_indent_req_ids = self.env['indent.request'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                 ("state", "in", ['to_approve']),
    #                                                                                 ("indent_type", "in", ['issue'])])

    #                     if pending_indent_req_ids:
    #                         for res in pending_indent_req_ids:
    #                             self.pending_indent_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "number": res.indent_sequence,
    #                                 "indent_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "indent_type": res.indent_type,
    #                                 "state" : res.state,
    #                             })

    #     submitted_indent_req_ids = self.env['indent.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                                 ("state", "in", ['draft', 'to_approve']),
    #                                                                   ("indent_type", "in", ['issue'])])

    #     if submitted_indent_req_ids:
    #         for res in submitted_indent_req_ids:
    #             self.submitted_indent_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "number": res.indent_sequence,
    #                 "indent_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "indent_type": res.indent_type,
    #                 "state": res.state,
    #             })

    #     upcoming_indent_req_ids = self.env['indent.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                                  ("date_of_receive", ">=", self.date),#requested_date
    #                                                                   ("state", "in", ['approved']),
    #                                                                   ("indent_type", "in", ['issue']),
    #                                                                  ])

    #     if upcoming_indent_req_ids:
    #         for res in upcoming_indent_req_ids:
    #             self.upcoming_indent_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "number": res.indent_sequence,
    #                 "indent_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "indent_type": res.indent_type,
    #                 "state": res.state,
    #             })

    #     # GRN
    #     if self.pending_grn_ids:
    #         for line in self.pending_grn_ids:
    #             line.unlink()

    #     if self.submitted_grn_ids:
    #         for line in self.submitted_grn_ids:
    #             line.unlink()

    #     if self.upcoming_grn_ids:
    #         for line in self.upcoming_grn_ids:
    #             line.unlink()

    #     group_id = self.env.ref('indent_stpi.group_Indent_request_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_grn_ids = self.env['indent.request'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                 ("state", "in", ['to_approve']),
    #                                                                                 ("indent_type", "in", ['grn'])])

    #                     if pending_grn_ids:
    #                         for res in pending_grn_ids:
    #                             self.pending_grn_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "number": res.indent_sequence,
    #                                 "indent_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "indent_type": res.indent_type,
    #                                 "state": res.state,
    #                             })

    #     submitted_grn_ids = self.env['indent.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['draft', 'to_approve']),
    #                                                                                 ("indent_type", "in", ['issue'])])

    #     if submitted_grn_ids:
    #         for res in submitted_grn_ids:
    #             self.submitted_grn_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "number": res.indent_sequence,
    #                 "indent_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "indent_type": res.indent_type,
    #                 "state": res.state,
    #             })

    #     upcoming_grn_ids = self.env['indent.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                           ("date_of_receive", ">=", self.date),
    #                                                           ("state", "in", ['approved']),
    #                                                           ("indent_type", "in", ['issue'])])

    #     if upcoming_grn_ids:
    #         for res in upcoming_grn_ids:
    #             self.upcoming_grn_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "number": res.indent_sequence,
    #                 "indent_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "indent_type": res.indent_type,
    #                 "state": res.state,
    #             })

    #     # Issue Request
    #     if self.pending_issue_req_ids:
    #         for line in self.pending_issue_req_ids:
    #             line.unlink()

    #     if self.submitted_issue_req_ids:
    #         for line in self.submitted_issue_req_ids:
    #             line.unlink()

    #     if self.upcoming_issue_req_ids:
    #         for line in self.upcoming_issue_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('indent_stpi.group_issue_request_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_issue_req_ids = self.env['issue.request'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                   ("state", "in", ['to_approve']),
    #                                                                                 ("indent_type", "in", ['issue'])])

    #                     if pending_issue_req_ids:
    #                         for res in pending_issue_req_ids:
    #                             self.pending_issue_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "issue_id": res.id,
    #                                 "indent_grn": res.Indent_id.id,
    #                                 "item_category_id": res.item_category_id.id,
    #                                 "item_id": res.item_id.id,
    #                                 "requested_quantity": res.requested_quantity,
    #                                 "approved_quantity": res.approved_quantity,
    #                                 "state": res.state,
    #                             })

    #     submitted_issue_req_ids = self.env['issue.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                            ("state", "in", ['draft', 'to_approve']),
    #                                                                  ("indent_type", "in", ['issue'])])
    #     if submitted_issue_req_ids:
    #         for res in submitted_issue_req_ids:
    #             self.submitted_issue_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "issue_id": res.id,
    #                 "indent_grn": res.Indent_id.id,
    #                 "item_category_id": res.item_category_id.id,
    #                 "item_id": res.item_id.id,
    #                 "requested_quantity": res.requested_quantity,
    #                 "approved_quantity": res.approved_quantity,
    #                 "state": res.state,
    #             })

    #     upcoming_issue_req_ids = self.env['issue.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                                ("requested_date", ">=", self.date),#approved_date
    #                                                                ("state", "in", ['approved']),
    #                                                                ("indent_type", "in", ['issue'])])
    #     if upcoming_issue_req_ids:
    #         for res in upcoming_issue_req_ids:
    #             self.upcoming_issue_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "issue_id": res.id,
    #                 "indent_grn": res.Indent_id.id,
    #                 "item_category_id": res.item_category_id.id,
    #                 "item_id": res.item_id.id,
    #                 "requested_quantity": res.requested_quantity,
    #                 "approved_quantity": res.approved_quantity,
    #                 "state": res.state,
    #             })

    #     #GRN Request
    #     if self.pending_grn_req_ids:
    #         for line in self.pending_grn_req_ids:
    #             line.unlink()

    #     if self.submitted_grn_req_ids:
    #         for line in self.submitted_grn_req_ids:
    #             line.unlink()

    #     if self.upcoming_grn_req_ids:
    #         for line in self.upcoming_grn_req_ids:
    #             line.unlink()

    #     group_id = self.env.ref('indent_stpi.group_issue_request_manager')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_grn_req_ids = self.env['issue.request'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                             ("state", "in", ['to_approve']),
    #                                                                                 ("indent_type", "in", ['grn'])])
    #                     if pending_grn_req_ids:
    #                         for res in pending_grn_req_ids:
    #                             self.pending_grn_req_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "issue_id": res.id,
    #                                 "indent_grn": res.Indent_id.id,
    #                                 "item_category_id": res.item_category_id.id,
    #                                 "item_id": res.item_id.id,
    #                                 "requested_quantity": res.requested_quantity,
    #                                 "approved_quantity": res.approved_quantity,
    #                                 "state": res.state,
    #                             })
    #     submitted_grn_req_ids = self.env['issue.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                                  ("state", "in", ['draft', 'to_approve']),
    #                                                               ("indent_type", "in", ['grn'])])
    #     if submitted_grn_req_ids:
    #         for res in submitted_grn_req_ids:
    #             self.submitted_grn_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "issue_id": res.id,
    #                 "indent_grn": res.Indent_id.id,
    #                 "item_category_id": res.item_category_id.id,
    #                 "item_id": res.item_id.id,
    #                 "requested_quantity": res.requested_quantity,
    #                 "approved_quantity": res.approved_quantity,
    #                 "state": res.state,
    #             })

    #     upcoming_grn_req_ids = self.env['issue.request'].search([("employee_id", "=", self.employee_id.id),
    #                                                              ("requested_date", ">=", self.date),
    #                                                              ("state", "in", ['approved']),
    #                                                              ("indent_type", "in", ['grn'])])
    #     if upcoming_grn_req_ids:
    #         for res in upcoming_grn_req_ids:
    #             self.upcoming_grn_req_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "employee_id": res.employee_id.id,
    #                 "issue_id": res.id,
    #                 "indent_grn": res.Indent_id.id,
    #                 "item_category_id": res.item_category_id.id,
    #                 "item_id": res.item_id.id,
    #                 "requested_quantity": res.requested_quantity,
    #                 "approved_quantity": res.approved_quantity,
    #                 "state": res.state,
    #             })

    #     #Check Birthday
    #     if self.pending_check_birth_ids:
    #         for line in self.pending_check_birth_ids:
    #             line.unlink()

    #     if self.submitted_check_birth_ids:
    #         for line in self.submitted_check_birth_ids:
    #             line.unlink()

    #     if self.upcoming_check_birth_ids:
    #         for line in self.upcoming_check_birth_ids:
    #             line.unlink()

    #     group_id = self.env.ref('birthday_check.group_approvar_birthday')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_check_birth_ids = self.env['cheque.requests'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                             ("state", "in", ['to_approve'])])

    #                     if pending_check_birth_ids:
    #                         for res in pending_check_birth_ids:
    #                             self.pending_check_birth_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "check_id": res.id,    #chek_id
    #                                 "employee_id": res.employee_id.id,
    #                                 "name": res.name,
    #                                 "birthday": res.birthday,
    #                                 "state": res.state,
    #                             })

    #     submitted_check_birth_ids = self.env['cheque.requests'].search([("employee_id", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['draft', 'to_approve'])])

    #     if submitted_check_birth_ids:
    #         for res in submitted_check_birth_ids:
    #             self.submitted_check_birth_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "check_id": res.id,  # chek_id
    #                 "employee_id": res.employee_id.id,
    #                 "name": res.name,
    #                 "birthday": res.birthday,
    #                 "state": res.state,
    #             })

    #     upcoming_check_birth_ids = self.env['cheque.requests'].search([("employee_id", "=", self.employee_id.id),
    #                                                                    ("create_date", ">=", datetime.now()),#("birthday", ">=", self.birthday),
    #                                                                     ("state", "in", ['approved'])])

    #     if upcoming_check_birth_ids:
    #         for res in upcoming_check_birth_ids:
    #             self.upcoming_check_birth_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "check_id": res.id,  # chek_id
    #                 "employee_id": res.employee_id.id,
    #                 "name": res.name,
    #                 "birthday": res.birthday,
    #                 "state": res.state,
    #             })

    #     #reimbursement

    #     if self.pending_reimbursement_ids:
    #         for line in self.pending_reimbursement_ids:
    #             line.unlink()

    #     if self.submitted_reimbursement_ids:
    #         for line in self.submitted_reimbursement_ids:
    #             line.unlink()

    #     if self.upcoming_reimbursement_ids:
    #         for line in self.upcoming_reimbursement_ids:
    #             line.unlink()

    #     group_id = self.env.ref('reimbursement_stpi.group_approving_authority')
    #     if group_id:
    #         for ln in group_id:
    #             for user in ln.users:
    #                 if user.id == self.employee_id.user_id.id:
    #                     # me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #                     HrEmployees = self.env['hr.employee'].sudo().search(
    #                         [("branch_id", "=", self.employee_id.branch_id.id)])
    #                     pending_reimbursement_ids = self.env['reimbursement'].search([("employee_id", "in", HrEmployees.ids),
    #                                                                                   ("state", "in", ['to_approve'])])
    #                     if pending_reimbursement_ids:
    #                         for res in pending_reimbursement_ids:
    #                             self.pending_reimbursement_ids.create({
    #                                 "exit_transfer_id": self.id,
    #                                 "reiburs_id": res.id,
    #                                 "employee_id": res.employee_id.id,
    #                                 "name": res.name,
    #                                 "claim_sub": res.date_range.id,
    #                                 "claimed_amount":res.claimed_amount,
    #                                 "net_amount": res.net_amount,
    #                                 "state": res.state,
    #                             })

    #     submitted_reimbursement_ids = self.env['reimbursement'].search([("employee_id", "=", self.employee_id.id),
    #                                                                   ("state", "in", ['draft','to_approve'])])
    #     if submitted_reimbursement_ids:
    #         for res in submitted_reimbursement_ids:
    #             self.submitted_reimbursement_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "reiburs_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "name": res.name,
    #                 "claim_sub": res.date_range.id,
    #                 "claimed_amount": res.claimed_amount,
    #                 "net_amount": res.net_amount,
    #                 "state": res.state,
    #             })

    #     upcoming_reimbursement_ids = self.env['reimbursement'].search([("employee_id", "=", self.employee_id.id),
    #                                                                    ("create_date", ">=", datetime.now()),
    #                                                                     ("state", "in", ['approved'])])
    #     if upcoming_reimbursement_ids:
    #         for res in upcoming_reimbursement_ids:
    #             self.upcoming_reimbursement_ids.create({
    #                 "exit_transfer_id": self.id,
    #                 "reiburs_id": res.id,
    #                 "employee_id": res.employee_id.id,
    #                 "name": res.name,
    #                 "claim_sub": res.date_range.id,
    #                 "claimed_amount": res.claimed_amount,
    #                 "net_amount": res.net_amount,
    #                 "state": res.state,
    #             })
    #     line = self.employee_id.user_id
    #     # template = self.env.ref('exit_transfer_management.email_template_notify_user', raise_if_not_found=False)
    #     # if template:
    #     #     ctx = {'rec':self, 'name': self.name, 'partner_name': line.name}
    #     #     template.with_context(ctx).send_mail(line.id, force_send=False, raise_exception=False)
    #     self.update({"state":"verify"})
    #     if self.employee_id.user_id:
    #         approval_date = datetime.now() + timedelta(days=2)
    #         self.activity_schedule(summary='Exit Transfer Management',activity_type_id=1,date_deadline=datetime.now().date(),user_id=self.employee_id.user_id.id)

    def button_confirm(self):
        roster = self.env['recruitment.roster']
        for res in self:
            if res.exit_type == 'Transferred':
                # import pdb;
                # pdb.set_trace()
                res.employee_id.branch_id = res.to_branch_id.id
                
                res.employee_id.work_location = res.to_branch_id.name
                res.employee_id.user_id.default_branch_id = res.to_branch_id.id
                if res.to_branch_id.id not in res.employee_id.user_id.branch_ids.ids:
                    res.employee_id.user_id.branch_ids = [(4,res.to_branch_id.id)]  

                if res.employee_id.roster_line_item:
                    res.employee_id.roster_line_item.current_status = res.exit_type
                    res.employee_id.roster_line_item.current_status_date = date.today()
                
                template = self.env.ref('exit_transfer_management.email_template_transfer_notify_user', raise_if_not_found=False)
                mail = self.env['mail.template'].sudo().browse(template.id)
                create_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)])
                mail_lis = self.mail_list()

                if mail:
                    ctx = {'email_from': create_employee_id.work_email,
                            'email_to': self.employee_id.parent_id.work_email,
                            'subject': f'{self.employee_id.name} | {self.name}',
                            'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',self.employee_id.parent_id.work_email)],limit=1).name
                        }
                    mail.with_context(ctx).send_mail(self.id, force_send=False, raise_exception=False)

                    for i, user_mail in enumerate(mail_lis.get('employee_manager_mail')):
                        ctx = {'email_from': create_employee_id.work_email,
                                'email_to': user_mail,
                                'subject': f'{self.employee_id.name} | {self.name}',
                                'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name
                                }
                        mail.with_context(ctx).send_mail(self.id, force_send=False, 
                                                        raise_exception=False)

                    for i, user_mail in enumerate(mail_lis.get('finance_users_mail')):
                        ctx = {'email_from': create_employee_id.work_email,
                                'email_to': user_mail,
                                'subject': f'{self.employee_id.name} | {self.name}',
                                'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name
                                }
                        mail.with_context(ctx).send_mail(self.id, force_send=False, 
                                                        raise_exception=False)
                    # Mail for Technical
                    for i, user_mail in enumerate(mail_lis.get('technical_users_mail')):
                        ctx = {'email_from': create_employee_id.work_email,
                                'email_to': user_mail,
                                'subject': f'{self.employee_id.name} | {self.name}',
                                'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name
                                }
                        mail.with_context(ctx).send_mail(self.id, force_send=False, 
                                                            raise_exception=False)
                    # Mail for Personal
                    for i, user_mail in enumerate(mail_lis.get('personal_users_mail')):
                        ctx = {'email_from': create_employee_id.work_email,
                                'email_to': user_mail,
                                'subject': f'{self.employee_id.name} | {self.name}',
                                'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name
                                }
                        mail.with_context(ctx).send_mail(self.id, force_send=False,
                                                            raise_exception=False)
                    # Mail for General
                    for i, user_mail in enumerate(mail_lis.get('general_users_mail')):
                        ctx = {'email_from': create_employee_id.work_email,
                                'email_to': user_mail,
                                'subject': f'{self.employee_id.name} | {self.name}',
                                'recipient_name': self.env['hr.employee'].sudo().search([('work_email','=',user_mail)],limit=1).name
                            }
                        mail.with_context(ctx).send_mail(self.id, force_send=False,
                                                            raise_exception=False)
                res.employee_id.parent_id = False
                res.employee_id.user_id.groups_id = False
                if res.employee_id.employee_type == 'regular':
                    group_id = self.env.ref('groups_inherit.group_employee_type_regular')
                elif res.employee_id.employee_type == 'contractual_with_agency':
                    group_id= self.env.ref('groups_inherit.group_employee_type_contractual_with_agency')
                else:
                    group_id= self.env.ref('groups_inherit.group_employee_type_contractual_with_stpi') 
                res.employee_id.user_id.write({
                    'groups_id':[(4, group_id.id)]
                })
                res.employee_id.user_id.write({'share':False})

                    # roster.create({'job_id': res.employee_id.roster_line_item.job_id.id,
                    # 'roster_point_id': res.employee_id.roster_line_item.roster_point_id.id,
                    # 'category_id':[[6,0,res.employee_id.roster_line_item.category_id.ids]],
                    # 'state':res.employee_id.roster_line_item.state.id,
                    # 'branch_id':res.employee_id.roster_line_item.branch_id.id,'current_status': 'Vacant','current_status_date': date.today(),
                    # 'group_id': res.employee_id.roster_line_item.job_id.pay_level_id.group_id.id})
                    
                    # roster_line_new = roster.search([('job_id', '=', res.employee_id.roster_line_item.job_id.id),
                    # ('branch_id','=',res.to_branch_id.id),('employee_id','=',False)],limit=1)
                    # res.employee_id.roster_line_item = res.roster_line_item.id

            elif res.exit_type == 'Suspended':
                if res.transferred_req == 'yes':
                     # res.employee_id.user_id.active = False
                    res.employee_id.branch_id = res.to_branch_id.id
                    res.employee_id.work_location = res.to_branch_id.name
                    res.employee_id.user_id.default_branch_id = res.to_branch_id.id
                    if res.to_branch_id.id not in res.employee_id.user_id.branch_ids.ids:
                        res.employee_id.user_id.branch_ids = [(4,res.to_branch_id.id)] 
                    if res.employee_id.roster_line_item:
                        res.employee_id.roster_line_item.current_status = res.exit_type 
                        res.employee_id.roster_line_item.current_status_date = date.today()
                else:
                    if res.employee_id.roster_line_item:
                        res.employee_id.roster_line_item.current_status = res.exit_type 
                        res.employee_id.roster_line_item.current_status_date = date.today()


            elif res.exit_type == 'technical resignation':
                if res.employee_id.roster_line_item:
                    res.employee_id.roster_line_item.current_status = 'technical resignation internal' if res.reg_type == 'internal' else 'deputation' if res.reg_type == 'deputation' else 'technical resignation external'
                    res.employee_id.roster_line_item.current_status_date = date.today()
                    res.employee_id.roster_line_item.remarks = False
                    if res.reg_type == 'external':
                        res.employee_id.user_id.active = False  
                    

                    roster.create({'job_id': res.employee_id.roster_line_item.job_id.id,
                    'roster_point_id': res.employee_id.roster_line_item.roster_point_id.id,
                    'category_id':[[6,0,res.employee_id.roster_line_item.category_id.ids]],
                    'state':res.employee_id.roster_line_item.state.id,
                    'branch_id':res.employee_id.roster_line_item.branch_id.id,'current_status': 'Vacant','current_status_date': date.today(),
                    'remarks' : 'This Position to be hired for Lien',
                    'group_id': res.employee_id.roster_line_item.job_id.pay_level_id.group_id.id})

                    # res.employee_id.roster_line_item = False

            elif res.exit_type == 'deputation':
                if res.employee_id.roster_line_item:
                    res.employee_id.roster_line_item.current_status = 'technical resignation internal' if res.reg_type == 'internal' else 'deputation' if res.exit_type == 'deputation' else 'technical resignation external'
                    res.employee_id.roster_line_item.current_status_date = date.today()
                    res.employee_id.roster_line_item.remarks = False
                    res.employee_id.user_id.active = False
                    roster.create({'job_id': res.employee_id.roster_line_item.job_id.id,
                    'roster_point_id': res.employee_id.roster_line_item.roster_point_id.id,
                    'category_id':[[6,0,res.employee_id.roster_line_item.category_id.ids]],
                    'state':res.employee_id.roster_line_item.state.id,
                    'branch_id':res.employee_id.roster_line_item.branch_id.id,'current_status': 'Vacant','current_status_date': date.today(),
                    'remarks' : 'This Position to be hired for Lien',
                    'group_id': res.employee_id.roster_line_item.job_id.pay_level_id.group_id.id})

            else:
                res.employee_id.user_id.active = False
                res.employee_id.active = False
                
                res.employee_id.last_working_date = date.today()
                res.employee_id.exit_type = res.exit_type

                if res.employee_id.roster_line_item:
                    res.employee_id.roster_line_item.current_status = res.exit_type
                    res.employee_id.roster_line_item.current_status_date = date.today()

                    roster.create({'job_id': res.employee_id.roster_line_item.job_id.id,
                    'roster_point_id': res.employee_id.roster_line_item.roster_point_id.id,
                    'category_id':[[6,0,res.employee_id.roster_line_item.category_id.ids]],
                    'state':res.employee_id.roster_line_item.state.id,
                    'branch_id':res.employee_id.roster_line_item.branch_id.id,
                    'current_status': 'Vacant',
                    'current_status_date': date.today(),
                    'group_id': res.employee_id.roster_line_item.job_id.pay_level_id.group_id.id})

            res.employee_remark_finance = res.employee_finance.id
            res.dues_remark_finance = res.dues_finance
            res.remarks_remark_finance = res.remarks_finance
            res.employee_remark_general = res.employee_general.id
            res.dues_remark_general = res.dues_general
            res.remarks_remark_general = res.remarks_general
            res.employee_remark_personal = res.employee_personal.id
            res.dues_remark_personal = res.dues_personal
            res.remarks_remark_personal = res.remarks_personal
            res.employee_remark_technical = res.employee_technical.id
            res.dues_remark_technical = res.dues_technical
            res.remarks_remark_technical = res.remarks_technical
            res.employee_remark_ro = res.employee_ro.id
            res.dues_remark_ro = res.dues_ro
            res.remarks_remark_ro = res.remarks_ro
            # roster = self.env['recruitment.roster'].search([('employee_id', '=', res.employee_id.id)])
            # if roster:
            #     for line in roster:
            #         line.employee_id == False
            #         line.Name_of_person == False
            #         line.Hired_category == False
            #         line.date_of_apointment == False
        self.env['exit_history_line'].sudo().create({
            'employee_id' : self.employee_id.id,
            'exit_type' : self.exit_type,
            'exit_date' : self.exit_date
        })
        self.update({"state":"complete"})
        if (self.exit_type == 'technical resignation') and (self.reg_type == 'internal' or self.reg_type == 'external'):
            # contract_id = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
            # if contract_id:
            #     contract_id.update({'state':'close','date_end': date.today()})
            self.employee_id.roster_line_item = False
        else:
            if self.exit_type == 'deputation':
                # contract_id = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
                # if contract_id:
                #     contract_id.update({'state':'close','date_end': date.today()})
                self.employee_id.roster_line_item = False
                self.employee_id.state = 'deputation'
            template_id = self.env.ref('exit_transfer_management.exit_management_noc_mail_template')
            report_template_id = self.env.ref('exit_transfer_management.noc_exit_id').render_qweb_pdf(self.id)
            data_record = base64.b64encode(report_template_id[0])
            ir_values = {
                'name': "Noc Report",
                'type': 'binary',
                'datas': data_record,
                'datas_fname': f"{self.employee_id.name} NOC",
                'mimetype': 'application/x-pdf',
            }
            data_id = self.env['ir.attachment'].create(ir_values)
            # template = self.template_id
            template_id.attachment_ids = [(6, 0, [data_id.id])]
            if template_id:
                for rec in self:
                    if rec.state == 'complete':
                            template_id.sudo().send_mail(rec.id,notif_layout="mail.mail_notification_light")
            # email_values = {'email_to': self.partner_id.email,
            #                 'email_from': self.env.user.email}
            # template.send_mail(self.id, email_values=email_values, force_send=True)
            template_id.attachment_ids = [(3, data_id.id)]

    


    def button_send_for_approval(self):
        msg = "Please complete all pending activities for :\n"
        if self.ignore_all == True:
            self.update({"state":"send_for_approval"})
        else:
            self.compute_exit_management()
            flag = 1
            for line in self.leave_line_ids:
                if line:
                    flag = 0
            for line in self.pending_leave_line_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_leave_line_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_tour_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_tour_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_tour_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_ltc_sequence_ids:
                if line:
                    flag = 0
            for line in self.submitted_ltc_sequence_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_ltc_sequence_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_ltc_claim_ids:
                if line:
                    flag = 0
            for line in self.submitted_ltc_claim_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_ltc_claim_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_tour_claim_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_tour_claim_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_tour_claim_req_ids:
            #     if line:
            #         flag = 0
            # for line in self.pending_vehicle_req_ids:
            #     if line:
            #         flag = 0
            # for line in self.submitted_vehicle_req_ids:
            #     if line:
            #         flag = 0
            # for line in self.upcoming_vehicle_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_pf_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_pf_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_pf_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_appraisal_request_ids:
                if line:
                    flag = 0
            for line in self.submitted_appraisal_request_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_appraisal_request_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_income_tax_ids:
                if line:
                    flag = 0
            for line in self.submitted_income_tax_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_income_tax_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_loan_request_ids:
                if line:
                    flag = 0
            for line in self.submitted_loan_request_ids:
                if line:
                    flag = 0
            if len(self.upcoming_loan_request_ids.filtered(lambda x: x.continue_emi == 'no'\
                                                            and self.exit_type == 'Transferred')) > 0:
                flag = 0
            for line in self.not_transferrred_loan_request_ids:
                if line:
                    flag = 0
            for line in self.my_correspondence_ids:
                if line:
                    flag = 0
            for line in self.my_file_ids:
                if line:
                    flag = 0
            for line in self.pending_indent_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_indent_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_indent_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_grn_ids:
                if line:
                    flag = 0
            for line in self.submitted_grn_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_grn_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_issue_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_issue_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_issue_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_grn_req_ids:
                if line:
                    flag = 0
            for line in self.submitted_grn_req_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_grn_req_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_check_birth_ids:
                if line:
                    flag = 0
            for line in self.submitted_check_birth_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_check_birth_ids:
            #     if line:
            #         flag = 0
            for line in self.pending_reimbursement_ids:
                if line:
                    flag = 0
            for line in self.submitted_reimbursement_ids:
                if line:
                    flag = 0
            # for line in self.upcoming_reimbursement_ids:
            #     if line:
            #         flag = 0
            if flag == 1:
                self.update({"state": "send_for_approval"})
            else:
                index = 0
                if self.leave_line_ids or self.pending_leave_line_ids:
                    index = index + 1
                    msg = msg + f'{index}. LEAVE\n'
                if self.pending_tour_req_ids or self.submitted_tour_req_ids or self.pending_tour_claim_req_ids or self.submitted_tour_claim_req_ids:
                    index = index + 1
                    msg = msg + f'{index}.TOUR\n'
                if self.pending_ltc_sequence_ids or self.submitted_ltc_sequence_ids or self.pending_ltc_claim_ids or self.submitted_ltc_claim_ids:
                    index = index + 1
                    msg = msg + f'{index}. LTC\n'
                if self.pending_pf_req_ids or self.submitted_pf_req_ids:
                    index = index + 1
                    msg = msg + f'{index}. PF\n' 
                if self.pending_appraisal_request_ids or self.submitted_appraisal_request_ids:
                    index = index + 1
                    msg = msg + f'{index}. APPRAISAL\n' 
                if self.pending_income_tax_ids or self.submitted_income_tax_ids:
                    index = index + 1
                    msg = msg + f'{index}. INCOME TAX\n'
                if self.pending_loan_request_ids or self.submitted_loan_request_ids or len(self.upcoming_loan_request_ids.filtered(lambda x: x.continue_emi == 'no'\
                                                            and self.exit_type == 'Transferred')) > 0 or self.not_transferrred_loan_request_ids:
                    index = index + 1
                    msg = msg + f'{index}. LOAN\n'
                if self.my_correspondence_ids or self.my_file_ids:
                    index = index + 1
                    msg = msg + f'{index}. EFILE\n'
                if self.pending_indent_req_ids or self.submitted_indent_req_ids or self.pending_grn_ids \
                 or self.submitted_grn_ids or self.pending_issue_req_ids or self.submitted_issue_req_ids or self.pending_grn_req_ids or self.submitted_grn_req_ids:
                    index = index + 1
                    msg = msg + f'{index}. INDENT\n'
                if self.pending_reimbursement_ids or self.submitted_reimbursement_ids:
                    index = index + 1
                    msg = msg + f'{index}. REIMBURSEMENT\n'
                if self.pending_check_birth_ids or self.submitted_check_birth_ids:
                    index = index + 1
                    msg = msg + f'{index}. BIRTHDAY CHEQUE\n'
                    
                raise UserError(msg)




    def button_cancel(self):
        self.update({"state":"cancel"})

    def button_redraft(self):
        self.update({"state":"draft"})



class EmployeeLeave(models.Model):
    _name = "leave.lines"
    _description = 'Exit Transfer Management'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    leave_id = fields.Many2one("hr.leave", string="Leave Id")
    leave_type_id = fields.Many2one("hr.leave.type")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approval'),
        ('validate1', 'Second Approval'),
        ('cancel', 'Cancelled'),
        ('refuse', 'Refuse'),
        ('validate', 'Approved'),
    ], string ="Status")


    def leave_cancel(self):
        if self.exit_transfer_id:
            # self.exit_transfer_id.update({"state":"cancel"})
            self.leave_id.update({"state": "cancel",'write_uid': self.env.uid})
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Leave',
                "action_taken_by": me.id,
                "action_taken_on": self.leave_id.employee_id.id
            })
            self.unlink()

class PendingEmployeeLeave(models.Model):
    _name = "pending.leave.lines"
    _description = 'Pending Leave Lines'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    leave_id = fields.Many2one("hr.leave", string="Leave Id")
    leave_type_id = fields.Many2one("hr.leave.type")
    employee_id = fields.Many2one("hr.employee", string="Requested By")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approval'),
        ('validate1', 'Second Approval'),
        ('cancel', 'Cancelled'),
        ('refuse', 'Refuse'),
        ('validate', 'Approved'),
    ], string ="Status")

    def leave_approved(self):
        if self.leave_id:
            self.leave_id.update({"state":"validate",'write_uid': self.env.uid})
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Leave',
                "action_taken_by": me.id,
                "action_taken_on": self.leave_id.employee_id.id
            })
            self.unlink()

    def leave_rejected(self):
        if self.leave_id:
            self.leave_id.update({"state":"refuse",'write_uid': self.env.uid})
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Leave',
                "action_taken_by": me.id,
                "action_taken_on": self.leave_id.employee_id.id
            })
            self.unlink()

class UpcomingEmployeeLeave(models.Model):
    _name = "upcoming.leave.lines"
    _description = 'Upcoming Leave Lines'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    leave_id = fields.Many2one("hr.leave", string="Leave Id")
    leave_type_id = fields.Many2one("hr.leave.type")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approval'),
        ('validate1', 'Second Approval'),
        ('cancel', 'Cancelled'),
        ('refuse', 'Refuse'),
        ('validate', 'Approved'),
    ], string ="Status")

    def leave_cancel(self):
        if self.leave_id:
            self.leave_id.update({"state":"cancel"})
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Leave',
                "action_taken_by": me.id,
                "action_taken_on": self.leave_id.employee_id.id
            })
            self.unlink()


class exit_history_line(models.Model):
    _name = "exit_history_line"
    _description = 'Exit History Line'


      
    employee_id = fields.Many2one("hr.employee", string ="Employee")
    exit_type = fields.Selection([("Suspended", "Suspended"),
                                  ("Resigned", "Resigned"),
                                  ("technical resignation","Technical Resignation"),
                                  ("Contract Expired ", "Contract Expired "),
                                  ("Superannuation", "Superannuation"),
                                  ("Terminated","Terminated"),
                                  ("Deceased","Deceased"),
                                  ("Absconding","Absconding"),
                                  ("Transferred","Transferred"),
                                  ("deputation","Deputation")], string='Type of Exit')
    exit_date = fields.Date('Exit Date')

class EmployeeInherits(models.Model):
    _inherit='hr.employee'


    last_working_date = fields.Date('Last Working Date')
    exit_type = fields.Selection([("Suspended", "Suspended"),
                                  ("Resigned", "Resigned"),
                                  ("technical resignation internal","Technical Resignation(Internal)"),
                                  ("technical resignation external","Technical Resignation(External)"),
                                  ("Contract Expired ", "Contract Expired "),
                                  ("Superannuation", "Superannuation"),
                                  ("Terminated","Terminated"),
                                  ("Deceased","Deceased"),
                                  ("Absconding","Absconding"),
                                  ("Transferred","Transferred")], string='Type of Exit')

    exit_history = fields.One2many('exit_history_line','employee_id',string='Exit history')

    validate_exit = fields.Boolean("Validate Exit Details",compute='_compute_validate_exit_details',default=True)



    @api.multi
    def _compute_validate_exit_details(self):
        for record in self:
            if 'hide_personal' not in self._context and (self.env.user.has_group('hr.group_hr_manager') or record.user_id == self.env.user):
                record.validate_exit = True
            else:
                record.validate_exit = False
        
        
        
    
    

    



    

