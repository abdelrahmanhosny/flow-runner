from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from runner.tasks import start_flow_task


class RunnerStartFlow(APIView):
    def post(self, request):
        flow_uuid = request.POST.get('flow_uuid', None)
        flow_repo_url = request.POST.get('flow_repo_url', None)

        if not flow_uuid or not flow_repo_url:
            return Response('Missing parameters', status=status.HTTP_400_BAD_REQUEST)

        # start_flow_task.delay(flow_uuid, flow_repo_url)

        return Response('Received', status=status.HTTP_202_ACCEPTED)
