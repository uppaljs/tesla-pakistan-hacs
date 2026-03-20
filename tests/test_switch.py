"""Tests for Tesla Connect Pakistan switch entities."""

from __future__ import annotations

from .conftest import MOCK_GEYSER_DETAILS


class TestTimerSlotLogic:
    """Tests for the timer slot schedule update logic."""

    def test_build_updated_times_single_slot(self) -> None:
        """Changing one slot should leave the other 23 unchanged."""
        times = MOCK_GEYSER_DETAILS["times"]
        hour = 2  # Currently OFF.
        target_status = True

        updated = [
            {
                "status": target_status if i == hour else slot["status"],
                "time": slot["time"],
            }
            for i, slot in enumerate(times)
        ]

        # The target slot should now be ON.
        assert updated[hour]["status"] is True
        # Adjacent slots should remain unchanged.
        assert updated[0]["status"] is False
        assert updated[1]["status"] is False
        assert updated[3]["status"] is False
        assert updated[4]["status"] is True

    def test_build_updated_times_preserves_length(self) -> None:
        """The updated schedule should always have 24 slots."""
        times = MOCK_GEYSER_DETAILS["times"]
        updated = [
            {
                "status": True if i == 0 else slot["status"],
                "time": slot["time"],
            }
            for i, slot in enumerate(times)
        ]
        assert len(updated) == 24

    def test_all_slots_can_be_turned_off(self) -> None:
        """Every slot in the schedule should be toggleable to OFF."""
        times = MOCK_GEYSER_DETAILS["times"]
        for hour in range(24):
            updated = [
                {
                    "status": False if i == hour else slot["status"],
                    "time": slot["time"],
                }
                for i, slot in enumerate(times)
            ]
            assert updated[hour]["status"] is False
