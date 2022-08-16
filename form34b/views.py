from typing import Callable, Any

from django.db.models import Exists, OuterRef, Q, Count, Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from form34b.models import Candidate, FormDetails, TallyResults
from form34b.serializers import CandidateSerializer, FormDetailsSerializer

allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'COPY', 'HEAD', 'OPTIONS', 'LINK',
                   'UNLINK', 'PURGE', 'LOCK', 'UNLOCK', 'PROPFIND', 'VIEW']


@api_view(allowed_methods)
def is_server_up(request):
    if request.method == 'GET':
        return Response(
            {
                "success": True,
                "message": "Server is up",
                "data": None
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "success": False,
                "message": "Method not allowed",
                "data": None
            },
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(allowed_methods)
def candidates(request):
    if request.method == 'GET':
        # Get all candidates
        candidates_list = Candidate.objects.all()

        # Serialize data
        serializer = CandidateSerializer(candidates_list, many=True)

        return Response(
            {
                "success": True,
                "message": "Candidates returned successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        # Create a serializer
        serializer = CandidateSerializer(data=request.data)

        # Add the data to db
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Candidate added successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {
                    "success": False,
                    "message": f"Could not create candidate because of the following error: {serializer.errors}",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {
                "success": False,
                "message": "Method not allowed",
                "data": None
            },
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(allowed_methods)
def candidate(request, id):
    if request.method == 'GET':
        try:
            # Get candidate
            current_candidate = Candidate.objects.get(id=id)

            # Serialize data
            serializer = CandidateSerializer(current_candidate)

            return Response(
                {
                    "success": True,
                    "message": "Candidate returned successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Candidate.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Candidate does not exist",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
    elif request.method == 'DELETE':
        try:
            current_candidate = Candidate.objects.get(id=id)
            current_candidate.delete()

            return Response(
                {
                    "success": True,
                    "message": "Candidate deleted successfully",
                    "data": None
                },
                status=status.HTTP_200_OK
            )
        except Candidate.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Candidate not found",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
    elif request.method == 'PATCH':
        # Update candidate
        current_candidate = Candidate.objects.get(id=id)
        serializer = CandidateSerializer(current_candidate, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Candidate updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {
                    "success": False,
                    "message": f"Could not update candidate because of the following error: {serializer.errors}",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {
                "success": False,
                "message": "Method not allowed",
                "data": None
            },
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(allowed_methods)
def forms(request):
    if request.method == 'GET':
        # Get all forms
        forms_list = FormDetails.objects.all()

        # Serialize data
        serializer = FormDetailsSerializer(forms_list, many=True)

        return Response(
            {
                "success": True,
                "message": "Forms returned successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        temp_dict = {
            'county': request.data['county'],
            'registered_voters': request.data['registered_voters'].replace(',', ''),
            'valid_votes': request.data['valid_votes'].replace(',', ''),
            'spoilt_votes': request.data['spoilt_votes'].replace(',', ''),
            'odinga': request.data['odinga'].replace(',', ''), 'ruto': request.data['ruto'].replace(',', ''),
            'wajackoyah': request.data['wajackoyah'].replace(',', ''),
            'mweure': request.data['mweure'].replace(',', '')
        }

        # Create a serializer
        serializer = FormDetailsSerializer(data=temp_dict)

        # Add the data to db
        if serializer.is_valid():

            # Calculate the total turnout percentage
            serializer.calculate_voter_turnout()
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Form added successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {
                    "success": False,
                    "message": f"Could not create form because of the following error: {serializer.errors}",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {
                "success": False,
                "message": "Method not allowed",
                "data": None
            },
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(allowed_methods)
def forms_summary(request):
    if request.method == 'GET':
        # Get all forms
        forms_list = FormDetails.objects.aggregate(
            total_counties=Count('county'),
            total_registered_voters=Sum('registered_voters'),
            total_valid_votes=Sum('valid_votes'),
            total_spoilt_votes=Sum('spoilt_votes'),
            total_odinga=Sum('odinga'),
            total_ruto=Sum('ruto'),
            total_wajackoyah=Sum('wajackoyah'),
            total_mweure=Sum('mweure')
        )

        round_off: Callable[[Any], Any] = lambda x: f"{round(x, 3)}%"

        comma_separated: Callable[[Any], Any] = lambda x: format(x, ',d')

        tally_response = {
            'total_counties': forms_list['total_counties'],
            'total_registered_voters': comma_separated(forms_list['total_registered_voters']),
            'total_valid_votes': {
                'value': comma_separated(forms_list['total_valid_votes']),
                'percentage': round_off(forms_list['total_valid_votes'] / forms_list['total_registered_voters'] * 100)
            },
            'total_spoilt_votes': {
                'count': comma_separated(forms_list['total_spoilt_votes']),
                'percentage': round_off(forms_list['total_spoilt_votes'] / forms_list['total_valid_votes'] * 100)
            },
            'raila_odinga': {
                'total': comma_separated(forms_list['total_odinga']),
                'percentage': round_off(forms_list['total_odinga'] / forms_list['total_valid_votes'] * 100)
            },
            'william_ruto': {
                'total': comma_separated(forms_list['total_ruto']),
                'percentage': round_off(forms_list['total_ruto'] / forms_list['total_valid_votes'] * 100)
            },
            'wajackoyah': {
                'total': comma_separated(forms_list['total_wajackoyah']),
                'percentage': round_off(forms_list['total_wajackoyah'] / forms_list['total_valid_votes'] * 100)
            },
            'mweure': {
                'total': comma_separated(forms_list['total_mweure']),
                'percentage': round_off(forms_list['total_mweure'] / forms_list['total_valid_votes'] * 100)
            }
        }

        # forms_list = FormDetails.objects.values('ruto')\
        #     .annotate(
        #     registered_voters=Sum('registered_voters'),
        #     valid_votes=Sum('valid_votes'),
        #     spoilt_votes=Sum('spoilt_votes')
        # )

        # Serialize data
        # serializer = FormDetailsSerializer(forms_list, many=True)

        return Response(
            {
                "success": True,
                "message": "Forms returned successfully",
                "data": tally_response
            },
            status=status.HTTP_200_OK
        )


@api_view(allowed_methods)
def form(request, id):
    if request.method == 'GET':
        try:
            # Get form
            current_form = FormDetails.objects.get(id=id)

            # Serialize data
            serializer = FormDetailsSerializer(current_form)

            return Response(
                {
                    "success": True,
                    "message": "Form returned successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except FormDetails.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Form does not exist",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
    elif request.method == 'DELETE':
        try:
            current_form = FormDetails.objects.get(id=id)
            current_form.delete()

            return Response(
                {
                    "success": True,
                    "message": "Form deleted successfully",
                    "data": None
                },
                status=status.HTTP_200_OK
            )
        except FormDetails.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Form not found",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
    elif request.method == 'PATCH':
        try:
            # Update form
            current_form = FormDetails.objects.get(id=id)
            serializer = FormDetailsSerializer(current_form, data=request.data, partial=True)

            if serializer.is_valid():

                # Validate votes
                are_votes_valid = serializer.validate_votes()

                if are_votes_valid.get("is_valid"):
                    # Calculate new total turnout percentage
                    serializer.calculate_voter_turnout()
                    serializer.save()

                    return Response(
                        {
                            "success": True,
                            "message": "Form updated successfully",
                            "data": serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            "success": False,
                            "message": are_votes_valid.get("message"),
                            "data": None
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response(
                    {
                        "success": False,
                        "message": f"Could not update form because of the following error: {serializer.errors}",
                        "data": None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except FormDetails.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Form not found",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {
                "success": False,
                "message": "Method not allowed",
                "data": None
            },
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(allowed_methods)
def tallies(request):
    if request.method == 'GET':
        # Get all tallies
        results = TallyResults.objects.raw('SELECT * FROM sqlite_master')

        # Serialize data
        # serializer = TallyDetailsSerializer(tallies_list, many=True)

        # return Response(
        #     {
        #         "success": True,
        #         "message": "Tallies returned successfully",
        #         "data": serializer.data
        #     },
        #     status=status.HTTP_200_OK
        # )
    # elif request.method == 'POST':
    #     # Create a serializer
    #     serializer = TallySerializer(data=request.data)
    #
    #     # Add the data to db
    #     if serializer.is_valid():
    #
    #         # Calculate the total turnout percentage
    #         serializer.calculate_voter_turnout()
    #         serializer.save()
    #
    #         return Response(
    #             {
    #                 "success": True,
    #                 "message": "Tally added successfully",
    #                 "data": serializer.data
    #             },
    #             status=status.HTTP_201_CREATED
    #         )
    #
    #     else:
    #         return Response(
    #             {
    #                 "success": False,
    #                 "message": f"Could not create tally because of the following error: {serializer.errors}",
    #                 "data": None
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    # else:
    #     return Response(
    #         {
    #             "success": False,
    #             "message": "Method not allowed",
    #             "data": None
    #         },
    #         status.HTTP_405_METHOD_NOT_ALLOWED
    #     )
