#pragma once

#include <cmath>

namespace tp4 {

struct Vec2 {
    double x{};
    double y{};

    Vec2& operator+=(const Vec2& other) noexcept {
        x += other.x;
        y += other.y;
        return *this;
    }

    Vec2& operator-=(const Vec2& other) noexcept {
        x -= other.x;
        y -= other.y;
        return *this;
    }

    bool operator==(const Vec2&) const = default;
};

inline Vec2 operator+(Vec2 left, const Vec2& right) noexcept { return left += right; }
inline Vec2 operator-(Vec2 left, const Vec2& right) noexcept { return left -= right; }
inline Vec2 operator*(double scalar, const Vec2& vector) noexcept {
    return {scalar * vector.x, scalar * vector.y};
}

inline double dot(const Vec2& left, const Vec2& right) noexcept {
    return left.x * right.x + left.y * right.y;
}

inline double norm_squared(const Vec2& vector) noexcept { return dot(vector, vector); }
inline double norm(const Vec2& vector) noexcept { return std::sqrt(norm_squared(vector)); }

}  // namespace tp4
