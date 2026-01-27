# library import
from rest_framework.views import APIView
from rest_framework.response import Response
# local app import
from .models import WorkItemModel
from .serializers import WorkItemSerializer
from django.db import transaction
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from redis.exceptions import ConnectionError as RedisConnectionError


class LoginApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        requires post method to create a token everytime for user
        :param request: request header
        :return: response with token
        """
        username = request.data.get("username")
        password = request.data.get("password")
        print(f"Authenticating user {username}")
        user = authenticate(username=username, password=password)
        if not user:  # if invalid creds return invalid 401
            print(f"{user = }")
            return Response(
                {
                    'error': "invalid username or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh_token = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh_token.access_token),
                'refresh': str(refresh_token)
            },
            status=status.HTTP_201_CREATED
        )


class RefreshTokenAPIView(APIView):
    """
    this is responsible for return of the access token based on the existing refresh token, if empty login may require again
    """
    # refresh token not require any authentication if you have a valid token, so allow anonymous request to get the access token
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                data={'detail': "refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # return the access token based on the refresh token
            refresh = RefreshToken(refresh_token)
            try:
                return Response(
                    data={
                        'access': str(refresh.access_token)
                    }
                )
            except Exception:
                return Response(
                    data={
                        'detail': "invalid refresh token"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )


class CreateSingleWorkItem(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pid):
        """
        Creates a single work item in the database.

        Args:
            request: The POST request containing the work item data
            pid: The process ID of the work item

        Returns:
            Response: The HTTP response containing the created work item data in JSON format

        Raises:
            ValidationError: If the request data is invalid
        """
        if not isinstance(pid, str):
            return Response(
                data={
                    'detail': "pid must be string value"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        pid_value = pid.split("=", 1)[1]
        print(f"{pid_value = }")
        # ensure the incoming data/payload is a single record to perform single item insertion
        if isinstance(request.data, list):
            return Response(
                data={
                    'detail': "bulk insert is not allowed on this endpoint"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        print("request payload => ", request.data)

        # inject the pid from provided URL,
        payload = request.data.copy()
        payload['process_id'] = pid_value
        # validate the payload on the services level, whether the payload contains all the required fields
        # and each fields dtype and max length
        serializer = WorkItemSerializer(data=payload)  # many=False by default

        # raise ex if validation fails
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # serializer.validated_data
            item = serializer.save()  # created resource save to db
            # TODO: publish kafka

        serializer_response = WorkItemSerializer(item)  # data= is only for input
        return Response(
            data=serializer_response.data,
            status=status.HTTP_201_CREATED
        )


class CreateBulkInsert(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pid):
        if not pid:
            return Response(
                data={

                    'detail': "process id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        print(f"provided pid = {pid}")
        # inject the pid to the payload
        if pid.startswith("pid="):
            pid_value = pid.split("=", 1)[1]
        else:
            pid_value = pid

        if not isinstance(request.data, list):
            return Response(
                data={
                    'detail': "payload required to be list[dict]"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = []
        for item in request.data:
            obj = item.copy()
            obj['process_id'] = pid_value
            payload.append(obj)

        serializer = WorkItemSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            instances = serializer.save() # saved to db
            # TODO kafka

        # respond back client with the
        serializer_response = WorkItemSerializer(instances, many=True)
        return Response(
            data={
                "pid": pid_value,
                "count": len(serializer_response.data),
                "result": serializer_response.data,

            },
            status=status.HTTP_201_CREATED
        )


class GetWorkItemByDateRange(APIView):
    permission_classes = [IsAuthenticated]  # authenticate user with the token

    def post(self, request):
        """
        payload = {
            "start_date": "",
            "end_date": "",
            "pid": "",

            "state":"", (optional)
            "status":"", (optional)
        }

        :param request:
        :return:
        """
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        pid = request.data.get("pid")
        state = request.data.get("state")
        w_status = request.data.get("status")

        if not (start_date and end_date and pid):
            return Response(
                data={
                    'detail': "pid, start_date & end_date required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = WorkItemModel.objects.filter(process_id=pid,created_at__date__range=[start_date, end_date])

        if state:
            print(f"{state=}")
            queryset = queryset.filter(state=state)

        if w_status:
            print(f"{w_status=}")
            queryset = queryset.filter(status=w_status)

        total_items = queryset.count()
        serializer_response = WorkItemSerializer(queryset, many=True)

        return Response(
            data={
                "count": total_items,
                "result": serializer_response.data
            },
            status=status.HTTP_200_OK
        )


class GetWorkItemByID(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workitem_id):
        print(f"{workitem_id= }")

        # ===== step -1 first try to get from redis =====
        print(f"Looking for data in cache first..")
        cache_key = f"workitem_id:{workitem_id}"

        try:
            cached_data = cache.get(cache_key)
        except RedisConnectionError:
            print("[Exception] Connection to redis to could not be established.")
            cached_data = None

        if cached_data:
            print(f"Data fetched from cache, instead of db")
            return Response(
                data=cached_data,
                status=status.HTTP_200_OK
            )

        # ===== Step 2 query the db get the work-item if not found in cache=====
        try:
            print("Fetching data from db...")
            workitem = get_object_or_404(WorkItemModel,
                                         workitem_id=workitem_id
                                         )
        except Exception as ex:
            return Response(
                {'detail': f"{str(ex)}"},
                status=status.HTTP_200_OK
            )

        # ===== step 3 prepare response to clint =====
        print("preparing response...")
        serializer_response = WorkItemSerializer(workitem, many=False)  # many is False by default

        # ===== step 4 save to cache =====
        # if not in key save to cache temporarily
        try:
            print("saving to cache..")
            cache.set(cache_key, serializer_response.data, timeout=300)
            print("data save to cached for 5 mins.")
        except RedisConnectionError as ex:
            print(f"Redis connection couldnt be established due to  {ex}")
            cached_data = None

        return Response(
            data=serializer_response.data,
            status=status.HTTP_200_OK
        )


