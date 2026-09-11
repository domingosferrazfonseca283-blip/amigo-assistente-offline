#pragma once

#include <string>

namespace noemia {

// Núcleo mínimo de execução nativa: mantém estado de sessão sem rede.
class RuntimeCore {
public:
    RuntimeCore();
    std::string execute(const std::string& request_json);

private:
    long long turn_count_ = 0;
    long long internal_cycle_count_ = 0;
    std::string last_input_;
};

} // namespace noemia
