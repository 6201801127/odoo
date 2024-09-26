from odoo import api, fields, models, _
import sys
sys.setrecursionlimit(10**6)


class Project(models.Model):
    _inherit = 'project.project'

    stakeholder_ids = fields.One2many('stakeholder.lines', 'project_task_id', 'Stakeholder Lines')

    @api.model
    def create(self, vals):
        rec = super(Project, self).create(vals)
        user_obj = self.env['res.users']
        stakeholder_list, partner_list = [], []
        if rec['stakeholder_ids']:
            for stakeholder in rec['stakeholder_ids']:
                if stakeholder.status is True:
                    stakeholder_list.append(stakeholder.partner_id.id)
                    partner_list.append(stakeholder.partner_id.id)
            if stakeholder_list:
                new_list = []
                for partner in stakeholder_list:
                    if partner not in rec.message_follower_ids.mapped('partner_id').ids:
                        new_list.append(partner)
                rec.message_subscribe(partner_ids=new_list)
                for partner in new_list:
                    user = self.env['res.users'].search([('partner_id', '=', partner)])
                    if user:
                        # Email notification
                        rec.message_post(partner_ids=[partner],
                                         body="Dear " + str(user.name) + " you have been added to " + str(rec.name) +
                                              " by " + str(self.env.user.name),
                                         message_type='email', email_from=rec.outgoing_email)
                        # Chat Notification
                        notification_ids = [((0, 0, {
                            'res_partner_id': partner,
                            'notification_type': 'inbox'}))]
                        rec.message_post(body="Dear " + str(user.name) + " you have been added to " + str(rec.name) +
                                              " by " + str(self.env.user.name), message_type='notification',
                                         subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
                                         notification_ids=notification_ids, notify_by_email=False)
        if rec['allowed_internal_user_ids']:
            for users in rec['allowed_internal_user_ids']:
                partner_list.append(users.partner_id.id)
        if rec['allowed_portal_user_ids']:
            for users in rec['allowed_portal_user_ids']:
                partner_list.append(users.partner_id.id)
        if rec['program_manager_id']:
            partner_list.append(rec['program_manager_id'].partner_id.id)
            if rec['program_manager_id'] and rec['program_manager_id'].partner_id.id:
                rec.message_subscribe(partner_ids=[rec['program_manager_id'].partner_id.id])
                # Email Notification
                rec.message_post(partner_ids=[rec['program_manager_id'].partner_id.id],
                                 body="Dear " + str(rec['program_manager_id'].partner_id.name) +
                                      " you have been assigned as " +
                                      "Program Manager for the following project " + str(rec.name),
                                 message_type='email', email_from=rec.outgoing_email)
                # Chat Notification
                notification_ids = [((0, 0, {
                    'res_partner_id': rec['program_manager_id'].partner_id.id,
                    'notification_type': 'inbox'}))]
                rec.message_post(body="Dear " + str(rec['program_manager_id'].partner_id.name) +
                                      " you have been assigned as " +
                                      "Program Manager for the following project " + str(rec.name),
                                 message_type='notification', subtype_xmlid='mail.mt_comment',
                                 author_id=self.env.user.partner_id.id, notification_ids=notification_ids,
                                 notify_by_email=False)
        if rec['user_id']:
            partner_list.append(rec['user_id'].partner_id.id)
            if rec['user_id'] and rec['user_id'].partner_id.id:
                rec.message_subscribe(partner_ids=[rec['user_id'].partner_id.id])
                # Email Notification
                rec.message_post(partner_ids=[rec['user_id'].partner_id.id],
                                 body="Dear " + str(rec['user_id'].partner_id.name) +
                                      " you have been assigned as " +
                                      "Project Manager for the following project " + str(rec.name),
                                 message_type='email', email_from=rec.outgoing_email)
                # Chat Notification
                notification_ids = [((0, 0, {
                    'res_partner_id': rec['user_id'].partner_id.id,
                    'notification_type': 'inbox'}))]
                rec.message_post(body="Dear " + str(rec['user_id'].partner_id.name) +
                                      " you have been assigned as " +
                                      "Project Manager for the following project " + str(rec.name),
                                 message_type='notification', subtype_xmlid='mail.mt_comment',
                                 author_id=self.env.user.partner_id.id, notification_ids=notification_ids,
                                 notify_by_email=False)
        if partner_list:
            new_list = list(set(partner_list))
            rec.message_subscribe(partner_ids=new_list)
        return rec

    def write(self, vals):
        user_obj = self.env['res.users']
        stakeholder_list = []
        if 'stakeholder_ids' in vals:
            for stakeholder in vals.get('stakeholder_ids'):
                if stakeholder[2] != False:
                    if stakeholder[0] == 0 and stakeholder[2].get('status') == True:
                        stakeholder_list.append(stakeholder[2].get('partner_id'))
                    if stakeholder[0] != 0 and stakeholder[2].get('status') == False:
                        for lines in self.stakeholder_ids:
                            if lines.id == stakeholder[1]:
                                self.message_unsubscribe(partner_ids=[lines.partner_id.id])
                    if stakeholder[0] != 0 and stakeholder[2].get('status') == True:
                        for lines in self.stakeholder_ids:
                            if lines.id == stakeholder[1]:
                                stakeholder_list.append(lines.partner_id.id)
            if stakeholder_list:
                new_list = []
                for partner in stakeholder_list:
                    if partner not in self.message_follower_ids.mapped('partner_id').ids:
                        new_list.append(partner)
                self.message_subscribe(partner_ids=new_list)
                for partner in new_list:
                    user = self.env['res.users'].search([('partner_id', '=', partner)])
                    if user:
                        # Email notification
                        self.message_post(partner_ids=[partner],
                                          body="Dear " + str(user.name) + " you have been added to " + str(self.name) +
                                               " by " + str(self.env.user.name),
                                          message_type='email', email_from=self.outgoing_email)
                        # Chat Notification
                        notification_ids = [((0, 0, {
                            'res_partner_id': partner,
                            'notification_type': 'inbox'}))]
                        self.message_post(body="Dear " + str(user.name) + " you have been added to " + str(self.name) +
                                               " by " + str(self.env.user.name), message_type='notification',
                                          subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids, notify_by_email=False)
        if 'program_manager_id' in vals:
            users = user_obj.search([('id', '=', vals.get('program_manager_id'))], limit=1)
            if users and users.partner_id:
                self.message_subscribe(partner_ids=[users.partner_id.id])
                # Email Notification
                self.message_post(partner_ids=[users.partner_id.id],
                                  body="Dear " + str(users.partner_id.name) + " you have been assigned as " +
                                  "Program Manager for the following project " + str(self.name),
                                  message_type='email', email_from=self.outgoing_email)
                # Chat Notification
                notification_ids = [((0, 0, {
                    'res_partner_id': users.partner_id.id,
                    'notification_type': 'inbox'}))]
                self.message_post(body="Dear " + str(users.partner_id.name) + " you have been assigned as " +
                                  "Program Manager for the following project " + str(self.name),
                                  message_type='notification', subtype_xmlid='mail.mt_comment',
                                  author_id=self.env.user.partner_id.id, notification_ids=notification_ids,
                                  notify_by_email=False)
        if 'user_id' in vals:
            users = user_obj.search([('id', '=', vals.get('user_id'))], limit=1)
            if users and users.partner_id:
                self.message_subscribe(partner_ids=[users.partner_id.id])
                # Email Notification
                self.message_post(partner_ids=[users.partner_id.id],
                                  body="Dear " + str(users.partner_id.name) + " you have been assigned as " +
                                       "Project Manager for the following project " + str(self.name),
                                  message_type='email', email_from=self.outgoing_email)
                # Chat Notification
                notification_ids = [((0, 0, {
                    'res_partner_id': users.partner_id.id,
                    'notification_type': 'inbox'}))]
                self.message_post(body="Dear " + str(users.partner_id.name) + " you have been assigned as " +
                                       "Project Manager for the following project " + str(self.name),
                                  message_type='notification', subtype_xmlid='mail.mt_comment',
                                  author_id=self.env.user.partner_id.id, notification_ids=notification_ids,
                                  notify_by_email=False)
        return super(Project, self).write(vals)


