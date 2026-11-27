def validate(self, attrs):
    instance = LeaveRequest(employee=self.context['request'].user, **attrs)
    try:
        instance.clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
    balance = getattr(self.context['request'].user, 'leave_balance', None)
    if balance and instance.business_days > balance.available_days:
        raise serializers.ValidationError('Saldo ferie insufficiente.')
    return attrs
