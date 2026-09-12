package com.noemia.assistente

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.ImageFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import androidx.core.content.ContextCompat
import org.json.JSONObject
import java.io.File

/** Câmara física real: captura frames e entrega-os à percepção visual local. */
class AndroidCamera(
    context: Context,
    private val onPerception: (String, JSONObject) -> Unit,
) {
    private val appContext = context.applicationContext
    private val manager = appContext.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private var camera: CameraDevice? = null
    private var session: CameraCaptureSession? = null
    private var reader: ImageReader? = null
    private var thread: HandlerThread? = null
    private var handler: Handler? = null

    fun start() {
        if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            onPerception("body.capability_unavailable", JSONObject().put("capability", "vision").put("reason", "permission_denied"))
            return
        }
        val cameraId = manager.cameraIdList.firstOrNull { id ->
            manager.getCameraCharacteristics(id).get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_BACK
        } ?: manager.cameraIdList.firstOrNull()
        if (cameraId == null) {
            onPerception("body.capability_unavailable", JSONObject().put("capability", "vision").put("reason", "no_camera"))
            return
        }
        thread = HandlerThread("noemia-camera").also { it.start() }
        handler = Handler(thread!!.looper)
        val sizes = manager.getCameraCharacteristics(cameraId)
            .get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
            ?.getOutputSizes(ImageFormat.JPEG)
        val size = sizes?.minByOrNull { it.width * it.height } ?: android.util.Size(640, 480)
        reader = ImageReader.newInstance(size.width, size.height, ImageFormat.JPEG, 2).also { imageReader ->
            imageReader.setOnImageAvailableListener({ source ->
                source.acquireLatestImage()?.use { image ->
                    val bytes = ByteArray(image.planes[0].buffer.remaining())
                    image.planes[0].buffer.get(bytes)
                    val file = File(appContext.cacheDir, "noemia-eye-${System.nanoTime()}.jpg")
                    file.writeBytes(bytes)
                    onPerception(
                        "vision.frame",
                        JSONObject()
                            .put("path", file.absolutePath)
                            .put("width", image.width)
                            .put("height", image.height),
                    )
                    analyzeFrame(file)
                }
            }, handler)
        }
        manager.openCamera(cameraId, object : CameraDevice.StateCallback() {
            override fun onOpened(device: CameraDevice) {
                camera = device
                val surface = reader!!.surface
                device.createCaptureSession(listOf(surface), object : CameraCaptureSession.StateCallback() {
                    override fun onConfigured(value: CameraCaptureSession) {
                        session = value
                        val request = device.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW).apply {
                            addTarget(surface)
                        }.build()
                        value.setRepeatingRequest(request, null, handler)
                        onPerception("body.capability", JSONObject().put("sense", "vision").put("camera", cameraId))
                    }
                    override fun onConfigureFailed(value: CameraCaptureSession) {
                        onPerception("body.capability_unavailable", JSONObject().put("capability", "vision").put("reason", "session_failed"))
                    }
                }, handler)
            }
            override fun onDisconnected(device: CameraDevice) { device.close(); camera = null }
            override fun onError(device: CameraDevice, error: Int) { device.close(); camera = null }
        }, handler)
    }

    private fun analyzeFrame(file: File) {
        val bounds = android.graphics.BitmapFactory.Options().apply { inJustDecodeBounds = true }
        android.graphics.BitmapFactory.decodeFile(file.absolutePath, bounds)
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return

        val options = android.graphics.BitmapFactory.Options().apply {
            inPreferredConfig = android.graphics.Bitmap.Config.ARGB_8888
            inSampleSize = when {
                maxOf(bounds.outWidth, bounds.outHeight) > 2048 -> 8
                maxOf(bounds.outWidth, bounds.outHeight) > 1024 -> 4
                maxOf(bounds.outWidth, bounds.outHeight) > 512 -> 2
                else -> 1
            }
        }
        val bitmap = android.graphics.BitmapFactory.decodeFile(file.absolutePath, options) ?: return
        try {
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
                    if (previous >= 0.0) edgeSum += kotlin.math.abs(luminance - previous)
                    previous = luminance
                    count++
                    x += step
                }
                y += step
            }
            val n = count.coerceAtLeast(1L).toDouble()
            val mean = luminanceSum / n
            val contrast = kotlin.math.sqrt((luminanceSquared / n - mean * mean).coerceAtLeast(0.0))
            onPerception(
                "vision.analysis",
                JSONObject()
                    .put("path", file.absolutePath)
                    .put("width", bounds.outWidth)
                    .put("height", bounds.outHeight)
                    .put("sample_width", bitmap.width)
                    .put("sample_height", bitmap.height)
                    .put("mean_luminance", mean)
                    .put("contrast", contrast)
                    .put("mean_red", redSum / n)
                    .put("mean_green", greenSum / n)
                    .put("mean_blue", blueSum / n)
                    .put("edge_change", edgeSum / n)
                    .put("scene_brightness", when {
                        mean < 0.18 -> "dark"
                        mean < 0.42 -> "dim"
                        mean < 0.72 -> "balanced"
                        else -> "bright"
                    }),
            )
        } finally {
            bitmap.recycle()
        }
    }

    fun stop() {
        session?.close(); session = null
        camera?.close(); camera = null
        reader?.close(); reader = null
        thread?.quitSafely(); thread = null; handler = null
    }
}
