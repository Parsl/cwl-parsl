"""Tests for correctness of the CommandLineTool"""

import os

import parsl
from parsl.configs.local_threads import config
from parsl.data_provider.files import File

from cwl import CWLApp

parsl.load(config)


test_cwl_files = os.path.join(os.getcwd(), "tests", "test-cwl-files")
test_runtime_files = os.path.join(os.getcwd(), "tests", "test-runtime-files")


def test_find() -> None:
    """Test for the find CWL CommandLineTool."""
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'find_stdout_1.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_2.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"find '.' -name '*.cwl' -maxdepth 3"
            f" > {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
        )
        == 0
    )

    # Create CommandLineTool app and run with parsl
    find = CWLApp(os.path.join(test_cwl_files, "find.cwl"))

    # Test 1
    find(
        dir=".",
        maxdepth=3,
        name="*.cwl",
        example_out=os.path.join(test_runtime_files, "find_stdout_1.txt"),
    ).result()

    with open(
        os.path.join(test_runtime_files, "find_stdout_1.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Test 2
    find(
        dir=".", name="*.cwl", example_out=os.path.join(test_runtime_files, "find_stdout_2.txt")
    ).result()

    with open(
        os.path.join(test_runtime_files, "find_stdout_2.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'find_stdout_1.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_2.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
        )
        == 0
    )


def test_find_list():
    """Test for the find CWL CommandLineTool with list inputs."""
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'find_stdout_1_list.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_2_list.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"find '.' -name '*.cwl' -maxdepth 3"
            f" > {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
        )
        == 0
    )

    # Create CommandLineTool app and run with parsl
    find = CWLApp(os.path.join(test_cwl_files, "find.cwl"))

    # Test 1
    find(
        dir=".",
        maxdepth=3,
        name="*.cwl",
        example_out=os.path.join(test_runtime_files, "find_stdout_1_list.txt"),
    ).result()

    with open(
        os.path.join(test_runtime_files, "find_stdout_1_list.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual_list.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Test 2
    find(
        dir=".",
        name="*.cwl",
        example_out=os.path.join(test_runtime_files, "find_stdout_2_list.txt"),
    ).result()

    with open(
        os.path.join(test_runtime_files, "find_stdout_2_list.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual_list.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'find_stdout_1_list.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_2_list.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
        )
        == 0
    )


def test_touch() -> None:
    """Test for the touch CWL CommandLineTool."""
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'touch1.txt')}"
        f" {os.path.join(test_runtime_files, 'touch2.txt')}"
    )

    # Create CommandLineTool app and run with parsl
    touch = CWLApp(os.path.join(test_cwl_files, "touch.cwl"))

    # Test 1
    touch(
        filenames=[
            os.path.join(test_runtime_files, "touch1.txt"),
            os.path.join(test_runtime_files, "touch2.txt"),
        ],
        output_files=[
            File(os.path.join(test_runtime_files, "touch1.txt")),
            File(os.path.join(test_runtime_files, "touch2.txt")),
        ],
    ).result()

    assert (
        os.system(
            f"[ -f {os.path.join(test_runtime_files, 'touch1.txt')} -a"
            f" -f {os.path.join(test_runtime_files, 'touch2.txt')} ]"
            " && exit 0 || exit 1"
        )
        == 0
    )

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'touch1.txt')}"
            f" {os.path.join(test_runtime_files, 'touch2.txt')}"
        )
        == 0
    )


def test_word_count() -> None:
    """Test for the wc CWL CommandLineTool."""
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'word_count_stdout.txt')}"
        f" {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"wc {os.path.join(test_cwl_files, 'wc.cwl')}"
            f" > {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
        )
        == 0
    )

    # Create CommandLineTool app and run with parsl
    word_count = CWLApp(os.path.join(test_cwl_files, "wc.cwl"))

    # Test 1
    word_count(
        text_file=File(os.path.join(test_cwl_files, "wc.cwl")),
        stdout=os.path.join(test_runtime_files, "word_count_stdout.txt"),
    ).result()

    with open(
        os.path.join(test_runtime_files, "word_count_stdout.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "word_count_stdout_manual.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'word_count_stdout.txt')}"
            f" {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
        )
        == 0
    )
