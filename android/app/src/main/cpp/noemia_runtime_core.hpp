#pragma once

#include <string>

namespace noemia {

// Estado mínimo persistente do ser digital. Não representa consciência humana.
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
    std::string last_input_;
    std::string last_activity_ = "resting";
    std::string affect_state_ = "calm";
    std::string phase_ = "resting";
    std::string focus_;
    long long last_tick_ms_ = 0;
};

} // namespace noemia
