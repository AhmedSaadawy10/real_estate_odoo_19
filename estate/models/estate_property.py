import requests

from odoo import models, fields, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class RealState(models.Model):
    _name = 'real.estate'
    _description = 'Real EState'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'The Selling price must be strictly positive'),
    ]

    # active = fields.Boolean(default=True, invisible=True)
    name = fields.Char(default="House", required=True)
    price = fields.Integer()
    state = fields.Selection([
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
    ],
        default='new',
        required=True,
        copy=False,
    )
    postcode = fields.Char()

    def _default_date(self):
        today = fields.Date.today()
        # Add 3 months to the current date
        three_months_from_today = today + relativedelta(months=3)
        return three_months_from_today

    date_availability = fields.Date(default=_default_date, copy=False)
    expected_price = fields.Float()
    best_offer = fields.Float()
    selling_price = fields.Float(readonly=True, copy=False)

    description = fields.Text()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('east', 'East'),
        ('south', 'South'),
        ('west', 'West'),
    ])

    # Many2one relation fields
    property_type_id = fields.Many2one('estate.property.type')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    salesperson_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)

    # One2many Relation fields
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offer')

    # many2many Relation fields
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    # computed fields
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Integer(compute='_compute_best_price')

    # ================================================================
    # crud operation
    @api.ondelete(at_uninstall=False)
    def check_state_before_delete(self):
        for rec in self:
            if rec.state not in ('new', 'canceled'):
                raise ValidationError(_("You can not delete an offer in state %s") % self.state)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if not record.offer_ids:
                record.best_price = 0
            else:
                record.best_price = max(record.offer_ids.mapped('price'))

    @api.onchange('garden')
    def _onchange_garden(self):
        for estate in self:
            if estate.garden:
                estate.garden_area = 10
                estate.garden_orientation = 'north'
            else:
                estate.garden_area = 0
                estate.garden_orientation = ''

    @api.onchange('date_availability')
    def _onchange_date_availability(self):
        for estate in self:
            if estate.date_availability < fields.Date.today():
                return {
                    "warning": {
                        "title": "Invalid date",
                        "message": "The date must be in the future",
                    }
                }

    def action_sold(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('A canceled property cannot be sold again.')
            record.state = 'sold'

    def action_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('A sold property cannot be canceled.')
            record.state = 'canceled'

    #integrate with third party app
    def get_properties(self):
        payload = dict()
        try:
            response = requests.get('http://localhost:8016/api/test', data=payload)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as e:
            print(e)
