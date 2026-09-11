package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/** Coordena restauração, ciclo de vida e gravação do estado cognitivo. */
class RuntimeCoordinator(context: Context, private val bridge: CognitiveBridge) {
    private val store = NoemiaStore(context.applicationContext)

    fun start() {
        bridge.restore(store.load())
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
        store.save(bridge.snapshot())
    }
}
