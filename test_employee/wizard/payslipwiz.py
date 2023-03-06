from odoo import api, fields, models

class CreatePayslip(models.TransientModel):

    _name = "payslip.wizard"
    _description = "payslip wizard"

    @api.model
    def default_get(self, fields):
        result = super(CreatePayslip, self).default_get('fields')
        print('..............',self._context)
        result['name'] = self._context.get('active_id')
        result['age'] = self._context.get('active_id')
        result['currency_id'] = self._context.get('active_id')
        return result

    name = fields.Many2one('employee.details', "Name of The Employee")
    age = fields.Integer("Age of The Employee")
    payment_amount = fields.Monetary("Payment Amount")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id)
    
    def create_payslip(self):
        context = dict(self._context)
        print('self Context>>>>>>>>>>>>>>>>>>>>>',context)
        empObj = self.env["employee.details"]
        userObj = self.env["res.users"]
        print("Context>>>>>>>>>>>>>>>>>",context)
        emp_details = empObj.browse(context.get("active_id"))
        print('current id>>>>>>>>>>>>>>>>>>>>>>>>>>',emp_details)
        user = userObj.browse(context.get("uid"))
        print("Name..",user.name)
        print("records, ", emp_details, context.get("activate_id"))
        print("Values in self",self.name, self.age, self.payment_amount, self.currency_id, emp_details.name)
        emp_details.name = self.name
        emp_details.age = self.age
        emp_details.payment_amount = self.payment_amount
        emp_details.currency_id = self.currency_id