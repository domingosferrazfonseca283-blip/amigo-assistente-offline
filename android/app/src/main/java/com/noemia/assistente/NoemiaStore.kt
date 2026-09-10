package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/**
 * Armazenamento local mínimo e atómico para o estado da Noémia.
 *
 * A cifra de dados sensíveis será ligada na camada de segurança antes de
 * guardar memórias privadas. O núcleo não depende de uma base remota.
 */
class NoemiaStore(context: Context) {
    private val prefs = context.getSharedPreferences("noemia_state", Context.MODE_PRIVATE)

    fun save(snapshot: JSONObject) {
        prefs.edit()
            .putString(KEY_SNAPSHOT, snapshot.toString())
            .apply()
    }

    fun load(): JSONObject? {
        val raw = prefs.getString(KEY_SNAPSHOT, null) ?: return null
        return runCatching { JSONObject(raw) }.getOrNull()
    }

    fun clear() {
        prefs.edit().remove(KEY_SNAPSHOT).apply()
    }

    companion object {
        private const val KEY_SNAPSHOT = "cognitive_snapshot"
    }
}
