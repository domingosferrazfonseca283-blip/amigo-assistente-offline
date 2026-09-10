package com.noemia.assistente

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

/**
 * Memória de longo prazo local, separando episódios de crenças.
 * A memória guarda origem e confiança para evitar transformar inferências em factos.
 */
class LongTermMemoryStore(context: Context) {
    private val prefs = context.getSharedPreferences("noemia_long_term_memory", Context.MODE_PRIVATE)

    fun addEpisode(summary: String, details: JSONObject = JSONObject(), importance: Double = 0.5): String {
        val item = JSONObject()
            .put("id", UUID.randomUUID().toString())
            .put("summary", summary)
            .put("details", details)
            .put("importance", importance.coerceIn(0.0, 1.0))
            .put("created_at", System.currentTimeMillis())
        val episodes = readArray(KEY_EPISODES)
        episodes.put(item)
        writeArray(KEY_EPISODES, trim(episodes, MAX_EPISODES))
        return item.getString("id")
    }

    fun learnBelief(subject: String, predicate: String, value: String, confidence: Double = 0.5, source: String = "internal"): String {
        val item = JSONObject()
            .put("id", UUID.randomUUID().toString())
            .put("subject", subject)
            .put("predicate", predicate)
            .put("value", value)
            .put("confidence", confidence.coerceIn(0.0, 1.0))
            .put("source", source)
            .put("created_at", System.currentTimeMillis())
            .put("updated_at", System.currentTimeMillis())
        val beliefs = readArray(KEY_BELIEFS)
        beliefs.put(item)
        writeArray(KEY_BELIEFS, trim(beliefs, MAX_BELIEFS))
        return item.getString("id")
    }

    fun search(query: String, limit: Int = 12): JSONObject {
        val terms = query.lowercase().split(Regex("\\s+")).filter { it.isNotBlank() }.toSet()
        val result = JSONObject()
        result.put("episodes", rank(readArray(KEY_EPISODES), terms, limit))
        result.put("beliefs", rank(readArray(KEY_BELIEFS), terms, limit))
        return result
    }

    fun snapshot(): JSONObject = JSONObject()
        .put("episodes", readArray(KEY_EPISODES))
        .put("beliefs", readArray(KEY_BELIEFS))

    fun restore(snapshot: JSONObject?) {
        if (snapshot == null) return
        snapshot.optJSONArray("episodes")?.let { writeArray(KEY_EPISODES, trim(it, MAX_EPISODES)) }
        snapshot.optJSONArray("beliefs")?.let { writeArray(KEY_BELIEFS, trim(it, MAX_BELIEFS)) }
    }

    private fun rank(items: JSONArray, terms: Set<String>, limit: Int): JSONArray {
        val scored = mutableListOf<Pair<Int, JSONObject>>()
        for (i in 0 until items.length()) {
            val item = items.getJSONObject(i)
            val text = item.toString().lowercase()
            val score = terms.count { text.contains(it) }
            if (score > 0) scored += score to item
        }
        val result = JSONArray()
        scored.sortedByDescending { it.first }.take(limit.coerceAtLeast(1)).forEach { result.put(it.second) }
        return result
    }

    private fun readArray(key: String): JSONArray = runCatching {
        JSONArray(prefs.getString(key, "[]") ?: "[]")
    }.getOrDefault(JSONArray())

    private fun writeArray(key: String, value: JSONArray) {
        prefs.edit().putString(key, value.toString()).apply()
    }

    private fun trim(source: JSONArray, max: Int): JSONArray {
        val start = (source.length() - max).coerceAtLeast(0)
        val result = JSONArray()
        for (i in start until source.length()) result.put(source.get(i))
        return result
    }

    companion object {
        private const val KEY_EPISODES = "episodes"
        private const val KEY_BELIEFS = "beliefs"
        private const val MAX_EPISODES = 5000
        private const val MAX_BELIEFS = 5000
    }
}
