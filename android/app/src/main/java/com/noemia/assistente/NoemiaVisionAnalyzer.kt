package com.noemia.assistente

import android.graphics.BitmapFactory
import org.json.JSONObject
import java.io.File

/** Preparação real do frame para o motor de visão, sem inventar interpretação. */
class NoemiaVisionAnalyzer(
    private val onPerception: (String, JSONObject) -> Unit,
) {
    fun analyze(jpegFile: File) {
        if (!jpegFile.exists()) return
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(jpegFile.absolutePath, bounds)
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return

        onPerception(
            "vision.frame",
            JSONObject()
                .put("path", jpegFile.absolutePath)
                .put("width", bounds.outWidth)
                .put("height", bounds.outHeight)
                .put("format", "jpeg"),
        )
    }
}
