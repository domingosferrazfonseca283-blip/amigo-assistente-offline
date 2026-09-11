package com.noemia.assistente

import org.json.JSONObject

/**
 * Ponte cognitiva orientada a protocolo.
 * O Android conhece apenas comandos, payloads e snapshots; não conhece a
 * implementação interna da mente local.
 */
class ProtocolCognitiveBridge(
    private val transport: LocalRuntimeTransport
) : CognitiveBridge {

    override fun restore(snapshot: JSONObject?) {
        if (snapshot == null) return
        transport.execute(
            RuntimeRequest(
                command = RuntimeCommands.SNAPSHOT,
                payload = JSONObject().put("restore", snapshot)
            )
        )
    }

    override fun perceive(kind: String, payload: JSONObject) {
        val enriched = JSONObject(payload.toString()).put("kind", kind)
        transport.execute(
            RuntimeRequest(RuntimeCommands.PERCEIVE, enriched)
        )
    }

    override fun converse(text: String): String {
        val response = transport.execute(
            RuntimeRequest(
                RuntimeCommands.THINK,
                JSONObject().put("text", text)
            )
        )
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha no núcleo cognitivo local")
        }
        return response.payload.optString("text", "")
    }

    override fun internalCycle(activity: String) {
        val response = transport.execute(
            RuntimeRequest(
                RuntimeCommands.INTERNAL_CYCLE,
                JSONObject().put("activity", activity)
            )
        )
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha no ciclo cognitivo interno")
        }
    }

    override fun snapshot(): JSONObject {
        val response = transport.execute(RuntimeRequest(RuntimeCommands.SNAPSHOT))
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha ao obter snapshot")
        }
        return response.payload
    }
}
