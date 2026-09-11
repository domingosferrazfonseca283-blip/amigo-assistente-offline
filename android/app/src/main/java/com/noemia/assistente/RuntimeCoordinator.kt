package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/** Coordena restauração, ciclo de vida e gravação do estado cognitivo. */
class RuntimeCoordinator(context: Context, private val bridge: CognitiveBridge) {
    private val store = NoemiaStore(context.applicationContext)
    private val presence = NoemiaPresence()

    fun start() {
        val saved = store.load()
        if (saved != null && saved.has("runtime")) {
            bridge.restore(saved.optJSONObject("runtime"))
            presence.restore(saved.optJSONObject("presence"))
        } else {
            // Compatibilidade com snapshots gravados antes da presença persistente.
            bridge.restore(saved)
            presence.pulse("primeiro arranque", "resting", "bootstrap")
        }
    }

    fun onPerception(kind: String, payload: JSONObject) {
        bridge.perceive(kind, payload)
        presence.onPerception(kind)
        persist()
    }

    fun converse(text: String): String {
        presence.onConversation()
        val response = bridge.converse(text)
        presence.setFocus(null)
        persist()
        return response
    }

    fun internalCycle(activity: String = "reflect") {
        presence.onInternalCycle(activity)
        bridge.internalCycle(activity)
        persist()
    }

    fun persist() {
        val snapshot = JSONObject()
            .put("schema_version", 2)
            .put("runtime", bridge.snapshot())
            .put("presence", presence.snapshot())
        store.save(snapshot)
    }
}
