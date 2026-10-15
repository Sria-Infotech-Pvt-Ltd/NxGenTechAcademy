import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactUsSerializer, DemoScheduleSerializer

logger = logging.getLogger(__name__)


class DemoSubmissionThrottle(SimpleRateThrottle):
    """Limits demo and contact form submissions to 10 requests per minute per IP."""
    scope = 'demo_submission'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class ContactUsView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [DemoSubmissionThrottle]

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()

            # Send Email to Admin (safe non-blocking fail)
            try:
                subject = "New Contact Us Submission"
                message = f"""
                New contact form submission:

                Name: {contact.name}
                Email: {contact.email}
                Mobile: {contact.phone}
                Message:
                {contact.message}
                """
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error("Failed to send contact us email notification: %s", str(e), exc_info=False)

            return Response(
                {"message": "Contact form submitted successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleDemoView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [DemoSubmissionThrottle]

    def post(self, request):
        serializer = DemoScheduleSerializer(data=request.data)

        if serializer.is_valid():
            demo = serializer.save()

            # Email to Admin (safe non-blocking fail)
            try:
                send_mail(
                    "New Demo Enquiry",
                    f"""
New Demo Enquiry:

Name: {demo.full_name}
Email: {demo.email}
Phone: {demo.phone}
Course: {demo.course}
Message: {demo.message or "No message provided"}
""",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error("Failed to send demo enquiry email notification: %s", str(e), exc_info=False)

            return Response(
                {"success": True, "message": "Demo enquiry submitted successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)