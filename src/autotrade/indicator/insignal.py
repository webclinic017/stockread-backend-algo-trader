from typing import List

import numpy as np
from pandas.core.series import Series


class IndicatorSignal:
    def __init__(self, series_data: Series):
        self._line_series = series_data

    def cross_down(self, another_series: Series):
        current_gaps = self._line_series - another_series
        previous_gaps = current_gaps.shift(1)
        conditions = [(previous_gaps > 0) & (current_gaps < 0)]
        cross_down_series = Series(np.where(conditions, -1, 0)[0])
        return cross_down_series

    def cross_up(self, another_series: Series):
        current_gaps = self._line_series - another_series
        previous_gaps = current_gaps.shift(1)
        conditions = [(previous_gaps < 0) & (current_gaps > 0)]
        cross_up_series = Series(np.where(conditions, 1, 0)[0])
        return cross_up_series

    def cross_over(self, another_series: Series):
        cross_over_series = self.cross_up(another_series) + self.cross_down(another_series)
        return cross_over_series

    def is_convergent(self, another_series: Series):
        current_gaps = self._line_series - another_series
        previous_gaps = current_gaps.shift(1)

        condition = [current_gaps < previous_gaps]
        is_convergent_series = Series(np.where(condition, 1, 0)[0])
        return is_convergent_series

    def is_divergent(self, another_series: Series):
        current_gaps = self._line_series - another_series
        previous_gaps = current_gaps.shift(1)
        condition = [current_gaps > previous_gaps]
        is_divergent_series = Series(np.where(condition, 1, 0)[0])
        return is_divergent_series

    @staticmethod
    def _get_previous_positions(shifting_series: Series, last_continuous_intervals: int):
        previous_positions = list()
        for i in range(last_continuous_intervals):
            shift_value = i + 1
            previous_positions.append(shifting_series.shift(shift_value))

        return previous_positions

    @staticmethod
    def _get_greater_than_conditions(current_position: Series, previous_positions: List[Series]):
        comparison = current_position > previous_positions[0]
        comparing_position = previous_positions[0]
        for position in previous_positions[1:]:
            comparison = comparison & (comparing_position > position)
            comparing_position = position

        conditions = [comparison]
        return conditions

    @staticmethod
    def _get_less_than_conditions(current_position: Series, previous_positions: List[Series]):
        comparison = current_position < previous_positions[0]
        comparing_position = previous_positions[0]
        for position in previous_positions[1:]:
            comparison = comparison & (comparing_position < position)
            comparing_position = position

        conditions = [comparison]
        return conditions

    def is_going_up(self, last_continuous_intervals: int):
        current_position = self._line_series

        previous_positions = self._get_previous_positions(shifting_series=current_position,
                                                          last_continuous_intervals=last_continuous_intervals)

        conditions = self._get_greater_than_conditions(current_position=current_position,
                                                       previous_positions=previous_positions)

        going_up_series = Series(np.where(conditions, 1, 0)[0])
        return going_up_series

    def is_going_down(self, last_continuous_intervals: int):
        current_position = self._line_series

        previous_positions = self._get_previous_positions(shifting_series=current_position,
                                                          last_continuous_intervals=last_continuous_intervals)

        conditions = self._get_less_than_conditions(current_position=current_position,
                                                    previous_positions=previous_positions)

        going_down_series = Series(np.where(conditions, -1, 0)[0])
        return going_down_series

    def is_trending(self, continuous_intervals: int):
        trending_series = self.is_going_up(continuous_intervals) + self.is_going_down(continuous_intervals)
        return trending_series

    def is_slowing_down(self, last_continuous_intervals: int):
        current_position = self._line_series
        previous_position = current_position.shift(1)

        change = (previous_position - current_position).abs()
        previous_changes = self._get_previous_positions(shifting_series=change,
                                                        last_continuous_intervals=last_continuous_intervals)

        conditions = self._get_less_than_conditions(current_position=change, previous_positions=previous_changes)

        slowing_down_series = Series(np.where(conditions, -1, 0)[0])
        return slowing_down_series

    def is_speeding_up(self, last_continuous_intervals: int):
        current_position = self._line_series
        previous_position = current_position.shift(1)

        change = (previous_position - current_position).abs()
        previous_changes = self._get_previous_positions(shifting_series=change,
                                                        last_continuous_intervals=last_continuous_intervals)

        conditions = self._get_greater_than_conditions(current_position=change, previous_positions=previous_changes)
        speeding_up_series = Series(np.where(conditions, 1, 0)[0])
        return speeding_up_series

    def get_acceleration(self, last_continuous_intervals: int):
        acceleration_series = self.is_speeding_up(last_continuous_intervals) + self.is_slowing_down(
            last_continuous_intervals)
        return acceleration_series

    def is_up_hit(self, target_value: float):
        current_position = self._line_series
        previous_position = current_position.shift(1)
        conditions = [(current_position > target_value) & (previous_position <= target_value)]
        up_hit_series = Series(np.where(conditions, 1, 0)[0])
        return up_hit_series

    def is_down_hit(self, target_value: float):
        current_position = self._line_series
        previous_position = current_position.shift(1)
        conditions = [(current_position < target_value) & (previous_position >= target_value)]
        down_hit_series = Series(np.where(conditions, -1, 0)[0])
        return down_hit_series

    def has_directional_hit(self, target_value: float):
        directional_hit = self.is_up_hit(target_value) + self.is_down_hit(target_value)
        return directional_hit


if __name__ == '__main__':
    pass
    series_data_up = Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    series_data_down = Series([10, 9, 8, 7, 6, 5, 4, 2, 1, 1])
    series_data_slow = Series([100, 90, 81, 73, 66, 60, 55, 51, 48, 46])
    sample_series = Series([46, 48, 51, 55, 60, 66, 73, 81, 88, 80, 73, 67, 62, 58, 55, 53, 52])
    counter_series = Series([0.1, 2.7, 3.9, 4.8, 3.2, 3, 8.2, 6.9, 8.3, 11.4])

    line_indicator = IndicatorSignal(sample_series)
    cross_values = line_indicator.has_directional_hit(55)
    print(cross_values)
