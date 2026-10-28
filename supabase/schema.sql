-- Run once in Supabase SQL Editor.
-- Tables are private: browser clients must never access them directly.
create table if not exists public.quiz_users (
 id bigint generated always as identity primary key,
 username text not null unique check (username ~ '^[A-Za-z0-9_-]{3,30}$'),
 password_hash text not null,
 role text not null check (role in ('teacher','student'))
);
create table if not exists public.quiz_daily (
 user_id bigint not null references public.quiz_users(id) on delete cascade,
 quiz_day date not null,
 question_ids jsonb not null,
 primary key (user_id, quiz_day)
);
create table if not exists public.quiz_answers (
 user_id bigint not null references public.quiz_users(id) on delete cascade,
 quiz_day date not null,
 prefecture_id integer not null check (prefecture_id between 1 and 47),
 number_answer integer not null,
 region_answer integer not null,
 name_answer text not null,
 correct boolean not null,
 hints integer not null check (hints between 1 and 3),
 score integer not null,
 created_at timestamptz not null default now(),
 primary key (user_id, quiz_day, prefecture_id)
);
create index if not exists quiz_answers_user_day_idx on public.quiz_answers(user_id, quiz_day);
alter table public.quiz_users enable row level security;
alter table public.quiz_daily enable row level security;
alter table public.quiz_answers enable row level security;
-- No anon/authenticated policies: access via trusted backend only.
revoke all on public.quiz_users, public.quiz_daily, public.quiz_answers from anon, authenticated;
revoke all on sequence public.quiz_users_id_seq from anon, authenticated;
