"""Tests for correctness of the CommandLineTool"""

import os

import parsl
from parsl.configs.local_threads import config
from parsl.data_provider.files import File

from tools import cat, find, touch, wc

parsl.load(config)

test_runtime_files = os.path.join(os.getcwd(), "tests", "test-runtime-files")
test_report_files = os.path.join(os.getcwd(), "tests", "test-reports")



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
            f" >> {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
        )
        == 0
    )

    # Test 1
    find(
        dir=".",
        maxdepth=3,
        name="*.cwl",
        redirect_to_file=os.path.join(test_runtime_files, "find_stdout_1.txt"),
        output_file=File(os.path.join(test_runtime_files, "find_stdout_1.txt")),
    ).result()

    with open(
        os.path.join(test_runtime_files, "find_stdout_1.txt"), "r", encoding="utf-8"
    ) as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual.txt"), "r", encoding="utf-8"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Test 2
    find(
        dir=".",
        name="*.cwl",
        redirect_to_file=os.path.join(test_runtime_files, "find_stdout_2.txt"),
        output_file=File(os.path.join(test_runtime_files, "find_stdout_2.txt")),
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


def test_touch() -> None:
    """Test for the touch CWL CommandLineTool."""
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'touch1.txt')}"
        f" {os.path.join(test_runtime_files, 'touch2.txt')}"
    )

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
        f" {os.path.join(test_runtime_files, 'word_count_stderr.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"wc {os.path.join("tests", "test_correctness.py")}"
            f" > {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
        )
        == 0
    )


    # Test 1
    wc(
        input_files=[File(os.path.join("tests", "test_correctness.py"))],
        stdout=os.path.join(test_runtime_files, "word_count_stdout.txt"),
        stderr=os.path.join(test_runtime_files, "word_count_stderr.txt"),
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
            f" {os.path.join(test_runtime_files, 'word_count_stderr.txt')}"
        )
        == 0
    )

def test_cat() -> None:
    """Test for the cat CWL CommandLineTool."""
    # Remove Prev Generated Files if Present
    os.system(
            "rm -rf" 
            f" {os.path.join(test_runtime_files, 'cat_redirect_file_manual.txt')}"
            f" {os.path.join(test_runtime_files, 'cat_redirect_file.txt')}"
    )

    # Run Manually
    assert(
        os.system(
            f"cat {os.path.join('tests', 'test_correctness.py')}"
            f" > {os.path.join(test_runtime_files, 'cat_redirect_file_manual.txt')}"
        ) == 0
    )

    # Test 1
    cat(
        from_files=[File(os.path.join('tests', 'test_correctness.py'))],
        redirect_to_file=os.path.join(test_runtime_files, 'cat_redirect_file.txt'),
        output_file=File(os.path.join(test_runtime_files, 'cat_redirect_file.txt'))
    ).result()

    with open(
        os.path.join(test_runtime_files, 'cat_redirect_file.txt'), 'r', encoding='utf-8'
    ) as f1, open(
        os.path.join(test_runtime_files, 'cat_redirect_file_manual.txt'), 'r', encoding='utf-8'
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert(
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'cat_redirect_file.txt')}"
            f" {os.path.join(test_runtime_files, 'cat_redirect_file_manual.txt')}"
        ) == 0
    )

def cat_cat_workflow():
    """Test for workflow cat, cat -> cat"""

    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_report_files, 'q1_report.csv')}"
        f" {os.path.join(test_report_files, 'q2_report.csv')}"
        f" {os.path.join(test_report_files, 'half_year_report.csv')}"
    )
    
    q1 = cat(
        from_files=[
            File(os.path.join(test_report_files, "january_report.csv")),
            File(os.path.join(test_report_files, "february_report.csv")),
            File(os.path.join(test_report_files, "march_report.csv")),
        ],
        redirect_to_file=os.path.join(test_report_files, "q1_report.csv"),
        output_file=File(os.path.join(test_report_files, "q1_report.csv")),
    )

    q2 = cat(
        from_files=[
            File(os.path.join(test_report_files, "april_report.csv")),
            File(os.path.join(test_report_files, "may_report.csv")),
            File(os.path.join(test_report_files, "june_report.csv")),
        ],
        redirect_to_file=os.path.join(test_report_files, "q2_report.csv"),
        output_file=File(os.path.join(test_report_files, "q2_report.csv")),
            
    )

    half_year_report = cat(
        from_files=[q1.outputs[0], q2.outputs[0]],
        redirect_to_file=os.path.join(test_report_files, "half_year_report.csv"),
        output_file=File(os.path.join(test_report_files, "half_year_report.csv")),
    )

    half_year_report.result()

    os.system(
        "rm"
        f" {os.path.join(test_report_files, 'q1_report.csv')}"
        f" {os.path.join(test_report_files, 'q2_report.csv')}"
        f" {os.path.join(test_report_files, 'half_year_report.csv')}"
    )

def test_workflows() -> None:
    """Test for various workflows."""
    cat_cat_workflow()
