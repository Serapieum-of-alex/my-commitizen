from __future__ import annotations

# Commitizen plugin that extends the built-in CustomizeCommitsCz
# and wires our changelog message builder hook for normalization & de-dup.

from commitizen.cz.customize.customize import CustomizeCommitsCz as _CustomizeCommitsCz
from my_commit.commitizen_hooks import normalize_and_dedup


class PyramidsCz(_CustomizeCommitsCz):
    # Commitizen reads this attribute when building the changelog
    changelog_message_builder_hook = staticmethod(normalize_and_dedup)
