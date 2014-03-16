# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.modules.incoterm.incoterm import Incoterm
from trytond.pyson import Eval, In, Not

__all__ = ['SaleOpportunity', 'IncotermSaleOpportunity']
__metaclass__ = PoolMeta


class SaleOpportunity:
    'Sale Oppotunity'
    __name__ = 'sale.opportunity'

    incoterms = fields.One2Many(
        'sale.opportunity.incoterm', 'opportunity',
        'Incoterm Sale Opportunity', states={
            'readonly': Not(In(Eval('state'), ['lead', 'opportunity'])),
        }, depends=['state']
    )

    def create_sale(self):
        '''
        Create a sale for the opportunity and return the sale
        '''
        SaleIncoterm = Pool().get('sale.incoterm')

        sale = super(SaleOpportunity, self).create_sale()

        SaleIncoterm.create(map(
            lambda incoterm: {
                'year': incoterm.year,
                'abbrevation': incoterm.abbrevation,
                'value': incoterm.value,
                'currency': incoterm.currency.id,
                'city': incoterm.city,
                'sale': sale.id,
            }, self.incoterms
        ))

        return sale


class IncotermSaleOpportunity(Incoterm, ModelSQL, ModelView):
    'Incoterm Sale Opportunity'
    __name__ = 'sale.opportunity.incoterm'

    opportunity = fields.Many2One(
        'sale.opportunity', 'Sale Opportunity', required=True
    )
