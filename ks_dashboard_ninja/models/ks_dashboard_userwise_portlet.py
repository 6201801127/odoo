from odoo import models, fields, api

class UserWiseKwantifyPortlet(models.Model):
  _name = 'kw_user_portlets'
  _description = "Kwantify Portlets User Wise"

  employee_id = fields.Many2one('hr.employee',string="Employee")
  ks_dashboard_ninja_board_id = fields.Many2one('ks_dashboard_ninja.board', string="Dashboard")
  ks_dashboard_items_id = fields.Many2many(comodel_name='ks_dashboard_ninja.item',
      relation='ks_dashboard_ninja_items_employee_rel',
      column1='item_id',
      column2='employee_id', string="Portlets")  

  def create_portlet(self, **kwargs):
    added_item_list = []
    for record in kwargs['item_ids']:
      if 'portletStatus' and 'value' in record:
        if record['portletStatus'] == 'Added':
          added_item_list.append(int(record['value']))
    
    portlet_records = self.env['kw_user_portlets'].search([('employee_id','in',self.env.user.employee_ids.ids),('ks_dashboard_ninja_board_id','=',int(kwargs['dashboard_id']) )])
    if portlet_records:
      portlet_records.write({'ks_dashboard_items_id': [(6, 0, added_item_list)]})
    else:
      self.create({
        'employee_id': self.env.user.employee_ids.id,
        'ks_dashboard_ninja_board_id': int(kwargs['dashboard_id']),
        'ks_dashboard_items_id':  [(6, 0, added_item_list)]
      })
      

  def delete_portlet(self, **kwargs):
    deleted_portlet_id = self.env['kw_user_portlets'].search([('employee_id.user_id','=',kwargs['user_id']),('ks_dashboard_ninja_board_id','=',kwargs['dashboard_id']),('ks_dashboard_items_id','=',kwargs['portlet_id'])])
    deleted_portlet_id.unlink()


class UserWisePortletGridstackConfig(models.Model):
  _name = 'kw_user_portlets_gridstack_config'
  _description = 'User Portlets Gridstack Configuration'

  employee_id = fields.Many2one('hr.employee',string="Employee")
  ks_dashboard_ninja_board_id = fields.Many2one('ks_dashboard_ninja.board')
  ks_gridstack_config = fields.Char('Gridstack Config details')

  def update_gridstack_config(self, **vals):
    emp_record = self.search([('employee_id.user_id','=',vals['user_id']),('ks_dashboard_ninja_board_id','=',vals['dashboard_id'])])
    if emp_record:
        emp_record.write({'ks_gridstack_config': vals['ks_gridstack_config']})
    else:
        self.create({
            'employee_id': self.env.user.employee_ids.id,
            'ks_dashboard_ninja_board_id': vals.get('dashboard_id'),
            'ks_gridstack_config': ''
        })