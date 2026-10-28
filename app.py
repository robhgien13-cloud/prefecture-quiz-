import os, json, random
from datetime import datetime
from zoneinfo import ZoneInfo
import psycopg
from psycopg.rows import dict_row
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=True)
DATA = json.load(open("data.json", encoding="utf-8"))
REGIONS = ["北海道地方","東北地方","関東地方","中部地方","近畿地方","中国地方","四国地方","九州・沖縄地方"]
def region(i):
    return 0 if i == 1 else 1 if i <= 7 else 2 if i <= 14 else 3 if i <= 23 else 4 if i <= 30 else 5 if i <= 35 else 6 if i <= 39 else 7
def today():
    return datetime.now(ZoneInfo("Asia/Tokyo")).date()
def db():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
def fail(message, code=400):
    return jsonify(error=message), code
def require(role):
    return session.get("role") == role and bool(session.get("uid"))
def hints(item):
    import re
    forbidden = sorted(set([x["name"] for x in DATA]+[re.sub("[都道府県]$","",x["name"]) for x in DATA]+REGIONS+[item["capital"],item["capital"].removesuffix("市")]), key=len, reverse=True)
    out=[]
    for term, desc in item["terms"][:3]:
        line=term+"："+desc
        for word in forbidden:
            if len(word)>1: line=line.replace(word,"この地域")
        out.append(line)
    return out
@app.get("/")
def index():
    return send_from_directory("static", "index.html")
@app.post("/api/login")
def login():
    body=request.get_json(silent=True) or {}
    username=str(body.get("username","")).strip()
    with db() as conn:
        user=conn.execute("select * from quiz_users where username=%s",(username,)).fetchone()
    if not user or (user["role"]=="teacher" and not check_password_hash(user["password_hash"],str(body.get("password","")))):
        return fail("IDまたはパスワードが違います",401)
    session.clear()
    session.update(uid=user["id"],role=user["role"],username=user["username"])
    return jsonify(role=user["role"],username=username)
@app.get("/api/me")
def me():
    return jsonify(role=session.get("role"),username=session.get("username"))
@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
@app.get("/api/today")
def daily():
    if not require("student"): return fail("ログインが必要です",403)
    uid=session["uid"]; date=today()
    with db() as conn:
        row=conn.execute("select question_ids from quiz_daily where user_id=%s and quiz_day=%s",(uid,date)).fetchone()
        if row: ids=row["question_ids"]
        else:
            ids=random.SystemRandom().sample(range(1,48),10)
            conn.execute("insert into quiz_daily(user_id,quiz_day,question_ids) values(%s,%s,%s::jsonb) on conflict do nothing",(uid,date,json.dumps(ids)))
            row=conn.execute("select question_ids from quiz_daily where user_id=%s and quiz_day=%s",(uid,date)).fetchone()
            ids=row["question_ids"]
        answers={r["prefecture_id"]:dict(r) for r in conn.execute("select * from quiz_answers where user_id=%s and quiz_day=%s",(uid,date)).fetchall()}
    return jsonify(day=str(date),regions=REGIONS,options=[dict(id=d["id"],name=d["name"],region=region(d["id"])) for d in DATA],questions=[dict(id=i,hints=hints(DATA[i-1]),answer=({"correct":a["correct"],"score":a["score"],"actual":DATA[i-1]["name"],"actualNumber":i,"actualRegion":region(i)} if (a:=answers.get(i)) else None)) for i in ids])
@app.post("/api/answer")
def answer():
    if not require("student"): return fail("ログインが必要です",403)
    x=request.get_json(silent=True) or {}
    try:
        pid=int(x["id"]); number=int(x["number"]); r=int(x["region"]); name=str(x["name"]); used=int(x["hints"])
    except (KeyError,ValueError,TypeError): return fail("回答を入力してください")
    if not (1<=pid<=47 and 1<=number<=47 and 0<=r<=7 and 1<=used<=3):return fail("入力を確認してください")
    date=today(); uid=session["uid"]; item=DATA[pid-1]
    correct=number==pid and r==region(pid) and name==item["name"]
    score=([100,70,40][used-1] if correct else 0)
    with db() as conn:
        row=conn.execute("select question_ids from quiz_daily where user_id=%s and quiz_day=%s",(uid,date)).fetchone()
        if not row or pid not in row["question_ids"]:return fail("本日の出題ではありません",403)
        conn.execute("insert into quiz_answers(user_id,quiz_day,prefecture_id,number_answer,region_answer,name_answer,correct,hints,score) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict do nothing",(uid,date,pid,number,r,name,correct,used,score))
        saved=conn.execute("select correct,score from quiz_answers where user_id=%s and quiz_day=%s and prefecture_id=%s",(uid,date,pid)).fetchone()
    return jsonify(correct=saved["correct"],score=saved["score"],actual=item["name"],actualNumber=pid,actualRegion=region(pid))
@app.post("/api/admin/students")
def add_student():
    if not require("teacher"):return fail("権限がありません",403)
    import re
    username=str((request.get_json(silent=True) or {}).get("username","")).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,30}",username):return fail("IDは英数字3〜30文字にしてください")
    try:
        with db() as conn:
            conn.execute("insert into quiz_users(username,password_hash,role) values(%s,%s,'student')",(username,generate_password_hash(os.urandom(32).hex())))
    except psycopg.errors.UniqueViolation:return fail("そのIDは使用済みです",409)
    return jsonify(ok=True)
@app.get("/api/admin/stats")
def stats():
    if not require("teacher"):return fail("権限がありません",403)
    with db() as conn:
        rows=conn.execute("""select u.username,count(a.prefecture_id) answered,coalesce(sum(a.correct::int),0) correct,coalesce(sum(a.score),0) score from quiz_users u left join quiz_answers a on a.user_id=u.id and a.quiz_day=%s where u.role='student' group by u.id,u.username order by u.username""",(today(),)).fetchall()
    return jsonify(students=rows,day=str(today()))
def init_admin():
    password=os.environ["ADMIN_PASSWORD"]
    username=os.environ.get("ADMIN_ID","teacher")
    with db() as conn:
        if not conn.execute("select id from quiz_users where role='teacher'").fetchone():
            conn.execute("insert into quiz_users(username,password_hash,role) values(%s,%s,'teacher')",(username,generate_password_hash(password)))
init_admin()
