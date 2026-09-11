package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/**
 * Coordena o corpo Android e o único estado persistente da Noémia.
 *
 * A fonte de verdade é o snapshot devolvido pelo núcleo cognitivo local.
 * O Android não mantém uma segunda cópia de necessidades, fase ou pulsos.
 */
class RuntimeCoordinator(context: Context, private val bridge: CognitiveBridge) {
    private val store = NoemiaStore(context.applicationContext)

    fun start() {
        val saved = store.load()
        val runtimeSnapshot = when {
            saved == null -> null
            saved.has("runtime") -> saved.optJSONObject("runtime")
            else -> saved // compatibilidade com snapshots antigos sem envelope
        }

        if (runtimeSnapshot != null) {
            bridge.restore(runtimeSnapshot)
        }
    }

    fun onPerception(kind: String, payload: JSONObject) {
        bridge.perceive(kind, payload)
        persist()
    }

    fun converse(text: String): String {
        val response = bridge.converse(text)
        persist()
        return response
    }

    fun internalCycle(activity: String = "reflect") {
        bridge.internalCycle(activity)
        persist()
    }

    fun persist() {
        store.save(
            JSONObject()
                .put("schema_version", 3)
                .put("runtime", bridge.snapshot())
        )
    }
}
