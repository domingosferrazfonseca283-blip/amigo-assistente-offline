package com.noemia.assistente

import android.app.Service
import android.content.Intent
import android.os.IBinder
import org.json.JSONObject

/** Corpo Android: hospeda o núcleo cognitivo local e persiste o seu estado. */
class NoemiaRuntimeService : Service() {
    private lateinit var coordinator: RuntimeCoordinator
    private lateinit var internalScheduler: InternalCognitionScheduler

    override fun onCreate() {
        super.onCreate()
        // O caminho oficial é o núcleo compilado no próprio APK: sem sockets,
        // sem HTTP e sem depender de um serviço remoto.
        coordinator = RuntimeCoordinator(applicationContext, RuntimeHost.createBridge())
        coordinator.start()
        internalScheduler = InternalCognitionScheduler {
            coordinator.internalCycle("reflect")
        }
        internalScheduler.start()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PERCEIVE -> {
                internalScheduler.externalActivity()
                val kind = intent.getStringExtra(EXTRA_KIND) ?: "system"
                val text = intent.getStringExtra(EXTRA_TEXT) ?: ""
                coordinator.onPerception(kind, JSONObject().put("text", text))
            }
            ACTION_INTERNAL_CYCLE -> coordinator.internalCycle(
                intent.getStringExtra(EXTRA_ACTIVITY) ?: "reflect"
            )
            ACTION_SNAPSHOT -> coordinator.persist()
        }
        return START_STICKY
    }

    override fun onDestroy() {
        internalScheduler.stop()
        coordinator.persist()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val ACTION_PERCEIVE = "com.noemia.assistente.PERCEIVE"
        const val ACTION_INTERNAL_CYCLE = "com.noemia.assistente.INTERNAL_CYCLE"
        const val ACTION_SNAPSHOT = "com.noemia.assistente.SNAPSHOT"
        const val EXTRA_KIND = "kind"
        const val EXTRA_TEXT = "text"
        const val EXTRA_ACTIVITY = "activity"
    }
}
