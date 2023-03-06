from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    _descpription = " Sale Inherit"


    @api.model
    def default_get(self, fields):
        tempObj = self.env['sale.order.template']
        result = super(SaleOrder, self).default_get(fields)
        result['po_reference'] = str(self.date_order) + "Reference"
        result['validity_date'] = result['date_order']
        template_id = tempObj.search([('name','=','4 person')], limit=1)
        if template_id :
            result["sale_order_template_id"] = template_id.id   
        return result

    @api.model
    def get_default_reference(self):
        cityObj = self.env['employee.city']
        city_id = cityObj.search(['city_name','=','Banglore'], limit=1)

        return city_id and city_id.code + "Reference" or "Reference"


    po_reference = fields.Char(string="Po Reference1")
    date_order = fields.Datetime(string="Sale Order Date")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')], 
                             string="Status",
                             default="draft")   


 