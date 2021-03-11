{
    "name"          : "Beauty Supervisor Card",
    "version"       : "1.0",
    "author"        : "Al Kidhma Group",
    "website"       : "",
    "category"      : "Point of Sale",
    "license"       : "LGPL-3",
    "summary"       : "Beauty Supervisor Card",
    "description"   : """
        Beauty Supervisor Card
    """,
    "depends"       : [
        "discounts_in_pos",
        "beauty_pos",
        "pos_staff",
        "beauty_foc",
        "pos_daily_report",
    ],
    "data"          : [
        "wizard/change_price_discount.xml",
        "views/user.xml",
        "views/pos_order.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    'qweb': [],
    "css"           : [],
    "sequence"   : 1,
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}