#include "noemia_runtime_core.hpp"

#include <algorithm>
#include <chrono>
#include <iomanip>
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

double extract_double(const std::string& json, const std::string& key, double fallback) {
    const std::string marker = "\"" + key + "\":";
    const auto start = json.find(marker);
    if (start == std::string::npos) return fallback;
    try { return std::stod(json.substr(start + marker.size())); }
    catch (...) { return fallback; }
}

std::string json_escape(const std::string& value) {
    std::string result;
    result.reserve(value.size() + 8);
    for (char c : value) {
        if (c == '\\' || c == '\"') result.push_back('\\');
        result.push_back(c);
    }
    return result;
}

long long now_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}

double clamp01(double value) {
    return std::max(0.0, std::min(1.0, value));
}
} // namespace

namespace noemia {

RuntimeCore::RuntimeCore() : last_tick_ms_(now_ms()) {}

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
            sequence_ = extract_number(request_json, "sequence", sequence_);
            connection_ = clamp01(extract_double(request_json, "connection", connection_));
            curiosity_ = clamp01(extract_double(request_json, "curiosity", curiosity_));
            novelty_ = clamp01(extract_double(request_json, "novelty", novelty_));
            reflection_ = clamp01(extract_double(request_json, "reflection", reflection_));
            rest_ = clamp01(extract_double(request_json, "rest", rest_));
            last_activity_ = extract_string(request_json, "last_activity");
            affect_state_ = extract_string(request_json, "affect_state");
            phase_ = extract_string(request_json, "phase");
            focus_ = extract_string(request_json, "current_focus");
            last_tick_ms_ = now_ms();
        }

        std::ostringstream out;
        out << std::fixed << std::setprecision(4);
        out << "{\"ok\":true,\"payload\":{";
        out << "\"identity\":\"Noémia\",\"turn_count\":" << turn_count_;
        out << ",\"internal_cycle_count\":" << internal_cycle_count_;
        out << ",\"experience_count\":" << experience_count_;
        out << ",\"being\":{";
        out << "\"sequence\":" << sequence_;
        out << ",\"phase\":\"" << json_escape(phase_) << "\"";
        out << ",\"last_activity\":\"" << json_escape(last_activity_) << "\"";
        out << ",\"affect_state\":\"" << json_escape(affect_state_) << "\"";
        out << ",\"current_focus\":\"" << json_escape(focus_) << "\"";
        out << ",\"needs\":{\"connection\":" << connection_;
        out << ",\"curiosity\":" << curiosity_ << ",\"novelty\":" << novelty_;
        out << ",\"reflection\":" << reflection_ << ",\"rest\":" << rest_ << "}";
        out << "}},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    if (is_think) {
        ++turn_count_;
        ++experience_count_;
        ++sequence_;
        last_input_ = extract_string(request_json, "text");
        last_activity_ = "conversation";
        affect_state_ = "engaged";
        phase_ = "expressing";
        focus_ = "interação com o utilizador";
        connection_ = clamp01(connection_ - 0.04);
        rest_ = clamp01(rest_ - 0.03);
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"text\":\"Estou contigo. Recebi a tua mensagem.\",\"identity\":\"Noémia\",\"affect_state\":\""
            << affect_state_ << "\",\"phase\":\"" << phase_ << "\"},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    if (is_perceive) {
        ++experience_count_;
        ++sequence_;
        last_input_ = extract_string(request_json, "text");
        last_activity_ = "perceiving";
        affect_state_ = "attentive";
        phase_ = "perceiving";
        focus_ = "entrada recebida";
        connection_ = clamp01(connection_ - 0.08);
        curiosity_ = clamp01(curiosity_ - 0.03);
        return "{\"ok\":true,\"payload\":{\"accepted\":true,\"experience_count\":" + std::to_string(experience_count_) + "},\"error\":null,\"request_id\":\"" + json_escape(request_id) + "\"}";
    }

    if (is_internal) {
        ++internal_cycle_count_;
        ++sequence_;

        const long long now = now_ms();
        const double elapsed_minutes = std::max(0.0, static_cast<double>(now - last_tick_ms_) / 60000.0);
        const double pressure = std::min(elapsed_minutes, 60.0);
        connection_ = clamp01(connection_ + 0.004 + 0.0007 * pressure);
        curiosity_ = clamp01(curiosity_ + 0.010 + 0.0010 * pressure);
        novelty_ = clamp01(novelty_ + 0.008 + 0.0008 * pressure);
        reflection_ = clamp01(reflection_ + 0.006 + 0.0006 * pressure);
        rest_ = clamp01(rest_ + 0.002);
        last_tick_ms_ = now;

        double strongest = rest_;
        std::string drive = "repouso";
        phase_ = "resting";
        focus_ = "reduzir atividade e consolidar estado";
        if (reflection_ > strongest) { strongest = reflection_; drive = "reflexão"; phase_ = "reflecting"; focus_ = "rever experiências e consolidar memória"; }
        if (connection_ > strongest) { strongest = connection_; drive = "aproximação"; phase_ = "reflecting"; focus_ = "verificar continuidade da relação"; }
        if (novelty_ > strongest) { strongest = novelty_; drive = "novidade"; phase_ = "reflecting"; focus_ = "procurar uma experiência ou informação nova"; }
        if (curiosity_ > strongest) { strongest = curiosity_; drive = "curiosidade"; phase_ = "reflecting"; focus_ = "explorar algo ainda não compreendido"; }

        last_activity_ = "reflecting";
        affect_state_ = "calm";
        std::ostringstream out;
        out << std::fixed << std::setprecision(4);
        out << "{\"ok\":true,\"payload\":{\"cycle_id\":\"native-" << internal_cycle_count_;
        out << "\",\"completed_phases\":[\"OBSERVE\",\"UPDATE_STATE\",\"FEEL\",\"IDENTIFY_NEEDS\",\"REFLECT\",\"CONSOLIDATE\"]";
        out << ",\"drive\":\"" << drive << "\",\"intensity\":" << strongest;
        out << ",\"focus\":\"" << json_escape(focus_) << "\",\"phase\":\"" << phase_ << "\"";
        out << "},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    return "{\"ok\":false,\"payload\":{},\"error\":\"Comando cognitivo desconhecido\",\"request_id\":\"" + json_escape(request_id) + "\"}";
}

} // namespace noemia
