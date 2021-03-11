# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Product Barcode',
    'version': '1.0',
    'author': 'Al Kidhma',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['product', 'stock'],
    'data': [
        # 'views/barcode.xml',
        'views/product.xml',
        'views/barcode.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
