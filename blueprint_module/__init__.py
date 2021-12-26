# -*- coding: utf-8 -*-
from flask import Blueprint

blueprint = Blueprint("fotolei_pssa_blueprint", __name__)

from . import added_skus_prepare
from . import bc1c2_associations
from . import case1
from . import case2
from . import case3
from . import case4
from . import case5
from . import case6
from . import file_download
from . import inventories_all_clean
from . import inventories_page
from . import inventories_total
from . import inventories_upload
from . import jit_inventory_upload
from . import keepalive
from . import oplogs_show
from . import options
from . import products_all_clean
from . import products_one_clean
from . import products_one_pick
from . import products_one_update
from . import products_page
from . import products_total
from . import products_upload
from . import selections
