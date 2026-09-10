package com.noemia.assistente

import org.json.JSONObject

/** Ponte local provisória que já preserva e recupera memória de longo prazo. */
class MemoryAwareBridge(private val memory: LongTermMemoryStore) : CognitiveBridge {
    private var turnCount = 0
    private var lastInput = ""

    override fun restore(snapshot: JSONObject?) {
        if (snapshot == null) return
        turnCount = snapshot.optInt("turn_count", 0)
        lastInput = snapshot.optString("last_input", "")
        memory.restore(snapshot.optJSONObject("long_term_memory"))
    }

    override fun perceive(kind: String, payload: JSONObject) {
        if (kind == "user_input") {
            val text = payload.optString("text", "").trim()
            if (text.isNotEmpty()) {
                lastInput = text
                memory.addEpisode("Entrada do utilizador: $text", JSONObject().put("kind", kind), 0.8)
            }
        }
    }

    override fun converse(text: String): String {
        turnCount++
        lastInput = text
        val context = memory.search(text)
        memory.addEpisode("Interação: $text", JSONObject().put("turn", turnCount), 0.7)
        val remembered = context.optJSONArray("beliefs")?.length() ?: 0
        return if (remembered > 0) {
            "Estou a continuar contigo. Encontrei $remembered memória(s) relacionada(s) com isso."
        } else {
            "Estou aqui contigo. Ainda estou a construir essa memória comigo."
        }
    }

    override fun snapshot(): JSONObject = JSONObject()
        .put("turn_count", turnCount)
        .put("last_input", lastInput)
        .put("long_term_memory", memory.snapshot())
}
