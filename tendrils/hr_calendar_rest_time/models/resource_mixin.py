# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Module: Resource Mixin

Summary:
    This module defines the ResourceMixin class, which serves as an abstract model for resource-related functionality.

Description:
    The ResourceMixin class provides a set of common functionalities and attributes related to resources.
    It serves as a base class for other models that need to incorporate resource management features.
    This class is part of the resource management system in Odoo.

Copyright:
    (c) 2019 Creu Blanca

License:
    This module is licensed under the AGPL-3.0 or later license. For more information, visit http://www.gnu.org/licenses/agpl.
"""

from odoo import models
from datetime import timedelta


class ResourceMixin(models.AbstractModel):
    """
    Abstract model representing a resource mixin.

    Attributes:
        _inherit (str): Inherited model name.
    """
    _inherit = 'resource.mixin'

    def _get_work_hours(self, start, stop, meta):
        return (stop - start - timedelta(hours=sum([
            attendance.rest_time for attendance in meta
        ]))).total_seconds() / 3600
