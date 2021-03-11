# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Qatar - Accounting',
    'version': '1.1',
    'category': 'Localization',
    'description': """
This is the base module to manage the qatar accounting chart in Odoo.
==============================================================================

Install qatar chart of accounts.
    """,
    'author': 'Al Kidhma Group',
    'depends': [
        'account',
    ],
    'data': [
        'data/l10n_qatar_chart_data.xml',
        'data/account_chart_template_data.yml',
    ],
    'test': [
        '../account/test/account_bank_statement.yml',
        '../account/test/account_invoice_state.yml',
    ],
    'demo': [
        '../account/demo/account_bank_statement.yml',
        '../account/demo/account_invoice_demo.yml',
    ],
    'website': 'https://www.odoo.com/page/accounting',
}
