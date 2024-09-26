# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""
Module for Upgrades and XML ID Renames.

This module contains upgrade scripts and XML ID renames for managing changes in Odoo modules.

Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""
from openupgradelib import openupgrade

xmlid_renames = [
    (
        "helpdesk_mgmt.helpesk_ticket_personal_rule",
        "helpdesk_mgmt.helpdesk_ticket_personal_rule",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    """
    Perform migration tasks for the specified version.

    Args:
        env (openupgrade.OpenUpgradeEnvironment): The OpenUpgrade environment.
        version (str): The version to migrate to.

    Returns:
        None
    """
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
