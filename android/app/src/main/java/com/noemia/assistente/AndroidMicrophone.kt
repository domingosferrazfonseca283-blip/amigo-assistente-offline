package com.noemia.assistente

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.core.content.ContextCompat
import org.json.JSONObject
import kotlin.concurrent.thread
import kotlin.math.sqrt

/** Microfone físico real. Emite atividade acústica sem fingir que áudio já foi compreendido. */
class AndroidMicrophone(
    context: Context,
    private val onPerception: (String, JSONObject) -> Unit,
) {
    private val appContext = context.applicationContext
    private val sampleRate = 16_000
    private val channel = AudioFormat.CHANNEL_IN_MONO
    private val encoding = AudioFormat.ENCODING_PCM_16BIT
    private var recorder: AudioRecord? = null
    @Volatile private var running = false

    fun start() {
        if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            onPerception("body.capability_unavailable", JSONObject().put("capability", "hearing").put("reason", "permission_denied"))
            return
        }
        if (running) return
        val minimum = AudioRecord.getMinBufferSize(sampleRate, channel, encoding)
        if (minimum <= 0) {
            onPerception("body.capability_unavailable", JSONObject().put("capability", "hearing").put("reason", "unsupported"))
            return
        }
        val bufferSize = (minimum * 2).coerceAtLeast(2048)
        val local = AudioRecord(MediaRecorder.AudioSource.MIC, sampleRate, channel, encoding, bufferSize)
        recorder = local
        local.startRecording()
        running = true
        onPerception("body.capability", JSONObject().put("sense", "hearing").put("sample_rate", sampleRate))
        thread(name = "noemia-microphone") {
            val buffer = ShortArray(bufferSize / 2)
            while (running) {
                val count = local.read(buffer, 0, buffer.size)
                if (count <= 0) continue
                var sum = 0.0
                for (i in 0 until count) {
                    val value = buffer[i].toDouble() / Short.MAX_VALUE
                    sum += value * value
                }
                val rms = sqrt(sum / count)
                onPerception("hearing.audio_level", JSONObject().put("rms", rms).put("samples", count))
            }
        }
    }

    fun stop() {
        running = false
        recorder?.let {
            try { it.stop() } catch (_: IllegalStateException) { }
            it.release()
        }
        recorder = null
    }
}
