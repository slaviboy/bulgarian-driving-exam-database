-- master.sqlite — data contract schema version 1 (docs/data-contract.md §4).
-- Plain SQLite: no extensions, no WITHOUT ROWID tables, TEXT primary keys, explicit foreign keys.
-- PRAGMA user_version is set to 1 by the builder.

CREATE TABLE dataset_info (
    key   TEXT NOT NULL PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE sources (
    id                    TEXT NOT NULL PRIMARY KEY,
    name                  TEXT NOT NULL,
    source_url            TEXT NOT NULL,
    attribution           TEXT NOT NULL,
    license               TEXT NOT NULL,
    redistribution_status TEXT NOT NULL,
    retrieved_at          TEXT
);

CREATE TABLE categories (
    id          TEXT    NOT NULL PRIMARY KEY,
    name        TEXT    NOT NULL,
    description TEXT,
    source_id   TEXT    NOT NULL REFERENCES sources (id),
    position    INTEGER NOT NULL
);
CREATE INDEX idx_categories_source ON categories (source_id);

CREATE TABLE variants (
    id             TEXT    NOT NULL PRIMARY KEY,
    category_id    TEXT    NOT NULL REFERENCES categories (id),
    title          TEXT    NOT NULL,
    description    TEXT    NOT NULL,
    effective_note TEXT,
    source_url     TEXT    NOT NULL,
    source_sha256  TEXT    NOT NULL,
    source_edition TEXT    NOT NULL,
    position       INTEGER NOT NULL,
    question_count INTEGER NOT NULL
);
CREATE INDEX idx_variants_category ON variants (category_id);

CREATE TABLE topics (
    id   TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE sections (
    id             TEXT    NOT NULL PRIMARY KEY,
    variant_id     TEXT    NOT NULL REFERENCES variants (id),
    category_id    TEXT    NOT NULL REFERENCES categories (id),
    topic_id       TEXT    NOT NULL REFERENCES topics (id),
    number         INTEGER NOT NULL,
    name           TEXT    NOT NULL,
    position       INTEGER NOT NULL,
    question_count INTEGER NOT NULL,
    UNIQUE (variant_id, number)
);
CREATE INDEX idx_sections_variant ON sections (variant_id);
CREATE INDEX idx_sections_category ON sections (category_id);
CREATE INDEX idx_sections_topic ON sections (topic_id);

CREATE TABLE media (
    id            TEXT    NOT NULL PRIMARY KEY,
    kind          TEXT    NOT NULL CHECK (kind IN ('image', 'video')),
    original_name TEXT    NOT NULL,
    relative_path TEXT    NOT NULL,
    mime_type     TEXT    NOT NULL,
    bytes         INTEGER NOT NULL,
    width         INTEGER,
    height        INTEGER,
    sha256        TEXT    NOT NULL,
    source_url    TEXT    NOT NULL,
    source_id     TEXT    NOT NULL REFERENCES sources (id)
);
CREATE INDEX idx_media_source ON media (source_id);

CREATE TABLE media_aliases (
    media_id TEXT NOT NULL REFERENCES media (id),
    name     TEXT NOT NULL,
    PRIMARY KEY (media_id, name)
);

CREATE TABLE media_derivatives (
    media_id      TEXT    NOT NULL REFERENCES media (id),
    format        TEXT    NOT NULL,
    relative_path TEXT    NOT NULL,
    mime_type     TEXT    NOT NULL,
    bytes         INTEGER NOT NULL,
    width         INTEGER,
    height        INTEGER,
    sha256        TEXT    NOT NULL,
    PRIMARY KEY (media_id, format)
);

CREATE TABLE questions (
    id            TEXT    NOT NULL PRIMARY KEY,
    original_id   TEXT    NOT NULL,
    source_id     TEXT    NOT NULL REFERENCES sources (id),
    question_text TEXT    NOT NULL,
    explanation   TEXT,
    answer_format TEXT    NOT NULL CHECK (answer_format IN ('text', 'image', 'mixed')),
    correct_count INTEGER NOT NULL,
    content_hash  TEXT    NOT NULL,
    UNIQUE (source_id, original_id)
);
CREATE INDEX idx_questions_source ON questions (source_id);

CREATE TABLE answers (
    id          TEXT    NOT NULL PRIMARY KEY,
    question_id TEXT    NOT NULL REFERENCES questions (id),
    position    INTEGER NOT NULL,
    answer_text TEXT,
    media_id    TEXT REFERENCES media (id),
    is_correct  INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    UNIQUE (question_id, position)
);
CREATE INDEX idx_answers_question ON answers (question_id, position);
CREATE INDEX idx_answers_media ON answers (media_id);

CREATE TABLE question_media (
    question_id TEXT    NOT NULL REFERENCES questions (id),
    media_id    TEXT    NOT NULL REFERENCES media (id),
    role        TEXT    NOT NULL CHECK (role IN ('image', 'video')),
    position    INTEGER NOT NULL,
    PRIMARY KEY (question_id, media_id, role)
);
CREATE INDEX idx_question_media_media ON question_media (media_id);

CREATE TABLE variant_questions (
    variant_id  TEXT    NOT NULL REFERENCES variants (id),
    question_id TEXT    NOT NULL REFERENCES questions (id),
    section_id  TEXT    NOT NULL REFERENCES sections (id),
    points      INTEGER NOT NULL CHECK (points BETWEEN 1 AND 3),
    position    INTEGER NOT NULL,
    PRIMARY KEY (variant_id, question_id),
    UNIQUE (variant_id, position)
);
CREATE INDEX idx_variant_questions_question ON variant_questions (question_id);
CREATE INDEX idx_variant_questions_section ON variant_questions (section_id);

CREATE TABLE exam_configs (
    id                  TEXT    NOT NULL PRIMARY KEY,
    variant_id          TEXT    NOT NULL REFERENCES variants (id),
    status              TEXT    NOT NULL CHECK (status IN ('official', 'unofficial')),
    question_count      INTEGER NOT NULL,
    max_points          INTEGER NOT NULL,
    pass_points         INTEGER NOT NULL,
    duration_minutes    INTEGER NOT NULL,
    video_questions     INTEGER NOT NULL,
    max_video_plays     INTEGER,
    scoring             TEXT    NOT NULL,
    show_correct_count  INTEGER NOT NULL CHECK (show_correct_count IN (0, 1)),
    section_quotas_json TEXT,
    points_mix_json     TEXT,
    verification_json   TEXT    NOT NULL,
    evidence_json       TEXT    NOT NULL,
    notes_json          TEXT    NOT NULL
);
CREATE INDEX idx_exam_configs_variant ON exam_configs (variant_id);

-- Translations (unofficial; Bulgarian is the source and prevails). Only translations of the current Bulgarian text
-- are stored: source_hash equals the content_hash of the question that was translated.
CREATE TABLE languages (
    code         TEXT    NOT NULL PRIMARY KEY,
    tag          TEXT    NOT NULL,
    native_name  TEXT    NOT NULL,
    english_name TEXT    NOT NULL,
    kind         TEXT    NOT NULL CHECK (kind IN ('source', 'translation')),
    status       TEXT    NOT NULL CHECK (status IN ('official', 'unofficial')),
    questions    INTEGER NOT NULL,
    coverage     REAL    NOT NULL
);

CREATE TABLE question_translations (
    question_id   TEXT NOT NULL REFERENCES questions (id),
    language      TEXT NOT NULL REFERENCES languages (code),
    source_hash   TEXT NOT NULL,
    question_text TEXT NOT NULL,
    PRIMARY KEY (question_id, language)
);
CREATE INDEX idx_question_translations_language ON question_translations (language);

CREATE TABLE answer_translations (
    answer_id   TEXT NOT NULL REFERENCES answers (id),
    language    TEXT NOT NULL REFERENCES languages (code),
    answer_text TEXT NOT NULL,
    PRIMARY KEY (answer_id, language)
);
CREATE INDEX idx_answer_translations_language ON answer_translations (language);

CREATE TABLE label_translations (
    kind       TEXT NOT NULL CHECK (kind IN ('category', 'variant_description', 'variant_note', 'topic')),
    label_id   TEXT NOT NULL,
    language   TEXT NOT NULL REFERENCES languages (code),
    label_text TEXT NOT NULL,
    PRIMARY KEY (kind, label_id, language)
);
CREATE INDEX idx_label_translations_language ON label_translations (language);

-- Explanations (unofficial, Bulgarian only) of why the correct answers are correct, written from the cited acts.
-- source_hash equals the content_hash of the question that was explained; quotes are word for word.
CREATE TABLE legal_acts (
    id              TEXT NOT NULL PRIMARY KEY,
    short_name      TEXT NOT NULL,
    title           TEXT NOT NULL,
    consolidated_to TEXT,
    source_url      TEXT NOT NULL
);

CREATE TABLE question_explanations (
    question_id      TEXT NOT NULL REFERENCES questions (id),
    language         TEXT NOT NULL CHECK (language = 'bg'),
    source_hash      TEXT NOT NULL,
    kind             TEXT NOT NULL CHECK (kind IN ('law', 'general')),
    explanation_text TEXT NOT NULL,
    PRIMARY KEY (question_id, language)
);

CREATE TABLE explanation_references (
    question_id TEXT    NOT NULL REFERENCES questions (id),
    language    TEXT    NOT NULL CHECK (language = 'bg'),
    position    INTEGER NOT NULL,
    act_id      TEXT    NOT NULL REFERENCES legal_acts (id),
    unit        TEXT    NOT NULL,
    quote       TEXT    NOT NULL,
    PRIMARY KEY (question_id, language, position)
);
CREATE INDEX idx_explanation_references_act ON explanation_references (act_id);

-- How each derivative was made (stamp removed, enlarged, vector drawing) and the third-party drawings it uses.
-- Credits are required by the drawings' licences (Wikimedia Commons: CC BY-SA, CC BY, CC0, public domain).
CREATE TABLE media_processing (
    media_id TEXT    NOT NULL REFERENCES media (id),
    format   TEXT    NOT NULL,
    position INTEGER NOT NULL,
    step     TEXT    NOT NULL,
    PRIMARY KEY (media_id, format, position)
);

CREATE TABLE media_credits (
    media_id    TEXT    NOT NULL REFERENCES media (id),
    position    INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    author      TEXT    NOT NULL,
    license     TEXT    NOT NULL,
    license_url TEXT,
    page_url    TEXT    NOT NULL,
    sha1        TEXT    NOT NULL,
    PRIMARY KEY (media_id, position)
);
CREATE INDEX idx_media_credits_title ON media_credits (title);
