package com.noemia.assistente

/** Seleciona explicitamente o hospedeiro do núcleo cognitivo. */
object RuntimeHost {
    fun createTransport(): LocalRuntimeTransport = UnavailableLocalRuntimeTransport()

    fun createBridge(): CognitiveBridge = ProtocolCognitiveBridge(createTransport())
}
