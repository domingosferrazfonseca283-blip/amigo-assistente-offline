package com.noemia.assistente

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * Saída de voz local da Noémia.
 *
 * Usa o motor TTS instalado no próprio dispositivo. Não cria nenhuma ligação
 * de rede e não assume que o motor tenha dados offline disponíveis.
 */
class NoemiaVoiceOutput(context: Context) : TextToSpeech.OnInitListener {
    private val tts = TextToSpeech(context.applicationContext, this)
    private var ready = false

    override fun onInit(status: Int) {
        if (status != TextToSpeech.SUCCESS) return

        val result = tts.setLanguage(Locale("pt", "PT"))
        ready = result != TextToSpeech.LANG_MISSING_DATA &&
            result != TextToSpeech.LANG_NOT_SUPPORTED
    }

    fun speak(text: String) {
        if (!ready || text.isBlank()) return
        tts.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null, "noemia-response")
    }

    fun stop() {
        tts.stop()
    }

    fun shutdown() {
        tts.stop()
        tts.shutdown()
    }
}
