package com.noemia.assistente

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import org.json.JSONObject
import java.io.File
import kotlin.math.abs

/**
 * Percepção visual local sem rede.
 *
 * Esta camada não inventa objetos nem usa um classificador inexistente: extrai
 * características observáveis diretamente do frame (luminância, cor média,
 * contraste e variação entre pixels) e entrega-as ao núcleo cognitivo.
 */
class NoemiaVisionAnalyzer(
    private val onPerception: (String, JSONObject) -> Unit,
) {
    fun analyze(jpegFile: File) {
        if (!jpegFile.exists()) return

        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(jpegFile.absolutePath, bounds)
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return

        val options = BitmapFactory.Options().apply {
            inPreferredConfig = Bitmap.Config.ARGB_8888
            inSampleSize = sampleSize(bounds.outWidth, bounds.outHeight)
        }
        val bitmap = BitmapFactory.decodeFile(jpegFile.absolutePath, options) ?: return
        try {
            val features = extractFeatures(bitmap)
            onPerception(
                "vision.analysis",
                JSONObject()
                    .put("path", jpegFile.absolutePath)
                    .put("width", bounds.outWidth)
                    .put("height", bounds.outHeight)
                    .put("format", "jpeg")
                    .put("sample_width", bitmap.width)
                    .put("sample_height", bitmap.height)
                    .put("mean_luminance", features.meanLuminance)
                    .put("contrast", features.contrast)
                    .put("mean_red", features.meanRed)
                    .put("mean_green", features.meanGreen)
                    .put("mean_blue", features.meanBlue)
                    .put("edge_change", features.edgeChange)
                    .put("scene_brightness", brightnessLabel(features.meanLuminance)),
            )
        } finally {
            bitmap.recycle()
        }
    }

    private fun sampleSize(width: Int, height: Int): Int {
        val largest = maxOf(width, height)
        return when {
            largest > 2048 -> 8
            largest > 1024 -> 4
            largest > 512 -> 2
            else -> 1
        }
    }

    private fun extractFeatures(bitmap: Bitmap): Features {
        val step = maxOf(1, minOf(bitmap.width, bitmap.height) / 96)
        var count = 0L
        var luminanceSum = 0.0
        var luminanceSquared = 0.0
        var redSum = 0.0
        var greenSum = 0.0
        var blueSum = 0.0
        var edgeSum = 0.0
        var previous = -1.0

        var y = 0
        while (y < bitmap.height) {
            var x = 0
            while (x < bitmap.width) {
                val pixel = bitmap.getPixel(x, y)
                val red = (pixel shr 16 and 0xff).toDouble() / 255.0
                val green = (pixel shr 8 and 0xff).toDouble() / 255.0
                val blue = (pixel and 0xff).toDouble() / 255.0
                val luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue

                luminanceSum += luminance
                luminanceSquared += luminance * luminance
                redSum += red
                greenSum += green
                blueSum += blue
                if (previous >= 0.0) edgeSum += abs(luminance - previous)
                previous = luminance
                count++
                x += step
            }
            y += step
        }

        val n = count.coerceAtLeast(1L).toDouble()
        val mean = luminanceSum / n
        val variance = (luminanceSquared / n - mean * mean).coerceAtLeast(0.0)
        return Features(
            meanLuminance = mean,
            contrast = kotlin.math.sqrt(variance),
            meanRed = redSum / n,
            meanGreen = greenSum / n,
            meanBlue = blueSum / n,
            edgeChange = edgeSum / n,
        )
    }

    private fun brightnessLabel(value: Double): String = when {
        value < 0.18 -> "dark"
        value < 0.42 -> "dim"
        value < 0.72 -> "balanced"
        else -> "bright"
    }

    private data class Features(
        val meanLuminance: Double,
        val contrast: Double,
        val meanRed: Double,
        val meanGreen: Double,
        val meanBlue: Double,
        val edgeChange: Double,
    )
}
