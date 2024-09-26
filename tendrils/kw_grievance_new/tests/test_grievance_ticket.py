import time
from odoo.tests import common


class TestgrievanceTicket(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestgrievanceTicket, cls).setUpClass()
        grievance_ticket = cls.env['grievance.ticket']
        cls.user_admin = cls.env.ref('base.user_root')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_portal = cls.env.ref('base.demo_user0')
        cls.stage_closed = cls.env.ref(
            'kw_grievance_new.grievance_ticket_stage_done'
        )

        cls.ticket = grievance_ticket.create({
            'name': 'Test 1',
            'description': 'Ticket test',
        })

    def test_grievance_ticket_datetimes(self):
        old_stage_update = self.ticket.last_stage_update

        self.assertTrue(self.ticket.last_stage_update,
                        'grievance Ticket: grievance ticket should '
                        'have a last_stage_update at all times.')

        self.assertFalse(self.ticket.closed_date,
                         'grievance Ticket: No closed date '
                         'should be set for a non closed '
                         'ticket.')

        time.sleep(1)

        self.ticket.write({
            'stage_id': self.stage_closed.id,
        })

        self.assertTrue(self.ticket.closed_date,
                        'grievance Ticket: A closed ticket '
                        'should have a closed_date value.')
        self.assertTrue(old_stage_update < self.ticket.last_stage_update,
                        'grievance Ticket: The last_stage_update '
                        'should be updated at every stage_id '
                        'change.')

        self.ticket.write({
            'user_id': self.user_admin.id,
        })
        self.assertTrue(self.ticket.assigned_date,
                        'grievance Ticket: An assigned ticket '
                        'should contain a assigned_date.')

    def test_grievance_ticket_number(self):
        self.assertNotEquals(self.ticket.number, '/',
                             'grievance Ticket: A ticket should have '
                             'a number.')
        ticket_number_1 = \
            int(self.ticket._prepare_ticket_number(values={})[2:])
        ticket_number_2 = \
            int(self.ticket._prepare_ticket_number(values={})[2:])
        self.assertEquals(ticket_number_1 + 1, ticket_number_2)

    def test_grievance_ticket_copy(self):
        old_ticket_number = self.ticket.number

        copy_ticket_number = self.ticket.copy().number

        self.assertTrue(
            copy_ticket_number != '/' and
            old_ticket_number != copy_ticket_number,
            'grievance Ticket: A new ticket can not '
            'have the same number than the origin ticket.')

    def test_grievance_ticket_create(self):
        partner = self.env.ref("base.main_partner")

        auto_named = self.env["grievance.ticket"].create(
            {
                "name": "Some name",
                "description": "Some description",
                "partner_id": partner.id,
            }
        )
        self.assertEqual(auto_named.partner_name, partner.name)
        self.assertEqual(auto_named.partner_email, partner.email)

        res = self.env["grievance.ticket"]._name_search(
            auto_named.number,
            args=None,
            operator="=",
            limit=1,
        )
        self.assertEqual(res[0][0], auto_named.id)
        res2 = self.env["grievance.ticket"]._name_search(
            auto_named.number,
            args=None,
            operator="!=",
            limit=None,
        )
        self.assertFalse(auto_named.id in [el[0] for el in res2])

        manual_named = self.env["grievance.ticket"].create(
            {
                "name": "Some name",
                "description": "Some description",
                "partner_id": partner.id,
                "partner_name": "Special name",
                "partner_email": "special@example.org",
            }
        )
        self.assertEqual(manual_named.partner_name, "Special name")
        self.assertEqual(manual_named.partner_email, "special@example.org")

    def test_grievance_ticket_access(self):
        self.assertEqual(self.ticket.access_url, '/my/grievance/%s' % self.ticket.id)
        self.ticket.partner_id = self.user_portal.partner_id.id
        self.assertTrue(self.ticket.partner_can_access())
