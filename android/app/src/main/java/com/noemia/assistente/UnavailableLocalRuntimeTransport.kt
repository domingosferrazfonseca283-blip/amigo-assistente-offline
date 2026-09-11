package com.noemia.assistente

/**
 * Host explícito enquanto o runtime cognitivo ainda não está empacotado no APK.
 * Falhar claramente é preferível a regressar silenciosamente à ponte simulada.
 */
class UnavailableLocalRuntimeTransport : LocalRuntimeTransport {
    override fun execute(request: RuntimeRequest): RuntimeResponse = RuntimeResponse(
        ok = false,
        error = "Núcleo cognitivo local ainda não foi carregado neste APK (comando=${request.command})",
        requestId = request.requestId
    )
}
