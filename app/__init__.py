import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dues_paid = db.Column(db.Boolean, default=False, nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint("member_id", "event_id"),)


def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.getenv(
        "DATABASE_URL", "sqlite:///clubiset.db"
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", version=os.getenv("APP_VERSION", "dev")), 200
        except Exception:
            return jsonify(status="db_error"), 503

    @app.post("/members")
    def add_member():
        data = request.get_json(force=True)
        if Member.query.filter_by(email=data["email"]).first():
            return jsonify(error="email déjà utilisé"), 409
        m = Member(name=data["name"], email=data["email"])
        db.session.add(m)
        db.session.commit()
        return jsonify(id=m.id, name=m.name, dues_paid=m.dues_paid), 201

    @app.get("/members")
    def list_members():
        return jsonify([
            {"id": m.id, "name": m.name, "email": m.email, "dues_paid": m.dues_paid}
            for m in Member.query.all()
        ])

    @app.post("/members/<int:member_id>/dues")
    def pay_dues(member_id):
        m = db.get_or_404(Member, member_id)
        m.dues_paid = True
        db.session.commit()
        return jsonify(id=m.id, dues_paid=True)

    @app.post("/events")
    def add_event():
        data = request.get_json(force=True)
        e = Event(title=data["title"],
                  date=datetime.fromisoformat(data["date"]),
                  capacity=data["capacity"])
        db.session.add(e)
        db.session.commit()
        return jsonify(id=e.id, title=e.title), 201

    @app.get("/events")
    def list_events():
        return jsonify([
            {"id": e.id, "title": e.title, "date": e.date.isoformat(),
             "capacity": e.capacity,
             "registered": Registration.query.filter_by(event_id=e.id).count()}
            for e in Event.query.all()
        ])

    @app.post("/events/<int:event_id>/register")
    def register(event_id):
        event = db.get_or_404(Event, event_id)
        member = db.get_or_404(Member, request.get_json(force=True)["member_id"])

        if not member.dues_paid:
            return jsonify(error="cotisation non payée"), 403
        if Registration.query.filter_by(member_id=member.id, event_id=event.id).first():
            return jsonify(error="déjà inscrit"), 409
        if Registration.query.filter_by(event_id=event.id).count() >= event.capacity:
            return jsonify(error="événement complet"), 409

        db.session.add(Registration(member_id=member.id, event_id=event.id))
        db.session.commit()
        return jsonify(status="inscrit"), 201

    return app