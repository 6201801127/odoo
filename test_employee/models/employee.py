import string
from odoo import fields, models,api
import datetime
import dateutil.parser
from odoo.exceptions import ValidationError
from random import randint


class EmployeeDetails(models.Model):
    _name = "employee.details"
    _description = "Employe Details"
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'priority desc'

    def print_report(self):
        self.ensure_one()
        """stock.action_report_stock_rule"""
        return self.env.ref('test_employee.employee_form_view')#.report_action(None, data="data")
    def _get_default_color(self):
        return randint(1, 11)
    
    @api.onchange('date_of_birth')
    def onchange_dateofbirth(self):
        if self.date_of_birth:
            self.age = (date.today() - self.date_of_birth).days/365

    duration = fields.Float(
            'Real Duration', store=True)
    image = fields.Binary(string="Employee image")
    name = fields.Char("Name of The Employee",
                        required=True,
                        help="please create employee")
    expiration_date = fields.Datetime(string="Expiry Date", compute='_compute_expiration_date')
    phone_no = fields.Char('Phone No.')
    date_of_birth = fields.Date("Date of Birth")
    employee_sequence = fields.Char(string="Employee Sequence", default="New")                   
    age = fields.Char("Age of The Employee")
    salary = fields.Float("Employee salary" ,default=10000, readonly=True)
    joining_date = fields.Date("Enter Joining Date")
    office_starttime = fields.Datetime("Joining time")
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender")
    maritial_status = fields.Selection([('married', 'Married'),
                                            ('unmarried','Un married')],
                                            default = "unmarried",
                                            string="Maritial status")
    vaccinated  = fields.Boolean("Is vaccinated ?")
    note  = fields.Text("Remarks")
    blood_group_id = fields.Many2one('blood.group','Blood Group')
    color = fields.Integer(string='Color Index', default=_get_default_color)
    #relational fields
    #Many2one
    city_id = fields.Many2one(comodel_name="employee.city", string="City Name")
    city_code = fields.Char(string="City Code",related="city_id.code")
    city_ab = fields.Many2one(comodel_name="res.city", string="city name",readonly=True, states={'draft': [('readonly', False)]}) #for readonly when state is confirm
    code = fields.Char(string="City code",related="city_id.code", store=True)
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    state_id = fields.Many2one(comodel_name="employee.state", string="State")
    state_ab = fields.Many2one(comodel_name="res.country.state", string="State AB")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')], 
                             string="Status",           
                             default="draft")
    #relational fields
    #One2Many
    training_ids = fields.One2many(comodel_name='employee.training',
                                    inverse_name="employee_details_id",
                                    string='Training',readonly=True, states={'draft': [('readonly', False)]})

    #relational fields
    #Many2Many
    language_ids = fields.Many2many(comodel_name="employee.language",
                                    relation="employee_language_rel",
                                    column1="employee_details_id", #reference to current model
                                    column2="language_id")  #reference to comodel

    user_id = fields.Many2one("res.users", string="User", default=lambda self:self.env.user)
    grade = fields.Char(string="Grade")
    comments = fields.Html(string="Comments")
    payment_amount = fields.Monetary(string="Payment Amount")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id)
    email = fields.Char(string="Email")
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High'), ('3', 'Very High')], default='3',index=True,string ='Priority')
    partner = fields.Many2one(comodel_name='res.partner',string="Partner" )
    hr_employee = fields.Many2one(string='Hr Employee', comodel_name='hr.employee')

    @api.depends('create_date')
    def _compute_expiration_date(self):
        for rec in self:
            new_date = rec.create_date + datetime.timedelta(days=7)
            rec.expiration_date = new_date
    def send_email(self):
        user = self.env['res.users'].sudo().search([])
        manager = user.filtered(lambda user: user.has_group('test_employee.csm_manager_group') == True)
        users = self.env['res.users'].sudo().search([])
        usersss = users.filtered(lambda user: user.has_group('test_employee.csm_employee_group') == True)
        email_to = ','.join(manager.mapped('email'))
        email_to_user = ','.join(usersss.mapped('email'))
        print('sssssssssssssssssssssssssssss>>>>>>>>>>>',email_to_user)
        print('email>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',email_to)
        template=self.env.ref('test_employee.email_template_employee_details')
        # template = self.env['mail.template'].browse(template_id)
        # template.send_mail(self.id,)
        users1 = self.env.user.email
        print('users...............',users1)
        template.with_context(to_email=email_to).send_mail(self.id)
        template=self.env.ref('test_employee.email_template_employee_details1')
        template.with_context(email_from=users1,to_email=email_to,too_email=email_to_user).send_mail(self.id)

    
        
    
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         # result.append((record.id, "{} ({})".format(record.city_ab,record.state_ab)))
    #         result.append((record.id, '%s - %s' % (record.city_ab,record.state_ab)))
    #         print("result......",result)
    #     return result    
    # @api.onchange('city_ab')
    # def onchange_city(self):
    #     if self.state_ab == 'jharkhand':
    #         self.city_ab = self.city_ab.append('jh')
        
    #         # self.grade = self.city_id.code


    #create, write, unlink, search, copy, browse and so on
    @api.model
    def create(self, values):
        print("value in create...",values)
        if values.get("name"):
             values.update({"name":values.get("name") + "CSM" + values.get('maritial_status')})


        if values.get("employee_sequence") == 'New':
            values['employee_sequence']= self.env['ir.sequence'].next_by_code('employee.details')

    # return super(EmployeeDetails, self).create(values)
        result= super(EmployeeDetails, self).create(values)
        print("result...",result)
        return result
    
    
    def copy(self):
        print("called in copy")
        return super(EmployeeDetails, self).copy()
    def custom_duplicate(self):
        record = self.copy()
        print("Record...",record)
        return True

    def write(self, values):
        print("value in write...",self,values)
        if values.get("maritial_status") == 'married':
            raise ValidationError("Invalid selection")
        return super(EmployeeDetails,self).write(values)


    def unlink(self, values):
        print("value in unlink...",values)
        if values.get("maritial_status") == 'unmarried':
            raise ValidationError("Invalid selection")
        return super(EmployeeDetails, self).unlink()

    def update_lines(self):
        for case in self:
            for line in case.training_ids:
                line.no_qty = 3
    
    def update_status(self):
        # return True
        # return {
        #     'name': 'Employee Details',
        #     'domain': [],
        #     'res_model': 'employee.details',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'context': {},
        #     'target': 'new',
        #     'res_id': self.id,            
        #     'flags': {'form': {'action_buttons': False},} 
        # }
        employees = self.search([])
        employee_dt = self.env['employee.details'].search([('name','=', 'samar kumarCSMunmarried')])
        print('employee_dt----->', employee_dt)
        print("employees......====>", employees)
        employees_count = self.search_count([])
        emp_count = self.env['employee.training'].search([('name', '=', 'odoo')])
        emp_counts = self.env['employee.training'].search_count([('name', '=', 'odoo')])
        emp_mapped = self.env['employee.training'].mapped('name')
        print("values,,,....====>", employees_count)
        print("emp_count,,,....====>", emp_count)
        print("emp_counts,,,....====>", emp_counts)
        print("emp_mapped,,,....====>", emp_mapped)
        brows = self.env['employee.training'].browse(['name'])
        print("brows,,,....====>", brows)

        query = ('SELECT * FROM res_partner')
        self.env.cr.execute(query)
        ree = self.env.cr.fetchall()
        print('record>>>>>>>>>>>>>>>>',ree)
       
        # create_emp = self.env['employee.details'].create({
        #     'name':'ajay'
        # })
        # print('create_emp=======>',create_emp)


        # if employees_count<50:
        #     raise ValidationError("Less Number of Records")
        male_employees = employees.filtered(lambda l: l.gender == 'male')
        print("mapped example", male_employees, male_employees.mapped('name'))
        print("Sorted example", male_employees.sorted(lambda x: x.name))
        female_employees = employees.filtered(lambda x: x.gender == 'female')
        print("values of male and female,,,", male_employees, female_employees)
        self.write({"state": 'confirm'})
        return True

    def update_draft_from_cron(self):
        print("ABC...............")
        employees = self.search[('state','=','draft')]
        employees.write({'state':'confirm'})
    
    def create_payslip(self):
        # return True
        # return {
        #     'name': 'Employee Payslip',
        #     'domain': [],
        #     'res_model': 'employee.payslip',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'context': {},
        #     'target': 'new',
        #     'res_id': self.id,            
        #     'flags': {'form': {'action_buttons': False},} 
        # }
        payslipObj = self.env["employee.payslip"]
        for case in self:
            payslip_vals = {
                "name": case.name,
                "age": case.age,
                "payment_amount": case.payment_amount
            }
            payslip = payslipObj.create(payslip_vals)
            print("Payslip...", payslip)
        

    def create_twitter(self):
        print("abc")
    
    def create_calendar(self):
        print("abc")

    #whatsapp integration in odoo14
    def action_share_whatsapp(self):
        msg ="Hi %s" %self.name
        whatsapp_api_url ='https://web.whatsapp.com/send?phone_no=%s&text=%s' % (self.phone_no, msg)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }


    # def remove_link(self):
    #     line_id = self.trainig_ids[-1].id
    #     self.write({
    #         'training_ids': [(3, line_id)]  #unlink one single record
    #     })

    # def update_link(self):
    #     line_id = self.trainig_ids.search([('employee_details_id','=', False)], limit=1)
    #     self.write({
    #         'training_ids': [(4, line_id.id)] 
    #     })

    # def unlink_all(self):
    #     self.write({
    #         'training_ids': [(5)]  #unlink for all record
    #     })
    # def create_newline(self):
    #     self.write({
    #         'training_ids': [(0,0, {
    #             'name': "Sample Line",
    #             'price': 500,
    #             'no_qty': 1.0
    #         })] 
    #     })
    #     return {
    #         'name': 'Employee Training',
    #         # 'domain': [],
    #         'res_model': 'employee.training',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         # 'context': {},
    #         'target': 'new',
    #     }
    # def create_newline(self):
    #     return {
    #         'name': 'Employee Training',
    #         'domain': [],
    #         'res_model': 'employee.training',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'context': {},
    #         'target': 'new',
    #         'res_id': self.id,            
    #         'flags': {'form': {'action_buttons': False},} 
    #     }
    # def update_line(self):
    #     line_id = self.training_ids[-1].id
    #     self.write({
    #         'training_ids': [(1,line_id, {
    #             'name': "Sample Line",
    #             'price': 500,
    #             'no_qty': 2.0
    #         })] 
    #     })
    #test_employee.email_template_employee_details


