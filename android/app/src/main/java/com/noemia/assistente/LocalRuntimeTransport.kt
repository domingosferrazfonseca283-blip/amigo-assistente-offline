package com.noemia.assistente

/**
 * Transporte local para o núcleo cognitivo.
 *
 * A implementação pode ser JNI/NDK, processo local empacotado ou outro runtime
 * embarcado. A interface não permite HTTP nem exige acesso à Internet.
 */
interface LocalRuntimeTransport {
    fun execute(request: RuntimeRequest): RuntimeResponse
}
