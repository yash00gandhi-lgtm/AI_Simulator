from rest_framework import serializers
from .models import Resume, Question, Answer
from django.contrib.auth import get_user_model

class ResumeSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Resume
        fields = ['id', 'file', 'parsed_text']
        read_only_fields = ['parsed_text']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'difficulty', 'role']

class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField()

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # 🔥 FIX
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

