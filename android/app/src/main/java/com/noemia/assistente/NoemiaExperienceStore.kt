package com.noemia.assistente

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/** Memória episódica local do corpo Android. Não depende da rede. */
class NoemiaExperienceStore(context: Context) : SQLiteOpenHelper(
    context.applicationContext,
    "noemia_experiences.db",
    null,
    1,
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                kind TEXT NOT NULL,
                summary TEXT NOT NULL,
                action TEXT NOT NULL DEFAULT 'none',
                action_payload TEXT NOT NULL DEFAULT ''
            )
            """.trimIndent()
        )
        db.execSQL("CREATE INDEX idx_experiences_kind_time ON experiences(kind, timestamp DESC)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) = Unit

    fun remember(kind: String, summary: String, action: String = "none", actionPayload: String = "") {
        if (summary.isBlank()) return
        val values = ContentValues().apply {
            put("timestamp", System.currentTimeMillis())
            put("kind", kind)
            put("summary", summary)
            put("action", action)
            put("action_payload", actionPayload)
        }
        writableDatabase.insert("experiences", null, values)
    }

    fun recent(limit: Int = 20): List<Experience> {
        val result = mutableListOf<Experience>()
        readableDatabase.query(
            "experiences",
            arrayOf("timestamp", "kind", "summary", "action", "action_payload"),
            null, null, null, null,
            "timestamp DESC",
            limit.coerceIn(1, 100).toString(),
        ).use { cursor ->
            while (cursor.moveToNext()) {
                result += Experience(
                    timestamp = cursor.getLong(0),
                    kind = cursor.getString(1),
                    summary = cursor.getString(2),
                    action = cursor.getString(3),
                    actionPayload = cursor.getString(4),
                )
            }
        }
        return result
    }

    data class Experience(
        val timestamp: Long,
        val kind: String,
        val summary: String,
        val action: String,
        val actionPayload: String,
    )
}
