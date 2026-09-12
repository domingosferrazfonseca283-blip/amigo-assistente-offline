package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/**
 * Coordena o corpo Android e o único estado persistente da Noémia.
 *
 * A fonte de verdade é o snapshot devolvido pelo núcleo cognitivo local.
 * O Android não mantém uma segunda cópia de necessidades, fase ou pulsos.
 */
class RuntimeCoordinator(
    context: Context,
    private val bridge: CognitiveBridge,
    private val onAction: (action: String, payload: String) -> Unit = { _, _ -> },
) {
    private val store = NoemiaStore(context.applicationContext)

    fun start() {
        val saved = store.load()
        val runtimeSnapshot = when {
            saved == null -> null
            saved.has("runtime") -> saved.optJSONObject("runtime")
            else -> saved
        }
        if (runtimeSnapshot != null) bridge.restore(runtimeSnapshot)
    }

    fun onPerception(kind: String, payload: JSONObject) {
        val decision = bridge.perceive(kind, payload)
        dispatchDecision(decision)
        persist()
    }

    fun converse(text: String): String {
        val response = bridge.converse(text)
        if (response.isNotBlank()) onAction("speak", response)
        persist()
        return response
    }

    fun internalCycle(activity: String = "reflect") {
        val decision = bridge.internalCycle(activity)
        dispatchDecision(decision)
        persist()
    }

    private fun dispatchDecision(payload: JSONObject) {
        val action = payload.optString("action", "none")
        if (action.isBlank() || action == "none") return
        onAction(action, payload.optString("action_payload", ""))
    }

    fun persist() {
        store.save(
            JSONObject()
                .put("schema_version", 3)
                .put("runtime", bridge.snapshot())
        )
    }
}
