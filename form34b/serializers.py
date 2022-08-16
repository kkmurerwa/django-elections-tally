from rest_framework import serializers
from form34b.models import Candidate, FormDetails


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            'id',
            'name',
            'keyword',
            'party',
            'votes',
            'votes_percentage'
        ]


class FormDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormDetails

        fields = [
            'id',
            'county',
            'registered_voters',
            'valid_votes',
            'spoilt_votes',
            'voter_turnout',
            "odinga",
            "ruto",
            "wajackoyah",
            "mweure"
        ]

    def validate_votes(self):
        message = ""
        is_valid = True

        # Calculate total votes cast
        total_votes = self.validated_data['valid_votes'] + self.validated_data['spoilt_votes']

        # Check if registered voters is greater than valid votes
        if total_votes > self.validated_data['registered_voters']:
            message = "Total votes cannot be more than registered voters"
            is_valid = False
        elif self.validated_data['spoilt_votes'] > self.validated_data['valid_votes']:
            message = "Spoilt votes cannot be more than valid votes"
            is_valid = False

        return {"is_valid": is_valid, "message": message}

    def calculate_voter_turnout(self):

        # Calculate new total turnout percentage
        total_voters = self.validated_data['registered_voters']
        valid_votes = self.validated_data['valid_votes']
        spoiled_votes = self.validated_data['spoilt_votes']

        turnout_percentage = (valid_votes + spoiled_votes) / total_voters * 100.0

        self.validated_data['voter_turnout'] = turnout_percentage
