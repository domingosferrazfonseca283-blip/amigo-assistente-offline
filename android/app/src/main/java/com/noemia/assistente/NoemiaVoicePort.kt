package com.noemia.assistente

/** Contrato para futuros motores de voz totalmente embarcados/offline. */
interface NoemiaVoicePort {
    fun speak(text: String)
    fun stop()
    fun shutdown()
}
