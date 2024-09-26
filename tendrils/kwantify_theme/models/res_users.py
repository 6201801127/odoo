import datetime,calendar
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    sidebar_visible = fields.Boolean("Show App Sidebar", default=True)
    chatter_position = fields.Selection([('normal', 'Normal'), ('sided', 'Sided'), ], string="Chatter Position",
                                        default='normal')

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sidebar_visible'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sidebar_visible'])

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
        Access rights are disabled by default, but allowed on some specific
        fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['chatter_position'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['chatter_position'])

    @api.model
    def store_recent_used_apps(self,**kwargs):
        menuId = kwargs.get('menuID',False)
        menu_id = self.env['ir.ui.menu'].sudo().search([('id','=',int(menuId))],limit=1)
        if not menu_id:
            menu_id = self.env['ir.ui.menu'].search([('id','=',int(menuId))],limit=1)
        if menu_id:
            self.env['most_used_apps'].create({
                'user_id': self.env.user.id,
                'menu_id': menu_id.id
                })
        
        return True
        
    @api.model
    def get_current_users_most_used_apps(self,**kwargs):
        current_date = date.today()
        current_month, current_year = current_date.month, current_date.year
        num_days = calendar.monthrange(current_year,current_month)[1]
        first_day = date(current_year,current_month,1) - relativedelta(months=1)
        last_day = date(current_year,current_month,num_days)

        current_user_all_used_menu_ids = self.env['most_used_apps'].search([('user_id','=',self.env.uid),('create_date','<',first_day)])
        current_users_recent_used_menu_ids = self.env['most_used_apps'].search([('user_id','=',self.env.uid),('create_date','>=',first_day),('create_date','<=',last_day)])
        remaining_used_menu_ids = current_user_all_used_menu_ids - current_users_recent_used_menu_ids
        remaining_used_menu_ids.unlink()

        menu_ids_list,menu_list,menu_dict,counter = [],[],{},0
        for menu_id in current_users_recent_used_menu_ids:
            menu_ids_list.append(menu_id.menu_id.id)

        unique_menu_id_list = self.get_unique_menu_ids(menu_ids_list)
        for unique_menu in unique_menu_id_list:
            menu_dict[unique_menu] = menu_ids_list.count(unique_menu)
        sorted_menu_dict = {k: v for k, v in sorted(menu_dict.items(), key=lambda item: item[1],reverse=True)}
        for menu in list(sorted_menu_dict.keys()):
            if counter != 6:
                menu = self.env['ir.ui.menu'].sudo().browse(menu)
                if menu:
                    actionID = self.get_action_id_from_menu(menu)
                    menu_list.append({
                        'menuId': menu.id,
                        'actionID': actionID.id if actionID else 'menu.action.id',
                        'name': menu.name,
                        'web_icon_data': menu.web_icon_data,
                    })
                    counter += 1
        return menu_list

    def get_action_id_from_menu(self,menu_id):
        if menu_id.action == False:
            parent_id = self.env['ir.ui.menu'].sudo().search([('parent_id','=',menu_id.id)],order="sequence asc",limit=1)
            if parent_id.action == False:
                self.get_action_id_from_menu(parent_id)
            else:
                return parent_id.action
        # else:
        #     return menu_id.action
            

    def get_unique_menu_ids(self,menu_ids):
        unique = []
        for menu in menu_ids:
            if menu not in unique:
                unique.append(menu)
        return unique
