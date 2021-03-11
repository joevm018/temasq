{
    "name"          : "POS RECEIPT - Invoice Delivery Note",
    "version"       : "1.0",
    "author"        : "Al Kidhma Group",
    "website"       : "",
    "category"      : "Point of Sale",
    "license"       : "LGPL-3",
    "summary"       : "POS RECEIPT - Invoice Delivery Note",
    "description"   : """
        POS RECEIPT - Invoice Delivery Note
    """,
    "depends"       : [
        "beauty_pos",
    ],
    "data"          : [
        'templates.xml',
        "views/pos_order_view.xml",
        "reports/report_pos_invoice.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    'qweb': [
         'static/src/xml/delivery_pos.xml',
        ],
    "css"           : [],
    "sequence"   : 1,
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}