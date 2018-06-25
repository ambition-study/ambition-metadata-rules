from ambition_labs.panels import pk_plasma_panel_t2, pk_plasma_panel_t4, pk_plasma_panel_t7
from ambition_labs.panels import pk_plasma_panel_t12, pk_plasma_panel_t23
from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_metadata_rules import CrfRule, CrfRuleGroup, register
from edc_metadata_rules import RequisitionRule, RequisitionRuleGroup

from ..predicates import Predicates

app_label = 'ambition_subject'
pc = Predicates()


@register()
class PkPdRuleGroup(CrfRuleGroup):

    pkpd = CrfRule(
        predicate=pc.rando_arm_blantyre,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=[f'{app_label}.pkpdcrf'])

    class Meta:
        app_label = app_label


@register()
class PkPdRequisitionRuleGroup(RequisitionRuleGroup):

    require_pk_plasma_t2 = RequisitionRule(
        predicate=pc.func_require_pkpd_stopcm,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[pk_plasma_panel_t2])

    require_pk_plasma_t2 = RequisitionRule(
        predicate=pc.func_require_pkpd_stopcm,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[pk_plasma_panel_t4])

    require_pk_plasma_t7 = RequisitionRule(
        predicate=pc.func_require_pkpd_stopcm,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[pk_plasma_panel_t7])

    require_pk_plasma_t12 = RequisitionRule(
        predicate=pc.func_require_pkpd_stopcm,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[pk_plasma_panel_t12])

    require_pk_plasma_t23 = RequisitionRule(
        predicate=pc.func_require_pkpd_stopcm,
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[pk_plasma_panel_t23])

    class Meta:
        app_label = app_label
        requisition_model = f'{app_label}.subjectrequisition'
