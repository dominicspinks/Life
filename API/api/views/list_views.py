from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from ..serializers import ListConfigurationSerializer, ListDataSerializer, ListItemSerializer
from ..models import UserModule, ListField, ListFieldRule, ListFieldOption, ListItem
from django.db import transaction
from datetime import datetime
from django.shortcuts import get_object_or_404

class ListConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on list configurations
    Allows users to view, create, update and delete their list configurations
    """
    serializer_class = ListConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        """
        Return lists that belong to the current authenticated user
        """
        return UserModule.objects.filter(user=self.request.user, module__name='list')

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "List creation is handled through the /api/modules/ endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "List deletion is handled through the /api/modules/ endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Update basic module info
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        if serializer.is_valid():
            self.perform_update(serializer)

            # Handle fields update logic
            if 'list_fields' in request.data:
                existing_fields = {field.id: field for field in ListField.objects.filter(user_module=instance)}
                submitted_field_ids = {field_data.get('id') for field_data in request.data.get('list_fields', [])
                                    if 'id' in field_data}

                # Fields to delete (exist in DB but not in submitted data)
                fields_to_delete = set(existing_fields.keys()) - submitted_field_ids
                ListField.objects.filter(id__in=fields_to_delete).delete()

                # Process submitted fields
                for idx, field_data in enumerate(request.data.get('list_fields', [])):
                    field_id = field_data.get('id')

                    if field_id and field_id in existing_fields:
                        # Update existing field
                        field = existing_fields[field_id]
                        field.field_name = field_data.get('field_name', field.field_name)
                        field.field_type_id = field_data.get('field_type', field.field_type_id)
                        field.is_mandatory = field_data.get('is_mandatory', field.is_mandatory)
                        field.order = field_data.get('order', idx)
                        field.save()

                        # Handle rules
                        if 'rules' in field_data:
                            existing_rules = ListFieldRule.objects.filter(list_field=field)
                            existing_rules.delete()

                            for rule_data in field_data.get('rules', []):
                                ListFieldRule.objects.create(
                                    list_field=field,
                                    field_type_rule_id=rule_data.get('field_type_rule')
                                )

                        # Handle options for dropdown fields
                        if field.field_type.name == 'dropdown' and 'options' in field_data:
                            existing_options = ListFieldOption.objects.filter(list_field=field)
                            existing_options.delete()

                            for option_data in field_data.get('options', []):
                                ListFieldOption.objects.create(
                                    list_field=field,
                                    option_name=option_data.get('option_name')
                                )
                    else:
                        # Create new field
                        field = ListField.objects.create(
                            user_module=instance,
                            field_type_id=field_data.get('field_type'),
                            field_name=field_data.get('field_name'),
                            is_mandatory=field_data.get('is_mandatory', False),
                            order=field_data.get('order', idx)
                        )

                        # Create rules
                        for rule_data in field_data.get('rules', []):
                            ListFieldRule.objects.create(
                                list_field=field,
                                field_type_rule_id=rule_data.get('field_type_rule')
                            )

                        # Create options for dropdown fields
                        if field.field_type.name == 'dropdown':
                            for option_data in field_data.get('options', []):
                                ListFieldOption.objects.create(
                                    list_field=field,
                                    option_name=option_data.get('option_name')
                                )

            return Response(self.get_serializer(instance).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for view list configuration with the data
    """
    serializer_class = ListDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        return UserModule.objects.filter(user=self.request.user, module__name='list')

class ListItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on list items
    """
    serializer_class = ListItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        list_id = self.kwargs.get('list_id')

        user_module = get_object_or_404(
            UserModule.objects.filter(user=self.request.user),
            id=list_id
        )

        return ListItem.objects.filter(user_module=user_module)

    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id')
        user_module = UserModule.objects.get(id=list_id, user=self.request.user)
        # Validate field IDs before saving
        field_values = self.request.data.get('field_values', [])
        self._validate_field_values(field_values, list_id)

        serializer.save(user_module=user_module)

    def perform_update(self, serializer):
        list_id = self.kwargs.get('list_id')

        # Validate field IDs before saving
        field_values = self.request.data.get('field_values', [])
        self._validate_field_values(field_values, list_id)

        serializer.save()

    def _validate_field_values(self, field_values, list_id):
        """
        Validate that:
        1. All field IDs belong to this list
        2. Required fields are present
        3. Field values match the expected type
        """
        if not field_values:
            return

        # Get all valid fields for this list
        valid_fields = {
            field.id: field for field in ListField.objects.filter(user_module_id=list_id)
        }

        # Check for required fields
        required_field_ids = {
            field_id for field_id, field in valid_fields.items() if field.is_mandatory
        }
        provided_field_ids = {item.get('field') for item in field_values if 'field' in item}

        missing_required = required_field_ids - provided_field_ids
        if missing_required:
            missing_field_names = [valid_fields[id].field_name for id in missing_required]
            raise serializers.ValidationError({
                "field_values": f"Missing required fields: {', '.join(missing_field_names)}"
            })

        # Validate each field value
        for item in field_values:
            field_id = item['field']

            # Check if field exists in this list
            if field_id not in valid_fields:
                raise serializers.ValidationError({
                    "field_values": f"Field ID {field_id} does not belong to this list"
                })

            # Validate value based on field type
            field = valid_fields[field_id]
            value = item['value']

            # Type-specific validation
            match field.field_type.name:
                case 'number':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        raise serializers.ValidationError({
                            "field_values": f"Field '{field.field_name}' must be a number"
                        })

                case 'date':
                    try:
                        if value:  # Allow empty dates for non-mandatory fields
                            datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise serializers.ValidationError({
                            "field_values": f"Field '{field.field_name}' must be a valid date in YYYY-MM-DD format"
                        })

                case 'dropdown':
                    # Validate dropdown option exists
                    if value:
                        valid_options = ListFieldOption.objects.filter(
                            list_field_id=field_id
                        ).values_list('option_name', flat=True)

                        if value not in valid_options:
                            raise serializers.ValidationError({
                                "field_values": f"'{value}' is not a valid option for field '{field.field_name}'"
                            })