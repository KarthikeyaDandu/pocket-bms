#include "soc.h"

float soc_update(float previous_soc, float current, float dt, float capacity)
{
    float new_soc = previous_soc - (current * dt / capacity);

    if (new_soc > 1.0f)
        new_soc = 1.0f;

    if (new_soc < 0.0f)
        new_soc = 0.0f;

    return new_soc;
}