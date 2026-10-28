-- PostgreSQL schema for prefecture-quiz (run once before first deployment).
-- Teacher account is created by app.py on startup using ADMIN_PASSWORD.
CREATE TABLE IF NOT EXISTS quiz_users (
 id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK (role IN ('student','teacher'))
);
CREATE TABLE IF NOT EXISTS quiz_daily (
 user_id BIGINT NOT NULL REFERENCES quiz_users(id) ON DELETE CASCADE,
 quiz_day DATE NOT NULL,
 question_ids JSONB NOT NULL,
 PRIMARY KEY (user_id, quiz_day)
);
CREATE TABLE IF NOT EXISTS quiz_answers (
 user_id BIGINT NOT NULL REFERENCES quiz_users(id) ON DELETE CASCADE,
 quiz_day DATE NOT NULL,
 prefecture_id INTEGER NOT NULL CHECK (prefecture_id BETWEEN 1 AND 47),
 number_answer INTEGER NOT NULL CHECK (number_answer BETWEEN 1 AND 47),
 region_answer INTEGER NOT NULL CHECK (region_answer BETWEEN 0 AND 7),
 name_answer TEXT NOT NULL,
 correct BOOLEAN NOT NULL,
 hints INTEGER NOT NULL CHECK (hints BETWEEN 1 AND 3),
 score INTEGER NOT NULL CHECK (score IN (0,40,70,100)),
 PRIMARY KEY (user_id, quiz_day, prefecture_id),
 FOREIGN KEY (user_id,quiz_day) REFERENCES quiz_daily(user_id,quiz_day) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS quiz_answers_day_idx ON quiz_answers(quiz_day);
