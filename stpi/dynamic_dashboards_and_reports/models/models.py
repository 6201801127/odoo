# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DynamicDashboards(models.Model):
    _inherit = 'ir.ui.menu'
    is_dashboard = fields.Boolean()
    iframe_dashboard = fields.Text()
    dashboard_view = fields.Many2one('ir.ui.view')
    state = fields.Selection([('published','Published'),('unpublished',"Unpublished")])



    def create_dashboard_or_report(self):
        act_obj = self.env['ir.actions.act_window']
        views = self.env['ir.ui.view']
        total_iframe = self.iframe_dashboard.replace('800','100%').replace('"600"','"100%"').replace('allowtransparency','')
        total_form = '''<form string="Embedded Webpage" version="7.0" edit="false" create="false">

              <div style="position:absolute; left:0; top:0; width:100%; height:100%;">
                 {0}


              </div>

          </form>'''.format(total_iframe)


        report_view = views.create({'name' : self.name + '.menudashboardmenu',
                                    'type' : 'form',
                                    'mode': 'primary',
                                    'active': True,
                                    'priority': 1 ,
                                    'model': 'board.board',
                                    'arch': total_form,

                         })

        print ('________________________________________________',report_view)
        self.dashboard_view = report_view.id



        print('____________________________________________________________',self.action)
        had = self.env['ir.actions.act_window'].create({
            'name': self.name + 'action',
            'res_model': 'board.board',
            'view_mode' : 'form',
            'context': '{}',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'view_id':report_view.id
        })
        print('**********************************************************',had)
        self.action = had
        self.state = 'published'


    def unpublish_dashboard(self):
        print ('_______________________________________________________')
        views = self.env['ir.ui.view'].search([('id','=',self.dashboard_view.id)])
        print ('_____________________________',views)
        views.unlink()
        self.action.unlink()
        self.state = 'unpublished'


