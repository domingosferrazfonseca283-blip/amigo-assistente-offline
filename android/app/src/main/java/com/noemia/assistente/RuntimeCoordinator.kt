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
            .put("history_visual_count", history.count { it.kind.startsWith("vision.") })
            .put("history_action_count", history.count { it.action != "none" })
            .put("history_vibration_count", history.count { it.action == "vibrate" })
            .put("history_failure_count", history.count { it.summary.contains("falha", ignoreCase = true) || it.summary.contains("erro", ignoreCase = true) })
        val decision = bridge.perceive(kind, enriched)
        val action = decision.optString("action", "none")
        val actionPayload = decision.optString("action_payload", "")
        val interpretation = decision.optString("interpretation", "")
        val semanticDescription = payload.optString("description", "").trim()
        val summary = when {
            interpretation.isNotBlank() -> interpretation
            semanticDescription.isNotBlank() -> semanticDescription
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
        } else {
            learnFromExperience("conversation.failure", "none", text)
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

    /** Liga memória episódica a uma avaliação de resultado no núcleo afetivo. */
    private fun learnFromExperience(kind: String, action: String, summary: String) {
        val history = experienceStore.recent(24)
        val failures = history.count {
            it.summary.contains("falha", ignoreCase = true) ||
                it.summary.contains("erro", ignoreCase = true) ||
                it.summary.contains("não consegui", ignoreCase = true)
        }
        val outcome = when {
            kind.contains("failure", ignoreCase = true) || kind.contains("error", ignoreCase = true) -> "negative"
            kind == "conversation" && action == "speak" -> "positive"
            kind == "vision.semantic_error" -> "negative"
            kind == "vision.analysis" && summary.contains("escura", ignoreCase = true) -> "uncertain"
            kind == "vision.analysis" || kind == "vision.semantic" -> "safe"
            kind.startsWith("speech.") -> "positive"
            failures >= 3 -> "negative"
            action != "none" -> "positive"
            else -> "uncertain"
        }

        val intensity = when {
            outcome == "negative" -> 0.80
            kind == "conversation" -> 0.70
            kind.startsWith("vision.") -> 0.45
            else -> 0.35
        }

        bridge.perceive(
            "experience.outcome",
            JSONObject()
                .put("text", summary)
                .put("learning_outcome", outcome)
                .put("learning_intensity", intensity)
        )
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
