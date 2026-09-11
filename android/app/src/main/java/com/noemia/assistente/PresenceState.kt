package com.noemia.assistente

/**
 * Snapshot visual imutável da Noémia.
 *
 * A presença visual pode interpretar este estado, mas nunca o altera.
 * O estado cognitivo continua a pertencer ao runtime persistente.
 */
data class PresenceState(
    val phase: String = "resting",
    val curiosity: Float = 0.40f,
    val connection: Float = 0.50f,
    val novelty: Float = 0.30f,
    val reflection: Float = 0.40f,
) {
    companion object {
        fun fromRuntime(saved: org.json.JSONObject): PresenceState {
            val runtime = saved.optJSONObject("runtime") ?: saved
            val being = runtime.optJSONObject("being") ?: return PresenceState()
            val needs = being.optJSONObject("needs")

            return PresenceState(
                phase = being.optString("phase", "resting"),
                curiosity = needs?.optDouble("curiosity", 0.40)?.toFloat()?.coerceIn(0f, 1f) ?: 0.40f,
                connection = needs?.optDouble("connection", 0.50)?.toFloat()?.coerceIn(0f, 1f) ?: 0.50f,
                novelty = needs?.optDouble("novelty", 0.30)?.toFloat()?.coerceIn(0f, 1f) ?: 0.30f,
                reflection = needs?.optDouble("reflection", 0.40)?.toFloat()?.coerceIn(0f, 1f) ?: 0.40f,
            )
        }
    }
}
