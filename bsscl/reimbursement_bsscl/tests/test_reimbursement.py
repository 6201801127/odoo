from odoo.tests.common import TransactionCase, tagged
from odoo.tests.common import Form
from odoo.exceptions import ValidationError

@tagged('post_install')
class TestReimbursement(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestReimbursement, self).setUp(*args, **kwargs)
        admin_user_id = self.env['hr.employee'].search([('user_id.login', '=', 'admin')])
        lunch_id = self.env['reimbursement.type'].search([('code', '=', 'lunch')])
        date_range_id = self.env['date.range'].search([('name', '=', '2022 Jan')])
        self.new_rec = self.env['reimbursement'].create({'employee_id': admin_user_id.id,
                                                            'reimbursement_type_id': lunch_id.id,
                                                            'date_range': date_range_id.id,
                                                            'working_days': str(10)})

    def test_default_state(self):
        self.assertEqual(self.new_rec.state, 'draft', 'State not changed!')

    def test_submit(self):
        try:
            self.new_rec.button_submit()
            self.assertEqual(self.new_rec.state, 'waiting_for_approval', 'State not changed!')
        except (ValidationError, AssertionError) as e:
            print(str(e))

    # def test_onchnage(self):
    #     reimbursement_form = Form(self.env['reimbursement'], 
    #                                 view='reimbursement.reimbursement_form_view')
        
    #     reimbursement = reimbursement_form.save()

    def tearDown(self):
        self.new_rec.write({'state': 'draft'})
        self.new_rec.unlink()
        super(TestReimbursement, self).tearDown()