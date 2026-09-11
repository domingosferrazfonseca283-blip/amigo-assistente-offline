#include "noemia_runtime_core.hpp"

#include <sstream>

namespace noemia {

RuntimeCore::RuntimeCore() = default;

std::string RuntimeCore::execute(const std::string& request_json) {
    // Parser JSON completo será substituído pelo protocolo nativo partilhado.
    // Por agora reconhecemos os comandos sem rede e sem modelo remoto.
    const bool is_think = request_json.find("\"command\":\"think\"") != std::string::npos;
    const bool is_perceive = request_json.find("\"command\":\"perceive\"") != std::string::npos;
    const bool is_internal = request_json.find("\"command\":\"internal_cycle\"") != std::string::npos;
    const bool is_snapshot = request_json.find("\"command\":\"snapshot\"") != std::string::npos;

    if (is_think) {
        ++turn_count_;
        last_input_ = request_json;
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"text\":\"O núcleo local recebeu a experiência. A memória e o modelo cognitivo continuam a ser processados no dispositivo.\"},\"error\":null,\"request_id\":\"\"}";
        return out.str();
    }
    if (is_perceive) {
        last_input_ = request_json;
        return "{\"ok\":true,\"payload\":{\"accepted\":true},\"error\":null,\"request_id\":\"\"}";
    }
    if (is_internal) {
        ++internal_cycle_count_;
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"cycle_id\":\"native-" << internal_cycle_count_
            << "\",\"completed_phases\":[\"OBSERVE\",\"RECALL\",\"INTERPRET\"],\"focus\":\"atividade interna\"},\"error\":null,\"request_id\":\"\"}";
        return out.str();
    }
    if (is_snapshot) {
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"turn_count\":" << turn_count_
            << ",\"internal_cycle_count\":" << internal_cycle_count_ << "},\"error\":null,\"request_id\":\"\"}";
        return out.str();
    }

    return "{\"ok\":false,\"payload\":{},\"error\":\"Comando cognitivo desconhecido\",\"request_id\":\"\"}";
}

} // namespace noemia
