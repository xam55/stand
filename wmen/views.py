from django.core.paginator import EmptyPage
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Report
from .serializers import ReportSerializer, WomenSerializer


class WomenApiView(APIView):
    @extend_schema(parameters=[OpenApiParameter("page", int, description="Номер страницы, с 1")])
    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            raise ValidationError({"page": "Номер страницы должен быть числом."})

        try:
            data = services.get_women_page(page=page)
        except EmptyPage:
            raise NotFound("Такой страницы нет.")

        return Response({
            "count": data["count"],
            "pages": data["pages"],
            "page": data["page"],
            "posts": WomenSerializer(data["results"], many=True).data,
        })

    def post(self, request):
        serializer = WomenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        woman = services.create_woman(data=serializer.validated_data)

        return Response(
            {"post": WomenSerializer(woman).data},
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        serializer = WomenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        woman = services.update_woman(pk=pk, data=serializer.validated_data)
        return Response({"post": WomenSerializer(woman).data})

    def delete(self, request, pk):
        services.delete_woman(pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReportCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(request=None, responses={202: ReportSerializer})
    def post(self, request):
        report, created = services.request_report(user=request.user)
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_202_ACCEPTED if created else status.HTTP_200_OK,
        )


class ReportDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses={200: ReportSerializer})
    def get(self, request, pk):
        try:
            report = services.get_user_report(user=request.user, pk=pk)
        except Report.DoesNotExist:
            raise NotFound("Отчёт не найден.")
        return Response(ReportSerializer(report).data)
