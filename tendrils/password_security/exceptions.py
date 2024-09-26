from odoo.exceptions import Warning as UserError


class PassError(UserError):
    """ Example: When you try to create an insecure password."""
    def __init__(self, msg):
        self.message = msg
        super(PassError, self).__init__(msg)
