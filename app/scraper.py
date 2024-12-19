import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

MONTHS_RU = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}


def convert_date(date_string):
    try:
        if "-" in date_string:
            date_string = date_string.split("-")[0].strip()

        parts = date_string.split()

        if len(parts) == 4:
            day, month, year, time = parts
        elif len(parts) == 3:
            day, month, time = parts
            year = str(datetime.now().year)
        else:
            raise ValueError(f"Некорректный формат даты: {date_string}")

        month = MONTHS_RU.get(month.lower())
        if not month:
            raise ValueError(f"Некорректный месяц: {date_string}")

        return f"{year}-{month}-{day.zfill(2)} {time}"

    except Exception as e:
        raise ValueError(f"Ошибка преобразования даты: {date_string} - {e}")


def scrape_event(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при запросе данных: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    event_elements = soup.find_all(
        "div", class_="elem", attrs={"data-elem-type": "event"}
    )
    events = []

    for elem in event_elements:
        title_tag = elem.find("span", class_="underline")
        title = title_tag.text.strip() if title_tag else "Нет названия"

        description_tag = elem.find("div", class_="d")

        description = (
            description_tag.text.strip() if description_tag else "Нет описания"
        )

        sessions = []
        session_columns = elem.find_all("div", class_="session-column")
        for column in session_columns:
            session_links = column.find_all("a", class_="notUnderline")
            for link in session_links:
                session_date = link.find("span", class_="underline").text.strip()
                sibling = link.find_next_sibling("span")
                ticket_status = (
                    "нет"
                    if sibling and "мест нет" in sibling.text.lower()
                    else "доступны"
                )

                try:
                    session_date_iso = convert_date(session_date)
                except ValueError as e:
                    print(f"Ошибка преобразования даты: {e}")
                    continue

                if session_date_iso not in [s["дата"] for s in sessions]:
                    sessions.append({"дата": session_date_iso, "места": ticket_status})

        events.append({"Название": title, "Описание": description, "Сеансы": sessions})

    conn = sqlite3.connect("app/events.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            UNIQUE(title, description) -- Ограничение уникальности
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            session_date DATETIME,
            ticket_status TEXT,
            UNIQUE(event_id, session_date), -- Ограничение уникальности
            FOREIGN KEY(event_id) REFERENCES Events(id)
        )
    """
    )

    for event in events:
        cursor.execute(
            "INSERT OR IGNORE INTO Events (title, description) VALUES (?, ?)",
            (event["Название"], event["Описание"]),
        )
        event_id = cursor.execute(
            "SELECT id FROM Events WHERE title = ? AND description = ?",
            (event["Название"], event["Описание"]),
        ).fetchone()[0]

        for session in event["Сеансы"]:
            cursor.execute(
                """
                INSERT OR IGNORE INTO Sessions (event_id, session_date, ticket_status)
                VALUES (?, ?, ?)
                """,
                (event_id, session["дата"], session["места"]),
            )

    conn.commit()
    conn.close()


url = "https://quicktickets.ru/bratsk-dramteatr"
scrape_event(url)
