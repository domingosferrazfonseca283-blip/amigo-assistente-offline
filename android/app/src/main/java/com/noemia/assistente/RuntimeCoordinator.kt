package com.noemia.assistente

import android.content.Context
import org.json.JSONObject

/** Coordena o corpo Android, memória episódica e estado afetivo persistente da Noémia. */
class RuntimeCoordinator(
    context: Context,
    private val bridge: CognitiveBridge,
    private val onAction: (action: String, payload: String) -> Unit = { _, _ -> },
) {
    private val store = NoemiaStore(context.applicationContext)
    private val experienceStore = NoemiaExperienceStore(context.applicationContext)

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
        val history = experienceStore.recent(20)
        val enriched = JSONObject(payload.toString())
            .put("history_count", history.size)
            .put("history_conversation_count", history.count { it.kind == "conversation" })
            .put("history_visual_count", history.count { it.kind == "vision.analysis" })
            .put("history_action_count", history.count { it.action != "none" })
            .put("history_vibration_count", history.count { it.action == "vibrate" })
            .put("history_failure_count", history.count { it.summary.contains("falha", ignoreCase = true) || it.summary.contains("erro", ignoreCase = true) })
        val decision = bridge.perceive(kind, enriched)
        val action = decision.optString("action", "none")
        val actionPayload = decision.optString("action_payload", "")
        val interpretation = decision.optString("interpretation", "")
        val summary = when {
            interpretation.isNotBlank() -> interpretation
            payload.optString("text").isNotBlank() -> payload.optString("text")
            else -> "Percepção recebida: $kind"
        }
        experienceStore.remember(kind, summary, action, actionPayload)
        learnFromExperience(kind, action, summary)
        dispatchDecision(decision)
        persist()
    }

    fun converse(text: String): String {
        val response = bridge.converse(text)
        if (response.isNotBlank()) {
            experienceStore.remember("conversation", "Utilizador: $text | Noémia: $response", "speak", response)
            learnFromExperience("conversation", "speak", text)
            onAction("speak", response)
        }
        persist()
        return response
    }

    fun internalCycle(activity: String = "reflect") {
        val decision = bridge.internalCycle(activity)
        val focus = decision.optString("focus", "")
        val drive = decision.optString("drive", "")
        if (focus.isNotBlank() || drive.isNotBlank()) {
            experienceStore.remember(
                "internal.$activity",
                "Impulso interno: $drive${if (focus.isNotBlank()) " — $focus" else ""}",
                decision.optString("action", "none"),
                decision.optString("action_payload", ""),
            )
        }
        dispatchDecision(decision)
        persist()
    }

    fun recentExperiences(limit: Int = 20): List<NoemiaExperienceStore.Experience> =
        experienceStore.recent(limit)

    /**
     * Converte consequências de experiências recentes em alterações pequenas e persistentes
     * do estado afetivo. O efeito é limitado para evitar que uma única experiência domine o estado.
     */
    private fun learnFromExperience(kind: String, action: String, summary: String) {
        val snapshot = bridge.snapshot()
        val being = snapshot.optJSONObject("being") ?: return
        val affect = being.optJSONObject("affect") ?: return
        val history = experienceStore.recent(24)
        val conversations = history.count { it.kind == "conversation" }
        val reactions = history.count { it.action != "none" }
        val failures = history.count {
            it.summary.contains("falha", ignoreCase = true) ||
                it.summary.contains("erro", ignoreCase = true) ||
                it.summary.contains("não consegui", ignoreCase = true)
        }
        val meaningful = summary.isNotBlank() && (kind == "conversation" || action != "none" || summary.length > 24)
        if (!meaningful) return

        fun bounded(name: String, delta: Double) {
            val current = affect.optDouble(name, 0.0)
            affect.put(name, (current + delta).coerceIn(0.0, 1.0))
        }

        when (kind) {
            "conversation" -> {
                bounded("affection", 0.008)
                bounded("joy", 0.006)
                bounded("loneliness", -0.025)
                bounded("calmness", 0.004)
            }
            "vision.analysis" -> {
                bounded("curiosity", 0.010)
                if (action == "vibrate") bounded("fear", 0.004)
            }
            else -> bounded("curiosity", 0.002)
        }

        if (conversations >= 5) bounded("affection", 0.004)
        if (reactions >= 3) bounded("novelty", 0.002)
        if (failures > 0) {
            bounded("frustration", 0.006 * failures.coerceAtMost(3))
            bounded("calmness", -0.004)
        }

        val updated = JSONObject(snapshot.toString()).put("being", being)
        bridge.restore(updated)
    }

    private fun dispatchDecision(payload: JSONObject) {
        val action = payload.optString("action", "none")
        if (action.isBlank() || action == "none") return
        onAction(action, payload.optString("action_payload", ""))
    }

    fun persist() {
        store.save(
            JSONObject()
                .put("schema_version", 4)
                .put("runtime", bridge.snapshot())
        )
    }
}
