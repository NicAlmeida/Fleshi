from flask import  render_template, url_for, redirect, request
from flask import request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from appflexi.forms import LoginForm, RegisterForm, PhotoForm
from appflexi import app, database, bcrypt
from appflexi.models import User, Photo, Comment
import os
from werkzeug.utils import secure_filename


@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('profile', user_id=user.id))
    return render_template('homepage.html', form=login_form)

@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    register_Form = RegisterForm()
    if register_Form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_Form.password.data)
        user = User(username = register_Form.username.data, password = password, email = register_Form.email.data)
        database.session.add(user)
        database.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id))
    return render_template('createaccount.html', form=register_Form)

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if int(user_id) == int(current_user.id):
        photo_form = PhotoForm()
        if photo_form.validate_on_submit():
            file = photo_form.photo.data
            secure_name = secure_filename(file.filename)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_name)
            file.save(path)
            photo = Photo(file_name=secure_name, user_id=current_user.id)
            database.session.add(photo)
            database.session.commit()

        return render_template('profile.html', user=current_user, form=photo_form)
    else:
        user = User.query.get(int(user_id))
        return render_template('profile.html', user=user)


@app.route('/post/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    texto_comentario = request.form.get('text_comment')
    parent_id = request.form.get('parent_id')

    if not texto_comentario:
        flash('O comentário não pode estar vazio.', 'danger')
        return redirect(request.referrer or url_for('homepage'))

    novo_comentario = Comment(
        comment=texto_comentario,
        user_id=current_user.id,
        photo_id=photo.id,
        parent_id=int(parent_id) if parent_id else None
    )

    database.session.add(novo_comentario)
    database.session.commit()

    flash('Comentário enviado!', 'success')
    return redirect(request.referrer or url_for('homepage'))


@app.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)

    database.session.delete(comment)
    database.session.commit()

    flash('Comentário excluído.', 'success')
    return redirect(request.referrer or url_for('homepage'))


@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    novo_texto = request.form.get('text_edit')

    if novo_texto:
        comment.comment = novo_texto
        database.session.commit()
        flash('Comentário atualizado!', 'success')

    return redirect(request.referrer or url_for('homepage'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/feed")
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template("feed.html", photos=photos)

