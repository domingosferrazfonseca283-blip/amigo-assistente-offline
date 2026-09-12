package com.noemia.assistente

import org.json.JSONObject

/**
 * Ponte cognitiva orientada a protocolo.
 * O Android conhece apenas comandos, payloads e snapshots; não conhece a
 * implementação interna da mente local.
 */
class ProtocolCognitiveBridge(
    private val transport: LocalRuntimeTransport,
    private val onDeviceModel: NoemiaOnDeviceModel? = null,
) : CognitiveBridge {

    override fun restore(snapshot: JSONObject?) {
        if (snapshot == null) return
        val response = transport.execute(
            RuntimeRequest(
                command = RuntimeCommands.SNAPSHOT,
                payload = JSONObject().put("restore", snapshot)
            )
        )
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha ao restaurar o núcleo cognitivo local")
        }
    }

    override fun perceive(kind: String, payload: JSONObject): JSONObject {
        val enriched = JSONObject(payload.toString()).put("kind", kind)
        val response = transport.execute(
            RuntimeRequest(RuntimeCommands.PERCEIVE, enriched)
        )
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha ao processar percepção local")
        }
        return response.payload
    }

    override fun converse(text: String): String {
        val state = transport.execute(
            RuntimeRequest(
                RuntimeCommands.THINK,
                JSONObject().put("text", text)
            )
        )
        if (!state.ok) {
            throw IllegalStateException(state.error ?: "Falha no núcleo cognitivo local")
        }

        val model = onDeviceModel
        if (model != null) {
            try {
                val prompt = buildModelPrompt(text, state.payload)
                val generated = model.generate(prompt)
                if (generated.isNotBlank()) return generated
            } catch (_: Exception) {
                // O núcleo continua funcional quando o modelo de dispositivo
                // não está disponível neste hardware/configuração.
            }
        }

        return state.payload.optString("text", "")
    }

    override fun internalCycle(activity: String): JSONObject {
        val response = transport.execute(
            RuntimeRequest(
                RuntimeCommands.INTERNAL_CYCLE,
                JSONObject().put("activity", activity)
            )
        )
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha no ciclo cognitivo local")
        }
        return response.payload
    }

    override fun snapshot(): JSONObject {
        val response = transport.execute(RuntimeRequest(RuntimeCommands.SNAPSHOT))
        if (!response.ok) {
            throw IllegalStateException(response.error ?: "Falha ao obter snapshot")
        }
        return response.payload
    }

    private fun buildModelPrompt(text: String, state: JSONObject): String {
        val affect = state.optString("affect_state", "calma")
        val focus = state.optString("current_focus", "")
        return """
            Você é a inteligência local de Noémia.
            Noémia é uma entidade artificial persistente; o modelo é apenas um componente da sua inteligência.
            Responda em português natural, com clareza e sem inventar memórias, perceções ou capacidades.
            Não diga que tem consciência biológica ou emoções reais.

            Estado funcional atual: $affect.
            Foco funcional: $focus.

            Mensagem do utilizador:
            $text
        """.trimIndent()
    }
}
