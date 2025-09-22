from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

class DeleteProfileView(APIView):
    """
    API endpoint for deleting the authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Your account has been deleted."}, status=status.HTTP_204_NO_CONTENT)
