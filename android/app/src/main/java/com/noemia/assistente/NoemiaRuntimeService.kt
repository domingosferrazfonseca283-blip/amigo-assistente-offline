package com.noemia.assistente

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.Vibrator
import androidx.core.app.NotificationCompat
import org.json.JSONObject

/** Corpo Android: hospeda o núcleo cognitivo local e liga sensores reais ao runtime. */
class NoemiaRuntimeService : Service() {
    private lateinit var coordinator: RuntimeCoordinator
    private lateinit var internalScheduler: InternalCognitionScheduler
    private lateinit var voiceOutput: NoemiaVoiceOutput
    private lateinit var bodySensors: AndroidBodySensors

    override fun onCreate() {
        super.onCreate()
        startForegroundRuntime()

        // Núcleo local: identidade/estado/memória permanecem no runtime persistente.
        coordinator = RuntimeCoordinator(applicationContext, RuntimeHost.createBridge())
        coordinator.start()

        voiceOutput = NoemiaVoiceOutput(applicationContext)
        bodySensors = AndroidBodySensors(applicationContext) { kind, payload ->
            internalScheduler.externalActivity()
            coordinator.onPerception(kind, payload)
        }
        bodySensors.start()

        internalScheduler = InternalCognitionScheduler(
            onCycle = { coordinator.internalCycle("observe") },
        )
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
            ACTION_SPEAK -> voiceOutput.speak(intent.getStringExtra(EXTRA_SPEECH_TEXT) ?: "")
            ACTION_STOP_SPEAKING -> voiceOutput.stop()
            ACTION_VIBRATE -> vibrate(intent.getLongExtra(EXTRA_DURATION_MS, 120L))
        }
        return START_STICKY
    }

    override fun onDestroy() {
        bodySensors.stop()
        internalScheduler.stop()
        voiceOutput.shutdown()
        coordinator.persist()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun vibrate(durationMs: Long) {
        val duration = durationMs.coerceIn(1L, 2_000L)
        val vibrator = getSystemService(Vibrator::class.java) ?: return
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(android.os.VibrationEffect.createOneShot(duration, 80))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(duration)
        }
    }

    private fun startForegroundRuntime() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    "Vida interna da Noémia",
                    NotificationManager.IMPORTANCE_LOW,
                ).apply {
                    description = "Núcleo cognitivo local persistente"
                },
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
        const val ACTION_VIBRATE = "com.noemia.assistente.VIBRATE"
        const val EXTRA_KIND = "kind"
        const val EXTRA_TEXT = "text"
        const val EXTRA_ACTIVITY = "activity"
        const val EXTRA_SPEECH_TEXT = "speech_text"
        const val EXTRA_DURATION_MS = "duration_ms"
        private const val CHANNEL_ID = "noemia_runtime"
        private const val NOTIFICATION_ID = 1001
    }
}
