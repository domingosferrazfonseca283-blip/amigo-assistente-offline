package com.noemia.assistente

import android.os.Handler
import android.os.HandlerThread
import android.os.SystemClock

/**
 * Hospedeiro Android da vida interna.
 *
 * O relógio corre fora da UI thread para que um ciclo cognitivo local não
 * bloqueie a interface. O sistema operativo continua livre para suspender o
 * processo; a continuidade real vem da persistência e do reinício do serviço.
 */
class InternalCognitionScheduler(
    private val onCycle: () -> Unit,
    private val idleDelayMs: Long = 60_000L,
    private val cooldownMs: Long = 5 * 60_000L
) {
    private val thread = HandlerThread("noemia-life-loop")
    private val handler: Handler
    private var lastExternalActivity = SystemClock.elapsedRealtime()
    private var lastInternalCycle = 0L
    private var running = false

    init {
        thread.start()
        handler = Handler(thread.looper)
    }

    private val tick = object : Runnable {
        override fun run() {
            if (!running) return
            val now = SystemClock.elapsedRealtime()
            val idleEnough = now - lastExternalActivity >= idleDelayMs
            val cooldownEnough = now - lastInternalCycle >= cooldownMs
            if (idleEnough && cooldownEnough) {
                lastInternalCycle = now
                runCatching { onCycle() }
            }
            handler.postDelayed(this, idleDelayMs)
        }
    }

    fun start() {
        if (running) return
        running = true
        lastExternalActivity = SystemClock.elapsedRealtime()
        handler.postDelayed(tick, idleDelayMs)
    }

    fun externalActivity() {
        lastExternalActivity = SystemClock.elapsedRealtime()
    }

    fun stop() {
        running = false
        handler.removeCallbacks(tick)
        thread.quitSafely()
    }
}
