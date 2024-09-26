from odoo import models, fields, api
from datetime import datetime ,date

class Kw_lost_and_found(models.Model):
    _name = 'kw_lost_and_found'
    _description = 'Lost & Found'
    _rec_name = "code"

    category = fields.Selection([('lost', 'Lost'),('found', 'Found')], 'Category',default='found')
    item_name = fields.Selection([('key', 'Key'),
                        ('money', 'Cash'),
                        ('mobile', 'Cell Phone'),
                        ('watch', 'Watch'),
                        ('laptop', 'Laptop'),
                        ('tablet', 'Tablet'),
                        ('jewellery', 'Jewellery'),
                        ('purses','Purses'),
                        ('backpacks','Backpacks'),
                        ('stationeries','Stationeries'),
                        ('eye_glasses','Eye Glasses'),
                        ('cosmetics','Cosmetics')
                        ], 'Items')
    item_attributes =fields.Char( string='Item Attributes')
    upload_image = fields.Binary(string=u'Image', attachment=True )
    remark= fields.Text(string="Remark")
    office_location_id = fields.Many2one('kw_res_branch_unit',string="Office Location")

    tentative_location = fields.Char(string="Found Location")
    lost_location = fields.Char(string="Lost Location")
    lost_datetime = fields.Datetime('Date & Time')

    state = fields.Selection([('draft', 'Draft'), ('informed', 'Informed'),('handover', 'Handover'),('discard','Discarded'),('close','Close')], default="draft" , string='Status', readonly=True, track_visibility='onchange', copy=False,)
    code = fields.Char(string="Reference No.")
    response_log = fields.One2many('lost_and_found_response_log','lf_id',string="Response Log")
    
    hand_over_to_emp =fields.Many2one("hr.employee" , string="Handover To")
    handover_remarks = fields.Text(string="Remarks")
    handover_date = fields.Datetime(string="Date")

    close_remarks = fields.Text(string="Close Remarks")
    close_date = fields.Datetime(string="Date")

    discarded_remarks = fields.Text(string="Discarded Remarks")
    discard_date = fields.Datetime(string="Date")
    
    requested_by = fields.Many2one('hr.employee',string="Request For")
    found_date = fields.Datetime(string="Informed Date")
    spoc_id = fields.Many2one('spoc_master_lnf',string="SPOC")
    informed_mail = fields.Boolean(string="Mail Sent")

    @api.multi
    def action_informed_send_mail(self):
        spoc_manager = self.env.user.has_group('kw_lost_and_found.lost_and_found_hr_user')
        attachment_id = 0
        sql_query = '''
                SELECT id  FROM ir_attachment
                WHERE res_model ='{res_model}' and res_id ={res_id} and name ='{name}' ;
            '''.format(
                res_model='kw_lost_and_found', res_id=self.id, name='upload_image'
            )

        self.env.cr.execute(sql_query, [])
        for val in self.env.cr.fetchall():
            attachment_id = val[0]
        
        spoc = self.env['spoc_master_lnf'].search([('office_location_id','=',self.office_location_id.id)],limit=1)
        spoc_member = spoc.employee_id.name + "(" + spoc.employee_id.emp_code + ")" if spoc.employee_id else ""
        template = self.env.ref('kw_lost_and_found.lost_and_found_email_template')
        item = dict(self.fields_get(allfields='item_name')['item_name']['selection'])[self.item_name]
        location = self.tentative_location if self.category == 'found' else self.lost_location
        template_data = self.env['mail.template'].browse(template.id)
        email_to = self.spoc_id.employee_id.work_email if self.category == 'lost' else 'csmho@csm.tech'
        email_from = 'tendrils@csm.tech' if self.category == 'lost' else self.env.user.employee_ids.work_email
        employee = 'employee' if not spoc_manager else 'spoc'
        """ send attachment if any"""
        template_data.with_context(image=attachment_id,item=item,location=location,employee=employee,spoc_member=spoc_member,email_from=email_from,email_to=email_to).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
        self.informed_mail = True
        if self.category == 'found':
            self.state = 'informed'
            self.found_date = datetime.today()

    @api.onchange('office_location_id')
    def get_emp(self):
        empl_id= self.env['spoc_master_lnf'].sudo().search([('office_location_id','=',self.office_location_id.id)])
        if empl_id:
            self.spoc_id=empl_id.id

    @api.model
    def create(self, vals):
        res = super(Kw_lost_and_found, self).create(vals)
        if res.category == 'lost':
            seq = self.env['ir.sequence'].next_by_code('lost_and_found.sequence')
            res.code = 'Lost/' + str(seq)
        else:
            seq = self.env['ir.sequence'].next_by_code('lost_and_found.sequence')
            res.code = 'Found/' + str(seq)
        return res

    @api.multi
    def action_button_informed(self):
        self.state='informed'
        self.found_date = datetime.today()
        self.action_informed_send_mail()
        
    
    @api.multi
    def action_button_handover(self):
        form_view_id = self.env.ref("kw_lost_and_found.kw_hand_over_to_employee_view_form").id
        return  {
            'name': 'Handover',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_lost_and_found',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id':self.ids[0],
            'view_id':form_view_id,
        }
        

    @api.multi 
    def action_button_discarded(self):
        form_view_id = self.env.ref("kw_lost_and_found.kw_discarded_request_view_form").id
        return  {
            'name': 'Discard',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_lost_and_found',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id':self.ids[0],
            'view_id':form_view_id,
        }
    
    def handover_to_employee(self):
        self.state = 'handover'
        self.handover_date = datetime.today()

    def discarded_lf_request(self):
        self.state = 'discard'
        self.discard_date = datetime.today()
    
    def action_request_close(self):
        form_view_id = self.env.ref("kw_lost_and_found.kw_close_view_form").id
        return  {
            'name': 'Close',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_lost_and_found',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id':self.ids[0],
            'view_id':form_view_id,
        }

    def close_lf_request(self):
        self.state = 'close'
        self.close_date = datetime.today()

    

   