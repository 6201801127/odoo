from openerp import models, fields, api, exceptions, _
import xml.etree.ElementTree as xee

class RegisterReport(models.TransientModel):
    _name = 'contribution.register.report'
    _description = "Contribution Register Report"
    
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    pay_from_date = fields.Date(string="Payslip From Date")
    pay_to_date = fields.Date(string="Payslip To Date")
    dep_id = fields.Many2one('hr.department',string="Department")
    manager_id = fields.Many2one('hr.employee',string="Manager")
    contib_regi = fields.Many2one('hr.contribution.register',string="Contribution Register")
    job_position = fields.Many2one('hr.job',string="Job Position")
    contract_id = fields.Many2one('hr.contract',string="Contract")
    wage = fields.Float(string="Wage")
    amt = fields.Float(string="Amount")
    rate = fields.Float(string="Rate")
    total = fields.Float(string="Total")
    payslip_name = fields.Char(string="Payslip Name")
    payslip_id = fields.Many2one('hr.payslip',invisible=True)
    branch_id = fields.Many2one('res.branch',string="Branch")
    state = fields.Selection([('draft','Draft'),
                              ('verify','Waiting'),
                              ('done','Done'),
                              ('cancel','Rejected')
                            ],string="state")
    register_info = fields.Text(string="Register Info")
    register_name = fields.Text(string=" ")
    model_id = fields.Integer(string="ID",default=lambda self: self.env['ir.model'].search([('model','=','hr.employee')]).id)
    
#     def get_dynamic_fields(self):
#         
#         for s in self:
#             con_reg_id = self.env['hr.contribution.register'].search([('id','=',s.contib_regi.id)])
#             print("22222222222222222222222222222",con_reg_id)
# #             for contri_id in con_reg_id:
# #                 print("@@@2222222222222222222",contri_id)
#             fields = ' '
#             for ir_fields in s.contib_regi.ir_model_fields:
#                 print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!",ir_fields)
#                 if con_reg_id == s.contib_regi:
#                     print("$$$$$$$$$$$$$$$$$$")
#                     fields += ir_fields.field_description + '\n'
#                     s.register_info = fields
#                     print("?????????????????????????",s.register_info)
#                     
#             ir_model_fields = self.env['ir.model.fields'].search([('model_id','=',s.model_id),('state','=','manual')])
#             for field in ir_model_fields:
#                 print("::::::::::::::::::::::::",field)
#                 employee_id = self.env['hr.employee']._fields
# #                 print("employee_idemployee_idemployee_idemployee_id",employee_id)
#                 r = ''
#                 for employee in employee_id:
#                     print("LLLLLLLLLLLLLLLLLLLLLL",employee == field.name)
#                     if employee == field.name:
#                         print("++++++++++++++++++++++",field.name,'!=',False)
#                         employee_id = self.env['hr.employee'].search([(field.name,'!=',False)])
#                         for emp in employee_id:
#                             r += employee + '\n'
#                             s.register_name = r
#                             print("register_nameregister_nameregister_name",employee,emp)
#                         
    
    @api.one
    def get_employee_pf_no(self):
        for s in self:
            for employee in s.employee_id.line_ids:
                pf_no = employee.pf
    
    @api.one
    def get_employee_total_days(self):
        for s in self:
            days = ''
            for payslip in s.payslip_id:
                days = payslip.lwp_att
    
    
class HRContributionRegister(models.Model):
    _inherit = 'hr.contribution.register'
    _description = 'HR Contribution Register'
    
    model_id = fields.Integer(string="ID",default=lambda self: self.env['ir.model'].search([('model','=','hr.employee')]).id)
    ir_model_fields = fields.One2many('ir.model.fields','hr_cont_reg_id',string="IR Model")
    
    
    
class IRModelFields(models.Model):
    _inherit = 'ir.model.fields'
    _description = 'IR Model Fields Register'
    
    @api.multi
    def set_domain(self):
        view_id = self.env.ref('hr.view_employee_form')
        data1 = str(view_id.arch_base)
        doc = xee.fromstring(data1)
        field_list = []
        for tag in doc.findall('.//field'):
            field_list.append(tag.attrib['name'])
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'hr.employee')])
        return [('model_id', '=', model_id.id), ('state', '=', 'base'), ('name', 'in', field_list)]
     
 
    hr_cont_reg_id = fields.Many2one('hr.contribution.register',string="Register")
    name = fields.Char(string='Field Name', default='x_', required=True, index=True)
    position_field = fields.Many2one('ir.model.fields', string='Field Name',
                                     domain=set_domain)
#     position_field1 = fields.Many2one('ir.model.fields', string='Field Name',
#                                      domain=set_domain1, required=True)
    ref_model_id = fields.Many2one('ir.model', string='Model', index=True)
    position = fields.Selection([('before', 'Before'),
                                 ('after', 'After')], string='Position')
    
    
    
    @api.model
    def create(self, vals):
        res = super(IRModelFields,self).create(vals)
#         print("===========workinggggggg=======>>>>.",res.model_id,res.name,res.position_field,res.position)
    
#         print("11111111111111111111")
        if self.name or res.name:
            inherit_id = self.env.ref('hr.view_employee_form')
            inherit_id_con = self.env.ref('hr_contract.hr_contract_view_form')
            name = self.name or res.name
            arch_base = _('<?xml version="1.0"?>'
                          '<data>'
                          '<field name="%s" position="%s">'
                          '<field name="%s"/>'
                          '</field>'
                          '</data>') % (res.position_field.name, res.position, name)
            print("arch_basearch_basearch_basearch_base",arch_base)
            if res.model_id.model ==  'hr.employee':
    #             name = self.model_id.model + 'dynamic.fields'
                d = {'name': 'hr.employee.dynamic.fields',
                      'type': 'form',
                      'model': 'hr.employee',
                      'mode': 'extension',
                      'inherit_id': inherit_id.id,
                      'arch_base': arch_base,
                      'active': True}
#                 print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",d)
            elif res.model_id.model == 'hr.contract':
    #
                d = {'name': 'hr.contract.dynamic.fields',
                                                'type': 'form',
                                                'model': 'hr.contract',
                                                'mode': 'extension',
                                                'inherit_id': inherit_id_con.id,
                                                'arch_base': arch_base,
                                                'active': True}
    #             print"??????????????????????????????????????????/",d
            self.env['ir.ui.view'].sudo().create(d)
    #         
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
        
        return res 