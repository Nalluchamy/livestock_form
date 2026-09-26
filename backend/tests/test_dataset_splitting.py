import pytest
from backend.evaluation.dataset_splitter import split_dataset_group_aware, extract_group_id


def test_extract_group_id():
    assert extract_group_id({"group_id": "COW-100"}) == "COW-100"
    assert extract_group_id({"animal_id": "COW-200"}) == "COW-200"
    assert extract_group_id({"sample_id": "ANIMAL-001-ANGLE1"}) == "ANIMAL-001"
    assert extract_group_id({"sample_id": "STANDALONE"}) == "STANDALONE"


def test_group_aware_splitting_no_leakage():
    # 20 samples belonging to 5 distinct animals (4 images per animal)
    samples = []
    for animal_idx in range(1, 6):
        for angle in range(1, 5):
            samples.append({
                "sample_id": f"COW-{animal_idx:02d}-IMG{angle}",
                "animal_id": f"COW-{animal_idx:02d}",
                "final_consensus_grade": "A" if animal_idx <= 2 else "B"
            })

    assert len(samples) == 20
    split_res = split_dataset_group_aware(samples, target_ratios=(0.60, 0.20, 0.20), random_seed=42)

    train_animals = set(s["animal_id"] for s in split_res["train"])
    val_animals = set(s["animal_id"] for s in split_res["val"])
    test_animals = set(s["animal_id"] for s in split_res["test"])

    # Strict separation: No animal can exist in more than one partition!
    assert train_animals.isdisjoint(val_animals)
    assert train_animals.isdisjoint(test_animals)
    assert val_animals.isdisjoint(test_animals)


def test_duplicate_image_conflict_warning():
    # Two different animals with identical image hash (duplicate leakage)
    samples = [
        {"sample_id": "ANIMAL-01", "animal_id": "A1", "image_hash": "hash_xyz_identical", "final_consensus_grade": "A"},
        {"sample_id": "ANIMAL-02", "animal_id": "A2", "image_hash": "hash_xyz_identical", "final_consensus_grade": "B"},
    ]
    split_res = split_dataset_group_aware(samples)
    warnings = split_res["limitations_warnings"]
    assert any("identical image hash" in w for w in warnings)


def test_small_dataset_warning():
    samples = [
        {"sample_id": f"COW-{i}", "final_consensus_grade": "A"} for i in range(10)
    ]
    split_res = split_dataset_group_aware(samples)
    warnings = split_res["limitations_warnings"]
    assert any("Small dataset size" in w for w in warnings)
