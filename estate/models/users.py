from odoo import models, fields, api


class User(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'real.estate',
        'salesperson_id',
        domain=[('state', '=', 'new')],
    )
