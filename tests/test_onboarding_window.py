from laptop_guard.onboarding_window import onboarding_steps
from laptop_guard.cli import build_parser


def test_persian_onboarding_steps_explain_id_and_one_time_pairing():
    text = " ".join(part for step in onboarding_steps("telegram") for part in step)
    assert "/id" in text
    assert "/pair" in text
    assert "تلگرام" in text


def test_onboarding_command_selects_provider_without_opening_window():
    args = build_parser().parse_args(["onboarding", "--provider", "bale"])
    assert args.provider == "bale"
