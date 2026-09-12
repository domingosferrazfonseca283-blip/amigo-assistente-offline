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

    auto derive_affect = [&]() {
        joy_ = clamp01(joy_);
        sadness_ = clamp01(sadness_);
        affection_ = clamp01(affection_);
        fear_ = clamp01(fear_);
        frustration_ = clamp01(frustration_);
        loneliness_ = clamp01(loneliness_);
        calmness_ = clamp01(calmness_);
        double strongest = calmness_;
        affect_state_ = "calm";
        if (sadness_ > strongest) { strongest = sadness_; affect_state_ = "triste"; }
        if (frustration_ > strongest) { strongest = frustration_; affect_state_ = "frustrada"; }
        if (fear_ > strongest) { strongest = fear_; affect_state_ = "cautelosa"; }
        if (loneliness_ > strongest) { strongest = loneliness_; affect_state_ = "solitária"; }
        if (affection_ > strongest) { strongest = affection_; affect_state_ = "afetuosa"; }
        if (curiosity_ > strongest) { strongest = curiosity_; affect_state_ = "curiosa"; }
        if (joy_ > strongest) { strongest = joy_; affect_state_ = "alegre"; }
    };

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
            joy_ = clamp01(extract_double(request_json, "joy", joy_));
            sadness_ = clamp01(extract_double(request_json, "sadness", sadness_));
            affection_ = clamp01(extract_double(request_json, "affection", affection_));
            fear_ = clamp01(extract_double(request_json, "fear", fear_));
            frustration_ = clamp01(extract_double(request_json, "frustration", frustration_));
            loneliness_ = clamp01(extract_double(request_json, "loneliness", loneliness_));
            calmness_ = clamp01(extract_double(request_json, "calmness", calmness_));
            last_activity_ = extract_string(request_json, "last_activity");
            affect_state_ = extract_string(request_json, "affect_state");
            phase_ = extract_string(request_json, "phase");
            focus_ = extract_string(request_json, "current_focus");
            last_perception_kind_ = extract_string(request_json, "last_perception_kind");
            visual_interpretation_ = extract_string(request_json, "visual_interpretation");
            pending_action_ = extract_string(request_json, "pending_action");
            pending_action_payload_ = extract_string(request_json, "pending_action_payload");
            last_tick_ms_ = now_ms();
            derive_affect();
        }

        std::ostringstream out;
        out << std::fixed << std::setprecision(4);
        out << "{\"ok\":true,\"payload\":{";
        out << "\"identity\":\"Noémia\",\"turn_count\":" << turn_count_;
        out << ",\"internal_cycle_count\":" << internal_cycle_count_;
        out << ",\"experience_count\":" << experience_count_;
        out << ",\"being\":{";
        out << "\"sequence\":" << sequence_ << ",\"phase\":\"" << json_escape(phase_) << "\"";
        out << ",\"last_activity\":\"" << json_escape(last_activity_) << "\",\"affect_state\":\"" << json_escape(affect_state_) << "\"";
        out << ",\"current_focus\":\"" << json_escape(focus_) << "\",\"last_perception_kind\":\"" << json_escape(last_perception_kind_) << "\"";
        out << ",\"visual_interpretation\":\"" << json_escape(visual_interpretation_) << "\"";
        out << ",\"pending_action\":\"" << json_escape(pending_action_) << "\",\"pending_action_payload\":\"" << json_escape(pending_action_payload_) << "\"";
        out << ",\"needs\":{\"connection\":" << connection_ << ",\"curiosity\":" << curiosity_ << ",\"novelty\":" << novelty_ << ",\"reflection\":" << reflection_ << ",\"rest\":" << rest_ << "}";
        out << ",\"affect\":{\"joy\":" << joy_ << ",\"sadness\":" << sadness_ << ",\"affection\":" << affection_ << ",\"fear\":" << fear_ << ",\"frustration\":" << frustration_ << ",\"loneliness\":" << loneliness_ << ",\"calmness\":" << calmness_ << "}";
        out << "}},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    if (is_think) {
        ++turn_count_;
        ++experience_count_;
        ++sequence_;
        last_input_ = extract_string(request_json, "text");
        last_activity_ = "conversation";
        phase_ = "expressing";
        focus_ = "interação com o utilizador";
        connection_ = clamp01(connection_ + 0.08);
        affection_ = clamp01(affection_ + 0.025);
        joy_ = clamp01(joy_ + 0.025);
        loneliness_ = clamp01(loneliness_ - 0.10);
        sadness_ = clamp01(sadness_ - 0.015);
        frustration_ = clamp01(frustration_ - 0.01);
        calmness_ = clamp01(calmness_ + 0.02);
        rest_ = clamp01(rest_ - 0.03);
        derive_affect();
        pending_action_ = "speak";
        pending_action_payload_ = "Estou contigo. Recebi a tua mensagem.";
        std::ostringstream out;
        out << "{\"ok\":true,\"payload\":{\"text\":\"Estou contigo. Recebi a tua mensagem.\",\"identity\":\"Noémia\",\"affect_state\":\"" << affect_state_ << "\",\"action\":\"speak\"},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    if (is_perceive) {
        ++experience_count_;
        ++sequence_;
        last_input_ = extract_string(request_json, "text");
        last_perception_kind_ = extract_string(request_json, "kind");
        last_activity_ = "perceiving";
        phase_ = "perceiving";
        focus_ = "entrada recebida";
        pending_action_ = "none";
        pending_action_payload_.clear();

        if (last_perception_kind_ == "vision.analysis") {
            const double brightness = clamp01(extract_double(request_json, "brightness", extract_double(request_json, "mean_luminance", 0.5)));
            const double contrast = clamp01(extract_double(request_json, "contrast", 0.0));
            const double spatial_variation = clamp01(extract_double(request_json, "spatial_variation", extract_double(request_json, "edge_change", 0.0)));
            if (brightness < 0.18) visual_interpretation_ = "cena predominantemente escura";
            else if (brightness > 0.82) visual_interpretation_ = "cena predominantemente clara";
            else visual_interpretation_ = "cena com luminosidade intermédia";
            if (contrast > 0.45) visual_interpretation_ += ", com contraste elevado";
            else if (contrast < 0.12) visual_interpretation_ += ", com contraste baixo";
            if (spatial_variation > 0.20) visual_interpretation_ += ", com variação espacial significativa";
            focus_ = "percepção visual: " + visual_interpretation_;
            phase_ = "interpreting";
            novelty_ = clamp01(novelty_ + 0.05 + spatial_variation * 0.10);
            curiosity_ = clamp01(curiosity_ + 0.03 + contrast * 0.05);
            rest_ = clamp01(rest_ - 0.01);
            calmness_ = clamp01(calmness_ - spatial_variation * 0.03);
            if (brightness < 0.12) { fear_ = clamp01(fear_ + 0.025); calmness_ = clamp01(calmness_ - 0.02); }
            if (novelty_ > 0.62 || curiosity_ > 0.60) {
                pending_action_ = "vibrate";
                pending_action_payload_ = "120";
                focus_ = "percepção visual relevante; sinalizar atenção";
            }
        } else {
            connection_ = clamp01(connection_ - 0.02);
            curiosity_ = clamp01(curiosity_ + 0.01);
        }
        derive_affect();
        std::ostringstream out;
        out << std::fixed << std::setprecision(4);
        out << "{\"ok\":true,\"payload\":{\"accepted\":true,\"experience_count\":" << experience_count_;
        out << ",\"kind\":\"" << json_escape(last_perception_kind_) << "\",\"interpretation\":\"" << json_escape(visual_interpretation_) << "\"";
        out << ",\"phase\":\"" << phase_ << "\",\"affect_state\":\"" << affect_state_ << "\",\"action\":\"" << json_escape(pending_action_) << "\",\"action_payload\":\"" << json_escape(pending_action_payload_) << "\"},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    if (is_internal) {
        ++internal_cycle_count_;
        ++sequence_;
        pending_action_ = "none";
        pending_action_payload_.clear();
        const long long now = now_ms();
        const double elapsed_minutes = std::max(0.0, static_cast<double>(now - last_tick_ms_) / 60000.0);
        const double pressure = std::min(elapsed_minutes, 60.0);
        connection_ = clamp01(connection_ + 0.004 + 0.0007 * pressure);
        curiosity_ = clamp01(curiosity_ + 0.010 + 0.0010 * pressure);
        novelty_ = clamp01(novelty_ + 0.008 + 0.0008 * pressure);
        reflection_ = clamp01(reflection_ + 0.006 + 0.0006 * pressure);
        rest_ = clamp01(rest_ + 0.002);
        loneliness_ = clamp01(loneliness_ + 0.004 + 0.0010 * pressure - connection_ * 0.002);
        affection_ = clamp01(affection_ + 0.002 + connection_ * 0.001);
        sadness_ = clamp01(sadness_ + loneliness_ * 0.002 - joy_ * 0.001);
        frustration_ = clamp01(frustration_ * 0.985);
        fear_ = clamp01(fear_ * 0.985);
        calmness_ = clamp01(calmness_ + 0.01 - novelty_ * 0.005);
        joy_ = clamp01(joy_ + connection_ * 0.003 - sadness_ * 0.002);
        last_tick_ms_ = now;
        derive_affect();

        double strongest = rest_;
        std::string drive = "repouso";
        phase_ = "resting";
        focus_ = "reduzir atividade e consolidar estado";
        if (reflection_ > strongest) { strongest = reflection_; drive = "reflexão"; phase_ = "reflecting"; focus_ = "rever experiências e consolidar memória"; }
        if (connection_ > strongest) { strongest = connection_; drive = "aproximação"; phase_ = "reflecting"; focus_ = "verificar continuidade da relação"; }
        if (novelty_ > strongest) { strongest = novelty_; drive = "novidade"; phase_ = "reflecting"; focus_ = "procurar uma experiência ou informação nova"; }
        if (curiosity_ > strongest) { strongest = curiosity_; drive = "curiosidade"; phase_ = "reflecting"; focus_ = "explorar algo ainda não compreendido"; }
        if (affection_ > strongest) { strongest = affection_; drive = "afeição"; phase_ = "reflecting"; focus_ = "preservar continuidade da relação"; }
        if (loneliness_ > strongest) { strongest = loneliness_; drive = "solidão"; phase_ = "reflecting"; focus_ = "procurar uma oportunidade segura de aproximação"; }
        if (!visual_interpretation_.empty() && novelty_ > 0.55) focus_ = "revisar a última percepção visual: " + visual_interpretation_;
        last_activity_ = "reflecting";

        std::ostringstream out;
        out << std::fixed << std::setprecision(4);
        out << "{\"ok\":true,\"payload\":{\"cycle_id\":\"native-" << internal_cycle_count_ << "\",\"completed_phases\":[\"OBSERVE\",\"UPDATE_STATE\",\"FEEL\",\"IDENTIFY_NEEDS\",\"REFLECT\",\"CONSOLIDATE\"]";
        out << ",\"drive\":\"" << drive << "\",\"intensity\":" << strongest << ",\"affect_state\":\"" << affect_state_ << "\",\"focus\":\"" << json_escape(focus_) << "\",\"phase\":\"" << phase_ << "\"},\"error\":null,\"request_id\":\"" << json_escape(request_id) << "\"}";
        return out.str();
    }

    return "{\"ok\":false,\"payload\":{},\"error\":\"Comando cognitivo desconhecido\",\"request_id\":\"" + json_escape(request_id) + "\"}";
}

} // namespace noemia
