#include "noemia_runtime_core.hpp"

#include <sstream>
#include <string>

namespace {
std::string extract_string(const std::string& json, const std::string& key) {
    const std::string marker = "\"" + key + "\":";
    const auto start = json.find(marker);
    if (start == std::string::npos) return "";
    auto pos = start + marker.size();
    if (pos >= json.size() || json[pos] != '\"') return "";
    ++pos;
    std::string value;
    bool escaped = false;
    for (; pos < json.size(); ++pos) {
        const char c = json[pos];
        if (escaped) { value.push_back(c); escaped = false; }
        else if (c == '\\') escaped = true;
        else if (c == '\"') break;
        else value.push_back(c);
    }
    return value;
}

long long extract_number(const std::string& json, const std::string& key, long long fallback) {
    const std::string marker = "\"" + key + "\":";
    const auto start = json.find(marker);
    if (start == std::string::npos) return fallback;
    try { return std::stoll(json.substr(start + marker.size())); }
    catch (...) { return fallback; }
}
} // namespace

namespace noemia {

RuntimeCore::RuntimeCore() = default;

std::string RuntimeCore::execute(const std::string& request_json) {
    const bool is_think = request_json.find("\"command\":\"think\"") != std::string::npos;
    const bool is_perceive = request_json.find("\"command\":\"perceive\"") != std::string::npos;
    const bool is_internal = request_json.find("\"command\":\"internal_cycle\"") != std::string::npos;
    const bool is_snapshot = request_json.find("\"command\":\"snapshot\"") != std::string::npos;
    const std::string request_id = extract_string(request_json, "request_id");

    if (is_snapshot) {
        if (request_json.find("\"restore\"") != std::string::npos) {
            turn_count_ = extract_number(request_json, "turn_count", turn_count_);
            internal_cycle_count_ = extract_number(request_json, "internal_cycle_count", internal_cycle_count_);
            experience_count_ = extract_number(request_json, "experience_count", experience_count_);
        }
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"identity\":\"Noémia\",\"turn_count\":" << turn_count_
            << ",\"internal_cycle_count\":" << internal_cycle_count_
            << ",\"experience_count\":" << experience_count_
            << ",\"last_activity\":\"" << last_activity_
            << "\",\"affect_state\":\"" << affect_state_
            << "\"},\"error\":null,\"request_id\":\"" << request_id << "\"}";
        return out.str();
    }

    if (is_think) {
        ++turn_count_;
        ++experience_count_;
        last_input_ = extract_string(request_json, "text");
        last_activity_ = "conversation";
        affect_state_ = "engaged";
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"text\":\"Estou contigo. Recebi a tua mensagem.\",\"identity\":\"Noémia\",\"affect_state\":\""
            << affect_state_ << "\"},\"error\":null,\"request_id\":\"" << request_id << "\"}";
        return out.str();
    }

    if (is_perceive) {
        ++experience_count_;
        last_input_ = extract_string(request_json, "text");
        last_activity_ = "perceiving";
        affect_state_ = "attentive";
        return "{\"ok\":true,\"payload\":{\"accepted\":true,\"experience_count\":" + std::to_string(experience_count_) + "},\"error\":null,\"request_id\":\"" + request_id + "\"}";
    }

    if (is_internal) {
        ++internal_cycle_count_;
        last_activity_ = "reflecting";
        affect_state_ = "calm";
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"cycle_id\":\"native-" << internal_cycle_count_
            << "\",\"completed_phases\":[\"OBSERVE\",\"RECALL\",\"REFLECT\",\"CONSOLIDATE\"],\"focus\":\"atividade interna\"},\"error\":null,\"request_id\":\"" << request_id << "\"}";
        return out.str();
    }

    return "{\"ok\":false,\"payload\":{},\"error\":\"Comando cognitivo desconhecido\",\"request_id\":\"" + request_id + "\"}";
}

} // namespace noemia
