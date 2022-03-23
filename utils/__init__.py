# -*- coding: utf-8 -*-
from .lookup_table import (
    init_lookup_table_k_sku_v_boolean,
    get_lookup_table_k_sku_v_boolean,
    put_lookup_table_k_sku_v_boolean,
    clean_lookup_table_k_sku_v_boolean,

    init_lookup_table_k_ct_sku_v_boolean,
    get_lookup_table_k_ct_sku_v_boolean,
    put_lookup_table_k_ct_sku_v_boolean,
    clean_lookup_table_k_ct_sku_v_boolean,

    init_lookup_table_k_sku_v_brand_c1_c2_is_combined,
    get_lookup_table_k_sku_v_brand_c1_c2_is_combined,
    clean_lookup_table_k_sku_v_brand_c1_c2_is_combined,

    init_lookup_table_k_c1_v_c1_c2,
    get_lookup_table_k_c1_v_c1_c2,
    get_lookup_table_k_c1_v_c1_c2_keys,
    clean_lookup_table_k_c1_v_c1_c2,

    init_lookup_table_k_brand_v_brand_c2,
    get_lookup_table_k_brand_v_brand_c2,
    get_lookup_table_k_brand_v_brand_c2_keys,
    clean_lookup_table_k_brand_v_brand_c2,

    init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c1,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c2,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_product_series,
    clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,
)
from .reg_patterns import REG_INT
from .reg_patterns import REG_INT_AND_FLOAT
from .reg_patterns import REG_POSITIVE_INT
from .util_funcs import util_calc_month_num
from .util_funcs import util_cost_count
from .util_funcs import util_generate_digest
from .util_funcs import util_generate_file_digest
from .util_funcs import util_generate_n_digit_nums_and_letters
from .util_funcs import util_remove_duplicates_for_list
from .util_funcs import util_silent_remove

__all__ = [
    init_lookup_table_k_sku_v_boolean,
    get_lookup_table_k_sku_v_boolean,
    put_lookup_table_k_sku_v_boolean,
    clean_lookup_table_k_sku_v_boolean,

    init_lookup_table_k_ct_sku_v_boolean,
    get_lookup_table_k_ct_sku_v_boolean,
    put_lookup_table_k_ct_sku_v_boolean,
    clean_lookup_table_k_ct_sku_v_boolean,

    init_lookup_table_k_sku_v_brand_c1_c2_is_combined,
    get_lookup_table_k_sku_v_brand_c1_c2_is_combined,
    clean_lookup_table_k_sku_v_brand_c1_c2_is_combined,

    init_lookup_table_k_c1_v_c1_c2,
    get_lookup_table_k_c1_v_c1_c2,
    get_lookup_table_k_c1_v_c1_c2_keys,
    clean_lookup_table_k_c1_v_c1_c2,

    init_lookup_table_k_brand_v_brand_c2,
    get_lookup_table_k_brand_v_brand_c2,
    get_lookup_table_k_brand_v_brand_c2_keys,
    clean_lookup_table_k_brand_v_brand_c2,

    init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c1,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c2,
    get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_product_series,
    clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name,

    REG_INT,
    REG_INT_AND_FLOAT,
    REG_POSITIVE_INT,

    util_calc_month_num,
    util_cost_count,
    util_generate_digest,
    util_generate_file_digest,
    util_generate_n_digit_nums_and_letters,
    util_remove_duplicates_for_list,
    util_silent_remove,
]

init_lookup_table_k_sku_v_boolean()
init_lookup_table_k_ct_sku_v_boolean()
init_lookup_table_k_sku_v_brand_c1_c2_is_combined()
init_lookup_table_k_c1_v_c1_c2()
init_lookup_table_k_brand_v_brand_c2()
init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name()
