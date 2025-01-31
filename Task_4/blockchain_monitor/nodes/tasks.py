from celery import shared_task
from .models import BlockchainNode
import requests
from django.utils import timezone

@shared_task
def check_node_health():
    nodes = BlockchainNode.objects.filter(is_active=True)
    for node in nodes:
        try:
            response = requests.get(f"{node.url}/health", timeout=5)
            data = response.json()
            
            node.status = 'healthy' if response.status_code == 200 else 'unhealthy'
            node.uptime = data.get('uptime', node.uptime)
            node.resource_utilization = {
                'cpu': data.get('cpu_usage'),
                'memory': data.get('memory_usage'),
                'storage': data.get('storage_usage')
            }
            node.last_checked = timezone.now()
            node.save()
            
        except Exception as e:
            node.status = 'unreachable'
            node.save()