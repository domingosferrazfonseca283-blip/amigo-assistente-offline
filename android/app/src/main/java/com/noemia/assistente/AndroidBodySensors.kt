package com.noemia.assistente

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import org.json.JSONObject

/**
 * Sentidos físicos reais disponíveis através do Android Sensor Framework.
 *
 * Cada sensor é descoberto em tempo de execução; o código não assume um modelo
 * específico de telefone. Quando um sensor não existe, esse sentido simplesmente
 * não é registado.
 */
class AndroidBodySensors(
    context: Context,
    private val onPerception: (kind: String, payload: JSONObject) -> Unit,
) : SensorEventListener {
    private val manager = context.applicationContext
        .getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val sensors = listOf(
        Sensor.TYPE_ACCELEROMETER to "motion.accelerometer",
        Sensor.TYPE_GYROSCOPE to "motion.gyroscope",
        Sensor.TYPE_LIGHT to "light",
        Sensor.TYPE_PROXIMITY to "proximity",
        Sensor.TYPE_AMBIENT_TEMPERATURE to "temperature",
    )
        .mapNotNull { (type, kind) -> manager.getDefaultSensor(type)?.let { it to kind } }

    fun start() {
        sensors.forEach { (sensor, _) ->
            manager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
        }
        onPerception(
            "body.capabilities",
            JSONObject().put("sensors", sensors.map { it.second })
        )
    }

    fun stop() {
        manager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        val kind = sensors.firstOrNull { it.first.type == event.sensor.type }?.second ?: return
        val values = org.json.JSONArray()
        event.values.forEach { values.put(it.toDouble()) }
        onPerception(
            kind,
            JSONObject()
                .put("values", values)
                .put("accuracy", event.accuracy)
                .put("timestamp_ns", event.timestamp),
        )
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit
}
