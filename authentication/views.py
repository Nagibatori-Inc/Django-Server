from django.http import Http404
from knox.models import AuthToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Profile
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.serializers import ProfileSerializer, SignUpRequestSerializer


class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({"err_msg": "no data was sent"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = serializer.save()
        auth_token = AuthToken.objects.create(profile.user)[1]

        return Response({
            "profile": ProfileSerializer(profile).data,
            "token": auth_token
        }, status=status.HTTP_200_OK)


# TODO rewrite with ViewSet
class ProfileView(APIView):
    permission_classes = [IsProfileOwnerOrReadOnly]

    def get_profile(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist as ex:
            raise Http404

        return profile

    def get(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(profile_id)

        return Response(ProfileSerializer(profile).data, status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(pk=profile_id)
        self.check_object_permissions(request, profile)

        new_profile_data = request.data
        print(new_profile_data)
        if not new_profile_data:
            return Response({"err_msg": "no data was sent"}, status=status.HTTP_400_BAD_REQUEST)

        updated_profile = ProfileSerializer(profile, data=new_profile_data)
        updated_profile.is_valid(raise_exception=True)
        updated_profile.save()

        return Response(updated_profile.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(profile_id)
        self.check_object_permissions(request, profile)

        profile.is_deleted = True
        profile.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
