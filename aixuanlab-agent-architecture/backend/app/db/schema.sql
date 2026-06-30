-- aixuanlab Excel AI Agent database schema
-- Adapt this SQL to your real database or ORM.

CREATE TABLE IF NOT EXISTS user_profiles (
  user_id TEXT PRIMARY KEY,
  excel_level TEXT DEFAULT 'beginner',
  target_role TEXT,
  learning_goal TEXT,
  preferred_scenarios TEXT,
  preferred_explanation_style TEXT DEFAULT '先给提示，再给答案',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS practice_questions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  role TEXT,
  difficulty TEXT NOT NULL,
  function_tags TEXT NOT NULL,
  scenario TEXT,
  question_json TEXT NOT NULL,
  answer_formula TEXT NOT NULL,
  created_by TEXT,
  source TEXT DEFAULT 'site',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS practice_attempts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  practice_id TEXT NOT NULL,
  target_cell TEXT,
  user_formula TEXT,
  expected_formula TEXT,
  is_correct INTEGER NOT NULL DEFAULT 0,
  error_type TEXT,
  hint_used_count INTEGER DEFAULT 0,
  answer_revealed INTEGER DEFAULT 0,
  time_spent_seconds INTEGER DEFAULT 0,
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_practice_attempts_user ON practice_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_attempts_practice ON practice_attempts(practice_id);

CREATE TABLE IF NOT EXISTS user_function_mastery (
  user_id TEXT NOT NULL,
  function_name TEXT NOT NULL,
  total_attempts INTEGER DEFAULT 0,
  correct_attempts INTEGER DEFAULT 0,
  accuracy_rate REAL DEFAULT 0,
  recent_accuracy_rate REAL DEFAULT 0,
  common_error_types TEXT,
  mastery_score INTEGER DEFAULT 0,
  mastery_level TEXT DEFAULT '未入门',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, function_name)
);

CREATE TABLE IF NOT EXISTS learning_memories (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  memory_type TEXT NOT NULL,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  confidence REAL DEFAULT 0,
  related_function TEXT,
  related_scenario TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_learning_memories_user ON learning_memories(user_id);

CREATE TABLE IF NOT EXISTS ai_conversations (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT,
  summary TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  related_practice_id TEXT,
  related_file_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation ON ai_messages(conversation_id);

CREATE TABLE IF NOT EXISTS uploaded_files (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  file_size INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generated_files (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  source_type TEXT,
  source_id TEXT,
  filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  download_url TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
