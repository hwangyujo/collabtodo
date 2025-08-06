from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from models import User, Friend

# ✅ Blueprint 생성
friend_bp = Blueprint('friend', __name__)

@friend_bp.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    # ===== 친구 요청 보내기 =====
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and user.id != current_user.id:
            existing = Friend.query.filter(
                ((Friend.requester_id == current_user.id) & (Friend.receiver_id == user.id)) |
                ((Friend.requester_id == user.id) & (Friend.receiver_id == current_user.id))
            ).first()
            if not existing:
                new_friend = Friend(requester_id=current_user.id, receiver_id=user.id)
                db.session.add(new_friend)
                db.session.commit()
                flash("친구 요청을 보냈습니다.")
            else:
                flash("이미 요청이 있거나 친구입니다.")
        else:
            flash("사용자를 찾을 수 없습니다.")

    # ===== 목록 불러오기 =====
    sent_requests = Friend.query.filter_by(requester_id=current_user.id, status='pending').all()
    received_requests = Friend.query.filter_by(receiver_id=current_user.id, status='pending').all()
    friends_list = Friend.query.filter(
        ((Friend.requester_id == current_user.id) | (Friend.receiver_id == current_user.id)) &
        (Friend.status == 'accepted')
    ).all()

    # ===== username 변환 함수 =====
    def with_username(friend_obj):
        if friend_obj.requester_id == current_user.id:
            friend_user = User.query.get(friend_obj.receiver_id)
        else:
            friend_user = User.query.get(friend_obj.requester_id)
        return {
            'id': friend_user.id,
            'username': friend_user.username,
            'friend_id': friend_obj.id
        }

    sent_display = [with_username(fr) for fr in sent_requests]
    received_display = [with_username(fr) for fr in received_requests]
    friends_display = [with_username(fr) for fr in friends_list]

    return render_template(
        'friends.html',
        sent_requests=sent_display,
        received_requests=received_display,
        friends=friends_display
    )

# ===== 친구 요청 수락 =====
@friend_bp.route('/friends/accept/<int:friend_id>')
@login_required
def accept_friend(friend_id):
    fr = Friend.query.get_or_404(friend_id)
    if fr.receiver_id == current_user.id:
        fr.status = 'accepted'
        db.session.commit()
    return redirect(url_for('friend.friends'))

# ===== 친구 요청 거절 =====
@friend_bp.route('/friends/reject/<int:friend_id>')
@login_required
def reject_friend(friend_id):
    fr = Friend.query.get_or_404(friend_id)
    if fr.receiver_id == current_user.id:
        fr.status = 'rejected'
        db.session.commit()
    return redirect(url_for('friend.friends'))

# ===== 친구 삭제 =====
@friend_bp.route('/friends/delete/<int:friend_id>')
@login_required
def delete_friend(friend_id):
    fr = Friend.query.get_or_404(friend_id)
    if fr.requester_id == current_user.id or fr.receiver_id == current_user.id:
        db.session.delete(fr)
        db.session.commit()
    return redirect(url_for('friend.friends'))
