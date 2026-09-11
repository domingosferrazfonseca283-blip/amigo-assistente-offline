package com.noemia.assistente

import android.content.Context

/** Liga respostas do núcleo à presença vocal sem colocar voz dentro da cognição. */
class NoemiaVoiceResponder(context: Context) {
    private val output = NoemiaVoiceOutput(context)

    fun respond(text: String) {
        output.speak(text)
    }

    fun stop() {
        output.stop()
    }

    fun shutdown() {
        output.shutdown()
    }
}
