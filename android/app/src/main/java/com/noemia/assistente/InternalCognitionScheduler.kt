package com.noemia.assistente

import android.os.Handler
import android.os.Looper

/**
 * Hospedeiro Android da vida interna: agenda ciclos pequenos quando Noémia fica inativa.
 * Não garante execução contínua; o sistema operativo pode suspender o processo.
 */
class InternalCognitionScheduler(
    private val onCycle: () -> Unit,
    private val idleDelayMs: Long = 60_000L,
    private val cooldownMs: Long = 5 * 60_000L
) {
    private val handler = Handler(Looper.getMainLooper())
    private var lastExternalActivity = System.currentTimeMillis()
    private var lastInternalCycle = 0L
    private var running = false

    private val tick = object : Runnable {
        override fun run() {
            if (!running) return
            val now = System.currentTimeMillis()
            val idleEnough = now - lastExternalActivity >= idleDelayMs
            val cooldownEnough = now - lastInternalCycle >= cooldownMs
            if (idleEnough && cooldownEnough) {
                lastInternalCycle = now
                onCycle()
            }
            handler.postDelayed(this, idleDelayMs)
        }
    }

    fun start() {
        if (running) return
        running = true
        lastExternalActivity = System.currentTimeMillis()
        handler.postDelayed(tick, idleDelayMs)
    }

    fun externalActivity() {
        lastExternalActivity = System.currentTimeMillis()
    }

    fun stop() {
        running = false
        handler.removeCallbacks(tick)
    }
}
