from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from db import init_db, DB_NAME

app = Flask(__name__)

# 로그인 세션을 쓰기 위한 비밀키 (실서비스에선 더 안전하게 관리)
app.secret_key = "dev-secret-key"

def query_db(query, params=(), one=False):
    """DB 편하게 쓰려고 만든 헬퍼 함수"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능하게
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return (rows[0] if rows else None) if one else rows


@app.route("/")
def index():
    # 메인 페이지
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uid = request.form.get("uid")
        pw = request.form.get("pw")

        # 1) 입력 체크
        if not uid or not pw:
            flash("아이디/비밀번호를 입력하세요.")
            return redirect(url_for("signup"))

        # 2) 비밀번호는 반드시 해시로 저장 (원문 저장 금지)
        pw_hash = generate_password_hash(pw)

        try:
            query_db("INSERT INTO users(uid, pw_hash) VALUES(?, ?)", (uid, pw_hash))
            flash("회원가입 완료! 로그인 해주세요.")
            return redirect(url_for("login"))
        except:
            flash("이미 존재하는 아이디입니다.")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form.get("uid")
        pw = request.form.get("pw")

        user = query_db("SELECT * FROM users WHERE uid = ?", (uid,), one=True)

        # 1) 아이디가 없거나 비번 불일치
        if not user or not check_password_hash(user["pw_hash"], pw):
            flash("로그인 실패: 아이디 또는 비밀번호 확인")
            return redirect(url_for("login"))

        # 2) 로그인 성공 -> 세션에 사용자 정보 저장
        session["user_id"] = user["id"]
        session["uid"] = user["uid"]
        flash("로그인 성공!")
        return redirect(url_for("board_list"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # 세션 삭제 -> 로그아웃
    session.clear()
    flash("로그아웃 완료")
    return redirect(url_for("index"))


def login_required():
    """로그인 여부 확인용 함수(가장 단순 버전)"""
    return "user_id" in session


@app.route("/board")
def board_list():
    # 로그인한 사람만 게시판 이용 가능
    if not login_required():
        flash("게시판은 로그인 후 이용 가능합니다.")
        return redirect(url_for("login"))

    posts = query_db("""
        SELECT posts.id, posts.title, posts.created_at, users.uid
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """)

    return render_template("board_list.html", posts=posts)


@app.route("/board/write", methods=["GET", "POST"])
def board_write():
    if not login_required():
        flash("로그인 후 글 작성 가능합니다.")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("제목/내용을 입력하세요.")
            return redirect(url_for("board_write"))

        query_db(
            "INSERT INTO posts(user_id, title, content) VALUES(?, ?, ?)",
            (session["user_id"], title, content)
        )
        flash("글 작성 완료!")
        return redirect(url_for("board_list"))

    return render_template("board_write.html")


if __name__ == "__main__":
    init_db()  # 앱 실행 시 DB 초기화
    app.run(debug=True)