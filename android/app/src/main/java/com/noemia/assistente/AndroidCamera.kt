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

/** Câmara física real: captura frames e entrega o caminho local ao núcleo. */
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
                    val file = java.io.File(appContext.cacheDir, "noemia-eye-${System.nanoTime()}.jpg")
                    file.writeBytes(bytes)
                    onPerception("vision.frame", JSONObject()
                        .put("path", file.absolutePath)
                        .put("width", image.width)
                        .put("height", image.height))
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

    fun stop() {
        session?.close(); session = null
        camera?.close(); camera = null
        reader?.close(); reader = null
        thread?.quitSafely(); thread = null; handler = null
    }
}
