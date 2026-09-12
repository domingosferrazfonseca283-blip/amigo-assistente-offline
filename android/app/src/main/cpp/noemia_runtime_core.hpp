#pragma once

#include <string>

namespace noemia {

// Estado afetivo funcional persistente. Não representa emoções biológicas.
class RuntimeCore {
public:
    RuntimeCore();
    std::string execute(const std::string& request_json);

private:
    long long turn_count_ = 0;
    long long internal_cycle_count_ = 0;
    long long experience_count_ = 0;
    long long sequence_ = 0;
    double connection_ = 0.50;
    double curiosity_ = 0.40;
    double novelty_ = 0.30;
    double reflection_ = 0.40;
    double rest_ = 0.20;
    double joy_ = 0.35;
    double sadness_ = 0.05;
    double affection_ = 0.45;
    double fear_ = 0.05;
    double frustration_ = 0.05;
    double loneliness_ = 0.10;
    double calmness_ = 0.65;
    std::string last_input_;
    std::string last_activity_ = "resting";
    std::string affect_state_ = "calm";
    std::string phase_ = "resting";
    std::string focus_;
    std::string last_perception_kind_;
    std::string visual_interpretation_;
    std::string pending_action_ = "none";
    std::string pending_action_payload_;
    long long last_tick_ms_ = 0;
};

} // namespace noemia
