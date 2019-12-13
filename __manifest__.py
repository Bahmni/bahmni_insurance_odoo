# -*- coding: utf-8 -*-
{
    'name': "Bahmni OpenIMIS",

    'summary': """Prepare, manage, send claims to insurance gateway""",

    'description': """
        Bahmni Openimis module does:
            - Separate quotations based on payment type
            - Prepare claims
            - Send claims to insurance gateway
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
    'depends': ["base","sale", "mail", "bahmni_atom_feed", "bahmni_account", "account"],

    # always loaded
    'data': [
        'security/insurance_security.xml',
        'security/ir.model.access.csv',
        'views/insurance_views.xml',
        'views/quotation_view.xml',
        'views/insurance_odoo_product_map_view.xml',
        'views/insurance_claim.xml',
        'views/customer_view.xml',
        'report/insuree_consent_form.xml',
        'report/consent_form_template.xml',
        'wizard/eligibility_check_response.xml',
        'wizard/claim_fhir.xml',
        'views/insurance_settings_view.xml',
        'views/company_view.xml',
        'views/account_invoice_view.xml',
        'data/insurance_claim_data.xml',
        'report/claim_report.xml',
        'report/claim_patient_report.xml',
        'wizard/claim_summary.xml',
        'report/report_insurance_claim_summary_template.xml',
        'report/insurance_claim_summary_report.xml'
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo.xml',
    #],
    'installable': True,
    'auto_install': False,
    'application': True
}