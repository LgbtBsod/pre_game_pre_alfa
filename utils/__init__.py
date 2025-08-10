"""Утилиты для игры."""

from .game_utils import (
    calculate_distance,
    normalize_vector,
    clamp_value,
    interpolate_values,
    random_point_in_circle,
    rgb_to_hex,
    format_time,
    format_number,
    is_point_in_rect,
    get_angle_between_points,
    rotate_point_around_center,
)

from .entity_id_generator import (
    EntityType,
    EntityID,
    EntityIDGenerator,
    LegacyIDConverter,
    generate_entity_id,
    generate_short_entity_id,
    convert_legacy_id,
    get_entity_id_stats,
    id_generator,
    legacy_converter,
)
