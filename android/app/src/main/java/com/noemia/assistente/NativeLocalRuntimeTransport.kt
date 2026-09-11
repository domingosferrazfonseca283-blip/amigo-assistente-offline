package com.noemia.assistente

/**
 * Transporte para um motor cognitivo compilado dentro do APK.
 *
 * A API trabalha apenas com JSON serializado e não cria sockets. O motor nativo
 * pode evoluir independentemente do corpo Android.
 */
class NativeLocalRuntimeTransport : LocalRuntimeTransport {
    override fun execute(request: RuntimeRequest): RuntimeResponse {
        return try {
            val raw = nativeExecute(request.toJson().toString())
            val json = org.json.JSONObject(raw)
            RuntimeResponse(
                ok = json.optBoolean("ok", false),
                payload = json.optJSONObject("payload") ?: org.json.JSONObject(),
                error = json.optString("error").ifBlank { null },
                requestId = json.optString("request_id", request.requestId),
            )
        } catch (error: UnsatisfiedLinkError) {
            RuntimeResponse(
                ok = false,
                error = "Motor nativo local não carregado: ${error.message}",
                requestId = request.requestId,
            )
        }
    }

    private external fun nativeExecute(requestJson: String): String

    companion object {
        private const val LIBRARY_NAME = "noemia_runtime"

        init {
            runCatching { System.loadLibrary(LIBRARY_NAME) }
        }
    }
}
