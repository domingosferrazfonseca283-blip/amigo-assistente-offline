#include <jni.h>

#include <string>

#include "noemia_runtime_core.hpp"

namespace {
noemia::RuntimeCore& runtime() {
    static noemia::RuntimeCore instance;
    return instance;
}
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_noemia_assistente_NativeLocalRuntimeTransport_nativeExecute(
        JNIEnv* env,
        jobject /* self */,
        jstring request_json) {
    if (request_json == nullptr) {
        return env->NewStringUTF("{\"ok\":false,\"payload\":{},\"error\":\"request_json nulo\",\"request_id\":\"\"}");
    }

    const char* chars = env->GetStringUTFChars(request_json, nullptr);
    const std::string request(chars ? chars : "");
    if (chars) {
        env->ReleaseStringUTFChars(request_json, chars);
    }

    const std::string response = runtime().execute(request);
    return env->NewStringUTF(response.c_str());
}
