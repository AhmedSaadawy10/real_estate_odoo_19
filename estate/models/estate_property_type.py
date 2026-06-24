from odoo import models, fields, api
from odoo.tools.translate import _


class EstimatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = "sequence, name"
    _sql_constraints = [
        ('unique_property_type_name', 'UNIQUE(name)', 'The Property Type name must be Unique'),
    ]

    sequence = fields.Integer(default=1)
    name = fields.Char(required=True)
    property_ids = fields.One2many('real.estate', 'property_type_id')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count', store=True)
    property_count = fields.Integer(compute='_compute_property_count', store=True)

# =================================================================
    # crud operations
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for vals in vals_list:
            self.env['estate.property.tag'].create(
                {
                    "name": vals.get('name'),
                }
            )
        return res

    def unlink(self):
        self.property_ids.state = 'canceled'
        return super().unlink()

    # Create action open property_ids
    def action_open_property_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related properties'),
            'res_model': 'real.estate',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('property_type_id', '=', self.id)],
            'context': {"default_property_type_id": self.id, }
        }

    def action_open_offer_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related properties'),
            'res_model': 'estate.property.offer',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('property_type_id', '=', self.id)],
            'context': {"default_property_type_id": self.id, }
        }

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)
