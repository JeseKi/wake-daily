#!/bin/sh
set -e

DB_PATH="/app/data/database.db"
BACKUP_PATH="${DB_PATH}.bak"

backup_database() {
    if [ ! -f "$DB_PATH" ]; then
        echo "未找到现有数据库，跳过备份"
        return 0
    fi

    echo "开始备份数据库..."
    rm -f "${BACKUP_PATH}.3"

    if [ -f "${BACKUP_PATH}.2" ]; then
        mv "${BACKUP_PATH}.2" "${BACKUP_PATH}.3"
    fi

    if [ -f "${BACKUP_PATH}.1" ]; then
        mv "${BACKUP_PATH}.1" "${BACKUP_PATH}.2"
    fi

    if [ -f "$BACKUP_PATH" ]; then
        mv "$BACKUP_PATH" "${BACKUP_PATH}.1"
    fi

    cp "$DB_PATH" "$BACKUP_PATH"
    echo "数据库备份完成: ${BACKUP_PATH}"
}

detect_existing_schema_revision() {
    DB_PATH="$DB_PATH" python - <<'PY'
import os
import sqlite3

db_path = os.environ["DB_PATH"]
conn = sqlite3.connect(db_path)
try:
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if "alembic_version" in tables:
        version = conn.execute("SELECT version_num FROM alembic_version").fetchone()
        if version and version[0]:
            print("")
            raise SystemExit

    if "journal_awareness_sessions" in tables:
        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(journal_awareness_sessions)"
            ).fetchall()
        }
        if {
            "entry_mode",
            "free_content",
            "analysis_marks_json",
            "inquiry_records_json",
        }.issubset(columns):
            print("20260604_0003")
        else:
            print("20260601_0002")
    elif "daily_questions" in tables:
        print("20260517_0001")
    else:
        print("")
finally:
    conn.close()
PY
}

stamp_existing_schema_if_needed() {
    BASELINE_REVISION="$(detect_existing_schema_revision)"
    if [ -z "$BASELINE_REVISION" ]; then
        return 0
    fi

    echo "检测到已有数据库结构但缺少迁移版本，标记基线: ${BASELINE_REVISION}"
    alembic stamp "$BASELINE_REVISION"
}

# 确保 data 目录存在（volume 挂载时可能为空）
mkdir -p /app/data

backup_database

# 运行数据库迁移

if [ ! -f "$DB_PATH" ]; then
    echo "未找到现有数据库，跳过迁移"

else
    echo "正在运行数据库迁移..."
    stamp_existing_schema_if_needed
    alembic upgrade head
    echo "数据库迁移完成"
fi

# 启动应用
exec python run.py
