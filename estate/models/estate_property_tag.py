from odoo import models, fields


class PropertyTags(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = "name"
    _sql_constraints = [
        ('unique_property_tag_name', 'UNIQUE(name)', 'The Property Tag name must be Unique'),

    ]

    name = fields.Char(required=True)
    color = fields.Integer()

