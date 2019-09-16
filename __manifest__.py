# -*- coding: utf-8 -*-
{
    'name': "Bahmni OpenIMIS",

    'summary': """Prepare, manage, send claims to imis gateway""",

    'description': """
        Bahmni Openimis moduel does:
            - Separate quotations based on payment type
            - Prepare claims
            - Send claims to imis gateway
            - Check status of the claims
    """,

    'author': "NepalEHR",
    'website': "http://www.nepalehr.org",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'insurance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ["base","sale","account"],

    # always loaded
    'data': [
        'views/quotation_view.xml',
        'views/imis_odoo_product_map_view.xml'
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo.xml',
    #],
    'Installable': True,
    'auto_install': False,
    'application': True
}