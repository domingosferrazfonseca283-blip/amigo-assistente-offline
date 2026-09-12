package com.noemia.assistente

import android.graphics.Bitmap
import com.google.mlkit.genai.common.FeatureStatus
import com.google.mlkit.genai.prompt.Generation
import com.google.mlkit.genai.prompt.ImagePart
import com.google.mlkit.genai.prompt.TextPart
import com.google.mlkit.genai.prompt.generateContentRequest
import com.google.mlkit.genai.prompt.java.GenerativeModelFutures
import java.util.concurrent.TimeUnit

/**
 * Adaptador de inteligência local. O modelo é uma capacidade do corpo Android,
 * não a identidade da Noémia.
 */
class NoemiaOnDeviceModel {
    private val model = Generation.getClient()
    private val futures = GenerativeModelFutures.from(model)

    private fun requireAvailable() {
        val status = futures.checkStatus().get(15, TimeUnit.SECONDS)
        if (status != FeatureStatus.AVAILABLE) {
            throw IllegalStateException("Gemini Nano indisponível neste dispositivo (estado=$status)")
        }
    }

    fun generate(prompt: String): String {
        requireAvailable()
        val response = futures.generateContent(prompt).get(120, TimeUnit.SECONDS)
        return response.candidates.firstOrNull()?.text?.trim().orEmpty()
    }

    /** Analisa uma imagem localmente no dispositivo, sem enviar a imagem para a rede. */
    fun describeImage(bitmap: Bitmap, prompt: String): String {
        requireAvailable()
        val request = generateContentRequest(
            ImagePart(bitmap),
            TextPart(prompt),
        )
        val response = futures.generateContent(request).get(120, TimeUnit.SECONDS)
        return response.candidates.firstOrNull()?.text?.trim().orEmpty()
    }

    fun close() {
        model.close()
    }
}
