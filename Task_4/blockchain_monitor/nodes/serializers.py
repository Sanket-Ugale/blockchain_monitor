from rest_framework import serializers
from .models import BlockchainNode
from django.core.validators import URLValidator

class BlockchainNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainNode
        fields = '__all__'
        extra_kwargs = {
            'name': {
                'min_length': 3,
                'max_length': 100
            },
            'url': {
                'validators': [URLValidator(schemes=['http', 'https'])]
            }
        }

    def validate_url(self, value):
        validator = URLValidator()
        validator(value)
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must include http:// or https://")
        return value
    
    def validate_resource_utilization(self, value):
        required_keys = {'cpu', 'memory', 'storage'}
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                "Resource utilization must contain cpu, memory, and storage metrics"
            )
        return value