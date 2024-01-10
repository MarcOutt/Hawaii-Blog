import smtplib

from flask import Flask, render_template, request

from personnal_infos import my_email, password

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html")


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