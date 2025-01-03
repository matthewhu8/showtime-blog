from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

class CreatePostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField('Submit')
@app.route('/')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/delete')
def delete_post(title):
    pass


@app.route('/edit-post/<string:title>', methods=['GET', 'POST'])
def edit_post(title):
    postToEdit = db.session.execute(db.select(BlogPost).filter_by(title=title)).scalar()
    edit_form = CreatePostForm(
        title=postToEdit.title,
        subtitle=postToEdit.subtitle,
        author=postToEdit,
        img_url=postToEdit.img_url,
        body=postToEdit.body
    )
    if edit_form.validate_on_submit():
        postToEdit.title = edit_form.title.data
        postToEdit.subtitle = edit_form.subtitle.data
        postToEdit.img_url = edit_form.img_url.data
        postToEdit.author = edit_form.author.data
        postToEdit.body = edit_form.body.data
        db.session.commit()

        return redirect(url_for("show_post", title=postToEdit.title))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/post/<string:title>")
def show_post(title):
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.title == title)).scalar()
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/delete/<string:title>")
def delete(title):
    toDelete = db.session.execute(db.select(BlogPost).where(BlogPost.title == title)).scalar()
    db.session.delete(toDelete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))




if __name__ == "__main__":
    app.run(debug=True, port=5001)