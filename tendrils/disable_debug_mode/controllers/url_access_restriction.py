# -*- coding: utf-8 -*-
"""
Module for Custom Odoo HTTP Controllers.

This module contains custom HTTP controllers for handling web requests in Odoo.

"""
import logging,werkzeug
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _

from odoo.addons.web.controllers import main
import logging
_logger = logging.getLogger(__name__)

class UrlAction(main.Action):
	"""
    Action class for URL redirection.

    This class extends the main Action class to provide functionality for redirecting
    users to a specified URL.

    """
	@http.route()
	def load(self, action_id, additional_context=None,):
		menu = False
		# print("action id--",action_id,type(action_id),)
		act_id = f"ir.actions.act_window,{action_id}"
		# act_client_id = f"ir.actions.client,{action_id}"
		# act_url_id = f"ir.actions.act_url,{action_id}"
		# act_server_id = f"ir.actions.server,{action_id}"
  
		# query = f"select action,id from ir_ui_menu where active = True and action = '{act_id}' or action = '{act_client_id}' or action = '{act_url_id}' or action = '{act_server_id}'"
		query = f"select action,id from ir_ui_menu where active = True and action = '{act_id}'"
		request._cr.execute(query)
		all_data = request._cr.fetchall()
		for record in all_data:			
			menu_data =  list(record)[-1]
			menu = request.env['ir.ui.menu'].browse(menu_data)
		# for rec in all_data:
		# 	print("rec-",rec)
		# 	menu_data = request.env['ir.ui.menu'].sudo().search([('action','!=',False)])
		# print("----------------------",abc,action_id,len(request.env['ir.ui.menu'].sudo().search(['|',('active','=',True),('active','=',False)])))
		# print("filtered data---",len(menu_ids),menu_ids.filtered(lambda menu: menu.action.id == action_id))
		# for menu_id in menu_ids:
		# 	if menu_id.action:
		# 		# print("menu_id.action===",menu_id.action.id,action_id,'id===',menu_id.id)
		# 		# act = request.env['ir.actions.act_window']
		# 		if menu_id.action.id == action_id:
		# 			print("111111111111===")
		# 			menu = menu_id
		# 			print("menu",menu)
		user = request.env['res.users'].sudo().browse(request.session.uid)
		# if isinstance(action_id, int) == True:
		# 	if not self._user_has_acces_right(action_id, menu, user):
		# 		print("not acess")
		# 		return  {
		# 			'name': 'WARNING',
		# 			'type': 'ir.actions.act_url',
		# 			'url': '/web/session/logout',
		# 			'target' : 'self'
		# 		}
		# else:
		# 	pass

		return super(UrlAction, self).load(action_id, additional_context=additional_context)


	def _user_has_acces_right(self, action_id, menu, user):
		action = request.env['ir.actions.act_window'].sudo().search([('id','=',action_id)], limit=1)
		# abc = False
		# menu_ids = request.env['ir.ui.menu'].sudo().search([])
		# for menu_id in menu_ids:
		# 	if menu_id.action:
		# 		if menu_id.action.id == action.id:
		# 			abc = menu_id
		# print('abc=============',abc)
		if action and len(action.groups_id) > 0:
			# print("=action=")
			if any(elem in user.groups_id.ids  for elem in action.groups_id.ids):
				return True
			return False
		if menu and len(menu.groups_id.ids) > 0:
			# print("=menu=",menu)
			if any(elem in user.groups_id.ids  for elem in menu.groups_id.ids):
				return True
			return False
		if menu and menu.parent_id:
			# print("=parent menu=",menu)
			return self._user_has_acces_right(action_id, menu.parent_id, user)

		return True
