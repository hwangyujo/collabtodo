from models import Todo, SharedTodo, Friend, User

@todo_bp.route('/')
@login_required
def index():
    my_todos = Todo.query.filter_by(user_id=current_user.id).all()
    shared_todos = SharedTodo.query.filter_by(shared_with_id=current_user.id).all()
    shared_list = [Todo.query.get(st.todo_id) for st in shared_todos]

    friends = Friend.query.filter(
        ((Friend.requester_id == current_user.id) | (Friend.receiver_id == current_user.id)) &
        (Friend.status == 'accepted')
    ).all()

    # 친구 목록에 username 추가
    friends_display = []
    for fr in friends:
        if fr.requester_id == current_user.id:
            friend_user = User.query.get(fr.receiver_id)
        else:
            friend_user = User.query.get(fr.requester_id)
        friends_display.append({
            'id': friend_user.id,
            'username': friend_user.username
        })

    return render_template(
        'index.html',
        todos=my_todos,
        shared_todos=shared_list,
        friends=friends_display
    )
