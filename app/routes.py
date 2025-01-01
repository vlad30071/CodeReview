from flask import render_template, request, jsonify
from app import app
from app.database import get_db_connection


@app.route("/")
def index():
    conn = get_db_connection()
    events = conn.execute("SELECT id, title, description FROM events").fetchall()
    conn.close()
    return render_template("index.html", events=events)


@app.route("/events/<int:id>")
def event_details(id):
    conn = get_db_connection()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (id,)).fetchone()
    sessions = conn.execute(
        """
        SELECT session_date, ticket_status 
        FROM sessions 
        WHERE event_id = ?
        ORDER BY DATETIME(session_date) ASC
    """,
        (id,),
    ).fetchall()

    grouped_sessions = {}
    for session in sessions:
        date = session["session_date"].split(" ")[0]
        time = " ".join(session["session_date"].split(" ")[1:])
        if date not in grouped_sessions:
            grouped_sessions[date] = []
        grouped_sessions[date].append(
            {"time": time, "ticket_status": session["ticket_status"]}
        )

    conn.close()
    if event is None:
        return "Событие не найдено", 404
    return render_template("event_details.html", event=event, sessions=grouped_sessions)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        filter_name = request.form.get("filter_name", "").strip()
        filter_date = request.form.get("filter_date", "").strip()
        filter_tickets = request.form.get("filter_tickets") == "on"

        query = """
            SELECT events.id, events.title, events.description, GROUP_CONCAT(sessions.session_date || ' (' || sessions.ticket_status || ')', ', ') AS dates
            FROM events
            LEFT JOIN sessions ON events.id = sessions.event_id
            WHERE 1=1
        """
        params = []
        if filter_name:
            query += " AND events.title LIKE ?"
            params.append(f"%{filter_name}%")
        if filter_date:
            query += " AND DATE(sessions.session_date) = DATE(?)"
            params.append(filter_date)
        if filter_tickets:
            query += " AND sessions.ticket_status = 'доступны'"

        query += " GROUP BY events.id ORDER BY MIN(DATETIME(sessions.session_date)) ASC"

        conn = get_db_connection()
        events = conn.execute(query, params).fetchall()
        conn.close()

        if not events:
            return render_template(
                "search_results.html", events=None, query=filter_name or filter_date
            )
        return render_template(
            "search_results.html", events=events, query=filter_name or filter_date
        )

    return render_template("search.html")


@app.route("/get_events", methods=["GET"])
def get_events():
    filter_name = request.args.get("filter_name", None)
    filter_date = request.args.get("filter_date", None)
    filter_tickets = request.args.get("filter_tickets", "false").lower() == "true"

    query = """
        SELECT events.id, events.title, events.description, 
               GROUP_CONCAT(sessions.session_date || ' (' || sessions.ticket_status || ')', ', ') AS dates
        FROM events
        LEFT JOIN sessions ON events.id = sessions.event_id
        WHERE 1=1
    """
    params = []
    if filter_name:
        query += " AND events.title LIKE ?"
        params.append(f"%{filter_name}%")
    if filter_date:
        query += " AND DATE(sessions.session_date) = DATE(?)"
        params.append(filter_date)
    if filter_tickets:
        query += " AND sessions.ticket_status = 'доступны'"

    query += " GROUP BY events.id ORDER BY MIN(DATETIME(sessions.session_date)) ASC"

    conn = get_db_connection()
    events = conn.execute(query, params).fetchall()
    conn.close()

    formatted_events = []
    for row in events:
        dates = row[3].split(", ") if row[3] else []
        grouped_dates = {}
        for date_entry in dates:
            date, status = date_entry.split(" (")
            status = status.rstrip(")")
            date_key = date.split(" ")[0]
            time = " ".join(date.split(" ")[1:])
            if date_key not in grouped_dates:
                grouped_dates[date_key] = []
            grouped_dates[date_key].append({"time": time, "ticket_status": status})
        formatted_events.append(
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "dates": grouped_dates,
            }
        )

    return jsonify({"events": formatted_events})
