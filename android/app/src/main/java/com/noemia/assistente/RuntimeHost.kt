package com.noemia.assistente

/** Instala as capacidades cognitivas locais no runtime da Noémia. */
object RuntimeHost {
    fun createTransport(): LocalRuntimeTransport = NativeLocalRuntimeTransport()

    fun createOnDeviceModel(): NoemiaOnDeviceModel = NoemiaOnDeviceModel()

    fun createBridge(onDeviceModel: NoemiaOnDeviceModel = createOnDeviceModel()): CognitiveBridge =
        ProtocolCognitiveBridge(
            transport = createTransport(),
            onDeviceModel = onDeviceModel,
        )
}
