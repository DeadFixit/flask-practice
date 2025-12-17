from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me-in-production"
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["DATABASE"] = os.path.join(app.instance_path, "citygreenhub.sqlite")

    site_meta = {
        "title": "City Green Hub",
        "tagline": "Практические решения по развитию зеленой инфраструктуры города",
        "contact_email": "contact@citygreenhub.example",
        "contact_phone": "+7 (495) 000-00-00",
        "address": "Москва, ул. Академическая, 10",
        "support_hours": "Пн-Пт с 9:00 до 18:00",
    }

    banner = {
        "headline": "Экосистемные сервисы для устойчивых городов",
        "subtext": (
            "Мы помогаем девелоперам, муниципалитетам и сообществам внедрять зелёные решения"
            " — от озеленения дворов до управления дождевыми водами."
        ),
    }

    article_sections: Dict[str, List[Dict[str, str]]] = {
        "Аналитика": [
            {
                "slug": "зелёные-крыши",
                "title": "Зелёные крыши как элемент климатической адаптации",
                "excerpt": "Что нужно учесть при проектировании зелёной кровли и как оценить её эффективность.",
                "content": (
                    "Зелёные крыши снижают тепловую нагрузку, повышают биоразнообразие и задерживают дождевые"
                    " воды. При выборе конструкции важно учитывать несущую способность здания, подбор субстрата"
                    " и схемы ухода. Дополнительный эффект дают модули с засухоустойчивыми растениями."
                ),
            },
            {
                "slug": "городские-деревья",
                "title": "Как подобрать деревья для плотной городской застройки",
                "excerpt": "Подбор пород, расчёт лунок и защитные меры против уплотнения почв.",
                "content": (
                    "Городские деревья сталкиваются с дефицитом влаги и загрязнением. При посадке важно"
                    " проектировать аэрационные каналы, использовать структурные грунты и предусматривать"
                    " защиту корневой зоны от техники. Породы нужно подбирать по устойчивости к засолению"
                    " и тепловым островам."
                ),
            },
            {
                "slug": "реабилитация-рек",
                "title": "Реабилитация малых рек: шаги для муниципалитетов",
                "excerpt": "Набор быстрых мер, которые можно запустить в течение одного сезона.",
                "content": (
                    "Базовый пакет работ включает очистку русел от мусора, восстановление прибрежной"
                    " растительности и внедрение природо-ориентированных береговых укреплений. Для"
                    " устойчивого результата необходим мониторинг качества воды и участие местных жителей"
                    " через волонтёрские программы."
                ),
            },
            {
                "slug": "сбор-дождевой-воды",
                "title": "Сбор дождевой воды для микрорайонов",
                "excerpt": "Малые системы задержания стока снижают нагрузку на ливнёвку и улучшают микроклимат.",
                "content": (
                    "Дождевые сады, биофильтры и перехватывающие канавы позволяют задержать часть осадков"
                    " на месте. Для расчётов используют коэффициент водонепроницаемости покрытия и"
                    " среднегодовой объём осадков. Важно предусмотреть обслуживание фильтрующих слоёв"
                    " и безопасный перепуск в сильные ливни."
                ),
            },
            {
                "slug": "общественное-участие",
                "title": "Как вовлекать жителей в проекты озеленения",
                "excerpt": "Рабочие механики соучастного проектирования и прозрачной отчётности.",
                "content": (
                    "Эффективное вовлечение строится на ранних интервью с сообществами, визуализациях"
                    " решений и регулярных отчётных встречах. Цифровая карта инициатив и открытые данные"
                    " о бюджете повышают доверие. Для поддержки ухода за зелёными объектами подходят"
                    " микро-гранты и календарь совместных работ."
                ),
            },
        ],
        "Практики": [
            {
                "slug": "пилотные-дворы",
                "title": "Пилотные дворы с устойчивым озеленением",
                "excerpt": "Как запускать небольшие демонстрационные участки и масштабировать решения.",
                "content": (
                    "Пилоты помогают протестировать новые материалы, схемы ухода и взаимодействие с"
                    " подрядчиками. Важно фиксировать метрики: снижение пыли, уровень шума, отзывы жителей."
                    " Успешные схемы масштабируются через типовые проектные решения и обученные команды."
                ),
            },
            {
                "slug": "пермакультура",
                "title": "Пермакультурные подходы в городской среде",
                "excerpt": "Сочетание съедобных ландшафтов и декоративных зон без лишнего ухода.",
                "content": (
                    "Пермакультурные принципы позволяют создать самоподдерживающиеся посадки с"
                    " минимальными затратами. Мульчирование, компостирование на месте и подбор растений"
                    " по ярусам сокращают полив и борьбу с сорняками."
                ),
            },
            {
                "slug": "звукоизоляция-зеленью",
                "title": "Шумозащитные посадки вдоль магистралей",
                "excerpt": "Грамотно подобранные полосы зелёных насаждений снижают шум на 5-7 дБ.",
                "content": (
                    "Комбинация кустарников и деревьев с плотной кроной снижает шумовое воздействие."
                    " Эффективны полосы шириной от 15 метров с чередованием вечнозелёных и лиственных"
                    " пород. Регулярная санитарная обрезка поддерживает плотность кроны."
                ),
            },
            {
                "slug": "инфраструктура-водоотведения",
                "title": "Природные решения для водоотведения",
                "excerpt": "Биоинженерные каналы и фильтрующие ландшафты против перегрузки ливнёвки.",
                "content": (
                    "Гибридные системы сочетают открытые каналы с фильтрующими субстратами и"
                    " водопроницаемыми покрытиями. Они снижают расходы на коллекторы и улучшают"
                    " качество воды."
                ),
            },
            {
                "slug": "мониторинг-зелени",
                "title": "Цифровой мониторинг зелёных насаждений",
                "excerpt": "Дроны, датчики влажности и публичные панели для контроля состояния зелёных зон.",
                "content": (
                    "Системы мониторинга позволяют планировать уход, прогнозировать риски и вовлекать"
                    " жителей. Важно обеспечить защиту данных, интеграцию с городскими ГИС и удобный"
                    " интерфейс для подрядчиков."
                ),
            },
        ],
    }

    seed_news: List[Dict[str, str]] = [
        {
            "id": 1,
            "title": "Новый гид по микро-климату двориков",
            "date": "2024-05-18",
            "summary": "Опубликован набор решений по уменьшению перегрева общественных пространств летом.",
            "author": "editor@citygreenhub.example",
        },
        {
            "id": 2,
            "title": "Вебинар по городским лесам",
            "date": "2024-06-02",
            "summary": "Обсуждаем стандарты ухода, мониторинг и вовлечение волонтёров.",
            "author": "editor@citygreenhub.example",
        },
        {
            "id": 3,
            "title": "Пилот биофильтрации стока",
            "date": "2024-06-15",
            "summary": "В одном из районов запущен демонстрационный участок с фильтрующими канавами.",
            "author": "admin@citygreenhub.example",
        },
        {
            "id": 4,
            "title": "Руководство по стандартам ГОСТ 34.602-2020",
            "date": "2024-06-28",
            "summary": "Подготовлена шпаргалка по структуре технического задания для цифровых проектов.",
            "author": "admin@citygreenhub.example",
        },
        {
            "id": 5,
            "title": "Программа микро-грантов",
            "date": "2024-07-01",
            "summary": "Открыт набор заявок на проекты по озеленению дворов с участием жителей.",
            "author": "editor@citygreenhub.example",
        },
    ]

    resources = [
        {
            "name": "Методичка по зелёным крышам",
            "description": "Пошаговые рекомендации по проектированию и сопровождению зелёных кровель.",
            "link": "https://example.com/green-roof-guide",
        },
        {
            "name": "Чек-лист по биофильтрам",
            "description": "Контрольные точки для приёмки объектов водоотведения.",
            "link": "https://example.com/biofilter-checklist",
        },
        {
            "name": "Шаблон карты стейкхолдеров",
            "description": "Помогает фиксировать роли участников проектов озеленения.",
            "link": "https://example.com/stakeholder-map",
        },
        {
            "name": "Калькулятор углеродного эффекта",
            "description": "Базовые расчёты по поглощению CO2 зелёными насаждениями.",
            "link": "https://example.com/carbon-calculator",
        },
        {
            "name": "Дорожная карта внедрения",
            "description": "Последовательность шагов для запуска программы зелёной инфраструктуры в городе.",
            "link": "https://example.com/roadmap",
        },
    ]

    seed_users = [
        {
            "email": "admin@citygreenhub.example",
            "password": "adminpass",
            "role": "admin",
        },
        {
            "email": "editor@citygreenhub.example",
            "password": "editorpass",
            "role": "editor",
        },
    ]

    def get_db():
        if "db" not in g:
            connection = sqlite3.connect(app.config["DATABASE"])
            connection.row_factory = sqlite3.Row
            g.db = connection
        return g.db

    def init_db():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                summary TEXT NOT NULL,
                author TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created TEXT NOT NULL
            );
            """
        )

        existing_users = {
            row["email"] for row in db.execute("SELECT email FROM users").fetchall()
        }
        for seed in seed_users:
            if seed["email"] not in existing_users:
                db.execute(
                    "INSERT INTO users (email, password, role, created_at) VALUES (?, ?, ?, ?)",
                    (
                        seed["email"],
                        seed["password"],
                        seed["role"],
                        datetime.utcnow().isoformat(),
                    ),
                )

        has_news = db.execute("SELECT COUNT(*) as c FROM news").fetchone()["c"]
        if has_news == 0:
            for item in seed_news:
                db.execute(
                    "INSERT INTO news (title, date, summary, author) VALUES (?, ?, ?, ?)",
                    (item["title"], item["date"], item["summary"], item["author"]),
                )
        db.commit()

    @app.cli.command("reset-db")
    def reset_db_command():
        """Reset SQLite database and seed users/news again."""

        db_path = app.config.get("DATABASE")
        existing_conn = g.pop("db", None)
        if existing_conn:
            existing_conn.close()

        if db_path and os.path.exists(db_path):
            os.remove(db_path)

        init_db()
        print(f"Database reset and seeded at {db_path}.")

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def fetch_news():
        rows = get_db().execute(
            "SELECT id, title, date, summary, author FROM news ORDER BY date(date) DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def fetch_news_item(news_id: int):
        row = (
            get_db()
            .execute("SELECT id, title, date, summary, author FROM news WHERE id = ?", (news_id,))
            .fetchone()
        )
        return dict(row) if row else None

    def current_user():
        user_email = session.get("user")
        if user_email:
            row = (
                get_db()
                .execute("SELECT email, role FROM users WHERE email = ?", (user_email,))
                .fetchone()
            )
            if row:
                return {"email": row["email"], "role": row["role"]}
        return None

    def login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user():
                flash("Требуется авторизация для просмотра страницы.", "warning")
                return redirect(url_for("login", next=request.path))
            return func(*args, **kwargs)

        return wrapper

    def roles_required(*roles):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = current_user()
                if not user:
                    flash("Требуется авторизация для выполнения действия.", "warning")
                    return redirect(url_for("login", next=request.path))
                if user["role"] not in roles:
                    abort(403)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @app.context_processor
    def inject_globals():
        return {
            "site_meta": site_meta,
            "nav_links": [
                ("Главная", "index"),
                ("О проекте", "about"),
                ("Решения", "services"),
                ("Статьи", "articles"),
                ("Практики", "practices"),
                ("Ресурсы", "resources_page"),
                ("Новости", "news_page"),
                ("Контакты", "contact"),
            ],
            "current_user": current_user(),
        }

    @app.route("/")
    def index():
        return render_template(
            "home.html",
            banner=banner,
            news=fetch_news(),
            sections=article_sections,
        )

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/services")
    def services():
        return render_template("services.html")

    @app.route("/articles")
    def articles():
        return render_template("articles.html", sections=article_sections)

    @app.route("/practices")
    def practices():
        return render_template("practices.html", practices=article_sections.get("Практики", []))

    @app.route("/articles/<slug>")
    def article_detail(slug: str):
        for group in article_sections.values():
            for article in group:
                if article["slug"] == slug:
                    return render_template("article_detail.html", article=article)
        abort(404)

    @app.route("/resources")
    def resources_page():
        return render_template("resources.html", resources=resources)

    @app.route("/news")
    def news_page():
        return render_template("news.html", news=fetch_news())

    @app.route("/manage/news", methods=["GET", "POST"])
    @roles_required("admin", "editor")
    def manage_news():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            date = request.form.get("date", "").strip()
            summary = request.form.get("summary", "").strip()
            if not (title and date and summary):
                flash("Заполните все поля для публикации новости.", "danger")
            else:
                db = get_db()
                db.execute(
                    "INSERT INTO news (title, date, summary, author) VALUES (?, ?, ?, ?)",
                    (title, date, summary, current_user()["email"]),
                )
                db.commit()
                flash("Новость добавлена.", "success")
                return redirect(url_for("manage_news"))
        return render_template("manage_news.html", news_items=fetch_news())

    @app.route("/manage/news/<int:news_id>/edit", methods=["GET", "POST"])
    @roles_required("admin", "editor")
    def edit_news(news_id: int):
        user = current_user()
        item = fetch_news_item(news_id)
        if not item:
            abort(404)
        if user["role"] != "admin" and user["email"] != item.get("author"):
            abort(403)
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            date = request.form.get("date", "").strip()
            summary = request.form.get("summary", "").strip()
            if not (title and date and summary):
                flash("Все поля обязательны для обновления.", "danger")
            else:
                db = get_db()
                db.execute(
                    "UPDATE news SET title = ?, date = ?, summary = ? WHERE id = ?",
                    (title, date, summary, news_id),
                )
                db.commit()
                flash("Новость обновлена.", "success")
                return redirect(url_for("manage_news"))
        return render_template(
            "manage_news.html", news_items=fetch_news(), active_item=fetch_news_item(news_id)
        )

    @app.route("/manage/news/<int:news_id>/delete", methods=["POST"])
    @roles_required("admin")
    def delete_news(news_id: int):
        db = get_db()
        deleted = db.execute("DELETE FROM news WHERE id = ?", (news_id,)).rowcount
        db.commit()
        if deleted:
            flash("Новость удалена.", "info")
        else:
            flash("Новость не найдена.", "warning")
        return redirect(url_for("manage_news"))

    @app.route("/search")
    def search():
        query = request.args.get("q", "").strip().lower()
        results = []
        if query:
            for group_name, group in article_sections.items():
                for article in group:
                    haystack = f"{article['title']} {article['excerpt']} {article['content']}".lower()
                    if query in haystack:
                        results.append({"article": article, "section": group_name})
            for item in fetch_news():
                haystack = f"{item['title']} {item['summary']}".lower()
                if query in haystack:
                    results.append({"news": item, "section": "Новости"})
        return render_template("search.html", query=query, results=results)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            message_text = request.form.get("message", "").strip()
            if not (name and email and message_text):
                flash("Заполните все поля, пожалуйста.", "danger")
            else:
                db = get_db()
                db.execute(
                    "INSERT INTO messages (name, email, message, created) VALUES (?, ?, ?, ?)",
                    (
                        name,
                        email,
                        message_text,
                        datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    ),
                )
                db.commit()
                flash("Сообщение отправлено. Мы свяжемся с вами в течение рабочего дня.", "success")
                return redirect(url_for("contact"))
        return render_template("contact.html")

    @app.route("/messages")
    @roles_required("admin", "editor")
    def view_messages():
        rows = get_db().execute(
            "SELECT id, name, email, message, created FROM messages ORDER BY id DESC"
        ).fetchall()
        return render_template("messages.html", messages=[dict(row) for row in rows])

    @app.route("/messages/<int:message_id>/delete", methods=["POST"])
    @roles_required("admin")
    def delete_message(message_id: int):
        db = get_db()
        deleted = db.execute("DELETE FROM messages WHERE id = ?", (message_id,)).rowcount
        db.commit()
        if deleted:
            flash("Сообщение удалено.", "info")
        else:
            flash("Сообщение не найдено.", "warning")
        return redirect(url_for("view_messages"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        next_url = request.args.get("next", url_for("index"))
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            user_record = (
                get_db()
                .execute("SELECT email, password, role FROM users WHERE email = ?", (email,))
                .fetchone()
            )
            if user_record and user_record["password"] == password:
                session["user"] = email
                flash("Вход выполнен", "success")
                return redirect(next_url)
            flash("Неверные учётные данные", "danger")
        return render_template("login.html", next_url=next_url)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "").strip()
            if not (email and password):
                flash("Введите e-mail и пароль.", "danger")
            elif (
                get_db()
                .execute("SELECT 1 FROM users WHERE email = ?", (email,))
                .fetchone()
            ):
                flash("Пользователь с таким e-mail уже существует.", "warning")
            else:
                db = get_db()
                db.execute(
                    "INSERT INTO users (email, password, role, created_at) VALUES (?, ?, ?, ?)",
                    (email, password, "member", datetime.utcnow().isoformat()),
                )
                db.commit()
                session["user"] = email
                flash("Регистрация успешна. У вас роль 'member'.", "success")
                return redirect(url_for("index"))
        return render_template("register.html")

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        flash("Вы вышли из аккаунта.", "info")
        return redirect(url_for("index"))

    @app.route("/sitemap")
    def sitemap():
        pages = [
            ("Главная", url_for("index")),
            ("О проекте", url_for("about")),
            ("Решения", url_for("services")),
            ("Статьи", url_for("articles")),
            ("Практики", url_for("practices")),
            ("Ресурсы", url_for("resources_page")),
            ("Новости", url_for("news_page")),
            ("Контакты", url_for("contact")),
            ("Поиск", url_for("search")),
            ("Вход", url_for("login")),
            ("Регистрация", url_for("register")),
        ]
        return render_template("sitemap.html", pages=pages)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
