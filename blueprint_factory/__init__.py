# -*- coding: utf-8 -*-
from .association import association_blueprint
from .case1 import case1_blueprint
from .case2 import case2_blueprint
from .case3 import case3_blueprint
from .case4 import case4_blueprint
from .case5 import case5_blueprint
from .case6 import case6_blueprint
from .common import common_blueprint
from .inventory import inventory_blueprint
from .jit_inventory import jit_inventory_blueprint
from .option import option_blueprint
from .product import product_blueprint
from .selection import selection_blueprint
from .unit_price import unit_price_blueprint
from .user import user_blueprint

__all__ = [
    association_blueprint,
    case1_blueprint,
    case2_blueprint,
    case3_blueprint,
    case4_blueprint,
    case5_blueprint,
    case6_blueprint,
    common_blueprint,
    inventory_blueprint,
    jit_inventory_blueprint,
    option_blueprint,
    product_blueprint,
    selection_blueprint,
    unit_price_blueprint,
    user_blueprint
]
