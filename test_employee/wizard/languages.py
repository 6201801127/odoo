from odoo import api, fields, models

class LanguageWizard(models.TransientModel):

    _name = "language.wizard"
    _description = " language wizard"
    @api.model
    def default_get(self, fields):
        result = super(LanguageWizard, self).default_get('fields')
        print('..............', self._context)
        result['language_ids'] = self._context.get('active_id')

    # @api.onchange('language_ids')
    # def onchange_language_ids(self):
    #     if self.language_ids:
    #         self.language_ids = self._context.get('active_id')

    payment_amount = fields.Float("Payment Amount")
    language_ids = fields.Many2many(comodel_name="employee.language",
                                    relation="wizard_language_rel",
                                    column1="lang_wiz_id",
                                    column2="language_id")
    def update_languages(self):
        context = dict(self._context)
        empObj = self.env["employee.details"]
        userObj = self.env["res.users"]
        print("Context...",context)
        emp_details = empObj.browse(context.get("active_id"))
        user = userObj.browse(context.get("uid"))
        print("Name..",user.name)
        print("records, ", emp_details, context.get("activate_id"))
        print("Values in self", self.payment_amount, self.language_ids, emp_details.name)
        emp_details.payment_amount = self.payment_amount
        emp_details.language_ids = self.language_ids