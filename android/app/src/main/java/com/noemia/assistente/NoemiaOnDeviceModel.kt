package com.noemia.assistente

import com.google.mlkit.genai.common.FeatureStatus
import com.google.mlkit.genai.prompt.Generation
import com.google.mlkit.genai.prompt.java.GenerativeModelFutures
import java.util.concurrent.TimeUnit

/**
 * Adaptador de inteligência local. O modelo é uma capacidade do corpo Android,
 * não a identidade da Noémia.
 */
class NoemiaOnDeviceModel {
    private val model = Generation.getClient()
    private val futures = GenerativeModelFutures.from(model)

    fun generate(prompt: String): String {
        val status = futures.checkStatus().get(15, TimeUnit.SECONDS)
        if (status != FeatureStatus.AVAILABLE) {
            throw IllegalStateException("Gemini Nano indisponível neste dispositivo (estado=$status)")
        }
        val response = futures.generateContent(prompt).get(120, TimeUnit.SECONDS)
        return response.candidates.firstOrNull()?.text?.trim().orEmpty()
    }

    fun close() {
        model.close()
    }
}
