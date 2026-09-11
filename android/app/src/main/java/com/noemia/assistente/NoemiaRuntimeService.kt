package com.noemia.assistente

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import org.json.JSONObject

/** Corpo Android: hospeda o núcleo cognitivo local e persiste o seu estado. */
class NoemiaRuntimeService : Service() {
    private lateinit var coordinator: RuntimeCoordinator
    private lateinit var internalScheduler: InternalCognitionScheduler
    private lateinit var voiceOutput: NoemiaVoiceOutput

    override fun onCreate() {
        super.onCreate()
        startForegroundRuntime()

        // O caminho oficial é o núcleo compilado no próprio APK: sem sockets,
        // sem HTTP e sem depender de um serviço remoto.
        coordinator = RuntimeCoordinator(applicationContext, RuntimeHost.createBridge())
        coordinator.start()
        internalScheduler = InternalCognitionScheduler {
            coordinator.internalCycle("reflect")
        }
        internalScheduler.start()
        voiceOutput = NoemiaVoiceOutput(applicationContext)
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
            ACTION_SPEAK -> voiceOutput.speak(intent.getStringExtra(EXTRA_SPEECH_TEXT) ?: "")
            ACTION_STOP_SPEAKING -> voiceOutput.stop()
        }
        return START_STICKY
    }

    override fun onDestroy() {
        internalScheduler.stop()
        voiceOutput.shutdown()
        coordinator.persist()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun startForegroundRuntime() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    "Vida interna da Noémia",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Núcleo cognitivo local persistente"
                }
            )
        }

        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Noémia está presente")
            .setContentText("Núcleo cognitivo local ativo")
            .setOngoing(true)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()

        startForeground(NOTIFICATION_ID, notification)
    }

    companion object {
        const val ACTION_PERCEIVE = "com.noemia.assistente.PERCEIVE"
        const val ACTION_INTERNAL_CYCLE = "com.noemia.assistente.INTERNAL_CYCLE"
        const val ACTION_SNAPSHOT = "com.noemia.assistente.SNAPSHOT"
        const val ACTION_SPEAK = "com.noemia.assistente.SPEAK"
        const val ACTION_STOP_SPEAKING = "com.noemia.assistente.STOP_SPEAKING"
        const val EXTRA_KIND = "kind"
        const val EXTRA_TEXT = "text"
        const val EXTRA_ACTIVITY = "activity"
        const val EXTRA_SPEECH_TEXT = "speech_text"
        private const val CHANNEL_ID = "noemia_runtime"
        private const val NOTIFICATION_ID = 1001
    }
}
