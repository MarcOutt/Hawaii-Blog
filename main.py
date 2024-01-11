import smtplib

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request

from personnal_infos import my_email, password

app = Flask(__name__)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("name")
        phone = request.form.get("phone")
        message_content = request.form.get("message")

        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                                to_addrs="your-email",
                                msg=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message_content}"
                                )
        return "Form submitted. Thank you for contacting me!"
    return render_template("contact.html")


if __name__ == '__main__':
    app.run(debug=True)