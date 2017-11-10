from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import YES

from edc_metadata_rules import PredicateCollection


class Predicates(PredicateCollection):

    app_label = 'ambition_subject'
    visit_model = f'{app_label}.subjectvisit'

    @property
    def death_report_model_cls(self):
        return django_apps.get_model(f'{self.app_label}.deathreport')

    @property
    def bloodresult_model_cls(self):
        return django_apps.get_model(f'{self.app_label}.bloodresult')

    @property
    def death_report_model_tmg1_cls(self):
        return django_apps.get_model(f'{self.app_label}.deathreporttmg1')

    def check_gt_3_months(self, visit=None, panel_name=None):
        values = self.exists(
            reference_name=f'{self.app_label}.patienthistory',
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            field_name=panel_name)
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

    def func_require_recurrence(self, visit, **kwargs):
        prn_required = self.model_field_exists(visit=visit,
                                               model_lower='prnmodel',
                                               model_field='recurrence_symptom')

        adverse_event_required = self.model_field_exists(visit=visit,
                                                         model_lower='adverseevent',
                                                         model_field='ae_cm_recurrence')
        return prn_required or adverse_event_required

    def func_require_cd4(self, visit, **kwargs):
        if visit.visit_code == '1000':
            return self.check_gt_3_months(visit=visit, panel_name='cd4_date')
        return False

    def func_require_vl(self, visit, **kwargs):
        if visit.visit_code == '1000':
            return self.check_gt_3_months(visit=visit, panel_name='viral_load_date')
        return False

    def func_require_ae(self, visit, **kwargs):
        if visit.visit_code != '1000':
            return self.blood_result_abnormal(visit=visit)
        return False

    def func_offstudy_required(self, visit, **kwargs):
        is_ineligible = False
        try:
            obj = self.bloodresult_model_cls.objects.get(
                subject_visit=visit,
                subject_visit__visit_code='1000')
            is_ineligible = (obj.neutrophils_result(obj=obj) or
                             obj.platelets_result(obj=obj) or
                             obj.alt_result(obj=obj))
        except ObjectDoesNotExist:
            return True
        return is_ineligible

    def func_require_death_report_tmg1(self, visit, **kwargs):
        try:
            death_report = self.death_report_model_cls.objects.get(
                subject_visit=visit)
            if death_report:
                return True
        except ObjectDoesNotExist:
            return False

    def func_require_death_report_tmg2(self, visit, **kwargs):
        try:
            death_report = self.death_report_model_cls.objects.get(
                subject_visit=visit)
            return self.cause_of_death(visit=visit, cause=death_report.cause_of_death)
        except ObjectDoesNotExist:
            return False
