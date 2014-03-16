# -*- coding: utf-8 -*-
"""
    Test Sale Opportunity

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.pyson import Eval


class TestSaleOpportunity(unittest.TestCase):
    '''
    Test sale
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('incoterm_sale_opportunity')
        self.Party = POOL.get('party.party')
        self.Country = POOL.get('country.country')
        self.Address = POOL.get('party.address')
        self.Subdivion = POOL.get('country.subdivision')
        self.Company = POOL.get('company.company')
        self.Currency = POOL.get('currency.currency')

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        Account = POOL.get('account.account')

        account_create_chart = POOL.get(
            'account.create_chart', type="wizard")

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec

        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = POOL.get('account.account')
        Company = POOL.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])[0]

    def create_defaults(self):
        "Create defaults"
        Template = POOL.get('product.template')
        Product = POOL.get('product.product')
        Uom = POOL.get('product.uom')
        User = POOL.get('res.user')
        Employee = POOL.get('company.employee')

        country, = self.Country.create([{
            'name': 'Australia',
            'code': 'AU',
        }])

        subdivision, = self.Subdivion.create([{
            'country': country.id,
            'name': 'New South Wales',
            'code': 'NSW',
            'type': 'state'
        }])

        Currency = POOL.get('currency.currency')
        currency = Currency(
            name='Euro', symbol=u'€', code='EUR',
            rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
            mon_decimal_point=','
        )
        currency.save()

        with Transaction().set_context({'company': None}):
            party, = self.Party.create([{
                'name': 'testuser',
                'addresses': [('create', [{
                    'party': Eval('id'),
                    'city': 'Melborne',
                    'invoice': True,
                    'country': country.id,
                    'subdivision': subdivision.id,
                }])],
                'contact_mechanisms': [('create', [{
                    'type': 'mobile',
                    'value': '12345'
                }])],
            }])
        self.assert_(party.id)
        self.assertEqual(len(party.addresses), 1)

        company, = self.Company.create([{
            'party': party.id,
            'currency': currency
        }])
        company2, = self.Company.create([{
            'party': party.id,
            'currency': currency
        }])

        User.write(
            [User(USER)], {
                'main_company': company.id,
                'company': company.id,
            }
        )

        self._create_coa_minimal(company=company.id)
        account_revenue = self._get_account_by_kind('revenue')
        uom, = Uom.search([('name', '=', 'Unit')])
        template1, = Template.create([{
            'name': 'product',
            'type': 'goods',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': uom,
            'salable': True,
            'sale_uom': uom.id,
            'account_revenue': account_revenue.id,
        }])

        product1, = Product.create([{
            'template': template1.id,
        }])

        employee, = Employee.create([{
            'party': party.id,
            'company': company.id,
        }])

        return {
            'party': party,
            'country': country,
            'subdivision': subdivision,
            'company': company,
            'currency': currency,
            'uom': uom,
            'product1': product1,
            'payment_term': self._create_payment_term(),
            'employee': employee,
        }

    def test0010_test_incoterm_propagation(self):
        '''
        Test incoterm propagation
        '''
        SaleOpportunity = POOL.get('sale.opportunity')
        Sale = POOL.get('sale.sale')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()

            # Create sale with incoterms
            saleopp, = SaleOpportunity.create([{
                'payment_term': defaults['payment_term'],
                'currency': defaults['currency'].id,
                'party': defaults['party'].id,
                'company': defaults['company'].id,
                'employee': defaults['employee'],
                'description': 'HelloWorld',
                'lines': [('create', [{
                    'sequence': 1,
                    'quantity': Decimal(2.0),
                    'unit': defaults['uom'].id,
                    'product': defaults['product1'],
                }])],
                'incoterms': [('create', [
                    {
                        'year': '2010',
                        'abbrevation': 'CPT',
                        'value': Decimal('10'),
                        'currency': defaults['currency'].id,
                        'city': 'Alabama',
                    }, {
                        'year': '2010',
                        'abbrevation': 'FOB',
                        'value': Decimal('20'),
                        'currency': defaults['currency'].id,
                        'city': 'Georgia',
                    }
                ])]
            }])

            with Transaction().set_context(company=defaults['company'].id):
                # Convert to Sale
                SaleOpportunity.lead([saleopp])
                SaleOpportunity.opportunity([saleopp])
                SaleOpportunity.convert([saleopp])

            # Check sale with incoterms has been created.
            sale, = Sale.search([])
            self.assertEqual(len(sale.incoterms), 2)
            self.assertEqual(sale.incoterms[0].year, '2010')
            self.assertEqual(sale.incoterms[0].abbrevation, 'CPT')
            self.assertEqual(sale.incoterms[0].value, Decimal('10'))
            self.assertEqual(sale.incoterms[0].city, 'Alabama')
            self.assertEqual(sale.incoterms[1].year, '2010')
            self.assertEqual(sale.incoterms[1].abbrevation, 'FOB')
            self.assertEqual(sale.incoterms[1].value, Decimal('20'))
            self.assertEqual(sale.incoterms[1].city, 'Georgia')


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSaleOpportunity),
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
