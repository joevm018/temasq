{
    "name"          : "Customer DOB and Birthday Wishes",
    "version"       : "1.0",
    "author"        : "Al Kidhma Group",
    "website"       : "",
    "category"      : "",
    "license"       : "LGPL-3",
    "summary"       : "Customer DOB and Birthday Wishes",
    "description"   : """
        Customer DOB and Birthday Wishes
    """,
    "depends"       : [
        "beauty_soft",
        "beauty_pos",
    ],
    "data"          : [
        "templates.xml",
        "views/res_partner_view.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    'qweb': ['static/src/xml/pos.xml'],
    "css"           : [],
    "sequence"   : 1,
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}