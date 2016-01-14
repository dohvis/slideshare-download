from flask import (
    session,
    redirect,
    request as req,
    flash,
)
from . import account_bp
from .. import (
    db,
)
from .models import User


@account_bp.route("/signin/", methods=['POST'])
def signin():
    try:
        session['email']
        return redirect('/')
    except KeyError:
        pass

    email = req.form['email']
    password = req.form['password']
    user = db.session.query(User).filter_by(email=email, is_active=True).first()
    print(user is None, user.check_password(password))
    if user is not None and user.check_password(password):
        session['email'] = email
        return redirect('/')
    elif user.is_active is False:
        flash('로그인이 차단된 계정입니다.')
        return redirect('/', code=403)
    else:
        flash('아이디 혹은 비밀번호가 잘못되었습니다.')
        return redirect('/')


@account_bp.route("/signup/", methods=['POST'])
def signup():
    try:
        session['email']
        return redirect('/')
    except KeyError:
        pass
    email = req.form['email']
    password = req.form['password']
    user = User(email, password)
    try:
        db.session.add(user)
        db.session.commit()
    except:
        flash('회원가입이 실패했습니다. 다른 이메일로 시도해 주세요.')
    return redirect('/')


@account_bp.route("/signout/", methods=['GET'])
def signout():
    del session['email']
    return redirect('/')
