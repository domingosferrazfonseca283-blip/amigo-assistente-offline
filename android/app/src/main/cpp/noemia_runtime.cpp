#include <jni.h>

#include <string>

extern "C" JNIEXPORT jstring JNICALL
Java_com_noemia_assistente_NativeLocalRuntimeTransport_nativeExecute(
        JNIEnv* env,
        jobject /* self */,
        jstring /* requestJson */) {
    const std::string response =
            R"({"ok":false,"payload":{},"error":"Motor cognitivo nativo ainda não empacotado","request_id":""})";
    return env->NewStringUTF(response.c_str());
}
