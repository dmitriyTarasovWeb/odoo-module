{
    "name": "Position Import",
    "version": "1.0.0",
    "category": "Human Resources",
    "summary": "Import positions from course application",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/position_views.xml",
        "views/import_wizard_views.xml",
    ],
    "installable": True,
    "application": True,
}