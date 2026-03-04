
from rest_framework import serializers
from .models import User, Company
from django.contrib.auth.password_validation import validate_password


class CompanyRegisterSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        company = Company.objects.create(
            name=validated_data['company_name']
        )

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            company=company,
            role='OWNER'
        )

        return user
    
from rest_framework import serializers
from .models import Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('company', 'created_by')


class TaskSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('company',)
        