from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import psycopg2
from psycopg2.errors import UniqueViolation
from psycopg2.extras import NamedTupleCursor
import validators

from page_analyzer.utils import send_request, parse_response


app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(database_url, sslmode="disable", cursor_factory=NamedTupleCursor)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/urls")
def get_urls():
    with conn.cursor() as cursor:
        sql = """
            SELECT DISTINCT
                u.id,
                u.name,
                FIRST_VALUE(c.created_date) OVER (PARTITION BY u.id ORDER BY c.created_date DESC) AS check_date,
                FIRST_VALUE(c.response_code) OVER (PARTITION BY u.id ORDER BY c.created_date DESC) AS check_code
            FROM urls u
            JOIN checks c ON u.id = c.url_id
            ORDER BY u.id DESC
        """
        cursor.execute(sql)
        rs = cursor.fetchall()
    conn.commit()
    urls = [{
        "id": r.id,
        "name": r.name,
        "check_date": r.check_date,
        "check_code": r.check_code,
    } for r in rs]
    return render_template(
        "urls.html",
        urls=urls,
    )


@app.post("/urls")
def post_urls():
    url = request.form.get("url")
    # TODO: add validation for url: must contain scheme
    if not validators.url(url):
        return render_template(
            "index.html",
            url=url,
        ), 422
    else:
        url_parsed = urlparse(url)
        url_normalized = f"{url_parsed.scheme}://{url_parsed.netloc}"
        try:
            with conn.cursor() as cursor:
                sql_insert = "INSERT INTO urls (name) VALUES (%s) RETURNING id;"
                cursor.execute(sql_insert, (url_normalized,))
                r = cursor.fetchone()

            conn.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for("get_url", id=r.id))
        except UniqueViolation as e:
            print(e)
            conn.rollback()

            with conn.cursor() as cursor:
                sql = "SELECT * FROM urls WHERE name=%s"
                cursor.execute(sql, (url_normalized,))
                r = cursor.fetchone()

            conn.commit()
            flash('Страница уже существует!', 'success')  # TODO: use another type, duplicate?
            return redirect(url_for("get_url", id=r.id))


@app.get("/urls/<id>")
def get_url(id):
    print("id: ", id)
    messages = get_flashed_messages(with_categories=True)
    with conn.cursor() as cursor:
        sql = "SELECT * FROM urls WHERE id=%s"
        cursor.execute(sql, (id,))
        r = cursor.fetchone()
        url = {
            "id": r.id,
            "name": r.name,
            "created_at": r.created_at,
            "created_date": r.created_at.date(),
        }
    conn.commit()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM checks WHERE url_id=%s ORDER BY id DESC"
        cursor.execute(sql, (id,))
        rs = cursor.fetchall()
        checks = [{
            "id": r.id,
            "response_code": r.response_code,
            "h1": r.h1,
            "title": r.title,
            "description": r.description,
            "created_date": r.created_date,
        } for r in rs]
    return render_template(
        "url.html",
        url=url,
        messages=messages,
        checks=checks,
    )


@app.post("/urls/<id>/checks")
def post_url_check(id):
    with conn.cursor() as cursor:
        sql = "SELECT name FROM urls WHERE id=%s"
        cursor.execute(sql, (id,))
        r = cursor.fetchone()
    url = r.name
    response = send_request(url)
    check = parse_response(response)
    check["url_id"] = id
    print("Check: ", check)
    if check["response_code"] != 200:
        flash("Произошла ошибка при проверке", "error")
        return redirect(url_for("get_url", id=id))
    else:
        with conn.cursor() as cursor:
            try:
                sql = """
                        INSERT INTO checks (response_code, h1, title, description, url_id)
                        VALUES (%(response_code)s, %(h1)s, %(title)s, %(description)s, %(url_id)s);
                """
                cursor.execute(sql, check)
                conn.commit()
                return redirect(url_for("get_url", id=id))
            except psycopg2.Error as e:
                print("Got error from psycopg2: ", e)
                conn.rollback()
                flash("Произошла ошибка при проверке", "error")   # TODO: this is error when inserting to PG, use another message?
                return redirect(url_for("get_url", id=id))
