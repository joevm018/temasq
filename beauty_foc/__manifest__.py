{
    "name"          : "Beauty Free of cost (FOC)",
    "version"       : "1.0",
    "author"        : "Al Kidhma Group",
    "website"       : "",
    "category"      : "Point of Sale",
    "license"       : "LGPL-3",
    "summary"       : "Beauty Free of cost (FOC)",
    "description"   : """
        Beauty Free of cost (FOC)
    """,
    "depends"       : [
        "discounts_in_pos",
        "pos_staff",
        "beauty_pos",
        "pos_daily_report",
    ],
    "data"          : [
        "views/pos_order.xml",
        "reports/report_sales_details.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    'qweb': [
        # 'static/src/xml/discount_card.xml'
        ],
    "css"           : [],
    "sequence"   : 1,
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}