{
    "name": "Real State",
    "author": "Ahmed Saadawy",
    "summary": "Test Module for Real State",
    "version": "19.0.0.0",
    "data": [
        #security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        #views
        "views/estate_property_view.xml",
        "views/estate_property_type_view.xml",
        "views/estate_property_offer_view.xml",
        "views/estate_property_tag_view.xml",
        #menus
        "views/estate_menus.xml",

    ],
    "demo": [
        "demo/demo.xml"
    ],
    "depends": ['base', 'mail'],
    "application": True
}
