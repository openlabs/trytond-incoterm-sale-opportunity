# -*- coding: utf-8 -*-
"""
    __init__


    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from opportunity import SaleOpportunity, IncotermSaleOpportunity


def register():
    Pool.register(
        SaleOpportunity,
        IncotermSaleOpportunity,
        module='incoterm_sale_opportunity', type_='model'
    )
