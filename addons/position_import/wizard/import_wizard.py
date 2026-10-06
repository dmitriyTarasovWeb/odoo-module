from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
import urllib3


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


class PositionImportWizard(models.TransientModel):
    _name = "position.import.wizard"
    _description = "Import Position from API"

    api_token = fields.Char(
        string="API Token",
        required=True
    )

    def action_import(self):
        self.ensure_one()

        api_url = "https://host.docker.internal:7206/api/positions/results"

        try:
            response = requests.get(
                api_url,
                params={
                    "token": self.api_token
                },
                timeout=15,
                verify=False
            )
        except requests.RequestException as e:
            raise UserError(
                _("Could not connect to ASP.NET API:\n%s") % e
            )

        if response.status_code == 401:
            raise UserError(_("Invalid API token."))

        if response.status_code != 200:
            raise UserError(
                _("ASP.NET API returned HTTP %s:\n%s")
                % (response.status_code, response.text)
            )

        try:
            data = response.json()
        except ValueError:
            raise UserError(
                _("ASP.NET API returned invalid JSON.")
            )

        position = data.get("position")

        if not position:
            raise UserError(
                _("API response does not contain position data.")
            )

        position_id = position.get("id")
        position_name = position.get("name")

        if position_id is None or not position_name:
            raise UserError(
                _("API response contains invalid position data.")
            )

        statistics = data.get("statistics") or {}

        vacancies_count = int(
            statistics.get("vacanciesCount") or 0
        )

        applications_count = int(
            statistics.get("applicationsCount") or 0
        )

        average_applications = float(
            statistics.get("averageApplicationsPerVacancy") or 0
        )

        min_applications = int(
            statistics.get("minApplicationsPerVacancy") or 0
        )

        max_applications = int(
            statistics.get("maxApplicationsPerVacancy") or 0
        )

        imported_position = self.env[
            "position.imported"
        ].sudo().search(
            [
                (
                    "external_position_id",
                    "=",
                    position_id
                )
            ],
            limit=1
        )

        position_values = {
            "name": position_name,
            "external_position_id": position_id,
            "vacancies_count": vacancies_count,
            "applications_count": applications_count,
            "average_applications": average_applications,
            "min_applications": min_applications,
            "max_applications": max_applications,
            "imported_at": fields.Datetime.now(),
        }

        if imported_position:
            imported_position.write(position_values)

            imported_position.attribute_ids.sudo().unlink()
            imported_position.vacancy_ids.sudo().unlink()
        else:
            imported_position = self.env[
                "position.imported"
            ].sudo().create(position_values)

        attributes = data.get("attributes") or []

        for attribute in attributes:
            attribute_record = self.env[
                "position.import.attribute"
            ].sudo().create({
                "position_id": imported_position.id,
                "title": attribute.get("title") or "",
                "attribute_type": attribute.get("type") or "",
                "average": float(attribute["average"])
                if attribute.get("average") is not None
                else 0,
                "min_value": float(attribute["min"])
                if attribute.get("min") is not None
                else 0,
                "max_value": float(attribute["max"])
                if attribute.get("max") is not None
                else 0,
            })

            popular_values = attribute.get("popularValues") or []

            for popular_value in popular_values:
                self.env[
                    "position.import.popular.value"
                ].sudo().create({
                    "attribute_id": attribute_record.id,
                    "value": str(
                        popular_value.get("value") or ""
                    ),
                    "count": int(
                        popular_value.get("count") or 0
                    ),
                })

        vacancies = data.get("vacancies") or []

        for vacancy in vacancies:
            self.env[
                "position.import.vacancy"
            ].sudo().create({
                "position_id": imported_position.id,
                "external_vacancy_id": str(
                    vacancy.get("id") or ""
                ),
                "title": vacancy.get("title") or "",
                "description": vacancy.get("description") or "",
                "applications_count": int(
                    vacancy.get("applicationsCount") or 0
                ),
            })

        return {
            "type": "ir.actions.act_window",
            "name": _("Imported Position"),
            "res_model": "position.imported",
            "view_mode": "form",
            "res_id": imported_position.id,
            "target": "current",
        }