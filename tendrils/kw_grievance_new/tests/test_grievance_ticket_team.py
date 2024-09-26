from odoo.tests import common


class TestgrievanceTicketTeam(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestgrievanceTicketTeam, cls).setUpClass()
        grievance_ticket = cls.env['grievance.ticket']
        grievance_ticket_team = cls.env['grievance.ticket.team']
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.stage_closed = cls.env.ref(
            'kw_grievance_new.grievance_ticket_stage_done'
        )
        cls.team_id = grievance_ticket_team.create({
            'name': "Team 1"
        })
        cls.grievance_ticket_1 = grievance_ticket.create({
            'name': "Ticket 1",
            'description': "Description",
            'team_id': cls.team_id.id,
            'priority': '3',
        })
        cls.grievance_ticket_2 = grievance_ticket.create({
            'name': "Ticket 2",
            'description': "Description",
            'team_id': cls.team_id.id,
            'user_id': cls.user_demo.id,
            'priority': '1',
        })

    def test_grievance_ticket_todo(self):
        self.assertEqual(self.team_id.todo_ticket_count,
                         2,
                         'grievance Ticket: grievance ticket team should '
                         'have two tickets to do.')
        self.assertEqual(self.team_id.todo_ticket_count_unassigned,
                         1,
                         'grievance Ticket: grievance ticket team should '
                         'have one tickets unassigned.')
        self.assertEqual(self.team_id.todo_ticket_count_high_priority,
                         1,
                         'grievance Ticket: grievance ticket team should '
                         'have two tickets with high priority.')
        self.assertEqual(self.team_id.todo_ticket_count_unattended,
                         2,
                         'grievance Ticket: grievance ticket team should '
                         'have two tickets unattended.')

        self.grievance_ticket_1.write({
            'stage_id': self.stage_closed.id,
        })

        self.assertEqual(self.team_id.todo_ticket_count_unattended,
                         1,
                         'grievance Ticket: grievance ticket team should '
                         'have one ticket unattended.')

        self.assertEqual(self.team_id.todo_ticket_count,
                         1,
                         'grievance Ticket: grievance ticket team should '
                         'have one ticket to do.')
