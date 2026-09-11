package com.noemia.assistente

import org.json.JSONObject
import java.util.UUID

/** Contrato neutro entre o corpo Android e qualquer núcleo cognitivo local. */
data class RuntimeRequest(
    val command: String,
    val payload: JSONObject = JSONObject(),
    val requestId: String = UUID.randomUUID().toString()
) {
    fun toJson(): JSONObject = JSONObject()
        .put("command", command)
        .put("payload", payload)
        .put("request_id", requestId)
}

data class RuntimeResponse(
    val ok: Boolean,
    val payload: JSONObject = JSONObject(),
    val error: String? = null,
    val requestId: String = ""
) {
    fun toJson(): JSONObject = JSONObject()
        .put("ok", ok)
        .put("payload", payload)
        .put("error", error)
        .put("request_id", requestId)
}

object RuntimeCommands {
    const val PERCEIVE = "perceive"
    const val THINK = "think"
    const val INTERNAL_CYCLE = "internal_cycle"
    const val SNAPSHOT = "snapshot"
}
