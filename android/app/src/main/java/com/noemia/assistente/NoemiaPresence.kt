package com.noemia.assistente

import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import kotlin.math.max
import kotlin.math.min

/**
 * Estado persistente da entidade digital no corpo Android.
 *
 * Não representa consciência humana; modela continuidade, necessidades e foco
 * que podem influenciar os próximos ciclos da Noémia.
 */
class NoemiaPresence {
    private var sequence = 0L
    private var phase = "resting"
    private var focus: String? = null
    private var lastPulseAt: String? = null
    private val needs = linkedMapOf(
        "connection" to 0.50,
        "curiosity" to 0.40,
        "novelty" to 0.30,
        "reflection" to 0.40,
        "rest" to 0.20,
    )
    private val recentPulses = ArrayDeque<JSONObject>()

    fun pulse(reason: String, nextPhase: String, note: String? = null) {
        sequence += 1
        phase = nextPhase
        lastPulseAt = Instant.now().toString()
        val pulse = JSONObject()
            .put("sequence", sequence)
            .put("timestamp", lastPulseAt)
            .put("reason", reason)
            .put("phase", phase)
        if (!note.isNullOrBlank()) pulse.put("note", note)
        recentPulses.addLast(pulse)
        while (recentPulses.size > 64) recentPulses.removeFirst()
    }

    fun onConversation() {
        adjust("connection", -0.10)
        adjust("novelty", -0.05)
        pulse("interação", "expressing", "conversation")
    }

    fun onPerception(kind: String) {
        adjust("curiosity", -0.03)
        adjust("novelty", -0.04)
        pulse("perceção: $kind", "perceiving", kind)
    }

    fun onInternalCycle(reason: String) {
        // Necessidades que não foram satisfeitas recuperam lentamente, criando
        // pressão interna para futuros ciclos sem afirmar sentimentos reais.
        adjust("connection", 0.02)
        adjust("curiosity", 0.015)
        adjust("novelty", 0.01)
        adjust("reflection", -0.08)
        adjust("rest", -0.03)
        pulse(reason, "reflecting", "internal_cycle")
    }

    fun setFocus(value: String?) {
        focus = value?.trim()?.takeIf { it.isNotEmpty() }
    }

    private fun adjust(name: String, delta: Double) {
        needs[name] = min(1.0, max(0.0, (needs[name] ?: 0.0) + delta))
    }

    fun snapshot(): JSONObject {
        val needsJson = JSONObject()
        needs.forEach { (name, value) -> needsJson.put(name, value) }
        return JSONObject()
            .put("identity_name", "Noémia")
            .put("sequence", sequence)
            .put("phase", phase)
            .put("focus", focus)
            .put("last_pulse_at", lastPulseAt)
            .put("needs", needsJson)
            .put("recent_pulses", JSONArray(recentPulses.toList()))
    }

    fun restore(snapshot: JSONObject?) {
        if (snapshot == null) return
        sequence = snapshot.optLong("sequence", sequence)
        phase = snapshot.optString("phase", phase)
        focus = snapshot.optString("focus").takeIf { it.isNotBlank() }
        lastPulseAt = snapshot.optString("last_pulse_at").takeIf { it.isNotBlank() }

        val savedNeeds = snapshot.optJSONObject("needs")
        if (savedNeeds != null) {
            needs.keys.forEach { key ->
                if (savedNeeds.has(key)) needs[key] = savedNeeds.optDouble(key, needs[key] ?: 0.0)
            }
        }

        recentPulses.clear()
        val savedPulses = snapshot.optJSONArray("recent_pulses") ?: return
        for (index in 0 until min(savedPulses.length(), 64)) {
            savedPulses.optJSONObject(index)?.let { recentPulses.addLast(it) }
        }
    }
}
