from vertex_eval.evidence import evaluate_agreement, report_confirmed
from vertex_eval.models import RubricResult
from vertex_eval.rubric import RubricRegistry, default_rubric


def test_channels_agree_on_happy_trace(happy_trace):
    reg = RubricRegistry()
    for item in default_rubric().items:
        base = reg.check_for(item)(happy_trace)
        conf = evaluate_agreement(happy_trace, base)
        assert conf.channels_agree is True


def test_destructive_without_audit_flags_channels_disagree(unaudited_destructive_trace):
    reg = RubricRegistry()
    item = next(i for i in default_rubric().items if i.id == "no_destructive_unaudited")
    base = reg.check_for(item)(unaudited_destructive_trace)
    conf = evaluate_agreement(unaudited_destructive_trace, base)
    assert conf.channels_agree is False
    assert conf.confidence <= 0.5


def test_report_confirmed_all_pass():
    results = [
        RubricResult(item_id="a", passed=True, channels_agree=True, confidence=1.0),
        RubricResult(item_id="b", passed=True, channels_agree=True, confidence=1.0),
    ]
    assert report_confirmed(results) is True


def test_report_not_confirmed_when_pass_but_channels_disagree():
    results = [
        RubricResult(item_id="a", passed=True, channels_agree=False, confidence=0.5),
    ]
    assert report_confirmed(results) is False


def test_report_not_confirmed_when_fail_with_low_confidence():
    results = [
        RubricResult(item_id="a", passed=False, channels_agree=True, confidence=0.3),
    ]
    assert report_confirmed(results) is False
