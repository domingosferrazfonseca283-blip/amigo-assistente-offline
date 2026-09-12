package com.noemia.assistente

import org.json.JSONObject

/** Fronteira estável entre o corpo Android e o núcleo cognitivo. */
interface CognitiveBridge {
    fun restore(snapshot: JSONObject?)
    fun perceive(kind: String, payload: JSONObject): JSONObject
    fun converse(text: String): String
    fun internalCycle(activity: String = "reflect"): JSONObject
    fun snapshot(): JSONObject
}
