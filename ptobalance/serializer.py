from rest_framework import serializers
from .models import PTOBalance
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from yearofexperience.models import YearOfExperience
from accuralrates.models import AccrualRates
class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = '__all__'

class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pay_Frequency
        fields = '__all__'

class YearOfExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOfExperience
        fields = '__all__'


class PTOBalanaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'ptobalance-detail')
    employee_type = EmployeeTypeSerializer(read_only=True)
    pay_frequency = PayFrequencySerializer(read_only=True)
    year_of_experience = YearOfExperienceSerializer(read_only=True)
    class Meta:
        model = PTOBalance
        fields ='__all__'
    def create(self, validated_data):
        user = validated_data['user']
        employeetype = validated_data['employee_type']
        payfrequency = validated_data['pay_frequency']

        year_exp = YearOfExperience.objects.filter(user=user).first()
        if year_exp:
            validated_data['year_of_experience'] = year_exp
            yoe = year_exp.years_of_experience

            if yoe < 1:
                x = 1
            elif yoe < 2:
                x = 2
            elif yoe < 3:
                x = 3
            elif yoe < 4:
                x = 4
            elif yoe < 5:
                x = 5
            elif yoe < 6:
                x = 6
            elif yoe < 7:
                x = 7
            elif yoe < 8:
                x = 8
            elif yoe < 9:
                x = 9
            elif yoe < 10:
                x = 10
            else:
                x = 11

            accrualrate = AccrualRates.objects.filter(
                employee_type=employeetype,
                pay_frequency=payfrequency,
                year_of_experience=x
            ).first()

            validated_data['accrual_rate'] = accrualrate

        return super().create(validated_data)