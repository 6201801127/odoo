from odoo import api, fields, models

class TrainingWizard(models.TransientModel):

    _name = "training.wizard"
    _description = "training wizard"


    name = fields.Char("Name of The Training")
    no_qty = fields.Integer("Number of Training")
    price = fields.Float("price")

    
    def update_training(self):
        training_ids = []
        context = dict(self._context)
        empdetailsObj = self.env["employee.details"]
        print("Context...",context)
        employee_details = empdetailsObj.browse(context.get("active_id"))
        training_ids.append([0,0, {
            'name': self.name,
            'price': self.no_qty,
            'no_qty': self.price
        }])
        print('employee_details ==>', employee_details)
        print('training_ids ==>', training_ids)
        employee_details.write({'training_ids': training_ids})
        return True

