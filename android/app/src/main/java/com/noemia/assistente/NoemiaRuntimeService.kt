package com.noemia.assistente

import android.app.Service
import android.content.Intent
import android.os.IBinder

/**
 * Corpo Android da Noémia.
 *
 * O serviço é deliberadamente um shell: o núcleo cognitivo e os adaptadores
 * locais serão ligados aqui sem conceder permissões implícitas.
 */
class NoemiaRuntimeService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // O runtime real será inicializado numa fase posterior, com estado
        // persistente e adaptadores de percepção explicitamente autorizados.
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
