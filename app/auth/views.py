from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import logout_user, login_required, current_user
from ..auth import auth
from .forms import UserEditForm, NewQuestionFormA
from .. import db
from ..models import Users, Cards
from ..decorators import admin_required, user_required


category_mapping = {
    "aikajaavaruus": "Aika ja avaruus",
    "luonnontieteet": "Luonnontieteet",
    "Ihmiselämä": "Ihmiselämä",
    "ihmisetjayhteiskunta": "Ihmiset ja yhteiskunta",
    "filosofiajauskonto": "Filosofia ja uskonto",
    "politiikkajaoikeus": "Politiikka ja oikeus",
    "tulevaisuudentutkimus": "Tulevaisuudentutkimus",
    "liiketoimintajatalous": "Liiketoiminta ja talous",
    "teknologia": "Teknologia",
    "ymparisto": "Ympäristö",
    "taidejaviihde": "Taide ja viihde",
    "urheilujavapaa-aika": "Urheilu ja vapaa-aika",
}

@auth.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    current_app.logger.info('home-reitille tultiin')
    if current_user.role == 16:
        return redirect(url_for('auth.editusers'))
    cards = Cards.query.filter_by(country='Finland', type_id=1, is_parent=True).all()
    if cards:
        current_app.logger.info('Kysymyksiä löytyi')
        for card in cards:
            current_app.logger.info('Kysymys: ' + card.question)
        return render_template('user/home.html', cards=cards, category_mapping=category_mapping)
    return render_template('user/home.html')

@auth.route('/newcard', methods=['GET', 'POST'])
@login_required
@user_required
def newcard():
    current_app.logger.info('Uusi kortti')
    form = NewQuestionFormA()
    if current_user.role == 16:
        return render_template('admin/dashboard.html')
    if form.validate_on_submit():
        current_app.logger.info('Tarkistetaan lomakkeen tiedot')
        country_id = current_user.country
        type_id = form.type_id.data
        primary_category = form.primary_category.data
        question = form.question.data
        status = form.status.data
        created_at = datetime.utcnow()
        user_id = current_user.id
        is_parent = bool(form.is_parent.data)
        parent_id = form.parent_id.data
        children = form.children.data
        current_app.logger.info('Tallennetaan kysymys')
        
        card = Cards(country=country_id, 
                     type_id=type_id, 
                     primary_category=primary_category, 
                     question=question, 
                     status=status, 
                     created_at=created_at, 
                     user_id=user_id, 
                     is_parent=is_parent, 
                     parent_id=parent_id,
                     children=children)
        db.session.add(card)
        db.session.commit()
        
        flash('Kysymys lähetetty onnistuneesti!', 'success')
        return redirect(url_for('auth.home'))
    return render_template('user/newcard.html', form=form)


@auth.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@auth.route('/editusers', methods=['GET', 'POST'])
@login_required
@admin_required
def editusers():
    form = UserEditForm() 
    users = Users.query.all()
    current_app.logger.info('Editoidaan käyttäjiä')

    if request.method == 'POST':
        for user in users:
            user_form = UserEditForm(obj=user)
            if user_form.validate_on_submit():
                user_form.populate_obj(user)
                db.session.commit()
                flash(f'Käyttäjätiedot päivitetty käyttäjälle {user.id}.')
            else:
                flash(f'Virheet käyttäjälle {user.id}: {user_form.errors}', 'error')

        return redirect(url_for('auth.editusers', form=form, users=users))  

    return render_template('admin/editusers.html', form=form, users=users)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@auth.route('/card/<int:id>', methods=['GET', 'POST'])
@login_required
def card(id):
    card = Cards.query.get_or_404(id)
    return render_template('user/card.html', card=card)