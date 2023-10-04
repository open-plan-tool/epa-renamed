from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.forms.models import modelformset_factory
from projects.forms import OpenPlanForm, OpenPlanModelForm, ProjectCreateForm

from projects.forms import StorageForm, AssetCreateForm, UploadTimeseriesForm
from projects.models import Project, EconomicData, Scenario
from .models import *

CURVES = (("Evening Peak", "Evening Peak"), ("Midday Peak", "Midday Peak"))


class ProjectForm(OpenPlanModelForm):
    start_date = forms.DateField(
        label=_("Simulation start"),
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "TestDateClass",
                "placeholder": "Select a start date",
                "type": "date",
            },
        ),
    )
    duration = forms.IntegerField(label=_("Project lifetime"))

    class Meta:
        model = Project
        exclude = ("country", "user", "viewers", "economic_data")

    def save(self, *args, **kwargs):
        user = kwargs.pop("user")
        kwargs["commit"] = False
        pr = super().save(*args, **kwargs)

        # The project does not exist yet so we created it as well as a scenario
        if pr.id is None:
            economic_data = EconomicData.objects.create(
                duration=self.cleaned_data["duration"],
                currency="NGN",
                discount=0,
                tax=0,
            )
            pr.economic_data = economic_data
            pr.user = user
            pr.country = "NIGERIA"
            pr.save()
            Scenario.objects.create(
                name=f'{self.cleaned_data["name"]}_scenario',
                start_date=self.cleaned_data["start_date"],
                time_step=60,
                evaluated_period=365,  # TODO this depends on the year
                project=pr,
            )
        # The project does exist and we update simply its values
        else:
            economic_data = EconomicData.objects.filter(id=pr.economic_data.id)
            economic_data.update(duration=self.cleaned_data["duration"])

            scenario = Scenario.objects.filter(project=pr)
            scenario.update(start_date=self.cleaned_data["start_date"])
            pr.save()

        return pr


class EconomicDataForm(OpenPlanModelForm):
    capex_fix = forms.FloatField(label=_("Fix project costs"), validators=[MinValueValidator(0.0)])

    class Meta:
        model = EconomicData
        exclude = ("tax",)

    def save(self, *args, **kwargs):
        ed = super().save(*args, **kwargs)
        scenario = Scenario.objects.filter(project__economic_data=ed)
        scenario.update(capex_fix=self.cleaned_data["capex_fix"])


class CPNLocationForm(ProjectCreateForm):
    weather = forms.FileField(label=_("Upload weather data"), required=False)


class DemandProfileForm(OpenPlanForm):
    consumer_type = forms.ModelChoiceField(queryset=ConsumerType.objects.all())
    facility_type = forms.ModelChoiceField(queryset=ConsumerType.objects.all())
    curve = forms.ChoiceField(
        label=_("Load curve"),
        choices=CURVES,
        widget=forms.Select(attrs={"data-bs-toggle": "tooltip", "title": _("Load curve")}),
    )
    households = forms.IntegerField(label=_("Number of households"))


class UploadDemandForm(UploadTimeseriesForm):
    class Meta:
        model = DemandTimeseries
        exclude = ["id", "user", "scenario", "ts_type"]
        widgets = {
            "start_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "TestDateClass",
                    "placeholder": "Select a start date",
                    "type": "date",
                },
            ),
        }


class PVForm(AssetCreateForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, asset_type="pv_plant", **kwargs)
        # which fields exists in the form are decided upon AssetType saved in the db
        self.prefix = self.asset_type_name

        # for field in self.fields:

        self.fields["input_timeseries"].required = False

        for field, value in zip(("name", "renewable_asset"), (self.asset_type_name, True)):
            self.fields[field].widget = forms.HiddenInput()
            self.fields[field].initial = value


class DieselForm(AssetCreateForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, asset_type="diesel_generator", **kwargs)
        # which fields exists in the form are decided upon AssetType saved in the db
        self.prefix = self.asset_type_name

        # for field in self.fields:

        for field, value in zip(("name",), (self.asset_type_name,)):
            self.fields[field].widget = forms.HiddenInput()
            self.fields[field].initial = value


class BessForm(StorageForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, asset_type="bess", **kwargs)
        # which fields exists in the form are decided upon AssetType saved in the db
        self.prefix = self.asset_type_name

        # for field in self.fields:

        for field, value in zip(("name",), (self.asset_type_name,)):
            self.fields[field].widget = forms.HiddenInput()
            self.fields[field].initial = value


class DummyForm(forms.Form):
    some_input = forms.ChoiceField(label=_("Some INput"), choices=(("a", "a"), ("b", "b")))


class ConsumerGroupForm(OpenPlanModelForm):
    class Meta:
        model = ConsumerGroup
        exclude = ["project", "group_id"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        advanced_opt = kwargs.pop("advanced_view", False)
        instance = kwargs.pop("instance", None)

        if instance is None:
            self.fields["timeseries"].queryset = DemandTimeseries.objects.none()
        else:
            consumer_type_id = instance.consumer_type_id
            self.fields["timeseries"].queryset = DemandTimeseries.objects.filter(consumer_type_id=consumer_type_id)

        if advanced_opt is False:
            for field in ["expected_consumer_increase", "expected_demand_increase"]:
                self.fields[field].widget = forms.HiddenInput()

        # Prevent automatic labels from being generated (to avoid issues with table display)
        for _field_name, field in self.fields.items():
            field.label = ""


ConsumerGroupFormSet = modelformset_factory(ConsumerGroup, form=ConsumerGroupForm, extra=1, can_delete=True)