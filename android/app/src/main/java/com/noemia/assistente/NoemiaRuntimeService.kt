package com.noemia.assistente

import android.app.Service
import android.content.Intent
import android.os.IBinder
import org.json.JSONObject

/** Corpo Android: mantém o núcleo vivo e restaura a memória local. */
class NoemiaRuntimeService : Service() {
    private lateinit var coordinator: RuntimeCoordinator

    override fun onCreate() {
        super.onCreate()
        val memory = LongTermMemoryStore(applicationContext)
        coordinator = RuntimeCoordinator(applicationContext, MemoryAwareBridge(memory))
        coordinator.start()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PERCEIVE -> {
                val kind = intent.getStringExtra(EXTRA_KIND) ?: "system"
                val text = intent.getStringExtra(EXTRA_TEXT) ?: ""
                coordinator.onPerception(kind, JSONObject().put("text", text))
            }
            ACTION_SNAPSHOT -> coordinator.persist()
        }
        return START_STICKY
    }

    override fun onDestroy() {
        coordinator.persist()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val ACTION_PERCEIVE = "com.noemia.assistente.PERCEIVE"
        const val ACTION_SNAPSHOT = "com.noemia.assistente.SNAPSHOT"
        const val EXTRA_KIND = "kind"
        const val EXTRA_TEXT = "text"
    }
}
