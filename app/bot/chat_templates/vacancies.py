from datetime import datetime
import re


def create_vacancies_template(vacancies_data):
    template = ""

    vacancies = vacancies_data
    if isinstance(vacancies_data, dict) and vacancies_data.get("items"):
        vacancies = vacancies_data["items"]
        found = vacancies_data.get("found", 0)
        template = f"<i>Найдено {found} вакансий</i>\n\n"

    for vacancy in vacancies:
        name = vacancy.get("name", "Без названия")
        city = vacancy.get("area", {}).get("name", "Не указан")
        employer = vacancy.get("employer", {}).get("name", "Не указан работодатель")

        # ---------- Salary ----------
        salary_info = vacancy.get("salary")
        if salary_info:
            s_from = salary_info.get("from")
            s_to = salary_info.get("to")
            currency = "RUB"

            fmt_from = f"{s_from:,}".replace(",", " ") if s_from else None
            fmt_to = f"{s_to:,}".replace(",", " ") if s_to else None

            if s_from and s_to:
                salary_text = f"От {fmt_from} до {fmt_to} {currency}"
            elif s_from:
                salary_text = f"От {fmt_from} {currency}"
            elif s_to:
                salary_text = f"До {fmt_to} {currency}"
            else:
                salary_text = "Не указана"
        else:
            salary_text = "Не указана"

        # ---------- Other ----------
        experience = vacancy.get("experience", {}).get("name", "Не указан")
        employment = vacancy.get("employment", {}).get("name", "Не указана")

        working_hours = (
            ", ".join([wh.get("name") for wh in vacancy.get("working_hours", [])])
            or "Не указаны"
        )

        work_format = (
            ", ".join([wf.get("name") for wf in vacancy.get("work_format", [])])
            or "Не указан"
        )

        requirements = vacancy.get("snippet", {}).get("requirement")
        if requirements:
            requirements = re.sub(r"</?highlighttext>", "", requirements)
        else:
            requirements = "Без требований"

        published_at = vacancy.get("published_at")
        if published_at:
            try:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_text = dt.strftime("%d.%m.%Y %H:%M")
            except Exception:
                published_text = published_at
        else:
            published_text = "Не указана"

        link = vacancy.get("alternate_url", "Ссылка не доступна")

        # ---------- Vacancy template ----------
        template += (
            f"📌 <b>Вакансия: {name} | {employer}</b>\n"
            f"💰 <b>Зарплата:</b> {salary_text}\n\n"
            f"🌆 Город: {city}\n"
            f"👔 Занятость: {employment}\n"
            f"🧾 Опыт работы: {experience}\n"
            f"🕒 Формат работы / часы: {work_format}, {working_hours}\n"
            f"📝 Требования: {requirements}\n"
            f"🔗 Смотреть вакансию: {link}\n"
            f"📅 <i>Опубликовано: {published_text}</i>\n\n"
            f"{'-' * 40}\n\n"
        )

    # ---------- Pagination ----------
    if (
        isinstance(vacancies_data, dict)
        and vacancies_data.get("page") is not None
        and vacancies_data.get("pages") is not None
    ):
        page = vacancies_data["page"] + 1
        pages = vacancies_data["pages"]
        template += f"<i>Страница {page}/{pages}</i>"

    return template
