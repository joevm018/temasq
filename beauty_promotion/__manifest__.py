{
    "name"          : "Beauty Promotion",
    "version"       : "1.0",
    "author"        : "Al Kidhma Group",
    "website"       : "",
    "category"      : "Point of Sale",
    "license"       : "LGPL-3",
    "summary"       : "Beauty Promotion",
    "description"   : """
        Beauty Promotion
    """,
    "depends"       : [
        "discounts_in_pos",
        "pos_staff",
        "beauty_pos",
        "pos_daily_report",
    ],
    "data"          : [
        'security/ir.model.access.csv',
        "wizard/apply_promotion.xml",
        "wizard/report_promotion.xml",
        "reports/report_promotion.xml",
        "reports/reports.xml",
        "views/pos_order.xml",
        "views/promotion.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    'qweb': [
        ],
    "css"           : [],
    "sequence"   : 1,
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}