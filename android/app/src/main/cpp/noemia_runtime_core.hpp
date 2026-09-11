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
    std::string last_input_;
    std::string last_activity_ = "resting";
    std::string affect_state_ = "calm";
};

} // namespace noemia
