# -*- coding: utf-8 -*-

# ####### STARt : Merged kw security ###############
from . import base
from . import mixins_locking
from . import mixins_access_rights
from . import mixins_access_groups
from . import access_groups
from . import ir_model_access
from . import res_users
from . import ir_rule
# #######END :  Merged kw security ###############


from . import mixins_thumbnail

from . import storage
from . import directory
from . import file

from . import category
from . import tag

from . import ir_http
from . import res_company
from . import res_config_settings

# from . import directory_download
# from . import check_file_revision
# from . import revision_file

# ####### Start : Merged kw filestore ###############
from . import filestore

# ####### Start : Merged DMS Access ###############
from . import dms_access

# ####### Start : Merged DMS Thumbnail ###############
from . import dms_thumbnail

# ###### Start : DMS Versioning ###############
from . import dms_version

# ###### Start : DMS Download Log ###############
from . import dms_download_log

# ######Start : DMS integration with other module
from . import dms_integration

# #Start : DMS revision history
from . import dms_revision_history

# #DIgi sign
from . import dms_digi_esign

# # DMS : public access url generation
from . import dms_public_access
