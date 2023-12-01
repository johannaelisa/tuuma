from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request, jsonify, make_response
from flask_login import logout_user, login_required, current_user
from ..auth import auth
from .forms import UserEditForm, NewQuestionFormA, EditMyProfileForm
from .. import db
from ..models import Users, Cards
from ..decorators import admin_required, user_required


category_mapping = {
    "kaikki": "Kaikki",
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
    
    category_filter = request.values.get('primary_category')
    query = Cards.query.filter_by(country='Finland', type_id=1, is_parent=True)
    
    if category_filter and category_filter.lower() != 'kaikki':
        query = query.filter_by(primary_category=category_filter)

    query = query.order_by(Cards.created_at.desc())
    cards = query.all()
    
    try:
        if request.is_json:
            current_app.logger.info(f'2. category_filter: {category_filter}')
            return jsonify(cards=[card.serialize() for card in cards])
        else:
            return render_template('user/home.html', cards=cards, category_mapping=category_mapping, category_filter=category_filter)
    except Exception as e:
        current_app.logger.error(f'Virhe reitillä /home: {str(e)}')
        if request.is_json:
            response = make_response(jsonify(error=str(e)), 500)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            flash('Jotain meni pieleen!', 'error')
            return render_template('user/home.html', category_mapping=category_mapping, category_filter=category_filter)
        
        
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

@auth.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
@user_required
def profile(id):
    form = EditMyProfileForm()
    user = Users.query.get_or_404(id)
    if form.validate_on_submit():
        current_app.logger.info('Tarkistetaan lomakkeen tiedot')
        user.username = form.username.data
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.country = form.country.data
        db.session.commit()
        flash('Profiilisi päivitetty onnistuneesti!', 'success')
        return redirect(url_for('auth.profile', id=id))
    return render_template('user/profile.html', user=user, form=form)