class StakeholderLines(models.Model):
    _name = 'stakeholder.lines'

    project_task_id = fields.Many2one('project.project', 'Project Task')
    partner_id = fields.Many2one('res.partner', 'Name', required=True)
    role_id = fields.Many2one('project.role', 'Role', required=True)
    department_id = fields.Many2one('hr.department', 'Department', required=True)
    role_in_project = fields.Many2one('project.role', 'Role in Project', required=True)
    type_of_stakeholder = fields.Many2one('project.stakeholder', 'Type of Stakeholder', required=True)
    type_of_communication = fields.Many2one('project.communication', 'Type of Communication', required=True)
    expectations = fields.Text('Expectations')
    status = fields.Boolean('Status', default=True)
    partners_ids = fields.Many2many('res.partner', 'Partners', compute='_compute_partners')
    
    @api.depends('type_of_stakeholder')
    def _compute_partners(self):
        users_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        for record in self:
            partner_list = []
            if record.type_of_stakeholder.name == 'Internal':
                users = users_obj.search([('groups_id', 'in', self.env.ref('base.group_user').id)])
                if users:
                    for user in users:
                        employee = employee_obj.search([('user_id', '=', user.id)])
                        if employee:
                            partner_list.append(user.partner_id.id)
            if record.type_of_stakeholder.name == 'External':
                users = users_obj.search([('groups_id', 'in', [self.env.ref('base.group_portal').id, self.env.ref('base.group_public').id, self.env.ref('base.group_user').id])])
                if users:
                    for user in users:
                        employee = employee_obj.search([('user_id', '=', user.id)])
                        if not employee:
                            partner_list.append(user.partner_id.id)
            record.partners_ids = [(6, 0, [partner for partner in partner_list])]

    def write(self, vals):
        prev_stakeholder_type = self.type_of_stakeholder.name
        prev_user = self.partner_id.name
        prev_role = self.role_id.name
        prev_department = self.department_id.name
        prev_role_in_project = self.role_in_project.name
        prev_communication = self.type_of_communication.name
        prev_expectations = self.expectations or ''
        prev_status = self.status
        rec = super(StakeholderLines, self).write(vals)
        message_body = """<b>Stakeholders</b><br/>"""
        if prev_stakeholder_type == self.type_of_stakeholder.name:
            message_body += """• Type of Stakeholder: {prev_stakeholder_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_stakeholder} <br/>""".format(
                prev_stakeholder_type=prev_stakeholder_type, type_of_stakeholder=self.type_of_stakeholder.name
            )
        else:
            message_body += """<span style='color:red;'>• Type of Stakeholder: {prev_stakeholder_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_stakeholder}</span><br/>""".format(
                prev_stakeholder_type=prev_stakeholder_type, type_of_stakeholder=self.type_of_stakeholder.name
            )
        if prev_user == self.partner_id.name:
            message_body += """• User Name: {prev_user} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {user_name}<br/>""".format(
                prev_user=prev_user, user_name=self.partner_id.name
            )
        else:
            message_body += """<span style='color:red;'>• User Name: {prev_user} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {user_name}</span><br/>""".format(
                prev_user=prev_user, user_name=self.partner_id.name
            )
        if prev_role == self.role_id.name:
            message_body += """• Role: {prev_role} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role}<br/>""".format(
                prev_role=prev_role, role=self.role_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Role: {prev_role} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role}</span><br/>""".format(
                prev_role=prev_role, role=self.role_id.name
            )
        if prev_department == self.department_id.name:
            message_body += """• Department: {prev_department} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {department}<br/>""".format(
                prev_department=prev_department, department=self.department_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Department: {prev_department} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {department}</span><br/>""".format(
                prev_department=prev_department, department=self.department_id.name
            )
        if prev_role_in_project == self.role_in_project.name:
            message_body += """• Role in Project: {prev_role_in_project} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role_of_project}<br/>""".format(
                prev_role_in_project=prev_role_in_project, role_of_project=self.role_in_project.name
            )
        else:
            message_body += """<span style='color:red;'>• Role in Project: {prev_role_in_project} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role_of_project}</span><br/>""".format(
                prev_role_in_project=prev_role_in_project, role_of_project=self.role_in_project.name
            )
        if prev_communication == self.type_of_communication.name:
            message_body += """• Type of Communication: {prev_communication} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_communication}<br/>""".format(
                prev_communication=prev_communication, type_of_communication=self.type_of_communication.name
            )
        else:
            message_body += """<span style='color:red;'>• Type of Communication: {prev_communication} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_communication}</span><br/>""".format(
                prev_communication=prev_communication, type_of_communication=self.type_of_communication.name
            )
        print('++++++++', prev_expectations, '----', self.expectations)
        if prev_expectations == '' and self.expectations is False:
            message_body += """• Expectations: {prev_expectations} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {expectations}<br/>""".format(
                prev_expectations=prev_expectations, expectations=self.expectations or ''
            )
        else:
            message_body += """<span style='color:red;'>• Expectations: {prev_expectations} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {expectations}</span><br/>""".format(
                prev_expectations=prev_expectations, expectations=self.expectations or ''
            )
        if prev_status == self.status:
            message_body += """• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}""".format(
                prev_status=prev_status, status=self.status
            )
        else:
            message_body += """<span style='color:red;'>• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}</span>""".format(
                prev_status=prev_status, status=self.status
            )
        # message_body = """<b>Stakeholders</b><br/>
        #                 • Type of Stakeholder: {prev_stakeholder_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_stakeholder} <br/>
        #                 • User Name: {prev_user} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {user_name}<br/>
        #                 • Role: {prev_role} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role}<br/>
        #                 • Department: {prev_department} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {department}<br/>
        #                 • Role in Project: {prev_role_in_project} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {role_of_project}<br/>
        #                 • Type of Communication: {prev_communication} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type_of_communication}<br/>
        #                 • Expectations: {prev_expectations} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {expectations}<br/>
        #                 • Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}"""\
        #     .format(prev_stakeholder_type=prev_stakeholder_type, type_of_stakeholder=self.type_of_stakeholder.name,
        #             prev_user=prev_user, user_name=self.partner_id.name, prev_role=prev_role, role=self.role_id.name,
        #             prev_department=prev_department, department=self.department_id.name,
        #             prev_role_in_project=prev_role_in_project, role_of_project=self.role_in_project.name,
        #             prev_communication=prev_communication, type_of_communication=self.type_of_communication.name,
        #             prev_expectations=prev_expectations, expectations=self.expectations or '',
        #             prev_status=prev_status, status=self.status)
        self.project_task_id.message_post(body=message_body)
        return rec


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stakeholder_employee_ids = fields.Many2many('hr.employee', 'Stakeholders', compute='_compute_get_stakeholders')

    @api.depends('project_id', 'project_id.stakeholder_ids', 'project_id.stakeholder_ids.status',
                 'project_id.stakeholder_ids.partner_id')
    def _compute_get_stakeholders(self):
        users_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        stakeholder_employee_list = []
        if self.project_id and self.project_id.stakeholder_ids:
            for lines in self.project_id.stakeholder_ids:
                if lines.status is True:
                    user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                    if user:
                        employee = employee_obj.search([('user_id', '=', user.id)], limit=1)
                        if employee:
                            stakeholder_employee_list.append(employee.id)
        self.stakeholder_employee_ids = [(6, 0, [id for id in stakeholder_employee_list])]


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    employee_id = fields.Many2one('hr.employee', "Employee")
