import { ListField } from "@core/models/list.model";

export function getFieldPayload(field: ListField) {
    return {
        ...field,
        rules: field.rules.map(r => ({
            field_type_rule: r.field_type_rule.id
        }))
    };
}