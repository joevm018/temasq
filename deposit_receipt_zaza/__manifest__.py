{
    "name": "Deposit Receipt Zaza",
    "version": "1.0",
    "author": "Al Kidhma Group",
    "website": "",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "summary": "Deposit Receipt print",
    "description": """ """,
    "depends": ['beauty_pos'],
    "data": [
        "reports/report_pos_deposit_receipt.xml",
        "reports/report_pos_deposit_receipt_small.xml",
        "views/order.xml",
    ],
    "demo": [],
    "test": [],
    "images": [],
    'qweb': ['static/src/xml/*.xml'],
    "css": [],
    "sequence": 1,
    "application": True,
    "installable": True,
    "auto_install": False,
}
