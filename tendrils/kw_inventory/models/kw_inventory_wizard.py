from datetime import date
from odoo import api, models, fields
# from odoo.exceptions import UserError
# from odoo import exceptions, _


class kw_inventory_wizard(models.TransientModel):
    _name = 'kw_inventory_wizard'
    _description = 'Inventory wizard'

    def _get_default_confirm(self):
        datas = self.env['kw_add_product'].browse(self.env.context.get('active_ids'))
        return datas

    @api.model
    def default_get(self, fields):
        res = super(kw_inventory_wizard, self).default_get(fields)
        # print("default get called", self._context)
        cons_records = self.env['kw_add_product'].browse(self._context.get('active_ids', []))
        message = ""
        message_new = "Indent will be created for Items : " + "\n"
        message_present_title = "Indent is already created for Items  : " + "\n"
        message_present = ""
        for record in cons_records:
            indent_rec = self.env['kw_add_product_consolidation'].sudo().search([('add_product_id', '=', record.id)])
            if indent_rec:
                for rec in indent_rec:
                    message_present += "Item Code - " + str(
                        rec.item_code.default_code) + " Created for Indent Number - " + str(
                        rec.indent_rel.indent_number) + "\n"
            else:
                message += "Item Code - " + str(record.item_code.default_code) + " with Item Quantity - " + str(
                    record.quantity_required) + "\n"

        # print(message_present)
        # print(message)

        if len(message) > 0 and len(message_present) == 0:
            res['message'] = message_new + message
        if len(message_present) > 0 and len(message) == 0:
            res['message'] = message_present_title + message_present
            res['button_hide'] = True
        if len(message_present) > 0 and len(message) > 0:
            res['message'] = message_present_title + message_present + message_new + message

        return res

    inventory = fields.Many2many('kw_add_product', readonly=1, default=_get_default_confirm)
    message = fields.Text(string="Message")
    button_hide = fields.Boolean(string='Button Hide', default=False)

    confirm_message = fields.Char(string="Confirm Message", default="Are you sure you want to Create Indent ?")

    @api.multi
    def button_indent(self):
        dept = []
        indt_dept = []
        prj_code = []
        for product_rec in self.inventory:
            # print("Record id====", product_rec)
            for pr_rec in product_rec.pr_rel:
                # print("Purchase Req ======", pr_rec.department_name)
                # print("PRJ CODE FOUND=====", pr_rec.project_code)
                if pr_rec.project_code:
                    prj_code.append(pr_rec.project_code)
                if pr_rec.department_name.id not in dept:
                    dept.append(pr_rec.department_name.id)
                if pr_rec.indenting_department.id not in indt_dept:
                    indt_dept.append(pr_rec.indenting_department.id)
        project_code = ','.join(prj_code)
        # print("Project code=====", project_code)
        # print("Prj list===", prj_code)

        vals = {}
        product_id = []
        val = []
        values = []
        # for record in self.inventory:
        indent_rec = lambda rec: self.env['kw_add_product_consolidation'].sudo().search(
            [('add_product_id', '=', rec.id)])
        r = self.inventory.filtered(lambda record: not len(indent_rec(record)) > 0)

        for record in r:
            if record.item_code.id in vals:
                vals[record.item_code.id][1] += record.quantity_required
                vals[record.item_code.id][3].append(record.id)
            else:
                vals[record.item_code.id] = [record.item_description, record.quantity_required, record.status,
                                             [record.id]]
            for rec in record.pr_rel:
                if rec.id not in val:
                    val.append(rec.id)

        for r in vals:
            values.append([0, 0, {
                "item_code": r,
                "item_description": vals[r][0],
                "quantity_required": vals[r][1],
                "status": vals[r][2],
                "add_product_id": [[6, False, vals[r][3]]],
            }])
        # print(values)

        Indent_Consolidation = self.env['kw_consolidation']
        cdate = date.today()
        record = Indent_Consolidation.create({
            "department": [[6, False, dept]],
            "indenting_department": [[6, False, indt_dept]],
            "project_code": project_code,
            "date": cdate,
            "state": "Indent",
            "requisition_rel": [[6, False, val]],
            "add_product_consolidation_rel": values,
            "create_check": True
        })
        # record.indent_number = f"INDNT{record.id}"
        self.env['kw_add_product'].show_indent()
        self.env.user.notify_success("Indent Record created Successfully")
