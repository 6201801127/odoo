from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class kw_approve_insurance(models.TransientModel):
    _name = 'kw_approve_insurance'
    _description = 'Approve Insurance'

    def _get_insurance_data(self):
        insurance_ids = self.env.context.get('selected_active_ids')
        res = self.env['health_insurance_dependant'].sudo().search(
            [('id', 'in', insurance_ids), ('state', 'in', ['draft', 'applied'])])
        return res

    insurance_ids = fields.Many2many('health_insurance_dependant', default=_get_insurance_data,
                                     string="Approve Insurance")


    def installment_changes(self,inst):
        if inst >= 6:
            return '6'
        elif(inst >= 4 and inst < 6):
            return '4'
        elif(inst >= 3 and inst < 4):
            return '3'
        elif(inst >= 1 and inst < 3):
            return '1'



    @api.multi
    def approve_insurance_record(self):
        current_fy_rec = self.insurance_ids.filtered(lambda x: date.today() >= x.date_range.date_start and  date.today() <= x.date_range.date_stop)
        for data in current_fy_rec:
            # print(data.date_diff(date.today()), "Difference is:")
            if datetime.now().day > 25:
                if int(data.no_of_installment) > data.date_diff(date.today()):
                    data.write({'no_of_installment': str(self.installment_changes(data.date_diff(date.today()))), 'state':'approved'})
                    data.get_insurance_emi_details()
                else:
                    data.state = 'approved'
                    data.get_insurance_emi_details()
            elif datetime.now().day <= 25:
                if int(data.no_of_installment) > data.date_diff(date.today())+1:
                    data.write({'no_of_installment': str(self.installment_changes(data.date_diff(date.today())+1)), 'state':'approved'})
                    data.get_insurance_emi_details()
                else:
                    data.state = 'approved'
                    data.get_insurance_emi_details()


        # month_dict_after25 = {1: 2, 2: 1, 3: 0, 4: 11, 5: 10, 6: 9, 7: 8, 8: 7, 9: 6, 10: 5, 11: 4, 12: 3}
        # month_dict_before25 = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
        # currentMonth = datetime.now().month
        # month_after25 = month_dict_after25.get(currentMonth)
        # month_before25 = month_dict_before25.get(currentMonth)
        # current_fy_rec = self.insurance_ids.filtered(lambda x:x.applied_on >= x.date_range.date_start and  x.applied_on <= x.date_range.date_stop)
        # for rec in current_fy_rec:
        #     print('@@@@@@@@@@@@@@@@@@@@@@@@@',datetime.now().day,rec.applied_on.month,datetime.now().month)
        #     if rec.applied_on.month !=  datetime.now().month:
        #         if  datetime.now().day > 25:
        #             if  int(rec.no_of_installment) > month_after25:
        #                 rec.write({'no_of_installment':month_after25,'state':'approved'})
        #                 rec.get_insurance_emi_details()
        #             else:
        #                 rec.state='approved'
        #                 rec.get_insurance_emi_details()
        #         else:
        #             if  int(rec.no_of_installment) > month_before25:
        #                 rec.write({'no_of_installment':month_before25,'state':'approved'})
        #                 rec.get_insurance_emi_details()
        #             else:
        #                 rec.state='approved'
        #                 rec.get_insurance_emi_details()
            # else:
            #     if datetime.now().day > 25:
            #         print(month_before25,'############')
            #         rec.write({'no_of_installment':month_before25,'state':'approved'})
            #         rec.get_insurance_emi_details()
            #     else:
            #         rec.state='approved'



# class UpdateInsurance(models.TransientModel):
#     _name = 'kw_update_insurance'
#     _description = 'Update Insurance'
#
#     def _get_insurance_data(self):
#         insurance_ids = self.env.context.get('selected_active_ids')
#         res = self.env['health_insurance_dependant'].sudo().search(
#             [('id', 'in', insurance_ids)])
#         return res
#
#     dependant_insurance_ids = fields.Many2many('health_insurance_dependant','update_insurance_rel','insurance_id','update_id', default=_get_insurance_data,
#                                      string="Update Insurance")
#
#
#     @api.multi
#     def update_insurance_record(self):
#         first_date = date(2022,7,1)
#         for rec in self.dependant_insurance_ids:
#             rec.emi_details_ids = [(5,)]
#             new_line = self.env['health_insurance_emi']
#             for emi, index in enumerate(range(int(rec.no_of_installment))):
#                 print('date.today()========',date.today())
#                 nextmonth = first_date + relativedelta.relativedelta(months=index)
#                 datetime_object = datetime.strptime(str(nextmonth.month), "%m")
#                 full_month_name = datetime_object.strftime("%B")
#                 rec.emi_details_ids = [(0, 0, {
#                                 'year': nextmonth.year,
#                                 'month': full_month_name,
#                                 'installment': rec.total_insurance_amount/int(rec.no_of_installment),
#                                 'status': 'paid' if nextmonth.month == 7 else 'unpaid',
#                                 'emi_date': nextmonth,
#                                 'emi_details_id':rec.id
#                             })]
#
#
       
           