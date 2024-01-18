import smtplib
from datetime import date

from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_gravatar import Gravatar
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from personnal_infos import my_email, password

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)

# INITIALIZE GRAVATAR
gravatar = Gravatar(app,
                    size=90,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by user ID for the Flask-Login extension.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        UserMixin: The loaded user.
    """
    return db.get_or_404(User, user_id)



# CONFIGURE TABLES
class User(UserMixin, db.Model):
    """
    Model representing a user.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address of the user (unique).
        password (str): The hashed password of the user.
        surname (str): The surname of the user.
        posts (relationship): Relationship with the BlogPost model representing blog posts created by the user.
        comments (relationship): Relationship with the Comment model representing comments made by the user.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    """
    Model representing a blog post.

    Attributes:
        id (int): The unique identifier for the blog post.
        author_id (int): The user ID of the author of the blog post.
        author (relationship): Relationship with the User model representing the author.
        title (str): The title of the blog post.
        subtitle (str): The subtitle of the blog post.
        date (str): The date of the blog post.
        body (str): The main content of the blog post.
        img_url (str): The URL of an image associated with the blog post.
        comments (relationship): Relationship with the Comment model representing comments on the post.
    """
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    """
    Model representing a comment on a blog post.

    Attributes:
        id (int): The unique identifier for the comment.
        author_id (int): The user ID of the author of the comment.
        comment_author (relationship): Relationship with the User model representing the comment author.
        post_id (int): The ID of the blog post to which the comment belongs.
        parent_post (relationship): Relationship with the BlogPost model representing the parent post.
        text (str): The content of the comment.
    """
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)



with app.app_context():
    db.create_all()


@app.route('/register', methods=['POST', 'GET'])
def register():
    """
    Handles user registration.

    Returns:
        str: Redirects to the home page if registration is successful.
        render_template: Renders the registration form template.
    """
    form = RegisterForm()
    if form.validate_on_submit():

        # Hash and salt the password using PBKDF2 and SHA256
        hash_and_salted_password = generate_password_hash(form.password.data,
                                                          method='pbkdf2:sha256',
                                                          salt_length=8)

        # Create a new User instance with registration data
        new_user = User(
            surname=form.surname.data,
            email=form.email.data,
            password=hash_and_salted_password
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log in the newly registered user
        login_user(new_user)

        # Display a flash message to indicate successful registration
        flash('Registration successful! Welcome, {}.'.format(new_user.surname), 'success')

        # Redirect to the home page after successful registration
        return redirect(url_for('get_all_posts'))

    # Render the registration form template
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handles user login.

    Returns:
        str: Redirects to the home page if login is successful.
        render_template: Renders the login form template.
    """
    form = LoginForm()
    if form.validate_on_submit():

        # Retrieve user information from the database based on the provided email
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))

        # Get the user instance from the result
        user = result.scalar()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):

            # Log in the user
            login_user(user)

            # Redirect to the home page after successful login
            return redirect(url_for('get_all_posts'))

    # Render the login form template
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    """
    Logs out the currently logged-in user.

    Returns:
        str: Redirects to the home page after logging out.
    """
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    """
    Displays all blog posts on the home page.

    Returns:
        render_template: Renders the home page template with all blog posts.
    """
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()

    # Print each post for debugging purposes
    for post in posts:
        print(post)

    # Render the home page template with all blog posts
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def get_post(post_id):
    """
    Displays a specific blog post and allows comments.

    Args:
        post_id (int): The ID of the blog post to display.

    Returns:
        render_template: Renders the blog post template with comments.
    """
    requested_post = db.get_or_404(BlogPost, post_id)
    comments = requested_post.comments

    # Print the ID of the current user for debugging purposes
    print(current_user.id)

    # Print each comment for debugging purposes
    for comment in comments:
        print(comment)

    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        # Create a new comment associated with the current user and the displayed post
        new_comment = Comment(
            text=comment_form.text.data,
            comment_author=current_user,
            parent_post=requested_post
        )

        # Add the new comment to the database
        db.session.add(new_comment)
        db.session.commit()

    # Render the blog post template with comments
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form,
                           all_comments=comments)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def create_new_post():
    """
    Creates a new blog post.

    Returns:
        str: Redirects to the home page if the post creation is successful.
        render_template: Renders the create post form template.
    """
    form = CreatePostForm()
    if form.validate_on_submit():
        # Create a new blog post associated with the current user
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )

        # Add the new post to the database
        db.session.add(new_post)
        db.session.commit()
        print("ok")

        # Redirect to the home page after successful post creation
        return redirect(url_for("get_all_posts"))

    # Render the create post form template
    return render_template("make-post.html", form=form)



@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """
    Edits an existing blog post.

    Args:
        post_id (int): The ID of the post to edit.

    Returns:
        str: Redirects to the edited post page if successful.
        render_template: Renders the create post form template for editing.
    """
    post = db.get_or_404(BlogPost, post_id)

    # Populate the edit form with the existing post data
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        # Update the existing post with the edited data
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the edited post page
        return redirect(url_for("get_post", post_id=post.id))

    # Render the create post form template for editing
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    """
    Deletes a blog post.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        str: Redirects to the home page after deleting the post.
    """
    post_to_delete = db.get_or_404(BlogPost, post_id)

    # Delete the specified post from the database
    db.session.delete(post_to_delete)
    db.session.commit()

    # Redirect to the home page after successful deletion
    return redirect(url_for('get_all_posts'))


@app.route("/delete/post/<int:post_id>/comments/<int:comment_id>")
@login_required
def delete_comment(post_id, comment_id):
    """
    Deletes a comment on a specific blog post.

    Args:
        post_id (int): The ID of the blog post containing the comment.
        comment_id (int): The ID of the comment to delete.

    Returns:
        str: Redirects to the blog post page after deleting the comment.
    """
    comment_id_delete = db.get_or_404(Comment, comment_id)

    # Delete the specified comment from the database
    db.session.delete(comment_id_delete)
    db.session.commit()

    # Redirect to the blog post page after successful deletion
    return redirect(url_for('get_post', post_id=post_id))


@app.route('/about')
def about():
    """
    Renders the about page.

    Returns:
        render_template: Renders the about page template.
    """
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handles the contact page with an email contact form.

    Returns:
        str: "Form submitted. Thank you for contacting me!" if the form is submitted successfully.
        render_template: Renders the contact form template.
    """
    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("name")
        phone = request.form.get("phone")
        message_content = request.form.get("message")

        # Use SMTP to send the contact form details via email
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                                to_addrs="your-email",
                                msg=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message_content}"
                                )

        # Display a message after successful form submission
        return "Form submitted. Thank you for contacting me!"

    # Render the contact form template
    return render_template("contact.html")



if __name__ == '__main__':
    app.run(debug=True)
