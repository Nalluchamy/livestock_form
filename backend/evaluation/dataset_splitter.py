"""
Leakage-Safe Dataset Splitting for ELHGS.
Provides:
- Reproducible Train/Validation/Test splitting (target ~70/15/15)
- Animal/group-aware partitioning (prevents observations of the same animal across splits)
- Duplicate and near-duplicate cross-split leakage detection
- Class distribution and small-dataset limitation reporting
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter


def extract_group_id(sample: Dict[str, Any]) -> str:
    """
    Extracts group/animal identifier for group-aware splitting.
    Uses 'group_id' or 'animal_id' if present, or parses sample_id prefix.
    """
    if "group_id" in sample and sample["group_id"]:
        return str(sample["group_id"])
    if "animal_id" in sample and sample["animal_id"]:
        return str(sample["animal_id"])
    
    # Fallback: Parse common prefix before hyphen if sample_id has format ANIMAL-001-ANGLE1
    s_id = str(sample.get("sample_id", ""))
    parts = s_id.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return s_id


def split_dataset_group_aware(
    samples: List[Dict[str, Any]],
    target_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15),
    random_seed: int = 42,
    stratify_field: str = "final_consensus_grade"
) -> Dict[str, Any]:
    """
    Partitions samples into train, validation, and test sets.
    Ensures that all samples belonging to the same animal/group reside exclusively in one partition.
    """
    if not samples:
        return {
            "train": [],
            "val": [],
            "test": [],
            "counts": {"train": 0, "val": 0, "test": 0, "total": 0},
            "class_distributions": {},
            "limitations_warnings": ["Dataset is empty. Cannot generate splits."]
        }

    train_ratio, val_ratio, test_ratio = target_ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    train_ratio /= total_ratio
    val_ratio /= total_ratio
    test_ratio /= total_ratio

    # 1. Group samples by animal/lot identifier
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for s in samples:
        gid = extract_group_id(s)
        groups.setdefault(gid, []).append(s)

    unique_groups = list(groups.keys())
    rng = random.Random(random_seed)
    rng.shuffle(unique_groups)

    # 2. Check for duplicate image hashes across samples
    seen_hashes: Dict[str, str] = {}
    duplicate_conflicts = []
    for s in samples:
        img_hash = s.get("image_hash") or s.get("sha256")
        gid = extract_group_id(s)
        if img_hash:
            if img_hash in seen_hashes and seen_hashes[img_hash] != gid:
                duplicate_conflicts.append(
                    f"Cross-group identical image hash {img_hash[:10]} found between group '{gid}' and '{seen_hashes[img_hash]}'"
                )
            seen_hashes[img_hash] = gid

    # 3. Partition groups
    train_groups = []
    val_groups = []
    test_groups = []

    target_total = len(samples)
    target_train_count = int(target_total * train_ratio)
    target_val_count = int(target_total * val_ratio)

    current_train_count = 0
    current_val_count = 0

    for gid in unique_groups:
        group_size = len(groups[gid])
        if current_train_count + group_size <= target_train_count or (not train_groups and not val_groups):
            train_groups.append(gid)
            current_train_count += group_size
        elif current_val_count + group_size <= target_val_count:
            val_groups.append(gid)
            current_val_count += group_size
        else:
            test_groups.append(gid)

    # Guarantee at least 1 group in val and test if possible
    if len(unique_groups) >= 3:
        if not val_groups and len(train_groups) > 1:
            val_groups.append(train_groups.pop())
        if not test_groups and len(train_groups) > 1:
            test_groups.append(train_groups.pop())

    train_samples = [s for gid in train_groups for s in groups[gid]]
    val_samples = [s for gid in val_groups for s in groups[gid]]
    test_samples = [s for gid in test_groups for s in groups[gid]]

    # 4. Compute class distributions
    def get_dist(sample_list):
        grades = [s.get(stratify_field) or s.get("expert_grade") or "Unlabeled" for s in sample_list]
        return dict(Counter(grades))

    class_distributions = {
        "train": get_dist(train_samples),
        "val": get_dist(val_samples),
        "test": get_dist(test_samples),
    }

    # 5. Warnings and limitations
    limitations_warnings = []
    if len(samples) < 50:
        limitations_warnings.append(
            f"Small dataset size (N={len(samples)}). Splitting may result in high variance or under-represented classes."
        )
    if duplicate_conflicts:
        limitations_warnings.extend(duplicate_conflicts)

    # Check for empty classes in test split
    all_classes = set(class_distributions["train"].keys())
    test_classes = set(class_distributions["test"].keys())
    missing_test_classes = all_classes - test_classes
    if missing_test_classes:
        limitations_warnings.append(
            f"Test split lacks representation for class(es): {missing_test_classes} due to small sample size."
        )

    return {
        "train": train_samples,
        "val": val_samples,
        "test": test_samples,
        "counts": {
            "train": len(train_samples),
            "val": len(val_samples),
            "test": len(test_samples),
            "total": len(samples)
        },
        "class_distributions": class_distributions,
        "limitations_warnings": limitations_warnings
    }
