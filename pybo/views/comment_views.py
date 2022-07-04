from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import CommentForm
from pybo.models import Comment, Answer

from .auth_views import login_required

bp = Blueprint('comment', __name__, url_prefix='/comment')


# @bp.route('/create/<int:answer_id>', methods=["GET", "POST"])
# def create(answer_id):
#     answer = Answer.query.get_or_404(answer_id)
#     question_id = answer.question.id
#     flash("comment usage working but gonna refine dd")
#     return redirect(url_for('question.detail', question_id=question_id))

    # answer = Answer.query.get_or_404(answser_id)
    # if form.validate_on_submit():
    #     content = request.form['content']
    #     comment = Comment(content=content, create_date=datetime.now(), user=g.user)
    #     answer.

@bp.route('/create/<int:answer_id>', methods=["GET", "POST"])
@login_required
def create(answer_id):
    form = CommentForm()
#     flash("comment usage working but gonna refine dd")
    return render_template('comment/comment_form.html', form=form)
