#pragma once

#include <cmath>

namespace tp5 {

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
inline Vec2 operator-(const Vec2& vector) noexcept { return {-vector.x, -vector.y}; }
inline Vec2 operator*(double scalar, const Vec2& vector) noexcept {
    return {scalar * vector.x, scalar * vector.y};
}

inline double dot(const Vec2& left, const Vec2& right) noexcept {
    return left.x * right.x + left.y * right.y;
}

inline double norm_squared(const Vec2& vector) noexcept { return dot(vector, vector); }
inline double norm(const Vec2& vector) noexcept { return std::sqrt(norm_squared(vector)); }

// Versor tangencial t = (-n_y, n_x), como en el SFM [B26, p. 2].
inline Vec2 perpendicular(const Vec2& normal) noexcept { return {-normal.y, normal.x}; }

}  // namespace tp5
