from odoo import models, fields, Command


class ImportedPosition(models.Model):
    _name = "position.imported"
    _description = "Imported Position"
    _order = "imported_at desc"

    name = fields.Char(
        string="Position",
        required=True,
        readonly=True
    )

    external_position_id = fields.Integer(
        string="Position ID",
        readonly=True
    )

    vacancies_count = fields.Integer(
        string="Vacancies",
        readonly=True
    )

    applications_count = fields.Integer(
        string="Applications",
        readonly=True
    )

    average_applications = fields.Float(
        string="Average applications",
        readonly=True
    )

    min_applications = fields.Integer(
        string="Min applications",
        readonly=True
    )

    max_applications = fields.Integer(
        string="Max applications",
        readonly=True
    )

    imported_at = fields.Datetime(
        string="Imported at",
        readonly=True
    )

    attribute_ids = fields.One2many(
        "position.import.attribute",
        "position_id",
        string="Attributes",
        readonly=True
    )

    vacancy_ids = fields.One2many(
        "position.import.vacancy",
        "position_id",
        string="Vacancies",
        readonly=True
    )

    _sql_constraints = [
        (
            "unique_external_position",
            "unique(external_position_id)",
            "Position is already imported."
        )
    ]


class ImportedAttribute(models.Model):
    _name = "position.import.attribute"
    _description = "Imported Position Attribute"
    _order = "title"

    position_id = fields.Many2one(
        "position.imported",
        string="Position",
        required=True,
        ondelete="cascade"
    )

    title = fields.Char(
        string="Attribute",
        required=True,
        readonly=True
    )

    attribute_type = fields.Char(
        string="Type",
        readonly=True
    )

    average = fields.Float(
        string="Average",
        readonly=True
    )

    min_value = fields.Float(
        string="Min",
        readonly=True
    )

    max_value = fields.Float(
        string="Max",
        readonly=True
    )

    popular_value_ids = fields.One2many(
        "position.import.popular.value",
        "attribute_id",
        string="Popular values",
        readonly=True
    )


class ImportedPopularValue(models.Model):
    _name = "position.import.popular.value"
    _description = "Imported Popular Value"
    _order = "count desc"

    attribute_id = fields.Many2one(
        "position.import.attribute",
        string="Attribute",
        required=True,
        ondelete="cascade"
    )

    value = fields.Char(
        string="Value",
        readonly=True
    )

    count = fields.Integer(
        string="Count",
        readonly=True
    )


class ImportedVacancy(models.Model):
    _name = "position.import.vacancy"
    _description = "Imported Vacancy"
    _order = "title"

    position_id = fields.Many2one(
        "position.imported",
        string="Position",
        required=True,
        ondelete="cascade"
    )

    external_vacancy_id = fields.Char(
        string="Vacancy ID",
        readonly=True
    )

    title = fields.Char(
        string="Title",
        required=True,
        readonly=True
    )

    description = fields.Text(
        string="Description",
        readonly=True
    )

    applications_count = fields.Integer(
        string="Applications",
        readonly=True
    )