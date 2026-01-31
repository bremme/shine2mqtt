import pytest

from shine2mqtt.util.dicttools import convert_to_nested_dict, merge_dict, remove_none_values


class TestMergeDict:
    def test_merges_nested_dicts_recursively(self):
        base = {"a": 1, "b": {"c": 1, "d": 2}}
        override = {"b": {"c": 3}, "e": 4}

        result = merge_dict(base=base, override=override)

        assert result == {"a": 1, "b": {"c": 3, "d": 2}, "e": 4}

    def test_does_not_mutate_base(self):
        base = {"a": 1, "b": {"c": 1}}
        override = {"b": {"c": 2}}

        _ = merge_dict(base=base, override=override)

        assert base == {"a": 1, "b": {"c": 1}}

    @pytest.mark.parametrize(
        ("base", "override", "expected"),
        [
            ({"a": 1}, {"a": {"b": 2}}, {"a": {"b": 2}}),
            ({"a": {"b": 2}}, {"a": 1}, {"a": 1}),
            ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        ],
    )
    def test_override_wins_for_non_dict_or_type_changes(self, base, override, expected):
        result = merge_dict(base=base, override=override)
        assert result == expected


class TestRemoveNoneValues:
    def test_removes_only_none(self):
        original = {"a": None, "b": 0, "c": "", "d": False, "e": [], "f": {}}

        result = remove_none_values(original)

        assert result == {"b": 0, "c": "", "d": False, "e": [], "f": {}}


class TestConvertToNestedDict:
    def test_converts_flat_keys_to_nested(self):
        flat = {"mqtt__host": "localhost", "mqtt__port": 1883, "log_level": "INFO"}

        nested = convert_to_nested_dict(flat, delimiter="__")

        assert nested == {
            "mqtt": {"host": "localhost", "port": 1883},
            "log_level": "INFO",
        }

    def test_supports_multiple_nested_levels(self):
        flat = {
            "a__b__c": 1,
            "a__b__d": 2,
            "a__e": 3,
        }

        nested = convert_to_nested_dict(flat, delimiter="__")

        assert nested == {"a": {"b": {"c": 1, "d": 2}, "e": 3}}

    def test_allows_custom_delimiter(self):
        flat = {"a.b": 1, "a.c": 2}

        nested = convert_to_nested_dict(flat, delimiter=".")

        assert nested == {"a": {"b": 1, "c": 2}}
