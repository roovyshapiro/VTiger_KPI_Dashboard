# import serializer from rest_framework
from rest_framework import serializers
 
# import model from models.py
from .models import Opportunities
 
# Create a model serializer
class DealSerializer(serializers.ModelSerializer):
    # specify model and fields
    class Meta:
        model = Opportunities
        fields = (
                    'opp_id', 
                    'opp_url_id',
                    'opp_amount',
                    'contact_id',
                    'opp_no',
                    'opp_name',
                    'opp_stage',
                    'createdtime',
                    'modifiedtime',
                    'created_user_id', 
                    'modifiedby',
                    'assigned_user_id',
                    'qualified_by_id',
                    'qualified_by_name',
                    'assigned_username',
                    'assigned_groupname',
                    'modified_username',
                    'current_stage_entry_time',
                    'demo_scheduled_changed_at',
                    'demo_given_changed_at',
                    'quote_sent_changed_at',
                    'pilot_changed_at',
                    'needs_analysis_changed_at',
                    'closed_lost_changed_at',
                    'closed_won_changed_at',
                    'date_created',
                    'date_modified',
                    )