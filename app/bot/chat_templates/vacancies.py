from datetime import datetime
import re


def create_vacancies_template(vacancies_data):
    template = ""

    if vacancies_data.get("items"):
        vacancies = vacancies_data.get("items")
        template = f"<i>Найдено {vacancies_data.get('found')} вакансий</i>\n\n"
    else:
        vacancies = vacancies_data

    for vacancy in vacancies:
        name = vacancy.get("name", "Без названия")
        city = vacancy.get("area", {}).get("name", "Не указан")

        salary_info = vacancy.get("salary")
        if salary_info:
            salary_from = salary_info.get("from")
            salary_to = salary_info.get("to")
            currency = "RUB"

            salary_from_fmt = (
                f"{salary_from:,}".replace(",", " ") if salary_from else None
            )
            salary_to_fmt = f"{salary_to:,}".replace(",", " ") if salary_to else None

            if salary_from and salary_to:
                salary_text = f"От {salary_from_fmt} до {salary_to_fmt} {currency}"
            elif salary_from:
                salary_text = f"От {salary_from_fmt} {currency}"
            elif salary_to:
                salary_text = f"До {salary_to_fmt} {currency}"
            else:
                salary_text = "Не указана"
        else:
            salary_text = "Не указана"

        experience = vacancy.get("experience", {}).get("name", "Не указан")
        employment = vacancy.get("employment", {}).get("name", "Не указана")
        working_hours = (
            ", ".join([wh.get("name") for wh in vacancy.get("working_hours", [])])
            or "Не указаны"
        )

        published_at = vacancy.get("published_at")
        if published_at:
            try:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_text = dt.strftime("%d.%m.%Y %H:%M")
            except Exception:
                published_text = published_at
        else:
            published_text = "Не указана"

        employer = vacancy.get("employer", {}).get("name", "Не указан работодатель")
        work_format = (
            ", ".join([wf.get("name") for wf in vacancy.get("work_format", [])])
            or "Не указан"
        )
        requirements = vacancy.get("snippet", {}).get("requirement", "")
        requirements = re.sub(
            r"</?highlighttext>",
            "",
            requirements if requirements is not None else "Без требований",
        )
        link = vacancy.get("alternate_url", "Ссылка не доступна")

        vacancy_text = (
            f"📌 <b>Вакансия: {name} | {employer}</b>\n"
            f"💰 <b>Зарплата: {salary_text}\n\n</b>"
            f"🌆 Город: {city}\n"
            f"👔 Занятость: {employment}\n"
            f"🧾 Опыт работы: {experience}\n"
            f"🕒 Формат работы / часы: {work_format}, {working_hours}\n"
            f"📝 Требования: {requirements}\n"
            f"🔗 Смотреть вакансию: {link}\n"
            f"📅 <i>Опубликовано: {published_text}</i>\n\n"
            f"{'-' * 40}\n\n"
        )

        template += vacancy_text

    if vacancies_data.get("page") or vacancies_data.get("pages"):
        return (
            template
            + f"<i>Страница {vacancies_data.get('page') + 1}/{vacancies_data.get('pages')}</i>"
        )

    return template
