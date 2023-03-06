from odoo import api, fields, models

class EmployeeTraining(models.Model):
    _name = 'employee.training'
    _rec_name = 'name'
    _description = 'Employee Training Model'

    @api.depends('no_qty','price')
    def get_total(self):
        for case in self:
            case.total_amount = case.no_qty * case.price
   
    


    name = fields.Char(string="Name of Training")
    no_qty = fields.Integer(string="Number of Training")
    price = fields.Float(string="Price")
    total_amount = fields.Float(string="Total Amount", compute="get_total")
    employee_details_id = fields.Many2one(comodel_name='employee.details',string="emp details")
    
    @api.model
    def update_status(self):
        training = self.search([])
        training_count = self.search_count([])
        print("values,,,",training_count)
        # if employees_count<50:
        #     raise ValidationError("Less Number of Records")
        # male_employees = employees.filtered(lambda l: l.gender == 'male')
        # print("mapped example", male_employees,male_employees.mapped('name'))
        # print("Sorted example",male_employees.sorted(lambda x:x.name))
        # female_employees = employees.filtered(lambda x: x.gender == 'female')
        # print("values of male and female,,,", male_employees, female_employees)
        self.write({"state":'confirm'})
        return True