from ambition_visit_schedule import DAY1
from ambition_rando.models import RandomizationList
from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_base.sites import SiteError
from edc_constants.constants import YES
from edc_metadata_rules import PredicateCollection


class Predicates(PredicateCollection):

    app_label = 'ambition_subject'
    visit_model = f'{app_label}.subjectvisit'

    def datetime_gt_3_months(self, visit=None, field=None):
        values = self.exists(
            reference_name=f'{self.app_label}.patienthistory',
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            field_name=field)
        return ((visit.report_datetime - relativedelta(months=3)).date() >
                (values[0] or (visit.report_datetime).date()))

    def blood_result_abnormal(self, visit=None):
        values = self.exists(
            reference_name=f'{self.app_label}.bloodresult',
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            field_name='abnormal_results_in_ae_range')
        return values[0] == YES

    def cause_of_death(self, visit=None, cause=None):
        values = self.exists(
            reference_name=f'{self.app_label}.deathreporttmg1',
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            field_name='cause_of_death')
        return not (values[0] == cause)

    def model_field_exists(self, visit=None, model_lower=None, model_field=None):
        values = self.exists(
            reference_name=f'{self.app_label}.{model_lower}',
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            field_name=f'{model_field}')
        return (values[0] == YES)

    def func_require_cd4(self, visit, **kwargs):
        if visit.visit_code == DAY1:
            return self.datetime_gt_3_months(
                visit=visit, field='cd4_date')
        return False

    def func_require_vl(self, visit, **kwargs):
        if visit.visit_code == DAY1:
            return self.datetime_gt_3_months(
                visit=visit, field='viral_load_date')
        return False

    def func_require_pkpd_stopcm(self, visit, **kwargs):
        site = Site.objects.get_current()
        if site.id == 40 and site.name != 'blantyre':
            raise SiteError(
                f'Expected site 40 to be "blantyre". Got {site.name}.')
        return site.id == 40

    def rando_arm_drug_assignment(self, visit, **kwargs):
        subject_identifier = visit.subject_identifier
        rando = RandomizationList.objects.get(
            subject_identifier=subject_identifier)
        return rando.drug_assignment == 'control'

    def rando_arm_blantyre(self, visit, **kwargs):
        return self.func_require_pkpd_stopcm(visit) and self.rando_arm_drug_assignment(visit)

    def func_require_qpcr_requisition(self, visit, **kwargs):
        site = Site.objects.get_current()
        if site.id == 40 and site.name != 'blantyre':
            raise SiteError(
                f'Expected site 40 to be "blantyre". Got {site.name}.')
        if site.id == 10 and site.name != 'gaborone':
            raise SiteError(
                f'Expected site 10 to be "gaborone". Got {site.name}.')
        return site.id == 40 or site.id == 10
