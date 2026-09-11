package com.noemia.assistente

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RadialGradient
import android.graphics.Shader
import android.os.Handler
import android.os.Looper
import android.view.View
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/**
 * Janela visual da Noémia.
 *
 * Não guarda estado cognitivo próprio: lê snapshots persistidos,
 * cria um estado visual transitório e interpola a expressão ao longo do tempo.
 */
class NoemiaPresenceView(context: Context) : View(context) {
    private val store = NoemiaStore(context.applicationContext)
    private val handler = Handler(Looper.getMainLooper())
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var targetState = PresenceState()
    private var visualState = PresenceState()
    private var startedAt = System.nanoTime()

    private val refresh = object : Runnable {
        override fun run() {
            readState()
            invalidate()
            handler.postDelayed(this, 100L)
        }
    }

    init {
        setBackgroundColor(0xFF000000.toInt())
        readState()
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        startedAt = System.nanoTime()
        handler.post(refresh)
    }

    override fun onDetachedFromWindow() {
        handler.removeCallbacks(refresh)
        super.onDetachedFromWindow()
    }

    private fun readState() {
        val saved = store.load() ?: return
        targetState = PresenceState.fromRuntime(saved)
    }

    private fun smoothState(): PresenceState {
        val phase = if (visualState.phase == targetState.phase) {
            visualState.phase
        } else {
            targetState.phase
        }
        val factor = 0.14f
        visualState = visualState.copy(
            phase = phase,
            curiosity = lerp(visualState.curiosity, targetState.curiosity, factor),
            connection = lerp(visualState.connection, targetState.connection, factor),
            novelty = lerp(visualState.novelty, targetState.novelty, factor),
            reflection = lerp(visualState.reflection, targetState.reflection, factor),
        )
        return visualState
    }

    private fun lerp(from: Float, to: Float, amount: Float): Float =
        from + (to - from) * amount

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val state = smoothState()
        val cx = width * 0.5f
        val cy = height * 0.54f
        val radius = min(width, height) * 0.235f
        val time = (System.nanoTime() - startedAt) / 1_000_000_000.0
        val breathSpeed = when (state.phase) {
            "perceiving" -> 1.65
            "expressing" -> 1.9
            "reflecting" -> 0.72
            else -> 1.15
        }
        val breathAmount = when (state.phase) {
            "expressing" -> 0.022f
            "perceiving" -> 0.016f
            "reflecting" -> 0.009f
            else -> 0.012f
        }
        val breath = (sin(time * breathSpeed) * breathAmount).toFloat()
        val r = radius * (1f + breath)

        drawAura(canvas, cx, cy, r, state)
        drawHead(canvas, cx, cy, r)
        drawEyes(canvas, cx, cy, r, time, state)
    }

    private fun drawAura(canvas: Canvas, cx: Float, cy: Float, r: Float, state: PresenceState) {
        val activity = when (state.phase) {
            "perceiving" -> 1.0f
            "expressing" -> 0.95f
            "reflecting" -> 0.78f
            else -> 0.58f
        }
        val intensity = (0.35f + state.curiosity * 0.35f + state.novelty * 0.20f + activity * 0.25f)
            .coerceIn(0.25f, 1f)
        paint.shader = RadialGradient(
            cx, cy, r * 1.55f,
            intArrayOf(
                0x001E73FF,
                (0x401E73FF or ((intensity * 255).toInt() shl 24)),
                0x001E73FF
            ),
            floatArrayOf(0.48f, 0.72f, 1f),
            Shader.TileMode.CLAMP
        )
        canvas.drawCircle(cx, cy, r * 1.55f, paint)
        paint.shader = null
    }

    private fun drawHead(canvas: Canvas, cx: Float, cy: Float, r: Float) {
        paint.style = Paint.Style.FILL
        paint.shader = RadialGradient(
            cx - r * 0.28f, cy - r * 0.35f, r * 1.25f,
            intArrayOf(0xFF061A3C.toInt(), 0xFF01050D.toInt(), 0xFF000000.toInt()),
            floatArrayOf(0f, 0.52f, 1f),
            Shader.TileMode.CLAMP
        )
        canvas.drawCircle(cx, cy, r, paint)
        paint.shader = null

        paint.style = Paint.Style.STROKE
        paint.strokeWidth = r * 0.012f
        paint.color = 0xFF287CFF.toInt()
        paint.alpha = 210
        canvas.drawCircle(cx, cy, r, paint)
        paint.alpha = 255
    }

    private fun drawEyes(canvas: Canvas, cx: Float, cy: Float, r: Float, time: Double, state: PresenceState) {
        val eyeY = cy - r * 0.05f
        val eyeSpacing = r * 0.43f
        val eyeR = r * 0.23f
        val blink = blinkAmount(time)
        val gaze = when (state.phase) {
            "perceiving", "expressing" -> 0.025f + state.connection * 0.018f
            "reflecting" -> -0.018f
            else -> 0f
        }
        val gazeVertical = when (state.phase) {
            "reflecting" -> -0.018f
            "perceiving" -> -0.006f
            else -> 0f
        }

        drawEye(canvas, cx - eyeSpacing, eyeY, eyeR, blink, gaze, gazeVertical, time)
        drawEye(canvas, cx + eyeSpacing, eyeY, eyeR, blink, gaze, gazeVertical, time + 0.17)
    }

    private fun drawEye(canvas: Canvas, cx: Float, cy: Float, r: Float, blink: Float, gaze: Float, gazeVertical: Float, time: Double) {
        val height = r * (1f - blink)
        if (height < 2f) return

        paint.style = Paint.Style.FILL
        paint.shader = RadialGradient(
            cx, cy, r * 1.35f,
            intArrayOf(0xFFB9E8FF.toInt(), 0xFF1674FF.toInt(), 0xFF00133D.toInt()),
            floatArrayOf(0.18f, 0.48f, 1f),
            Shader.TileMode.CLAMP
        )
        canvas.save()
        canvas.scale(1f, height / r, cx, cy)
        canvas.drawCircle(cx, cy, r, paint)
        paint.shader = null

        val pupilX = cx + gaze * r + (sin(time * 0.8) * r * 0.025).toFloat()
        val pupilY = cy + gazeVertical * r + (cos(time * 0.65) * r * 0.012).toFloat()
        paint.color = 0xFF00030A.toInt()
        canvas.drawCircle(pupilX, pupilY, r * 0.55f, paint)
        paint.color = 0xFFFFFFFF.toInt()
        canvas.drawCircle(pupilX - r * 0.20f, pupilY - r * 0.22f, r * 0.12f, paint)
        canvas.restore()

        paint.style = Paint.Style.STROKE
        paint.strokeWidth = r * 0.035f
        paint.color = 0xFF2585FF.toInt()
        canvas.drawOval(cx - r, cy - height, cx + r, cy + height, paint)
    }

    private fun blinkAmount(time: Double): Float {
        val cycle = time % 4.7
        return when {
            cycle in 3.72..3.79 -> 0.35f
            cycle in 3.79..3.86 -> 0.90f
            cycle in 3.86..3.94 -> 0.35f
            else -> 0f
        }
    }
}
