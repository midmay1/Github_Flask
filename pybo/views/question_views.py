from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.models import Question, Answer, User
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')



@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1) #페이지
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()

        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) | # 질문 제목
                    Question.content.ilike(search) | # 질문 내용
                    User.username.ilike(search) | # 질문 작성장
                    sub_query.c.content.ilike(search) | # 답변 내용
                    sub_query.c.username.ilike(search) # 답변 작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page, per_page=10) # 이것도 per_page를 버튼으로 받아오면 바꿀 수 있겠네
    return render_template('question/question_list.html', question_list = question_list, page=page, kw=kw)


@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)

    # sub_query = db.session.query(answer_voter.c.user_id, func.count(*).label('num_voter')) \
                # .group_by(answer_voter.c.user_id).subquery()
    # answer_list = Answer.query \
                # .outerjoin(sub_query, Answer.id == sub_query.c.question_id) \
                # .ouder_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    # answer_list = answer_list.paginate(page, per_page=10)
    ###
    # db에 query를 할거야. 추천이 달린 답변글들의 answer id 를 저장하고 싶어. !Note : answer id가 뭐지?
    # count 해서 num_voter라는 라벨 달자
    # 1 질문에 N 개의 추천이 있으므로 각 질문당 몇 개의 추천수가 있는지 group by 한다.
    # Answer의 id와 추천이 달린 답변 글의 id 가 같은 것을 join + 추천 없는 것도 들고감 (outerjoin)
    # num_voter를 기준으로 order_by 를 하면 추천수를 기준으로 답변이 정렬되어 question_detail 가능
    # 결국에 지금 모르는 것은 Answer id가 무엇인가.
    return render_template('question/question_detail.html', question = question, form=form)#, answer_list = answer_list)


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)


@bp.route('/modify/<int:question_id>', methods=["GET", "POST"])
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다.')
        return redirect(url_for('question.detail', qeustion_id=question_id))
    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할 수 없습니다. (잠시동안은.. 조만간 자추 가능하도록 만들거임)')
    elif g.user in _question.voter:
        print(_question.voter)
        flash('이미 니가 질문 추천함.')
    else:
        _question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id = question_id))
