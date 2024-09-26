# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
OpenUpgrade Migration Script

This module contains a migration script for upgrading the system using OpenUpgrade.
It handles necessary operations to ensure compatibility with the new version.
(c) 2020 Creu Blanca, Licensed under AGPL-3.0 or later.
"""

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Migrate function for upgrading the system using OpenUpgrade.

    Args:
        env (Environment): Odoo environment.
        version (str): Version string representing the target version.

    Returns:
        None
    """
    calendars = env['resource.calendar'].search([])
    for calendar in calendars:
        calendar._onchange_hours_per_day()
