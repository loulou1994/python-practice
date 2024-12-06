import sqlalchemy.orm as so
import sqlalchemy as sa
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from typing import Optional
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy.sql.functions import now

load_dotenv()  # take environment variables


app = Flask(__name__)

app.config["SECRET_KEY"] = "just random character set for the secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")
    def __repr__(self):
        return "<User {}>".format(self.username)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return '<Post {}>'.format(self.body)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.shell_context_processor
def make_shell_ctx():
    return {"app": app, "db": db, "User": User, "Post": Post, "sa": sa, "so": sa}
